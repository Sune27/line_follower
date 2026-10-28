# 🔌 Hướng Dẫn Đấu Nối Phần Cứng & Hiệu Chuẩn Cảm Biến

Tài liệu hướng dẫn chi tiết cách đấu nối **Bảng mở rộng ESP32 Shield 30-Pin (Chuẩn S - V - G)** với cụm cảm biến dò line **TCRT5000 5 mắt** và mạch công suất **TB6612FNG (loại 4 dây điều khiển PWM)**.

---

## 1. Đặc điểm Bảng Mở Rộng ESP32 Shield 30-Pin

1. **Cổng nhận nguồn Pin chính:**
   - Giắc tròn DC màu đen ở góc dưới (`DC 6.5–16V`), cắm trực tiếp đầu ra từ khay 2 pin 18650 (`7.4V – 8.4V`).
2. **Khung hộp trắng 8 chân nguồn (ngay phía trên cổng Type-C):**
   - **Hàng trên:** `[ 5V ]  [ 5V ]  [ 3V ]  [ 3V ]`
   - **Hàng dưới:** `[ GND ] [ GND ] [ GND ] [ GND ]`
3. **Quy ước 3 hàng cọc kim theo chuẩn `S - V - G`:**
   - **Cột `S` (Signal - Ngoài cùng sát mép bo):** Chân tín hiệu GPIO.
   - **Cột `V` (Voltage - Ở giữa):** Chân cấp nguồn (chọn mức `5V` hoặc `3.3V` bằng Jumper màu vàng).
   - **Cột `G` (Ground - Trong cùng sát chip ESP32):** Chân âm / Mass (`GND`).

---

## 2. Sơ đồ Đấu nối Driver Động cơ TB6612FNG (Mạch Đỏ)

### 2.1. Nguồn và Tín hiệu từ ESP32 Shield sang TB6612FNG

| Chân trên TB6612FNG | Vị trí cắm trên ESP32 Shield | Chức năng |
| :--- | :--- | :--- |
| **`[ VM ]`** *(1 phải)* | Cọc **`[ 5V ]`** thứ 1 *(Khung trắng 8 chân)* | Nguồn nuôi động cơ (hoặc nối thẳng `+7.4V` từ Pin) |
| **`[ NC / VCC ]`** *(2 phải)* | Cọc **`[ 3V ]`** *(hoặc để trống nếu là chân NC)* | Nguồn nuôi logic IC |
| **`[ GND ]`** *(3 phải)* | Cọc **`[ GND ]`** thứ 1 *(Khung trắng 8 chân)* | Mass chung hệ thống |
| **`[ STBY ]`** *(4 trái)* | Cọc **`[ 3V ]`** hoặc **`[ 5V ]`** | Kích hoạt IC TB6612FNG hoạt động |
| **`[ AIN1 ]`** *(3 trái)* | Cột `[ S ]` tại cọc **`[ D13 ]`** *(GPIO 13)* | PWM Bánh Trái - Chiều thuận |
| **`[ AIN2 ]`** *(2 trái)* | Cột `[ S ]` tại cọc **`[ D12 ]`** hoặc **`[ D14 ]`** | PWM Bánh Trái - Chiều ngược *(Hỗ trợ song song cả D12 và D14)* |
| **`[ BIN1 ]`** *(5 trái)* | Cột `[ S ]` tại cọc **`[ D27 ]`** *(GPIO 27)* | PWM Bánh Phải - Chiều thuận |
| **`[ BIN2 ]`** *(6 trái)* | Cột `[ S ]` tại cọc **`[ D26 ]`** *(GPIO 26)* | PWM Bánh Phải - Chiều ngược |

> **Lưu ý:** Trên mạch TB6612FNG phiên bản 4 dây PWM, các chân `1 trái`, `7 trái` và `2 phải` được ký hiệu là **`NC` (Not Connected)** nên không cần cắm dây.

### 2.2. Đấu nối từ TB6612FNG ra 2 Động cơ DC TT

