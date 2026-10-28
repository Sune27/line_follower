# ==============================================================================
# CONFIG.PY – CẤU HÌNH HỆ THỐNG XE DÒ LINE (TỐI ƯU GIA TỐC BẺ LÁI MẮT 1 & 5)
# ==============================================================================

# ==============================================================================
# 1. CẤU HÌNH ESP32 TỰ ĐỘNG TÌM VÀ KẾT NỐI WI-FI "Sune" (STATION MODE)
# ==============================================================================
WIFI_SSID = "Sune"                  # Tên Wi-Fi (Hotspot điện thoại) cần kết nối
WIFI_PASSWORD = "mouse_love_rice"   # Mật khẩu Wi-Fi "Sune"
WIFI_CONNECT_TIMEOUT_SEC = 10       # Thời gian chờ mỗi lần thử kết nối (giây)

PIN_STATUS_LED = 2                  # Chân đèn LED xanh báo trạng thái trên ESP32

# ==============================================================================
# 2. CẤU HÌNH MẢNG CẢM BIẾN DÒ LINE TCRT5000 5 MẮT (MẠNG BÊN PHẢI LIỀN KỀ)
# ==============================================================================
PIN_LINE_S1 = 21             # Mắt 1: Ngoài cùng bên Trái -> Cọc D21 (GPIO 21)
PIN_LINE_S2 = 19             # Mắt 2: Giữa bên Trái       -> Cọc D19 (GPIO 19)
PIN_LINE_S3 = 18             # Mắt 3: Chính giữa (Tâm)    -> Cọc D18 (GPIO 18)
PIN_LINE_S4 = 5              # Mắt 4: Giữa bên Phải       -> Cọc D5  (GPIO 5)
PIN_LINE_S5 = 17             # Mắt 5: Ngoài cùng bên Phải -> Cọc D17 (GPIO 17)

SENSOR_ACTIVE_LOW = True     # True: Gặp vạch đen xuất mức 0 (LOW)

# ==============================================================================
# 3. CẤU HÌNH ĐỘNG CƠ TB6612FNG & XUNG BỨT MA SÁT NGHỈ (KICKSTART)
# ==============================================================================
PIN_MOTOR_AIN1 = 13          # Bánh Trái - Chiều thuận (Cọc D13 - GPIO 13)
PIN_MOTOR_AIN2 = 12          # Bánh Trái - Chiều ngược (Cọc D12 hoặc D14)
PIN_MOTOR_BIN1 = 27          # Bánh Phải - Chiều thuận (Cọc D27 - GPIO 27)
PIN_MOTOR_BIN2 = 26          # Bánh Phải - Chiều ngược (Cọc D26 - GPIO 26)

MOTOR_PWM_FREQ = 1000        # Tần số băm xung PWM 1000Hz
MOTOR_LEFT_SCALE = 1.0       # Giữ 1.0 để xuất đúng 100% giá trị tốc độ cài đặt
MOTOR_RIGHT_SCALE = 1.0      # Giữ 1.0 để xuất đúng 100% giá trị tốc độ cài đặt

# XUNG BỨT KHỎI TRẠNG THÁI NGHỈ (KICKSTART ANTI-STICTION):
MOTOR_KICKSTART_SPEED = 98   # Xung đề-pa cực đại (98%) để bứt khỏi trạng thái đứng im
MOTOR_KICKSTART_MS = 70      # Thời gian giữ xung đề-pa (70ms)

# ==============================================================================
# 4. CẤU HÌNH CHẾ ĐỘ DÒ LINE & TĂNG GIA TỐC KHI CHẠM MẮT 1 / MẮT 5
# ==============================================================================
# Với đường cong mượt không có góc nhọn 90°, đặt "SMOOTH" làm mặc định để xe
# giữ đà lăn liên tục và bơm gia tốc mạnh ở mắt 1/5 (không bị dừng khựng lại)!
DEFAULT_DRIVE_MODE = "SMOOTH"   # "SMOOTH": Giữ đà + Tăng gia tốc cua (Khuyên dùng)
                                # "STEP"  : Băm nhịp + Xoay mạnh liên tục khi lệch

