# 🧠 Nguyên Lý Thuật Toán & Hướng Dẫn Tinh Chỉnh Thông Số PID

Tài liệu giải thích chi tiết cấu trúc thuật toán điều khiển trong `firmware/modules/line_tracker.py`, `firmware/modules/motor_driver.py` và cách tinh chỉnh các tham số trong `firmware/config.py`.

---

## 1. Bảng Quy Đổi Sai Số Vị Trí 5 Mắt Cảm Biến (`Error`)

Mảng 5 mắt TCRT5000 trả về mảng 5 bit `[S1, S2, S3, S4, S5]` (trong đó `1` là Vạch Đen, `0` là Nền Trắng):

| Trạng thái `[S1 S2 S3 S4 S5]` | Sai số (`Error`) | Ý nghĩa vị trí vạch đen | Hành động điều khiển |
| :---: | :---: | :--- | :--- |
| **`1 0 0 0 0`** | **`-4.0`** | Lệch hẳn ra mép ngoài cùng bên Trái (`S1`) | **Bơm gia tốc cua Trái tối đa** (Bánh phải `+90%`, Bánh trái `-65%`) |
| **`1 1 0 0 0`** / **`1 1 1 0 0`** | **`-3.2` .. `-3.5`** | Chạm vùng cua gắt bên Trái | **Bơm gia tốc cua Trái mạnh** |
| **`0 1 0 0 0`** | **`-2.0`** | Lệch vừa sang Trái (`S2`) | **Bẻ lái Trái vừa** (Bánh phải `+78%`, Bánh trái `0%`) |
| **`0 1 1 0 0`** | **`-1.0`** | Chớm lệch nhẹ sang Trái (`S2 + S3`) | Điều chỉnh PID nhẹ sang Trái |
| **`0 0 1 0 0`** | **`0.0`** | **Vạch nằm chính giữa tâm (`S3`)** | **Đi thẳng ổn định** (`LINE_BASE_SPEED = 62%`) |
| **`0 0 1 1 0`** | **`+1.0`** | Chớm lệch nhẹ sang Phải (`S3 + S4`) | Điều chỉnh PID nhẹ sang Phải |
| **`0 0 0 1 0`** | **`+2.0`** | Lệch vừa sang Phải (`S4`) | **Bẻ lái Phải vừa** (Bánh trái `+78%`, Bánh phải `0%`) |
| **`0 0 0 1 1`** / **`0 0 1 1 1`** | **`+3.2` .. `+3.5`** | Chạm vùng cua gắt bên Phải | **Bơm gia tốc cua Phải mạnh** |
| **`0 0 0 0 1`** | **`+4.0`** | Lệch hẳn ra mép ngoài cùng bên Phải (`S5`) | **Bơm gia tốc cua Phải tối đa** (Bánh trái `+90%`, Bánh phải `-65%`) |
| **`0 0 0 0 0`** | *Giữ dấu cũ* | Lọt khe giữa 2 đèn hoặc trôi khỏi mép ngoài | Nội suy đón vạch hoặc xoay tìm lại line theo mắt cuối cùng nhìn thấy |

---

## 2. Các Cơ Chế Vật Lý Chuyên Biệt Đã Tích Hợp

### 2.1. Xung Mồi Thắng Ma Sát Nghỉ Tự Động (`Kickstart Anti-Stiction`)
- **Vấn đề vật lý:** Động cơ giảm tốc vàng DC TT có ma sát tĩnh (ma sát nghỉ) lớn hơn nhiều so với ma sát lăn. Khi bánh xe đang đứng yên (`0%`), cần xung `> 85%` mới bắt đầu nhúc nhích được; nhưng khi đã lăn bánh thì chỉ cần `60% – 62%` là chạy ổn định.
- **Giải pháp trong `motor_driver.py`:**
  - Mỗi khi một bánh xe chuyển từ trạng thái dừng (`0%`) hoặc đổi chiều quay sang trạng thái chạy, mạch tự động phóng xung **`MOTOR_KICKSTART_SPEED = 98%` trong `70ms` đầu tiên**, sau đó tự động hạ về tốc độ điều khiển bình thường (`62%`).

