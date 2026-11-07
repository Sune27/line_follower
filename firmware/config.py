# ==============================================================================
# CONFIG.PY – CẤU HÌNH HỆ THỐNG XE DÒ LINE (THUẬT TOÁN PID MƯỢT & GIA TỐC CUA)
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
# 4. CẤU HÌNH THUẬT TOÁN CHẠY MƯỢT PID & TĂNG GIA TỐC CUA (MẮT 2/4 & MẮT 1/5)
# ==============================================================================
CONTROL_LOOP_MS = 10            # Chu kỳ quét cảm biến & cập nhật PID (10ms = 100Hz)

LINE_BASE_SPEED = 72            # Tốc độ đi thẳng phóng nhanh (72%)
LINE_MIN_SPEED = 60             # Tốc độ tối thiểu khi bám tâm (60%)
LINE_STARTUP_SPEED = 90         # Tốc độ khởi hành ban đầu (90% trong 450ms đầu)
LINE_STARTUP_DURATION_MS = 450

# Khi lệch sang Mắt 2 hoặc Mắt 4 (Cua vừa):
MID_TURN_OUTER_SPEED = 85       # Bánh ngoài tăng lực lên 85% để bẻ lái nhanh
MID_TURN_INNER_SPEED = 30       # Bánh trong vẫn lăn 30% giữ trớn lướt cua mượt mà, không bị mất đà

# Khi lệch ra đến Mắt 1 hoặc Mắt 5 (Rìa ngoài cùng):
CORNER_TURN_OUTER_SPEED = 92    # Bơm gia tốc bánh ngoài lên 92%
CORNER_TURN_INNER_SPEED = 0     # Bánh trong về 0% làm trụ xoay nhanh (không lùi âm để tránh hãm tốc/xoay vòng)

# Khi lỡ trôi quá Mắt 1/5 ra ngoài (00000 - Cứu mất line):
LINE_LOST_TIMEOUT_MS = 3000     # Thời gian tối đa quét tìm lại line (3 giây)
LINE_SEARCH_OUTER_SPEED = 90    # Bánh ngoài đẩy 90%
LINE_SEARCH_REVERSE_SPEED = -45 # Bánh trong lùi nhẹ -45% để tìm lại vạch
AUTO_STOP_ON_CROSS = False

PID_KP = 6.8                    # Kp tối ưu cho tốc độ cao (êm ái, bớt rung lắc phanh)
PID_KI = 0.04                   # Hệ số Tích phân (I)
PID_KD = 4.2                    # Hệ số Đạo hàm (D)
PID_FILTER_ALPHA = 0.85         # Hệ số lọc thông thấp làm mịn sai số
