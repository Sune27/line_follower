# ==============================================================================
# MOTOR_DRIVER.PY – ĐIỀU KHIỂN ĐỘNG CƠ TB6612FNG + BÙ MA SÁT NGHỈ (KICKSTART)
# ==============================================================================
# Tích hợp cơ chế Xung Mồi Tự Động (Kickstart Anti-Stiction):
#   - Khi bánh xe đang đứng yên (0%) hoặc đổi chiều quay mà nhận lệnh chạy ở tốc độ
#     thấp (VD: 38%), mạch tự động phóng xung mồi 78% trong 35ms đầu tiên để bứt
#     khỏi ma sát nghỉ, sau đó hạ ngay xuống mức 38% để xe lăn chậm và êm!
# ==============================================================================

import time
from machine import Pin, PWM
import config

if not hasattr(time, "ticks_ms"):
    time.ticks_ms = lambda: int(time.time() * 1000)
if not hasattr(time, "ticks_diff"):
    time.ticks_diff = lambda a, b: a - b


class MotorDriver:
    def __init__(self, pin_ain1=13, pin_ain2=12, pin_bin1=27, pin_bin2=26, freq=1000, pin_ain2_alt=14):
        self.freq = freq

        self.pwm_a1 = PWM(Pin(pin_ain1), freq=self.freq, duty=0)
        self.pwm_a2 = PWM(Pin(pin_ain2), freq=self.freq, duty=0)
        try:
            self.pwm_a2_alt = PWM(Pin(pin_ain2_alt), freq=self.freq, duty=0)
        except Exception:
            self.pwm_a2_alt = None

        self.pwm_b1 = PWM(Pin(pin_bin1), freq=self.freq, duty=0)
        self.pwm_b2 = PWM(Pin(pin_bin2), freq=self.freq, duty=0)

        self.kickstart_speed = int(getattr(config, "MOTOR_KICKSTART_SPEED", 78))
        self.kickstart_ms = int(getattr(config, "MOTOR_KICKSTART_MS", 35))

        # Theo dõi trạng thái chiều quay & thời điểm bắt đầu khởi hành của từng bánh
        self.prev_dir_l = 0
        self.prev_dir_r = 0
        self.kick_until_l = 0
        self.kick_until_r = 0

        self.current_speed_left = 0
        self.current_speed_right = 0
        self.stop()

    def _set_duty(self, pwm_obj, duty_10bit):
        if pwm_obj is None:
            return
        val = max(0, min(1023, int(duty_10bit)))
        if hasattr(pwm_obj, "duty"):
            pwm_obj.duty(val)
        elif hasattr(pwm_obj, "duty_u16"):
            pwm_obj.duty_u16(int(val * 65535 // 1023))

    def _apply_kickstart(self, target_pct, prev_dir, kick_until, now_ms):
        """
        Kiểm tra nếu bánh xe vừa chuyển từ Đứng Yên (0) hoặc Đổi Chiều sang Quay:
        -> Bơm xung mồi kickstart_speed (78%) trong 35ms đầu để thắng ma sát nghỉ!
        """
        if target_pct == 0:
            return 0, 0, 0

        cur_dir = 1 if target_pct > 0 else -1
        # Nếu trước đó đang dừng (0) hoặc quay ngược chiều -> Kích hoạt cửa sổ Kickstart 35ms
        if prev_dir != cur_dir:
            kick_until = now_ms + self.kickstart_ms

        if time.ticks_diff(kick_until, now_ms) > 0:
            boosted = max(abs(target_pct), self.kickstart_speed)
            actual_pct = boosted if cur_dir > 0 else -boosted
        else:
            actual_pct = target_pct

        return actual_pct, cur_dir, kick_until

    def set_differential(self, left_percent, right_percent):
        left_percent = max(-100, min(100, int(left_percent)))
        right_percent = max(-100, min(100, int(right_percent)))

        now_ms = time.ticks_ms()

        # Áp dụng xung mồi thắng ma sát nghỉ độc lập cho từng bánh
        eff_l, self.prev_dir_l, self.kick_until_l = self._apply_kickstart(
            left_percent, self.prev_dir_l, self.kick_until_l, now_ms
        )
        eff_r, self.prev_dir_r, self.kick_until_r = self._apply_kickstart(
            right_percent, self.prev_dir_r, self.kick_until_r, now_ms
        )

        self.current_speed_left = left_percent
        self.current_speed_right = right_percent

        # --- Bánh Trái (AIN1, AIN2) ---
        duty_a = abs(eff_l) * 1023 // 100
        if eff_l > 0:
            self._set_duty(self.pwm_a2, 0)
            self._set_duty(self.pwm_a2_alt, 0)
            self._set_duty(self.pwm_a1, duty_a)
        elif eff_l < 0:
            self._set_duty(self.pwm_a1, 0)
            self._set_duty(self.pwm_a2, duty_a)
            self._set_duty(self.pwm_a2_alt, duty_a)
        else:
            self._set_duty(self.pwm_a1, 0)
            self._set_duty(self.pwm_a2, 0)
            self._set_duty(self.pwm_a2_alt, 0)

        # --- Bánh Phải (BIN1, BIN2) ---
        duty_b = abs(eff_r) * 1023 // 100
        if eff_r > 0:
            self._set_duty(self.pwm_b2, 0)
            self._set_duty(self.pwm_b1, duty_b)
        elif eff_r < 0:
            self._set_duty(self.pwm_b1, 0)
            self._set_duty(self.pwm_b2, duty_b)
        else:
            self._set_duty(self.pwm_b1, 0)
            self._set_duty(self.pwm_b2, 0)

    def stop(self):
        self.prev_dir_l = 0
        self.prev_dir_r = 0
        self.kick_until_l = 0
        self.kick_until_r = 0
        self.current_speed_left = 0
        self.current_speed_right = 0
        self._set_duty(self.pwm_a1, 0)
        self._set_duty(self.pwm_a2, 0)
        self._set_duty(self.pwm_a2_alt, 0)
        self._set_duty(self.pwm_b1, 0)
        self._set_duty(self.pwm_b2, 0)