### 2.2. Bơm Gia Tốc Khi Lệch Ra Mắt 1 & Mắt 5 (`Corner Acceleration Boost`)
- **Vấn đề vật lý:** Khi đi thẳng ở tốc độ `62%`, cả 2 bánh cùng đẩy xe. Nhưng khi xe lệch ra mắt ngoài cùng (`S1` hoặc `S5`), chỉ có 1 bánh ngoài gánh toàn bộ trọng lượng xe cộng với lực ma sát trượt ngang của lốp. Nếu giữ nguyên lực `62%` thì bánh ngoài sẽ bị kẹt và dừng lại.
- **Giải pháp trong `line_tracker.py`:**
  - Khi lệch vừa ở **Mắt 2 / Mắt 4**: Tự động tăng lực bánh ngoài lên **`MID_TURN_OUTER_SPEED = 78%`**, bánh trong hạ về `0%`.
  - Khi lệch ra **Mắt 1 / Mắt 5**: Tự động bơm lực bánh ngoài lên **`CORNER_TURN_OUTER_SPEED = 90%`**, đồng thời bánh trong lùi trợ lực ở mức **`CORNER_TURN_INNER_SPEED = -65%`** (vượt ngưỡng ma sát tĩnh `60%`), tạo ngẫu lực kéo đầu xe quay lại tâm vạch ngay lập tức mà không bị dừng khựng.

### 2.3. Nội Suy Khi Vạch Đen Lọt Khe Giữa 2 Đèn (`00000`)
- Nếu trước đó vạch đang ở mắt trong (`S3`, `S2`, `S4`) mà đột ngột báo `00000` (do vạch đen hẹp lọt vào khe trống giữa 2 bóng đèn), xe không phanh dừng mà tự động nhích đón nhẹ về phía mắt vừa thấy để đưa vạch trở lại vùng quét của đèn.

---

## 3. Ý Nghĩa & Cách Tinh Chỉnh Các Thông Số Trong `firmware/config.py`

### 3.1. Ba hệ số `Kp`, `Ki`, `Kd`
- **`PID_KP` (Khâu Tỷ lệ – Mặc định `7.5`):**
  - Quyết định **độ nhạy và độ gắt tay lái** khi xe chớm lệch khỏi tâm.
  - *Tăng `Kp`* nếu xe phản ứng chậm khi vào đoạn cong; *Giảm `Kp`* nếu xe đi trên đường thẳng mà đầu cứ lắc qua lắc lại.
- **`PID_KD` (Khâu Đạo hàm – Mặc định `4.5`):**
  - Đóng vai trò **bộ giảm chấn chống văng đuôi**, tự động trả lái sớm khi mũi xe đang lao nhanh từ mép ngoài về lại mắt giữa `S3`.
  - *Tăng `Kd`* nếu xe cua xong hay bị văng lố sang mép bên kia của vạch.
- **`PID_KI` (Khâu Tích phân – Mặc định `0.04`):**
  - Cộng dồn sai số để **bù độ lệch cơ khí** nếu 2 động cơ Trái/Phải mạnh yếu không đều nhau. Luôn giữ ở mức nhỏ (`0.0` – `0.06`).

### 3.2. Các thông số tốc độ & lực cua quan trọng trong `config.py`

| Tên biến trong `config.py` | Giá trị chuẩn | Tác dụng & Cách chỉnh |
| :--- | :---: | :--- |
| `LINE_BASE_SPEED` | `62` | Tốc độ đi thẳng ổn định (%). Tăng lên `65–68` nếu pin yếu; giảm về `58–60` khi pin mới sạc đầy. |
| `MID_TURN_OUTER_SPEED` | `78` | Lực bánh ngoài khi lệch vào Mắt 2 hoặc Mắt 4 (%). |
| `CORNER_TURN_OUTER_SPEED` | `90` | Gia tốc bánh ngoài khi lệch ra Mắt 1 hoặc Mắt 5 (%). Tăng lên `95–98` nếu xe vẫn còn hơi lì khi cua gắt. |
| `CORNER_TURN_INNER_SPEED` | `-65` | Lực lùi trợ xoay của bánh trong khi chạm Mắt 1 hoặc Mắt 5 (%). |
| `MOTOR_KICKSTART_SPEED` | `98` | Xung mồi thắng ma sát nghỉ khi bánh bắt đầu quay (%). |
| `MOTOR_KICKSTART_MS` | `70` | Thời gian duy trì xung mồi (ms). |