CONTROL_LOOP_MS = 10            # Chu kỳ quét cảm biến (10ms = 100Hz)

# --- Thông số Tốc độ & Gia tốc Bẻ Lái (Giải quyết triệt để lỗi dừng ở Mắt 1 & 5) ---
LINE_BASE_SPEED = 62            # Tốc độ đi thẳng ổn định (2 bánh cùng đẩy: 62%)
LINE_MIN_SPEED = 55             # Tốc độ tối thiểu khi bám tâm
LINE_STARTUP_SPEED = 88         # Tốc độ khởi hành ban đầu (88% trong 450ms đầu)
LINE_STARTUP_DURATION_MS = 450

# Khi lệch sang Mắt 2 hoặc Mắt 4 (Cua vừa):
MID_TURN_OUTER_SPEED = 78       # Tăng gia tốc bánh ngoài lên 78% để thắng ma sát bẻ lái
MID_TURN_INNER_SPEED = 0        # Hạ bánh trong về 0% làm trụ xoay mượt

# Khi lệch ra đến Mắt 1 hoặc Mắt 5 (Rìa ngoài cùng - Cần gia tốc lớn để kéo đầu xe vào):
CORNER_BRAKE_DURATION_MS = 0    # TẮT phanh dừng đầu cua (0ms) để KHÔNG làm xe mất đà bị dừng lại!
CORNER_BRAKE_SPEED = 0
CORNER_TURN_OUTER_SPEED = 90    # Bơm gia tốc bánh ngoài lên 90% để kéo mạnh đầu xe vào line!
CORNER_TURN_INNER_SPEED = -65   # Bánh trong lùi khỏe (-65%, vượt ngưỡng ma sát 60%) để trợ lực xoay!

# Khi lỡ trôi quá Mắt 1/5 ra ngoài (00000 - Cứu mất line):
LINE_LOST_TIMEOUT_MS = 3000     # Thời gian tối đa quét tìm lại line (3 giây)
LINE_SEARCH_OUTER_SPEED = 90    # Bánh ngoài đẩy 90%
LINE_SEARCH_REVERSE_SPEED = -68 # Bánh trong lùi -68% để xoay đầu nhanh về lại vạch
AUTO_STOP_ON_CROSS = False

# --- Thông số cho Chế độ STEP (Băm nhịp tiến, nhưng xoay LIÊN TỤC lực 88% ở Mắt 1/5) ---
STEP_FWD_PULSE_MS = 45          # Thời gian cấp xung tiến mỗi nhịp (45ms)
STEP_FWD_COAST_MS = 15          # Thời gian ngắt nghỉ ngắn (15ms) để giữ đà lăn
STEP_BACKUP_MS = 0              # Tắt lùi ở đường cong thường để không làm xe dừng khựng
STEP_BACKUP_SPEED = -75
STEP_PAUSE_MS = 0               # Không dừng ngắt đà
STEP_PIVOT_ON_MS = 60           # Nhịp xoay dài và khỏe (60ms)
STEP_PIVOT_OFF_MS = 10          # Nhịp nghỉ cực ngắn (10ms) để không bị kẹt ma sát tĩnh
STEP_PIVOT_SPEED = 88           # Lực xoay mạnh 88% khi chạm Mắt 1 hoặc Mắt 5
STEP_LOCK_HEAD_MS = 30

PID_KP = 7.5                    # Tăng Kp lên 7.5 để phản ứng bẻ lái mạnh hơn ngay khi chớm lệch
PID_KI = 0.04
PID_KD = 4.5
PID_FILTER_ALPHA = 0.85

DAMPING_DURATION_MS = 120
DAMPING_SPEED = 58
