# 📖 Tài Liệu Chi Tiết Các Method Trong Class `LineFollowerSensor`

> **File mã nguồn:** [`firmware/modules/line_sensor.py`](../../firmware/modules/line_sensor.py)  
> **Phần cứng kết nối:** Mảng 5 mắt cảm biến hồng ngoại TCRT5000 (D21, D19, D18, D5, D17)

---

## 🎯 1. Tổng Quan Về Class `LineFollowerSensor`

Class `LineFollowerSensor` chịu trách nhiệm toàn bộ tầng thu thập dữ liệu quang học dưới gầm xe:
1. Đọc điện áp từ 5 chân GPIO của ESP32.
2. Xử lý logic đảo bit qua cờ `active_low`.
3. Ghép 5 mắt thành số nhị phân 5-bit (`bitmask`).
4. Tính toán sai số vị trí độ lệch vạch (`Error` từ `-4` đến `+4`) phục vụ thuật toán PID.
5. Đóng gói trạng thái gửi lên giao diện Web qua Wi-Fi.

---

## 📋 2. Bảng Tóm Tắt Danh Sách Các Method

| Tên Method | Tham Số Đầu Vào | Kiểu Trả Về | Tác Dụng Chính |
| :--- | :--- | :---: | :--- |
| **`__init__()`** | `s1_pin, s2_pin, s3_pin, s4_pin, s5_pin, active_low` | `None` | Khởi tạo 5 chân GPIO Input PULL_UP và các biến nội bộ. |
| **`read_all_raw()`** | Không có | `list[int]` | Đọc trực tiếp 5 mắt, trả về mảng 5 số `[s1, s2, s3, s4, s5]` (1=Đen, 0=Trắng). |
| **`read_bitmask()`** | `raw_list` (tùy chọn) | `int` | Ép mảng 5 phần tử thành 1 số nguyên nhị phân 5-bit duy nhất (0b00000 .. 0b11111). |
| **`calculate_error()`** | `raw_list` (tùy chọn) | `int` | **(Quan trọng nhất)** Tính toán sai số vị trí từ `-4` đến `+4` để truyền vào bộ PID. |
| **`read_status()`** | Không có | `dict` | Đóng gói toàn bộ thông tin cảm biến dạng JSON gửi lên Web Server. |

---

## 🔍 3. Chi Tiết Từng Method

### 3.1. Method `__init__(s1_pin=21, s2_pin=19, s3_pin=18, s4_pin=5, s5_pin=17, active_low=True)`
- **Loại:** Constructor (Hàm khởi tạo).
- **Mục đích:** Thiết lập cấu hình phần cứng ngay khi bật nguồn ESP32.
- **Nhiệm vụ chi tiết:**
  - Cấu hình 5 chân GPIO tương ứng ở chế độ Ngõ vào số (`Pin.IN`).
  - Kích hoạt điện trở kéo lên nội (`Pin.PULL_UP`) của ESP32 để giữ mức điện áp ổn định, chống nhiễu sóng điện từ từ 2 động cơ DC.
  - Khởi tạo biến nhớ vị trí `self.last_valid_error = 0`.
  - Lưu cờ `self.active_low = active_low`.

```python
# Ví dụ khởi tạo trong main.py:
sensor = LineFollowerSensor(
    s1_pin=21, s2_pin=19, s3_pin=18, s4_pin=5, s5_pin=17,
    active_low=True
)
```

---

### 3.2. Method `read_all_raw()`
- **Mục đích:** Lấy trạng thái tức thời của 5 mắt cảm biến dưới dạng danh sách (List).
- **Nguyên lý chuyển đổi Logic (`active_low`):**
  - **Phần cứng:** Module TCRT5000 khi gặp vạch đen sẽ kéo chân về mức `0V` (`Pin.value() == 0`).
  - **Phần mềm:** Nếu `active_low = True`, method tự động đảo `0V` thành `1` để thuận tiện cho tư duy con người và thuật toán:
    $$\text{Giá trị xuất ra} = \begin{cases} 1 & \text{khi mắt nhìn thấy Vạch Đen} \\ 0 & \text{khi mắt ở Nền Trắng} \end{cases}$$
- **Giá trị trả về:** `list` gồm 5 số nguyên `[s1, s2, s3, s4, s5]`.
  - Ví dụ: `[0, 0, 1, 0, 0]` $\to$ Vạch nằm ngay mắt giữa $S_3$.
  - Ví dụ: `[1, 0, 0, 0, 0]` $\to$ Vạch nằm ở mắt ngoài cùng bên trái $S_1$.

