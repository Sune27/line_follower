# 📖 Tài Liệu Chi Tiết Các Method Trong Class `LineTracker`

> **File mã nguồn:** [`firmware/modules/line_tracker.py`](../../firmware/modules/line_tracker.py)  
> **Vai trò:** "Bộ não" điều khiển chính của robot — tính toán giải thuật PID rời rạc, cơ chế bơm gia tốc cua gắt (Corner Boost) và thuật toán cứu vạch khi lọt khe (`00000`).

---

## 🎯 1. Tổng Quan Về Class `LineTracker`

Class `LineTracker` nhận dữ liệu mảng 5 mắt từ `LineFollowerSensor`, tính toán sai số vị trí và ra lệnh tốc độ trực tiếp cho `MotorDriver`:
1. Chạy vòng lặp điều khiển thời gian thực theo chu kỳ cố định 10ms (100Hz).
2. Tích hợp bộ lọc làm mịn sai số số học (Low-Pass Filter) chống rung lắc đầu xe.
3. Giải thuật PID rời rạc kết hợp cơ chế xóa tích phân khi qua tâm (Zero-crossing Anti-Windup).
4. **Cơ chế Bơm Gia Tốc Cua Gắt (Corner Acceleration Boost):** Khi lệch ra mắt $S_1$ hoặc $S_5$, tự động tăng lực bánh ngoài lên 90% và đảo chiều bánh trong -65% để bẻ lái không bị chết đà.
5. **Cơ chế Xử Lý Lọt Khe / Mất Line (`00000`):** Nhớ hướng lệch gần nhất để xoay tìm lại line trong thời gian timeout an toàn.

---

## 📋 2. Bảng Tóm Tắt Danh Sách Các Method

| Tên Method | Tham Số Đầu Vào | Kiểu Trả Về | Tác Dụng Chính |
| :--- | :--- | :---: | :--- |
| **`__init__()`** | `motor_driver` | `None` | Khởi tạo các hệ số PID ($K_p, K_i, K_d$), ngưỡng tốc độ cua và tiêm phụ thuộc `MotorDriver`. |
| **`reset_pid()`** | Không có | `None` | Đặt lại toàn bộ biến tích phân, đạo hàm và bộ nhớ sai số về 0 khi bắt đầu hoặc dừng xe. |
| **`_drive()`** | `left, right` | `tuple[int, int]` | Áp dụng hệ số cân bằng cơ khí (`left_scale, right_scale`) trước khi xuất lệnh sang `MotorDriver`. |
| **`start()`** | `speed` (tùy chọn) | `None` | Kích hoạt chế độ tự hành dò line, phát xung khởi hành ban đầu (`startup_speed`). |
| **`stop()`** | Không có | `None` | Hủy kích hoạt dò line, reset bộ PID và phanh dừng xe ngay lập tức. |
| **`set_params()`** | `base_speed, kp, ki, kd, left_scale, right_scale` | `None` | Cho phép cập nhật nóng các hệ số PID và tốc độ từ xa qua Web Server mà không cần nạp lại code. |
| **`_compute_error()`** | `sensors` | `tuple[float, str]` | Ánh xạ trạng thái 5 mắt thành sai số thực và nhận diện các chế độ đặc biệt (`TRACKING`, `CROSS_LINE`, `LOST_LINE`). |
| **`update()`** | `sensors, now_ms` | `tuple[int, int, str]` | **(Quan trọng nhất)** Vòng lặp điều khiển tính toán PID, phân chia 3 vùng lệch và ra lệnh tốc độ 2 bánh. |

---

## 🔍 3. Chi Tiết Từng Method

### 3.1. Method `__init__(motor_driver)`
- **Loại:** Constructor.
- **Dependency Injection:** Nhận đối tượng `MotorDriver` truyền từ bên ngoài vào để điều khiển phần cứng.
- **Nhiệm vụ:**
  - Nạp các thông số vận hành từ `config.py`:
    - `base_speed = 62%`: Tốc độ chạy thẳng cơ sở.
    - `mid_turn_outer_speed = 78%`: Lực bánh ngoài khi lệch Mắt 2 hoặc Mắt 4.
    - `corner_turn_outer_speed = 90%` / `corner_turn_inner_speed = -65%`: Lực khi chạm Mắt 1 hoặc Mắt 5.
    - `kp = 7.5`, `ki = 0.04`, `kd = 4.5`: Ba thông số PID tối ưu.
    - `filter_alpha = 0.85`: Hệ số lọc thông thấp chống nhiễu quang học.
  - Khởi tạo trạng thái `is_active = False`, `last_action = "STANDBY"`.
  - Gọi `reset_pid()`.

---

### 3.2. Method `reset_pid()`
- **Mục đích:** Xóa sạch quán tính tích phân và sai số cũ.
- **Nhiệm vụ:** Đặt lại các biến trạng thái: `current_error = 0.0`, `smooth_error = 0.0`, `prev_smooth_error = 0.0`, `integral = 0.0`, `lost_line_start_time = 0`.
- **Ứng dụng:** Tránh hiện tượng xe bị giật mạnh do lượng tích phân $K_i$ dồn từ lần chạy trước.

---

### 3.3. Method `_drive(left, right)`
- **Mục đích:** Bộ bù sai lệch cơ khí giữa 2 động cơ.
- **Công thức:**
  $$\text{out\_l} = \text{round}(\text{left} \times \text{left\_scale}), \quad \text{out\_r} = \text{round}(\text{right} \times \text{right\_scale})$$
