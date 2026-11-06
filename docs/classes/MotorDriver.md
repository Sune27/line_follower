# 📖 Tài Liệu Chi Tiết Các Method Trong Class `MotorDriver`

> **File mã nguồn:** [`firmware/modules/motor_driver.py`](../../firmware/modules/motor_driver.py)  
> **Phần cứng điều khiển:** Mạch cầu H TB6612FNG (4 kênh PWM trực tiếp `AIN1, AIN2, BIN1, BIN2` + chân dự phòng `D14` cho `D12`) và 2 động cơ DC giảm tốc TT (tỷ số truyền 1:48).

---

## 🎯 1. Tổng Quan Về Class `MotorDriver`

Class `MotorDriver` đóng vai trò là "đôi chân" điều khiển toàn bộ hệ thống cơ cấu chấp hành:
1. Quản lý 4 kênh băm xung PWM tần số 1000Hz (1kHz) độc lập trên ESP32.
2. Ánh xạ tốc độ từ phần trăm ($-100\% \dots +100\%$) sang độ phân giải 10-bit (`0 .. 1023`).
3. **Cơ chế độc quyền `Kickstart Anti-Stiction` (Xung mồi thắng ma sát nghỉ):** Giải quyết triệt để hiện tượng kẹt bánh của động cơ DC TT ở tốc độ thấp.
4. Điều khiển vi sai 2 bánh: Tiến, Lùi, Quay tại chỗ, Phanh và Dừng tự do.

---

## 📋 2. Bảng Tóm Tắt Danh Sách Các Method

| Tên Method | Tham Số Đầu Vào | Kiểu Trả Về | Tác Dụng Chính |
| :--- | :--- | :---: | :--- |
| **`__init__()`** | `pin_ain1, pin_ain2, pin_bin1, pin_bin2, freq, pin_ain2_alt` | `None` | Khởi tạo 4 kênh PWM phần cứng, chân mirror dự phòng D14 và các biến theo dõi Kickstart. |
| **`_set_duty()`** | `pwm_obj, duty_10bit` | `None` | Ghi giá trị Duty Cycle (0..1023) an toàn xuống phần cứng PWM (tương thích cả MicroPython cũ và mới). |
| **`_apply_kickstart()`** | `target_pct, prev_dir, kick_until, now_ms` | `tuple[int, int, int]` | Thuật toán kiểm tra và phóng xung mồi (Kickstart) khi bánh chuyển trạng thái từ đứng yên sang quay. |
| **`set_differential()`** | `left_percent, right_percent` | `None` | **(Quan trọng nhất)** Điều khiển tốc độ và chiều quay độc lập của 2 bánh Trái/Phải ($-100\% \dots +100\%$). |
| **`stop()`** | Không có | `None` | Dừng khẩn cấp cả 2 động cơ (hạ Duty về 0), reset toàn bộ cờ Kickstart. |

---

## 🔍 3. Chi Tiết Từng Method

### 3.1. Method `__init__(pin_ain1=13, pin_ain2=12, pin_bin1=27, pin_bin2=26, freq=1000, pin_ain2_alt=14)`
- **Loại:** Constructor (Hàm khởi tạo).
- **Mục đích:** Thiết lập cấu hình PWM phần cứng cho 4 chân động cơ.
- **Nhiệm vụ chi tiết:**
  - Cấu hình 4 đối tượng `PWM` tại các chân:
    - Bánh Trái: `pwm_a1` (`GPIO 13`), `pwm_a2` (`GPIO 12`).
    - Chân dự phòng: `pwm_a2_alt` (`GPIO 14`) song song với chân 12 (giúp tránh lỗi Strapping Pin khi cắm mạch).
    - Bánh Phải: `pwm_b1` (`GPIO 27`), `pwm_b2` (`GPIO 26`).
  - Thiết lập tần số mặc định: `freq = 1000Hz` (1kHz giúp động cơ chạy êm, không phát tiếng rít).
  - Khởi tạo thông số Kickstart: `kickstart_speed = 78%` (hoặc 98% theo `config.py`), thời gian mồi `kickstart_ms = 35ms` (hoặc 70ms).
  - Khởi tạo bộ nhớ chiều quay cũ (`prev_dir_l, prev_dir_r`) và mốc thời gian mồi (`kick_until_l, kick_until_r`).
  - Gọi ngay `self.stop()` để khóa động cơ lúc bật nguồn, không để xe tự trôi.

