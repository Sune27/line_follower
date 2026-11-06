# 📖 Tài Liệu Chi Tiết Các Method Trong Class `WebControlServer`

> **File mã nguồn:** [`firmware/network/web_server.py`](../../firmware/network/web_server.py)  
> **Kiến trúc:** Web Server HTTP Non-blocking chạy trên cổng 80, phục vụ giao diện người dùng tách biệt (`index.html`, `style.css`, `app.js`) và xử lý các RESTful API điều khiển robot theo thời gian thực.

---

## 🎯 1. Tổng Quan Về Class `WebControlServer`

Class `WebControlServer` là cầu nối tương tác giữa người điều khiển (qua Điện thoại/Laptop) và xe:
1. Đóng vai trò là một HTTP Web Server hoạt động ở chế độ **Non-blocking** (bất đồng bộ/không chặn), đảm bảo chu kỳ chạy PID 100Hz của xe không bao giờ bị dừng giật khi có người truy cập web.
2. Nạp trước (Pre-load) toàn bộ giao diện HTML, CSS, JavaScript vào bộ nhớ đệm RAM lúc khởi động để tải trang cực nhanh.
3. Cung cấp bộ API chuẩn RESTful định dạng JSON để App/Web gửi lệnh: Bắt đầu dò, Dừng xe, Lái thủ công D-Pad, Cập nhật thông số PID.
4. Cơ chế chống lỗi kết nối mạng trên di động: đọc xả sạch bộ đệm TCP (draining buffer) và hỗ trợ đa nền tảng (CORS enabled).

---

## 📋 2. Bảng Tóm Tắt Danh Sách Các Method

| Tên Method | Tham Số Đầu Vào | Kiểu Trả Về | Tác Dụng Chính |
| :--- | :--- | :---: | :--- |
| **`__init__()`** | `line_sensor, motor, tracker, port, web_dir` | `None` | Khởi tạo máy chủ, tiêm 3 đối tượng phụ thuộc, nạp web assets vào RAM và mở socket cổng 80. |
| **`_read_text_file()`** | `filename` | `str` | Đọc an toàn nội dung các file giao diện tĩnh (`index.html`, `style.css`, `app.js`) từ bộ nhớ Flash. |
| **`_load_web_assets()`**| Không có | `None` | Đọc và nén CSS/JS trực tiếp vào HTML trong RAM để tối ưu hóa truyền tin trên ESP32. |
| **`_start_server()`** | Không có | `None` | Tạo TCP Socket, thiết lập chế độ Non-blocking và lắng nghe trên cổng 80. |
| **`_parse_query()`** | `query_str` | `dict` | Phân tích các tham số trong URL query string (ví dụ: `spd=65&kp=8.0`). |
| **`_build_status_dict()`**| Không có | `dict` | Đóng gói toàn bộ thông tin cảm biến, vận tốc 2 bánh và thông số PID thành Dictionary. |
| **`_write_all()`** | `cl, data_bytes` | `None` | Gửi dữ liệu qua Socket có chia nhỏ từng gói 1024 bytes và tự động xử lý chờ (EAGAIN). |
| **`_send_response()`** | `cl, body_bytes, content_type` | `None` | Tạo đầy đủ HTTP Header (200 OK, Content-Length, CORS) và gửi kèm nội dung. |
| **`_send_json()`** | `cl, data_dict` | `None` | Chuyển đổi dữ liệu Python sang chuỗi JSON và gửi về cho Web Client. |
| **`_read_request()`** | `cl` | `bytes` | Đọc xả toàn bộ HTTP Header gửi lên từ trình duyệt để tránh lỗi mạng `TCP RST`. |
| **`poll()`** | Không có | `None` | **(Quan trọng nhất)** Vòng lặp lắng nghe request từ trình duyệt và điều phối gọi hàm trong xe. |

---

## 🔍 3. Chi Tiết Từng Method

### 3.1. Method `__init__(line_sensor, motor, tracker, port=80, web_dir="network")`
- **Loại:** Constructor.
- **Mô hình Dependency Injection:** Nhận cả 3 đối tượng đại diện cho 3 tầng của xe:
  - `line_sensor`: Lấy dữ liệu 5 mắt.
  - `motor`: Lái thủ công bằng tay (D-Pad).
  - `tracker`: Điều khiển bật/tắt PID và cập nhật tham số.
- **Nhiệm vụ:**
  - Gọi `_load_web_assets()` để nạp toàn bộ file giao diện vào RAM.
  - Gọi `_start_server()` để mở cổng HTTP.

