# 📖 Tài Liệu Chi Tiết Các Method Trong Class `WiFiStationClient`

> **File mã nguồn:** [`firmware/network/wifi_ap.py`](../../firmware/network/wifi_ap.py)  
> **Phần cứng quản lý:** Bộ thu phát sóng Wi-Fi 2.4GHz tích hợp trên ESP32 và đèn LED xanh báo trạng thái (`GPIO 2`).

---

## 🎯 1. Tổng Quan Về Class `WiFiStationClient`

Class `WiFiStationClient` đảm nhiệm toàn bộ tầng kết nối mạng không dây của robot:
1. **Tắt hoàn toàn chế độ phát sóng Access Point (`AP_IF`):** Giúp giảm thiểu tối đa điện năng tiêu thụ từ pin và hạn chế nóng chip ESP32.
2. **Kích hoạt chế độ thu Wi-Fi Station Mode (`STA_IF`):** Tự động dò quét và kết nối vào Hotspot cá nhân của điện thoại (`Sune`).
3. Đặt tên định danh thiết bị trên mạng cục bộ là `xedoline`.
4. Điều khiển nhấp nháy đèn LED xanh trên mạch để người dùng biết khi nào xe đang tìm mạng và khi nào đã kết nối thành công.
5. Cung cấp địa chỉ IP cục bộ cho Web Server và người dùng.

---

## 📋 2. Bảng Tóm Tắt Danh Sách Các Method

| Tên Method | Tham Số Đầu Vào | Kiểu Trả Về | Tác Dụng Chính |
| :--- | :--- | :---: | :--- |
| **`__init__()`** | `ssid, password, timeout_sec, led_pin` | `None` | Khởi tạo giao diện mạng `STA_IF`, tắt `AP_IF` và cấu hình chân LED trạng thái. |
| **`_blink()`** | `count, on_ms, off_ms` | `None` | Hàm nhấp nháy đèn LED xanh (GPIO 2) theo chu kỳ định sẵn. |
| **`start()`** | Không có | `str` (IP) | **(Quan trọng nhất)** Quét tìm sóng Wi-Fi và tiến hành kết nối, trả về địa chỉ IP điều khiển. |
| **`check_connection()`**| Không có | `bool` | Kiểm tra kết nối định kỳ trong lúc xe nghỉ và đồng bộ trạng thái đèn LED. |
| **`get_ip()`** | Không có | `str` | Trả về địa chỉ IP hiện tại của xe (hoặc `"0.0.0.0"` nếu chưa kết nối). |

---

## 🔍 3. Chi Tiết Từng Method

### 3.1. Method `__init__(ssid=None, password=None, timeout_sec=10, led_pin=2)`
- **Loại:** Constructor.
- **Nhiệm vụ:**
  - Lấy tên Wi-Fi và mật khẩu từ `config.py` (mặc định: SSID `"Sune"`, Password `"mouse_love_rice"`).
  - Khởi tạo 2 giao diện mạng của MicroPython:
    ```python
    self.sta = network.WLAN(network.STA_IF)
    self.ap = network.WLAN(network.AP_IF)
    ```
  - Cấu hình chân `GPIO 2` làm ngõ ra điều khiển đèn LED màu xanh trên mạch ESP32.

---

### 3.2. Method `_blink(count=4, on_ms=70, off_ms=70)`
- **Loại:** Private Helper Method.
- **Mục đích:** Tạo hiệu ứng chớp tắt đèn LED làm tín hiệu báo động cho người dùng.
- **Ứng dụng:** Được gọi khi ESP32 bắt được mạng thành công (chớp nhanh 5 cái liên tiếp trước khi chuyển sang sáng đứng).

---

### 3.3. Method `start()` *(Quan trọng nhất)*
- **Loại:** Public Method.
- **Mục đích:** Quy trình tự động quét và kết nối vào điểm phát sóng.
- **Trình tự các bước thực hiện:**
  1. **Bước 1 (Tiết kiệm năng lượng):** Tắt dứt điểm bộ phát AP: `self.ap.active(False)`.
  2. **Bước 2 (Cấu hình thu):** Bật `self.sta.active(True)`, đặt công suất phát `txpower = 14dBm` và đặt Hostname là `"xedoline"`.
  3. **Bước 3 (Dò quét sóng - Scan):** Quét danh sách các mạng xung quanh để tìm chính xác sóng mang tên `Sune` (không phân biệt chữ hoa/thường).
  4. **Bước 4 (Kết nối có kiểm soát thời gian):**
     - Thực hiện tối đa 3 lần thử kết nối.
     - Trong lúc chờ, đèn LED xanh sẽ nhấp nháy mỗi `250ms`.
  5. **Bước 5 (Thành công):**
     - Khi `self.sta.isconnected() == True`: chớp đèn 5 lần, giữ đèn LED xanh **SÁNG ĐỨNG** và in ra địa chỉ IP (ví dụ: `10.174.162.159`).
  6. **Bước 6 (Dự phòng nếu chưa bật Hotspot):**
     - Nếu sau 3 lần vẫn chưa thấy sóng `Sune` (do bạn chưa kịp bật Hotspot trên điện thoại), hàm vẫn giữ lệnh kết nối ngầm để khi bạn vừa gạt bật Hotspot trên điện thoại thì ESP32 sẽ tự động bắt vào ngay lập tức.
- **Giá trị trả về:** Chuỗi String chứa địa chỉ IP điều khiển (ví dụ `"10.174.162.159"`).

---

### 3.4. Method `check_connection()`
- **Loại:** Public Method.
- **Mục đích:** Giám sát "sức khỏe" kết nối Wi-Fi.
- **Nhiệm vụ:**
  - Được gọi mỗi 5 giây trong lúc xe đang ở trạng thái dừng (`STOPPED`).
  - Cập nhật lại đèn LED: Nếu bị rớt mạng thì tắt đèn LED, nếu mạng ổn định thì giữ đèn sáng.
- **Giá trị trả về:** `True` (nếu đang kết nối), `False` (nếu mất mạng).

---

### 3.5. Method `get_ip()`
- **Mục đích:** Lấy địa chỉ IP hiện thời của xe mà không cần khởi tạo lại kết nối mạng.
- **Giá trị trả về:** `self.sta.ifconfig()[0]` (ví dụ `"10.174.162.159"`).
