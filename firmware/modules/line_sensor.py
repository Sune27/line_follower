# ==============================================================================
# LINE_SENSOR.PY – MODULE ĐỌC MẢNG CẢM BIẾN DÒ LINE TCRT5000 5 MẮT
# ==============================================================================
# Phân bổ chân GPIO theo sơ đồ đấu nối:
#   - Mắt 1 (S1 - Ngoài Trái) : D21 (GPIO 21)
#   - Mắt 2 (S2 - Giữa Trái)  : D19 (GPIO 19)
#   - Mắt 3 (S3 - Chính Giữa) : D18 (GPIO 18)
#   - Mắt 4 (S4 - Giữa Phải)  : D5  (GPIO 5)
#   - Mắt 5 (S5 - Ngoài Phải) : D17 (GPIO 17)
# ==============================================================================

from machine import Pin


class LineFollowerSensor:
    # Bảng tra nhanh sai số vị trí từ bitmask 5-bit (S1..S5)
    MAP_ERROR = {
        0b10000: -4,
        0b11000: -3,
        0b11100: -3,   # Cua vuông 90 độ bên Trái (3 mắt trái cùng đen)
        0b11110: -4,   # Cua vuông gắt bên Trái (4 mắt trái cùng đen)
        0b01000: -2,
        0b01100: -1,
        0b00100:  0,
        0b00110:  1,
        0b00010:  2,
        0b00011:  3,
        0b00111:  3,   # Cua vuông 90 độ bên Phải (3 mắt phải cùng đen)
        0b01111:  4,   # Cua vuông gắt bên Phải (4 mắt phải cùng đen)
        0b00001:  4,
        0b11111:  0,   # Ngã tư / Vạch ngang
        0b01110:  0,   # Vạch dày ở tâm
    }

    def __init__(self, s1_pin=21, s2_pin=19, s3_pin=18, s4_pin=5, s5_pin=17, active_low=True):
        self.active_low = active_low
        self.pins_num = [s1_pin, s2_pin, s3_pin, s4_pin, s5_pin]

        # Khởi tạo 5 chân GPIO Input có trở kéo lên nội (PULL_UP) chống nhiễu
        self.s1 = Pin(s1_pin, Pin.IN, Pin.PULL_UP)
        self.s2 = Pin(s2_pin, Pin.IN, Pin.PULL_UP)
        self.s3 = Pin(s3_pin, Pin.IN, Pin.PULL_UP)
        self.s4 = Pin(s4_pin, Pin.IN, Pin.PULL_UP)
        self.s5 = Pin(s5_pin, Pin.IN, Pin.PULL_UP)
        self.sensors = [self.s1, self.s2, self.s3, self.s4, self.s5]

        self.last_valid_error = 0

    def read_all_raw(self):
        """
        Đọc đồng thời 5 mắt cảm biến:
        Trả về list 5 phần tử [s1, s2, s3, s4, s5]:
          1 = VẠCH ĐEN
          0 = NỀN TRẮNG
        """
        if self.active_low:
            return [
                1 if self.s1.value() == 0 else 0,
                1 if self.s2.value() == 0 else 0,
                1 if self.s3.value() == 0 else 0,
                1 if self.s4.value() == 0 else 0,
                1 if self.s5.value() == 0 else 0,
            ]
        return [
            self.s1.value(),
            self.s2.value(),
            self.s3.value(),
            self.s4.value(),
            self.s5.value(),
        ]

    def read_bitmask(self, raw_list=None):
        if raw_list is None:
            raw_list = self.read_all_raw()
        return (
            (raw_list[0] << 4)
            | (raw_list[1] << 3)
            | (raw_list[2] << 2)
            | (raw_list[3] << 1)
            | raw_list[4]
        )

    def calculate_error(self, raw_list=None):
        """
        Tính sai số vị trí từ -4 đến +4:
          -4: Lệch trái tối đa (chỉ S1 gặp đen) -> Cần cua gắt sang Trái
           0: Giữa tâm vạch (S3 gặp đen)       -> Đi thẳng
          +4: Lệch phải tối đa (chỉ S5 gặp đen) -> Cần cua gắt sang Phải
        """
        if raw_list is None:
            raw_list = self.read_all_raw()

        s1, s2, s3, s4, s5 = raw_list
        bitmask = (s1 << 4) | (s2 << 3) | (s3 << 2) | (s4 << 1) | s5

        if bitmask in self.MAP_ERROR:
            err = self.MAP_ERROR[bitmask]
            self.last_valid_error = err
            return err

        if bitmask == 0b00000:
            return self.last_valid_error

        total = s1 + s2 + s3 + s4 + s5
        if total > 0:
            weighted = ((-4 * s1) + (-2 * s2) + (0 * s3) + (2 * s4) + (4 * s5)) / total
            err = int(weighted + 0.5) if weighted >= 0 else int(weighted - 0.5)
            err = max(-4, min(4, err))
            self.last_valid_error = err
            return err

        return self.last_valid_error

    def read_status(self):
        raw = self.read_all_raw()
        err = self.calculate_error(raw)
        return {
            "array": raw,
            "bin_str": "".join(str(x) for x in raw),
            "error": err,
        }