- Nếu một bên động cơ chạy khỏe hơn bên kia do gia công cơ khí, ta chỉ cần chỉnh `MOTOR_LEFT_SCALE` hoặc `MOTOR_RIGHT_SCALE` trong `config.py` (từ $0.3 \dots 1.0$) mà không phải sửa code thuật toán.

---

### 3.4. Method `start(speed=None)` & `stop()`
- **`start(speed)`**:
  - Đặt `is_active = True`.
  - Nếu có truyền tham số `speed` (từ Web), cập nhật `base_speed = speed`.
  - Gọi `reset_pid()`.
  - Phóng xung khởi động `startup_speed = 88%` trong 450ms đầu tiên để xe bứt tốc nhanh từ vạch xuất phát.
- **`stop()`**:
  - Đặt `is_active = False`.
  - Dừng động cơ qua `self.motor.stop()`.
  - Cập nhật trạng thái `last_action = "STOPPED"`.

---

### 3.5. Method `set_params(base_speed, kp, ki, kd, left_scale, right_scale)`
- **Mục đích:** Tinh chỉnh trực tiếp khi xe đang ở trên sân (Live Tuning).
- **Ứng dụng:** Khi bạn thay đổi thanh trượt trên Web điều khiển và nhấn nút "💾 CẬP NHẬT THÔNG SỐ PID", Web Server sẽ gọi trực tiếp method này để áp dụng giá trị mới ngay trong chu kỳ tiếp theo mà không cần khởi động lại ESP32.

---

### 3.6. Method `_compute_error(sensors)`
- **Mục đích:** Quy đổi mảng 5 mắt `sensors` thành sai số số thực $e$ và nhận diện chế độ.
- **Các trường hợp đặc biệt:**
  - `0b11111` (Cả 5 mắt cùng đen) $\to$ Trả về `(0.0, "CROSS_LINE")` (Gặp vạch ngang đích / ngã tư).
  - `0b00000` (Cả 5 mắt cùng trắng) $\to$ Trả về `(0.0, "LOST_LINE")` (Mất line hoặc lọt khe).
  - Các trường hợp còn lại $\to$ Tra bảng `MAP_ERROR` hoặc tính trung bình trọng số, trả về `(err, "TRACKING")`.
  - Luôn cập nhật biến nhớ `last_valid_error` để phục vụ cứu vạch.

---

### 3.7. Method `update(sensors, now_ms)` *(Quan trọng nhất)*
- **Chu kỳ thực thi:** 10ms một lần (100Hz) trong vòng lặp chính của `main.py`.
- **Quy trình 3 bước xử lý:**

#### Bước 1: Xử lý khi mất vạch (`LOST_LINE - 00000`)
- Nếu mất vạch vượt quá `lost_line_timeout_ms = 3000ms` (3 giây) $\to$ Tự động ngắt động cơ dừng xe an toàn.
- Nếu trước đó đang ở tâm ($|\text{last\_error}| < 1.0$) $\to$ Đi thẳng tiếp qua khe hẹp.
- Nếu trước đó vừa chớm lệch Mắt 2/4 ($< 3.0$) và mới lọt khe $< 150\text{ms}$ $\to$ Nhích nhẹ bánh ngoài `78%` đón lại vạch.
- Nếu trước đó văng mạnh ra Mắt 1/5 ($\ge 3.0$) $\to$ Bơm quay gắt tại chỗ (bánh ngoài 90%, bánh trong lùi -68%) theo hướng `last_valid_error` để kéo xe quay lại vạch.

#### Bước 2: Tính toán bộ điều khiển PID
1. **Lọc thông thấp (Low-pass Filter):**
   $$\text{smooth\_err} = \alpha \cdot \text{raw\_error} + (1 - \alpha) \cdot \text{smooth\_err}_{\text{prev}}$$
2. **Khâu Tỷ lệ (Proportional):** $P = K_p \times \text{smooth\_err}$
3. **Khâu Tích phân (Integral):**
   - Tự động reset $I = 0$ khi xe đi qua tâm hoặc đổi dấu sai số (Anti-windup).
   - Kẹp giới hạn tích phân $[-20.0, +20.0]$: $I = K_i \times \sum \text{smooth\_err}$
4. **Khâu Đạo hàm (Derivative):** $D = K_d \times (\text{smooth\_err} - \text{prev\_smooth\_err})$
5. **Tổng tín hiệu điều khiển:** $\text{pid\_val} = P + I + D$

#### Bước 3: Phân chia 3 vùng lệch và xuất lực động cơ
- **VÙNG TÂM ($|\text{err}| \le 1.2$ - Mắt 3):**  
  Điều khiển vi sai êm dịu quanh tốc độ cơ sở:
  $$\text{speed\_l} = \text{base\_speed} + \text{pid\_val}, \quad \text{speed\_r} = \text{base\_speed} - \text{pid\_val}$$
- **VÙNG LỆCH VỪA ($1.2 < |\text{err}| \le 2.6$ - Mắt 2 hoặc 4):**  
  Bánh ngoài tăng tốc $\ge 78\%$, bánh trong hạ về $0\%$ để tạo lực bẻ lái khỏe.
- **VÙNG RÌA NGOÀI ($|\text{err}| > 2.6$ - Mắt 1 hoặc 5):**  
  Bánh ngoài được bơm cực đại **`90%`**, bánh trong lùi trợ xoay **`-65%`**, tạo ngẫu lực kép kéo đầu xe quặt ngược vào tâm vạch ngay lập tức mà không bị kẹt lốp.
