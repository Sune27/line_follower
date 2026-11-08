# ==============================================================================
# ROBOTIC_ARM.PY – BỘ ĐIỀU KHIỂN CÁNH TAY ROBOT 4-DOF KHÔNG GIỚI HẠN GÓC (SMOOTH DRIVE)
# ==============================================================================
# Bản chất điều khiển trực tiếp độ rộng xung (Pulse-Width Continuous Control):
#   - Không còn giới hạn góc cứng 0 - 180°
#   - Điều khiển hướng mượt mà: Nhấn giữ để quay/nâng/vươn liên tục, nhả tay là dừng
#   - Khởi động tĩnh (Silent Boot): Bật nguồn đứng im 100%, không giật tải làm rớt Wi-Fi
# ==============================================================================

import time
from machine import Pin, PWM
import config


class ServoJoint:
    """Điều khiển một khớp Servo trực tiếp theo xung PWM mượt mà."""

    def __init__(self, pin_num, name="Joint", min_us=450, max_us=2550, default_us=1500, speed_us=25):
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

    def _ensure_pwm(self):
        if self.pwm is None:
            try:
                self.pwm = PWM(Pin(self.pin_num), freq=getattr(config, "ARM_SERVO_FREQ", 50))
            except Exception as e:
                print(f"[Servo] ⚠️ Lỗi chân D{self.pin_num} ({self.name}):", e)
                self.pwm = None

    def _write_hw(self, pulse_us):
        self._ensure_pwm()
        if self.pwm is None:
            return

        pulse_us = max(self.min_us, min(self.max_us, int(pulse_us)))
        pulse_ns = int(pulse_us * 1000)

        try:
            if hasattr(self.pwm, "duty_ns"):
                self.pwm.duty_ns(pulse_ns)
            else:
                self.pwm.duty_u16(int(pulse_us * 65535 // 20000))
        except Exception as e:
            print(f"[Servo {self.name}] Lỗi PWM:", e)

    def drive(self, direction):
        """Lái liên tục theo hướng (1: quay tới, -1: quay ngược, 0: dừng tại chỗ)."""
        self.is_active = True
        if direction > 0:
            self.target_us = self.max_us
        elif direction < 0:
            self.target_us = self.min_us
        else:
            self.target_us = self.current_us

    def set_target(self, target_angle, immediate=False):
        """Hỗ trợ tương thích nếu có lệnh góc."""
        self.is_active = True
        target_us = self.min_us + (self.max_us - self.min_us) * int(target_angle) // 180
        self.target_us = max(self.min_us, min(self.max_us, int(target_us)))
        if immediate:
            self.current_us = self.target_us
            self._write_hw(self.current_us)

    def set_angle(self, angle):
        self.set_target(angle, immediate=False)

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
    """Quản lý cụm 4 khớp cánh tay robot."""

    def __init__(
        self,
        base_pin=getattr(config, "PIN_ARM_BASE", 15),
        shoulder_pin=getattr(config, "PIN_ARM_SHOULDER", 2),
        elbow_pin=getattr(config, "PIN_ARM_ELBOW", 4),
        gripper_pin=getattr(config, "PIN_ARM_GRIPPER", 32),
    ):
        min_u = getattr(config, "ARM_MIN_US", 450)
        max_u = getattr(config, "ARM_MAX_US", 2550)

        self.base = ServoJoint(base_pin, "Base", min_u, max_u, 1500)
        self.shoulder = ServoJoint(shoulder_pin, "Shoulder", min_u, max_u, 1500)
        self.elbow = ServoJoint(elbow_pin, "Elbow", min_u, max_u, 1500)
        self.gripper = ServoJoint(gripper_pin, "Gripper", min_u, max_u, 1000)

        self.joints = (self.base, self.shoulder, self.elbow, self.gripper)
        print(f"[Arm] 🦾 Khởi tạo Cánh tay Robot 4-DOF Tự do: D{base_pin}, D{shoulder_pin}, D{elbow_pin}, D{gripper_pin}")

    def drive_joint(self, joint_name, direction):
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
        for j in self.joints:
            j.update(now_ms)

    def get_angles(self):
        return {
            "b": self.base.current_us,
            "s": self.shoulder.current_us,
            "e": self.elbow.current_us,
            "g": self.gripper.current_us,
        }

    def pose_home(self):
        return self.set_angles(90, 90, 90, 45)

    def pose_rest(self):
        return self.set_angles(90, 30, 150, 20)

    def pose_grab(self):
        return self.set_angles(90, 120, 60, 90)

    def grip(self, close=True):
        angle = 20 if close else 90
        self.gripper.set_target(angle)
        return self.get_angles()

    def stop_all(self):
        for j in self.joints:
            j.drive(0)
        return self.get_angles()

    def deinit(self):
        for j in self.joints:
            j.deinit()
