# ==============================================================================
# ROBOTIC_ARM.PY – BỘ ĐIỀU KHIỂN CÁNH TAY ROBOT 4-DOF VỚI QUY TRÌNH ĐỖ AN TOÀN (PARK ROUTINE)
# ==============================================================================
# Áp dụng Quy trình Đỗ cánh tay chuẩn công nghiệp (Safe Park Mode):
#   - Trước khi tắt nguồn hoặc khi chạy dò line, cánh tay gập gọn vào lưng xe (Park)
#   - Khi khởi động lại nguồn, cánh tay bắt đầu mượt mà ngay từ tư thế đỗ an toàn này
#   - Không còn hiện tượng giật nảy góc ở lần nhấn đầu tiên
#   - Không ghi đè Flash liên tục, bảo vệ tuổi thọ chip nhớ ESP32
#   - ĐỖ TUẦN TỰ (SEQUENTIAL PARK): Đưa lần lượt từng khớp về vị trí đỗ:
#     1. D32 (Kẹp - Gripper)
#     2. D2 (Vai - Shoulder)
#     3. D4 (Khuỷu - Elbow)
#     4. D15 (Đế - Base)
#     => Ngăn chặn hoàn toàn hiện tượng sụt áp nguồn do 4 servo cùng chạy một lúc!
# ==============================================================================

import time
from machine import Pin, PWM
import config