---

### 3.3. Method `read_bitmask(raw_list=None)`
- **Mục đích:** Nén mảng 5 phần tử thành duy nhất một số nguyên (Bitmask) bằng phép toán dịch bit (`bit shifting`).
- **Công thức tính:**
  $$\text{mask} = (S_1 \ll 4) \mid (S_2 \ll 3) \mid (S_3 \ll 2) \mid (S_4 \ll 1) \mid S_5$$
- **Ví dụ minh họa:**
  - Nếu `raw_list = [0, 1, 1, 0, 0]`
  - Kết quả ghép bit: `0b01100` (ở hệ thập phân là số $12$).
- **Lợi ích:** Giúp vi điều khiển so sánh điều kiện cực nhanh (chỉ tốn 1 chu kỳ xung nhịp CPU) thay vì phải duyệt vòng lặp qua từng phần tử của mảng.

---

### 3.4. Method `calculate_error(raw_list=None)` *(Quan trọng nhất)*
- **Mục đích:** Tính toán sai số khoảng cách từ tâm xe đến tâm vạch đen thành một giá trị số thực/nguyên trong dải $[-4, +4]$:
  - **`-4`**: Lệch sang phải tối đa (vạch đen ở mép trái ngoài cùng $S_1$) $\to$ Cần bẻ lái gấp sang Trái.
  - **`0`**: Xe nằm chuẩn tâm vạch (vạch đen ở $S_3$) $\to$ Đi thẳng ổn định.
  - **`+4`**: Lệch sang trái tối đa (vạch đen ở mép phải ngoài cùng $S_5$) $\to$ Cần bẻ lái gấp sang Phải.

#### Quy trình xử lý 3 tầng của `calculate_error`:
1. **Tầng 1 - Tra bảng nhanh (`MAP_ERROR`):**  
   Dò tìm số `bitmask` trong từ điển được định nghĩa sẵn bằng tiền tố nhị phân `0b`:
   ```python
   MAP_ERROR = {
       0b10000: -4,  # Chỉ mắt S1 đen
       0b11000: -3,  # S1, S2 đen
       0b11100: -3,  # Cua vuông 90 độ trái
       0b01000: -2,  # Chỉ mắt S2 đen
       0b01100: -1,  # S2, S3 đen
       0b00100:  0,  # Mắt S3 giữa đen
       0b00110:  1,  # S3, S4 đen
       0b00010:  2,  # Chỉ mắt S4 đen
       0b00011:  3,  # S4, S5 đen
       0b00111:  3,  # Cua vuông 90 độ phải
       0b00001:  4,  # Chỉ mắt S5 đen
       0b11111:  0,  # Vạch ngang vạch đích / ngã tư
   }
   ```
2. **Tầng 2 - Xử lý mất vạch / lọt khe (`0b00000`):**  
   Khi cả 5 mắt đều báo trắng (`00000`) do vạch đen lọt vào khe hở giữa 2 mắt hoặc khi xe chớm văng ra khỏi vạch ở cua gắt:  
   $\to$ Hàm trả về giá trị **`self.last_valid_error`** (sai số hợp lệ gần nhất vừa ghi nhớ). Nhờ đó xe không bị giật hay mất phương hướng mà vẫn tiếp tục bẻ lái đón lại vạch.
3. **Tầng 3 - Thuật toán trung bình trọng số (Weighted Average):**  
   Nếu gặp trạng thái lạ không có trong bảng tra cứu (ví dụ do ánh sáng môi trường), hàm tự động nội suy trọng số:
   $$\text{Weighted} = \frac{(-4 \cdot S_1) + (-2 \cdot S_2) + (0 \cdot S_3) + (2 \cdot S_4) + (4 \cdot S_5)}{S_1 + S_2 + S_3 + S_4 + S_5}$$

---

### 3.5. Method `read_status()`
- **Mục đích:** Đóng gói toàn bộ thông tin cảm biến thành một từ điển (Dictionary) định dạng JSON để cung cấp cho máy chủ Web (`web_server.py`).
- **Giá trị trả về:**
  ```python
  {
      "array": [0, 0, 1, 0, 0],   # Danh sách trạng thái 5 mắt
      "bin_str": "00100",         # Chuỗi nhị phân hiển thị
      "error": 0                  # Sai số hiện tại
  }
  ```
- **Ứng dụng:** Trình duyệt trên điện thoại đọc JSON này để đổi màu trực tiếp 5 đèn tròn hiển thị trạng thái xe theo thời gian thực (vàng = vạch đen, xám = nền trắng).