| Chân trên TB6612FNG | Kết nối tới Động cơ |
| :--- | :--- |
| **`[ AO1 ]`** *(4 phải)* & **`[ AO2 ]`** *(5 phải)* | 2 dây của **Động cơ Bánh TRÁI** |
| **`[ BO1 ]`** *(7 phải)* & **`[ BO2 ]`** *(6 phải)* | 2 dây của **Động cơ Bánh PHẢI** |

*(Nếu khi bấm nút `▲ TIẾN` trên giao diện điều khiển mà bánh nào quay lùi, chỉ cần đảo chéo 2 dây `AO1/AO2` hoặc `BO1/BO2` của bánh đó).*

---

## 3. Sơ đồ Đấu nối Mảng Cảm biến Dò Line TCRT5000 5 Mắt

Mảng 5 mắt được đặt ngang phía trước mũi xe, nhìn từ trên xuống theo thứ tự từ Trái sang Phải:
`[ S1 - Ngoài Trái ]` — `[ S2 - Giữa Trái ]` — `[ S3 - Chính Giữa ]` — `[ S4 - Giữa Phải ]` — `[ S5 - Ngoài Phải ]`

### 3.1. Cấp nguồn cho mảng cảm biến
- **`[ VCC ]`** $\rightarrow$ Cọc **`[ 3V ]`** (Khung hộp trắng) hoặc hàng `[ V ]` (nấc 3.3V) để tín hiệu xuất ra chuẩn 3.3V an toàn cho ESP32.
- **`[ GND ]`** $\rightarrow$ Cọc **`[ GND ]`** (Khung hộp trắng) hoặc hàng `[ G ]`.

### 3.2. Cắm 5 dây tín hiệu vào 5 cọc liền kề bên phải (`D21 -> D17`)

| Chân Cảm Biến | Cọc trên Shield | GPIO ESP32 | Vai trò trong thuật toán dò line |
| :--- | :--- | :--- | :--- |
| **`[ OUT1 / D1 ]`** | **`[ D21 ]`** *(Cột S)* | `GPIO 21` | **Mắt 1 (Ngoài Trái)** – Sai số `-4` (Tăng gia tốc cua trái mạnh) |
| **`[ OUT2 / D2 ]`** | **`[ D19 ]`** *(Cột S)* | `GPIO 19` | **Mắt 2 (Giữa Trái)** – Sai số `-2` (Bẻ lái trái vừa) |
| **`[ OUT3 / D3 ]`** | **`[ D18 ]`** *(Cột S)* | `GPIO 18` | **Mắt 3 (Chính Giữa)** – Sai số `0` (Đi thẳng bám tâm) |
| **`[ OUT4 / D4 ]`** | **`[ D5 ]`** *(Cột S)* | `GPIO 5` | **Mắt 4 (Giữa Phải)** – Sai số `+2` (Bẻ lái phải vừa) |
| **`[ OUT5 / D5 ]`** | **`[ D17 ]`** *(Cột S)* | `GPIO 17` | **Mắt 5 (Ngoài Phải)** – Sai số `+4` (Tăng gia tốc cua phải mạnh) |

---

## 4. Quy trình Kiểm tra & Cân chỉnh Cảm biến trước khi chạy

1. **Độ cao lắp đặt:** Đặt thanh cảm biến cách mặt sàn khoảng **`8mm – 12mm`** và vươn ra phía trước trục 2 bánh xe khoảng **`6cm – 8cm`**.
2. **Chỉnh biến trở độ nhạy:**
   - Đặt cả 5 mắt lên **nền trắng**: Cả 5 đèn LED báo tín hiệu trên lưng module cảm biến phải **SÁNG** (trên giao diện Web hiển thị `0 0 0 0 0`).
   - Đưa vạch băng dính đen lần lượt đi qua từng mắt từ `S1` đến `S5`: Mắt nào đè lên vạch đen thì đèn LED trên lưng mắt đó phải **TẮT** ngay lập tức (trên giao diện Web chấm tròn của mắt đó sẽ đổi sang màu vàng `1`).
   - Nếu mắt chưa nhạy hoặc vùng mù giữa 2 đèn rộng, dùng tuốc-nơ-vít xoay nhẹ biến trở trên thanh cảm biến để đạt ngưỡng nhạy tối ưu.