class ServoJoint:
    """Điều khiển một khớp Servo trực tiếp theo xung PWM mượt mà."""

    def __init__(self, pin_num, name="Joint", min_us=450, max_us=2550, default_us=1500, speed_us=25, reverse=False):
        self.pin_num = pin_num
        self.name = name
        self.min_us = min_us
        self.max_us = max_us
        self.current_us = default_us
        self.target_us = default_us
        self.speed_us = speed_us
        self.step_interval_ms = 15
        self.last_step_ms = 0
        self.pwm = None
        self.is_active = False
        self.reverse = reverse

    def _ensure_pwm(self, initial_pulse_ns=1500000):
        if self.pwm is None:
            try:
                self.pwm = PWM(Pin(self.pin_num), freq=getattr(config, "ARM_SERVO_FREQ", 50), duty_ns=initial_pulse_ns)
            except Exception:
                try:
                    self.pwm = PWM(Pin(self.pin_num), freq=getattr(config, "ARM_SERVO_FREQ", 50))
                    self.pwm.duty_ns(initial_pulse_ns)
                except Exception as e:
                    print(f"[Servo] ⚠️ Lỗi chân D{self.pin_num} ({self.name}):", e)
                    self.pwm = None

    def _write_hw(self, pulse_us):
        pulse_us = max(self.min_us, min(self.max_us, int(pulse_us)))
        pulse_ns = int(pulse_us * 1000)

        self._ensure_pwm(pulse_ns)
        if self.pwm is None:
            return

        try:
            if hasattr(self.pwm, "duty_ns"):
                self.pwm.duty_ns(pulse_ns)
            else:
                self.pwm.duty_u16(int(pulse_us * 65535 // 20000))
        except Exception as e:
            print(f"[Servo {self.name}] Lỗi PWM:", e)

    def drive(self, direction):
        """Lái liên tục theo hướng (1: tới, -1: lùi, 0: dừng tại chỗ)."""
        self.is_active = True
        d = int(direction)
        if self.reverse and d != 0:
            d = -d
        if d > 0:
            self.target_us = self.max_us
        elif d < 0:
            self.target_us = self.min_us
        else:
            self.target_us = self.current_us

    def set_target(self, target_angle, immediate=False):
        """Hỗ trợ tương thích nếu có lệnh góc."""
        self.is_active = True
        ang = int(target_angle)
        if self.reverse:
            ang = 180 - ang
        target_us = self.min_us + (self.max_us - self.min_us) * ang // 180
        self.target_us = max(self.min_us, min(self.max_us, int(target_us)))
        if immediate:
            self.current_us = self.target_us
            self._write_hw(self.current_us)

    def set_target_us(self, target_us):
        """Đặt đích trực tiếp theo micro-giây."""
        self.is_active = True
        self.target_us = max(self.min_us, min(self.max_us, int(target_us)))

    def get_angle(self):
        """Tính góc vật lý hiện tại (0 - 180 độ) từ xung PWM."""
        span = self.max_us - self.min_us
        if span <= 0:
            return 90
        ang = (self.current_us - self.min_us) * 180 // span
        return max(0, min(180, int(ang)))

    def update(self, now_ms):
        if not self.is_active:
            return

        if self.current_us == self.target_us:
            return

        if time.ticks_diff(now_ms, self.last_step_ms) < self.step_interval_ms:
            return

        self.last_step_ms = now_ms

        if self.current_us < self.target_us:
            self.current_us = min(self.target_us, self.current_us + self.speed_us)
        else:
            self.current_us = max(self.target_us, self.current_us - self.speed_us)

        self._write_hw(self.current_us)

    def deinit(self):
        if self.pwm:
            try:
                self.pwm.deinit()
            except Exception:
                pass
        self.pwm = None
        self.is_active = False


class RoboticArm:
    """Quản lý cụm 4 khớp cánh tay robot với Quy trình Đỗ An Toàn Tuần Tự (Sequential Park)."""

    def __init__(
        self,
        base_pin=getattr(config, "PIN_ARM_BASE", 15),
        shoulder_pin=getattr(config, "PIN_ARM_SHOULDER", 2),
        elbow_pin=getattr(config, "PIN_ARM_ELBOW", 4),
        gripper_pin=getattr(config, "PIN_ARM_GRIPPER", 32),
    ):
        min_u = getattr(config, "ARM_MIN_US", 450)
        max_u = getattr(config, "ARM_MAX_US", 2550)
        speed = getattr(config, "ARM_SPEED_US", 25)

        park_b = getattr(config, "ARM_PARK_BASE_US", 742)
        park_s = getattr(config, "ARM_PARK_SHOULDER_US", 450)
        park_e = getattr(config, "ARM_PARK_ELBOW_US", 1500)
        park_g = getattr(config, "ARM_PARK_GRIPPER_US", 1000)

        # Cánh tay khởi tạo ngay tại tư thế Đỗ An Toàn (Park Position)
        self.base = ServoJoint(base_pin, "Base", min_u, max_u, park_b, speed, reverse=getattr(config, "ARM_REVERSE_BASE", False))
        self.shoulder = ServoJoint(shoulder_pin, "Shoulder", min_u, max_u, park_s, speed, reverse=getattr(config, "ARM_REVERSE_SHOULDER", True))
        self.elbow = ServoJoint(elbow_pin, "Elbow", min_u, max_u, park_e, speed, reverse=getattr(config, "ARM_REVERSE_ELBOW", True))
        self.gripper = ServoJoint(gripper_pin, "Gripper", min_u, max_u, park_g, speed, reverse=getattr(config, "ARM_REVERSE_GRIPPER", False))

        self.joints = (self.base, self.shoulder, self.elbow, self.gripper)
        
        # Quản lý trình tự đỗ tuần tự từng khớp (Chống sụt áp)
        self.park_sequence = []
        self.park_step = -1
        self.park_settle_until = 0

        print(f"[Arm] 🦾 Khởi tạo Cánh tay 4-DOF Chế độ Đỗ Tuần Tự: Base=D{base_pin}, Shoulder=D{shoulder_pin}, Elbow=D{elbow_pin}, Gripper=D{gripper_pin}")

    def drive_joint(self, joint_name, direction):
        """Lái một khớp quay liên tục hoặc dừng lại."""
        self.park_step = -1  # Huỷ đỗ tuần tự nếu có thao tác điều khiển thủ công
        joint_map = {
            "b": self.base, "base": self.base,
            "s": self.shoulder, "shoulder": self.shoulder,
            "e": self.elbow, "elbow": self.elbow,
            "g": self.gripper, "gripper": self.gripper,
        }
        j = joint_map.get(joint_name)
        if j:
            j.drive(int(direction))
        return self.get_angles()

    def set_angles(self, base=None, shoulder=None, elbow=None, gripper=None, immediate=False):
        self.park_step = -1
        if base is not None:
            self.base.set_target(base, immediate)
        if shoulder is not None:
            self.shoulder.set_target(shoulder, immediate)
        if elbow is not None:
            self.elbow.set_target(elbow, immediate)
        if gripper is not None:
            self.gripper.set_target(gripper, immediate)
        return self.get_angles()

    def update(self, now_ms):
        # 1. Cập nhật chuyển động của các servo
        for j in self.joints:
            j.update(now_ms)

        # 2. Xử lý logic đỗ tuần tự từng khớp theo thứ tự: D32 -> D2 -> D4 -> D15
        if 0 <= self.park_step < len(self.park_sequence):
            current_joint, target_us, label = self.park_sequence[self.park_step]

            # Kiểm tra xem khớp hiện tại đã về đến vị trí đích chưa
            if current_joint.current_us == target_us:
                if self.park_settle_until == 0:
                    # Chờ 200ms để dòng điện mô-tơ ổn định trước khi chuyển sang khớp tiếp theo
                    self.park_settle_until = time.ticks_add(now_ms, 200)
                elif time.ticks_diff(now_ms, self.park_settle_until) >= 0:
                    self.park_step += 1
                    self.park_settle_until = 0
                    if self.park_step < len(self.park_sequence):
                        next_joint, next_target, next_label = self.park_sequence[self.park_step]
                        next_joint.set_target_us(next_target)
                        print(f"[Arm] 📦 Đỗ tuần tự: Bước {self.park_step + 1}/{len(self.park_sequence)} -> {next_label}")
                    else:
                        print("[Arm] ✅ Hoàn tất đỗ tuần tự cả 4 khớp an toàn (D32->D2->D4->D15)!")
                        self.park_step = -1

    def get_angles(self):
        return {
            "b": self.base.get_angle(),
            "s": self.shoulder.get_angle(),
            "e": self.elbow.get_angle(),
            "g": self.gripper.get_angle(),
        }

    # ==========================================================================
    # CÁC QUY TRÌNH TƯ THẾ CHUẨN (PROCEDURAL POSES)
    # ==========================================================================
    def pose_park(self):
        """QUY TRÌNH ĐỖ AN TOÀN TUẦN TỰ (SEQUENTIAL SAFE PARK):
        Lần lượt đưa từng khớp về vị trí đỗ theo thứ tự:
          1. D32 (Khớp Kẹp - Gripper)
          2. D2  (Khớp Vai - Shoulder)
          3. D4  (Khớp Khuỷu - Elbow)
          4. D15 (Khớp Đế - Base)
        Tuyệt đối không chạy đồng thời để chống sụt áp nguồn ESP32."""
        park_b = getattr(config, "ARM_PARK_BASE_US", 742)
        park_s = getattr(config, "ARM_PARK_SHOULDER_US", 450)
        park_e = getattr(config, "ARM_PARK_ELBOW_US", 1500)
        park_g = getattr(config, "ARM_PARK_GRIPPER_US", 1000)

        # Thứ tự chuẩn xác theo yêu cầu: D32 -> D2 -> D4 -> D15
        self.park_sequence = [
            (self.gripper, park_g, "D32 (Kẹp)"),
            (self.shoulder, park_s, "D2 (Vai)"),
            (self.elbow, park_e, "D4 (Khuỷu)"),
            (self.base, park_b, "D15 (Đế)"),
        ]
        self.park_step = 0
        self.park_settle_until = 0

        # Kích hoạt bước đầu tiên (D32)
        joint, target, label = self.park_sequence[0]
        joint.set_target_us(target)
        print(f"[Arm] 📦 Bắt đầu Đỗ tuần tự: Bước 1/4 -> {label}")
        return self.get_angles()

    def pose_home(self):
        """Vị trí sẵn sàng (Vươn lên tư thế trung tâm)."""
        self.park_step = -1
        self.base.set_target_us(1500)
        self.shoulder.set_target_us(1500)
        self.elbow.set_target_us(1500)
        self.gripper.set_target_us(1300)
        return self.get_angles()

    def pose_grab(self):
        """Hạ thấp tay về phía trước để chuẩn bị gắp vật."""
        self.park_step = -1
        self.base.set_target_us(1500)
        self.shoulder.set_target_us(1800)
        self.elbow.set_target_us(1200)
        self.gripper.set_target_us(1800)
        return self.get_angles()

    def grip(self, close=True):
        self.park_step = -1
        us = 900 if close else 1800
        self.gripper.set_target_us(us)
        return self.get_angles()

    def stop_all(self):
        self.park_step = -1
        for j in self.joints:
            j.drive(0)
        return self.get_angles()

    def deinit(self):
        self.park_step = -1
        for j in self.joints:
            j.deinit()