---

### 3.2. Method `_set_duty(pwm_obj, duty_10bit)`
- **Loại:** Private Helper Method (Hàm trợ giúp nội bộ).
- **Mục đích:** Xuất giá trị điều chế độ rộng xung (PWM) an toàn xuống phần cứng.
- **Xử lý tương thích:**
  - Cắt giá trị an toàn trong đoạn $[0, 1023]$ (10-bit).
  - Tự động nhận diện phiên bản MicroPython:
    - Nếu có phương thức `.duty()`: gọi `pwm_obj.duty(val)` (chuẩn 10-bit của ESP32).
    - Nếu là bản MicroPython mới chỉ hỗ trợ `.duty_u16()`: tự động quy đổi `val * 65535 // 1023`.

---

### 3.3. Method `_apply_kickstart(target_pct, prev_dir, kick_until, now_ms)` *(Vật lý chuyên sâu)*
- **Loại:** Private Helper Method.
- **Mục đích:** **Giải quyết bài toán ma sát tĩnh (Static Friction) của động cơ giảm tốc.**
- **Nguyên lý hoạt động:**
  1. Khi bánh xe đang đứng yên (`prev_dir == 0`) hoặc đang quay lùi mà đổi sang tiến (`prev_dir != cur_dir`):
     - Hệ thống lập tức kích hoạt một "cửa sổ thời gian mồi":  
       $$\text{kick\_until} = \text{now\_ms} + \text{kickstart\_ms}$$
  2. Trong suốt khoảng thời gian này (ví dụ 70ms đầu tiên), dù lệnh điều khiển chỉ yêu cầu chạy chậm `35%`, method này sẽ tự động **bơm xung cực mạnh** lên mức:
     $$\text{boosted} = \max(|\text{target\_pct}|, \text{kickstart\_speed}) \quad (\text{ví dụ } 98\%)$$
  3. Ngay sau khi hết 70ms, bánh xe đã có đà lăn (chuyển sang ma sát trượt/lăn nhỏ hơn nhiều), tốc độ tự động hạ về đúng `target_pct` ban đầu (`35%`).
- **Giá trị trả về:** `(actual_pct, cur_dir, kick_until)`.

---

### 3.4. Method `set_differential(left_percent, right_percent)` *(Quan trọng nhất)*
- **Loại:** Public Method.
- **Mục đích:** Điều khiển tốc độ và chiều quay của 2 bánh xe để điều hướng robot vi sai.
- **Tham số:**
  - `left_percent`: Tốc độ bánh trái từ $-100$ (Lùi tối đa) đến $+100$ (Tiến tối đa). `0` là dừng.
  - `right_percent`: Tốc độ bánh phải từ $-100$ (Lùi tối đa) đến $+100$ (Tiến tối đa). `0` là dừng.
- **Quy trình thực thi:**
  1. Kẹp giá trị vào khoảng an toàn $[-100, +100]$.
  2. Gọi `_apply_kickstart()` độc lập cho từng bánh xe để đảm bảo bánh nào khởi hành cũng được cấp xung mồi.
  3. Phân luồng cầu H TB6612FNG:
     - **Tiến (`eff > 0`):** Kéo chân 2 về `0`, băm xung PWM chân 1 với `duty = eff * 1023 // 100`.
     - **Lùi (`eff < 0`):** Kéo chân 1 về `0`, băm xung PWM chân 2 và chân dự phòng D14.
     - **Dừng (`eff == 0`):** Kéo cả 2 chân về `0` (trạng thái thả trôi bánh mượt mà).
  4. Lưu trạng thái vào `current_speed_left` và `current_speed_right` để Web Server đọc hiển thị.

---

### 3.5. Method `stop()`
- **Loại:** Public Method.
- **Mục đích:** Dừng khẩn cấp toàn bộ hệ thống truyền động.
- **Nhiệm vụ:**
  - Hạ toàn bộ Duty của cả 4 chân PWM (`AIN1, AIN2, AIN2_ALT, BIN1, BIN2`) về `0`.
  - Reset toàn bộ cờ hướng và thời gian mồi Kickstart về `0`.
  - Đặt `current_speed_left = 0`, `current_speed_right = 0`.