---

### 3.2. Method `_load_web_assets()` & `_read_text_file(filename)`
- **Mục đích:** Tối ưu hóa hiệu năng vi điều khiển.
- **Giải pháp kỹ thuật:**
  - Nếu mỗi lần người dùng bấm F5 trên điện thoại mà ESP32 phải mở file trên bộ nhớ Flash để đọc thì sẽ tốn rất nhiều thời gian và làm gián đoạn việc dò line.
  - Do đó, method này **chỉ đọc Flash 1 lần duy nhất lúc khởi động**: Đọc `index.html`, `style.css`, `app.js` và nhúng trực tiếp CSS/JS vào chuỗi HTML trong RAM (`self.html_bytes`).
  - Khi trình duyệt yêu cầu tải trang, ESP32 chỉ cần bắn chuỗi byte trong RAM ra ngoài mạng trong vài mili-giây!

---

### 3.3. Method `_start_server()`
- **Mục đích:** Tạo Socket Server mạng TCP.
- **Điểm then chốt:**
  ```python
  self.server_sock.setblocking(False)
  ```
  Lệnh `setblocking(False)` là yếu tố sống còn: Nó đảm bảo khi không có điện thoại nào kết nối, hàm `accept()` sẽ thoát ra ngay lập tức chứ không treo đứng CPU của ESP32.

---

### 3.4. Method `_read_request(cl)` *(Khắc phục lỗi mạng di động)*
- **Mục đích:** Đọc trọn vẹn yêu cầu HTTP từ điện thoại.
- **Kỹ thuật chống lỗi `TCP RST` trên Android:**  
  Trình duyệt Chrome trên điện thoại thường gửi kèm User-Agent và Cookie rất dài (lên đến 800 - 1500 bytes). Nếu vi điều khiển chỉ đọc 256 bytes rồi đóng kết nối ngay, ngăn xếp lwIP của ESP32 sẽ phát tín hiệu ngắt kết nối cưỡng bức (`TCP RST`), khiến điện thoại báo lỗi "Không thể kết nối máy chủ". Method này đọc vòng lặp gom đủ dữ liệu đến khi gặp dấu kết thúc HTTP `\r\n\r\n`.

---

### 3.5. Method `_build_status_dict()` & `_send_json(cl, data_dict)`
- **`_build_status_dict()`**: Gom dữ liệu tức thời thành Dictionary chuẩn:
  ```json
  {
    "run": true,
    "act": "ĐI THẲNG BÁM TÂM",
    "s": [0, 0, 1, 0, 0],
    "err": 0.0,
    "l": 62,
    "r": 62,
    "spd": 62,
    "kp": 7.5,
    "ki": 0.04,
    "kd": 4.5
  }
  ```
- **`_send_json()`**: Bổ sung HTTP Header chuẩn `Content-Type: application/json` và bật quyền `Access-Control-Allow-Origin: *` để cả Web và App Android đều có thể gọi API mà không bị chặn bảo mật CORS.

---

### 3.6. Method `poll()` *(Quan trọng nhất)*
- **Chu kỳ thực thi:** Được gọi liên tục trong vòng lặp chính của `main.py`.
- **Cơ chế xử lý:**
  1. Kiểm tra xem có kết nối mới nào từ trình duyệt không (`accept()`). Nếu không có $\to$ thoát ngay (`return`).
  2. Đọc dòng đầu tiên của HTTP Request để tách đường dẫn URL (`path`) và các tham số (`params`):
     - **`GET /api/start?spd=65`**: Gọi `self.tracker.start(65)`.
     - **`GET /api/stop`**: Gọi `self.tracker.stop()`.
     - **`GET /api/manual?l=65&r=65`**: Dừng PID và gọi `self.motor.set_differential(l, r)` để lái thử bằng tay trên Web.
     - **`GET /api/pid?spd=65&kp=8.0&ki=0.05&kd=5.0`**: Gọi `self.tracker.set_params(...)` để cập nhật nóng tham số vào xe.
     - **`GET /api/status`**: Gửi trả dữ liệu JSON để giao diện cập nhật đèn cảm biến và đồ thị mỗi 0.5s.
     - **`GET /` (Trang chủ)**: Gửi mã HTML của giao diện điều khiển về cho trình duyệt.
  3. Đóng socket (`cl.close()`) và gọi giải phóng rác RAM `gc.collect()`.
