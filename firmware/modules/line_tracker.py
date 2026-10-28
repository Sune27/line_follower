# ==============================================================================
# LINE_TRACKER.PY – BỘ ĐIỀU KHIỂN DÒ LINE PID MƯỢT (OOP)
# ==============================================================================
# Thuật toán PID chạy mượt liên tục kết hợp Bơm Gia Tốc Cua (Corner Boost):
#   - Đi thẳng (Mắt 3): Chạy êm quanh tốc độ cơ sở (LINE_BASE_SPEED = 62%).
#   - Lệch vừa (Mắt 2 / Mắt 4): Tăng gia tốc bánh ngoài lên >= 78%, bánh trong 0%.
#   - Lệch rìa ngoài (Mắt 1 / Mắt 5): Bơm gia tốc bánh ngoài 90%, bánh trong -65%
#     để vượt ngưỡng ma sát nghỉ và cuốn đầu xe quay vào tâm vạch mượt mà.
# ==============================================================================

import time
import config

if not hasattr(time, "ticks_ms"):
    time.ticks_ms = lambda: int(time.time() * 1000)
if not hasattr(time, "ticks_diff"):
    time.ticks_diff = lambda a, b: a - b


class LineTracker:
    MAP_ERROR = {
        0b10000: -4.0,
        0b11000: -3.2,
        0b11100: -3.5,
        0b11110: -3.8,
        0b01000: -2.0,
        0b01100: -1.0,
        0b00100:  0.0,
        0b00110:  1.0,
        0b00010:  2.0,
        0b00011:  3.2,
        0b00111:  3.5,
        0b01111:  3.8,
        0b00001:  4.0,
        0b01110:  0.0,
    }

    def __init__(self, motor_driver):
        self.motor = motor_driver

        self.min_speed = int(getattr(config, "LINE_MIN_SPEED", 55))
        self.base_speed = int(getattr(config, "LINE_BASE_SPEED", 62))
        self.startup_speed = int(getattr(config, "LINE_STARTUP_SPEED", 88))
        self.startup_duration_ms = int(getattr(config, "LINE_STARTUP_DURATION_MS", 450))

        # Gia tốc bẻ lái ở Mắt 2/4 và Mắt 1/5
        self.mid_turn_outer_speed = int(getattr(config, "MID_TURN_OUTER_SPEED", 78))
        self.mid_turn_inner_speed = int(getattr(config, "MID_TURN_INNER_SPEED", 0))
        self.corner_turn_outer_speed = int(getattr(config, "CORNER_TURN_OUTER_SPEED", 90))
        self.corner_turn_inner_speed = int(getattr(config, "CORNER_TURN_INNER_SPEED", -65))

        # Thông số PID
        self.kp = float(getattr(config, "PID_KP", 7.5))
        self.ki = float(getattr(config, "PID_KI", 0.04))
        self.kd = float(getattr(config, "PID_KD", 4.5))
        self.filter_alpha = float(getattr(config, "PID_FILTER_ALPHA", 0.85))

        self.lost_line_timeout_ms = int(getattr(config, "LINE_LOST_TIMEOUT_MS", 3000))
        self.search_outer_speed = int(getattr(config, "LINE_SEARCH_OUTER_SPEED", 90))
        self.search_reverse_speed = int(getattr(config, "LINE_SEARCH_REVERSE_SPEED", -68))
        self.auto_stop_on_cross = bool(getattr(config, "AUTO_STOP_ON_CROSS", False))

        self.left_scale = float(getattr(config, "MOTOR_LEFT_SCALE", 1.0))
        self.right_scale = float(getattr(config, "MOTOR_RIGHT_SCALE", 1.0))

        self.is_active = False
        self.last_action = "STANDBY"
        self.start_ticks = 0
        self.reset_pid()

    def reset_pid(self):
        self.current_error = 0.0
        self.smooth_error = 0.0
        self.prev_smooth_error = 0.0
        self.last_valid_error = 0.0
        self.integral = 0.0
        self.pid_output = 0.0
        self.lost_line_start_time = 0

    def _drive(self, left, right):
        out_l = int(round(left * self.left_scale))
        out_r = int(round(right * self.right_scale))
        self.motor.set_differential(out_l, out_r)
        return (out_l, out_r)

    def start(self, speed=None):
        if speed is not None:
            self.base_speed = max(40, min(98, int(speed)))
        self.reset_pid()
        self.is_active = True
        self.start_ticks = time.ticks_ms()
        self.last_action = "START PID"
        self._drive(self.startup_speed, self.startup_speed)
        print(f"[Tracker PID] ▶ BẮT ĐẦU DÒ LINE | Base={self.base_speed}%, Kp={self.kp}, Ki={self.ki}, Kd={self.kd}")

    def stop(self):
        self.is_active = False
        self.reset_pid()
        self.last_action = "STOPPED"
        self.motor.stop()
        print("[Tracker PID] ⏹ ĐÃ DỪNG XE")

    def set_params(self, base_speed=None, kp=None, ki=None, kd=None, left_scale=None, right_scale=None):
        if base_speed is not None:
            self.base_speed = max(40, min(98, int(base_speed)))
        if kp is not None:
            self.kp = float(kp)
        if ki is not None:
            self.ki = float(ki)
        if kd is not None:
            self.kd = float(kd)
        if left_scale is not None:
            self.left_scale = max(0.3, min(1.0, float(left_scale)))
        if right_scale is not None:
            self.right_scale = max(0.3, min(1.0, float(right_scale)))

    def _compute_error(self, sensors):
        s1, s2, s3, s4, s5 = sensors[0], sensors[1], sensors[2], sensors[3], sensors[4]
        bitmask = (s1 << 4) | (s2 << 3) | (s3 << 2) | (s4 << 1) | s5

        if bitmask == 0b11111:
            return (0.0, "CROSS_LINE")
        if bitmask == 0b00000:
            return (0.0, "LOST_LINE")

        if bitmask in self.MAP_ERROR:
            err = self.MAP_ERROR[bitmask]
        else:
            total = s1 + s2 + s3 + s4 + s5
            err = ((-4.0 * s1) + (-2.0 * s2) + (0.0 * s3) + (2.0 * s4) + (4.0 * s5)) / total

        if err != 0.0:
            self.last_valid_error = err
        elif bitmask == 0b00100:
            self.last_valid_error *= 0.4

        return (err, "TRACKING")

    def update(self, sensors, now_ms=None):
        if not self.is_active:
            return (0, 0, "IDLE")

        if now_ms is None:
            now_ms = time.ticks_ms()

        is_startup = (
            self.startup_duration_ms > 0
            and time.ticks_diff(now_ms, self.start_ticks) < self.startup_duration_ms
        )
        current_base = self.startup_speed if is_startup else self.base_speed

        raw_error, mode = self._compute_error(sensors)

        # 1. Xử lý khi cảm biến báo 00000 (Lọt khe giữa 2 đèn hoặc trôi quá Mắt 1/5)
        if mode == "LOST_LINE":
            if self.lost_line_start_time == 0:
                self.lost_line_start_time = now_ms
            lost_ms = time.ticks_diff(now_ms, self.lost_line_start_time)

            if lost_ms >= self.lost_line_timeout_ms:
                self.stop()
                self.last_action = "MẤT LINE - DỪNG"
                return (0, 0, "MẤT LINE - DỪNG")

            # Nếu vừa ở tâm S3 (|last_valid_error| < 1.0) -> Đi tiến tiếp
            if abs(self.last_valid_error) < 1.0:
                self.last_action = "LỌT KHE TÂM -> TIẾN"
                self._drive(current_base, current_base)
                return (current_base, current_base, self.last_action)

            # Nếu vừa ở Mắt 2/4 (< 3.0) và mới lọt khe < 150ms -> Đẩy mạnh bánh ngoài (78%), bánh trong 0%
            if abs(self.last_valid_error) < 3.0 and lost_ms < 150:
                boost_mid = max(78, self.mid_turn_outer_speed)
                if self.last_valid_error < 0:
                    self.last_action = "ĐÓN LINE TRÁI"
                    self._drive(0, boost_mid)
                    return (0, boost_mid, self.last_action)
                else:
                    self.last_action = "ĐÓN LINE PHẢI"
                    self._drive(boost_mid, 0)
                    return (boost_mid, 0, self.last_action)

            # Nếu vừa lệch ra Mắt 1 hoặc Mắt 5 (|last_valid_error| >= 3.0) -> Bơm 90% bánh ngoài, -68% bánh trong!
            if self.last_valid_error < 0:
                self.last_action = "XOAY MẠNH TÌM TRÁI"
                self._drive(self.search_reverse_speed, self.search_outer_speed)
                return (self.search_reverse_speed, self.search_outer_speed, self.last_action)
            else:
                self.last_action = "XOAY MẠNH TÌM PHẢI"
                self._drive(self.search_outer_speed, self.search_reverse_speed)
                return (self.search_outer_speed, self.search_reverse_speed, self.last_action)
        else:
            self.lost_line_start_time = 0

        # 2. Xử lý khi gặp vạch ngang (11111)
        if mode == "CROSS_LINE":
            if self.auto_stop_on_cross:
                self.stop()
                return (0, 0, "STOPPED_CROSS")
            self.last_action = "CROSS_LINE"
            self._drive(current_base, current_base)
            return (current_base, current_base, "CROSS_LINE")

        # 3. Tính toán PID (P - I - D) & Bơm gia tốc theo vùng lệch
        smooth_err = (self.filter_alpha * raw_error) + ((1.0 - self.filter_alpha) * self.smooth_error)

        # Khâu P
        p_term = self.kp * smooth_err

        # Khâu I (kèm xóa tích phân khi qua tâm Zero-Crossing)
        if self.ki == 0.0:
            self.integral = 0.0
            i_term = 0.0
        else:
            if abs(smooth_err) < 0.1 or (smooth_err * self.prev_smooth_error < 0):
                self.integral = 0.0
            else:
                self.integral = max(-20.0, min(20.0, self.integral + smooth_err))
            i_term = self.ki * self.integral

        # Khâu D
        derivative = smooth_err - self.prev_smooth_error
        d_term = self.kd * derivative

        self.prev_smooth_error = smooth_err
        self.smooth_error = smooth_err
        self.current_error = round(smooth_err, 2)

        abs_err = abs(smooth_err)
        pid_val = p_term + i_term + d_term
        self.pid_output = round(pid_val, 2)

        if abs_err <= 1.2:
            # VÙNG TÂM (Mắt 3, hoặc Mắt 2+3 / 3+4): Chạy êm quanh base_speed (62%)
            speed_l = max(self.min_speed, min(92, int(round(current_base + pid_val))))
            speed_r = max(self.min_speed, min(92, int(round(current_base - pid_val))))
            self.last_action = "ĐI THẲNG BÁM TÂM"

        elif abs_err <= 2.6:
            # VÙNG LỆCH VỪA (Mắt 2 hoặc Mắt 4):
            # Tăng gia tốc bánh ngoài lên >= 78%, hạ bánh trong về 0% để bẻ lái khỏe!
            outer_spd = max(self.mid_turn_outer_speed, min(92, int(current_base + abs(pid_val))))
            if smooth_err < 0:
                speed_l = self.mid_turn_inner_speed
                speed_r = outer_spd
                self.last_action = "CUA TRÁI (MẮT 2)"
            else:
                speed_l = outer_spd
                speed_r = self.mid_turn_inner_speed
                self.last_action = "CUA PHẢI (MẮT 4)"

        else:
            # VÙNG RÌA NGOÀI (Mắt 1 hoặc Mắt 5 - |err| >= 3.0):
            # Bơm gia tốc tối đa cho bánh ngoài (90%) + Bánh trong lùi khỏe (-65%)
            outer_max = max(self.corner_turn_outer_speed, min(96, int(current_base + abs(pid_val) * 1.2)))
            inner_rev = self.corner_turn_inner_speed
            if smooth_err < 0:
                speed_l, speed_r = inner_rev, outer_max
                self.last_action = "TĂNG TỐC CUA TRÁI (MẮT 1)"
            else:
                speed_l, speed_r = outer_max, inner_rev
                self.last_action = "TĂNG TỐC CUA PHẢI (MẮT 5)"

        self._drive(speed_l, speed_r)
        return (speed_l, speed_r, self.last_action)
