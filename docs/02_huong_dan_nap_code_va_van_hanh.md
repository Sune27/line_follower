# 🚀 Hướng Dẫn Nạp Code & Vận Hành Hệ Thống Qua Wi-Fi

Tài liệu hướng dẫn từng bước cách nạp chương trình vào ESP32 và điều khiển xe dò line bằng **Điện thoại** hoặc **Máy tính** thông qua kết nối Wi-Fi.

---

## 1. Cách Nạp Code Vào ESP32 (1-Click Upload)

1. **Chuẩn bị:**
   - Máy tính cài đặt sẵn **Python 3** (kèm thư viện `pyserial`).
   - Cắm cáp USB (loại có truyền dữ liệu) từ cổng Type-C / Micro-USB của mạch ESP32 vào máy tính.
2. **Thực hiện nạp:**
   - Nhấp đúp chuột vào file **`nap_code_esp32.bat`** ở thư mục gốc của dự án (`D:\ki5\line_follower\nap_code_esp32.bat`).
   - Công cụ `firmware/nap_code_esp32.py` sẽ tự động:
     1. Quét tìm cổng COM của ESP32 (ví dụ: `COM3`).
     2. Dừng chương trình cũ đang chạy trên ESP32.
     3. Nạp toàn bộ các file cấu hình và module (`config.py`, `boot.py`, `main.py`, `modules/*`) vào bộ nhớ Flash của ESP32.
     4. Khởi động lại ESP32 và hiển thị địa chỉ IP điều khiển ngay trên màn hình.

---

## 2. Cấu hình Kết nối Wi-Fi (Hotspot Điện Thoại)

Mặc định, ngay khi cấp nguồn (từ Pin hoặc USB), ESP32 sẽ tự động tìm và kết nối vào điểm phát sóng cá nhân (Hotspot) trên điện thoại của bạn:

- **Tên Wi-Fi (SSID) mặc định:** `Sune`
- **Mật khẩu mặc định:** `mouse_love_rice`

> **Cách đổi Tên Wi-Fi và Mật khẩu:**
> Mở file `firmware/config.py`, chỉnh sửa 2 dòng đầu tiên:
> ```python
> WIFI_SSID = "Ten_Hotspot_Cua_Ban"
> WIFI_PASSWORD = "Mat_Khau_Cua_Ban"
> ```
> Sau đó chạy lại `nap_code_esp32.bat` để lưu lên ESP32.

### Lưu ý quan trọng khi bật Hotspot trên điện thoại:
- Hãy chọn băng tần điểm phát sóng là **2.4 GHz** (vì vi điều khiển ESP32 chỉ hỗ trợ Wi-Fi 2.4 GHz, không thu sóng 5 GHz).
- Khi ESP32 đang dò tìm sóng `Sune`, đèn LED màu xanh dương (`GPIO 2`) trên mạch sẽ **nhấp nháy**.
- Ngay khi kết nối thành công vào `Sune`, đèn LED xanh dương sẽ chớp nhanh 5 cái rồi **SÁNG ĐỨNG**.

---

## 3. Mở Giao Diện Điều Khiển Trên Điện Thoại & Máy Tính

### 3.1. Điều khiển bằng Điện thoại
1. Mở trình duyệt **Chrome** (hoặc Safari) trên điện thoại đang bật Hotspot `Sune`.
2. Nhập địa chỉ IP của ESP32 vào thanh địa chỉ:
   ```text
   http://10.174.162.159
   ```
   *(Lưu ý: Nếu điện thoại cấp IP khác, bạn có thể xem địa chỉ IP in trên cửa sổ `nap_code_esp32.bat` lúc nạp code, hoặc vào phần **Cài đặt Hotspot -> Thiết bị đã kết nối -> `xedoline`** trên điện thoại).*

### 3.2. Điều khiển đồng thời bằng Máy tính
1. Cho **Máy tính** kết nối vào cùng mạng Wi-Fi **`Sune`**.
2. Mở trình duyệt Web trên máy tính và truy cập cùng địa chỉ `http://10.174.162.159`.
3. Màn hình trên Điện thoại và Máy tính sẽ **tự động đồng bộ trạng thái với nhau mỗi 0.5 giây**.

---

## 4. Các Chức Năng Trên Bảng Điều Khiển Web

1. **Khối Điều Khiển Chính:**
   - **`▶ BẮT ĐẦU DÒ`:** Kích hoạt chế độ tự hành bám line.
   - **`⏹ DỪNG XE`:** Ngắt xung PWM dừng khẩn cấp cả 2 động cơ ngay lập tức.
   - **Chọn Kiểu Chạy Dò Line:**
     - `🌊 Chạy PID Mượt Liên Tục` (`SMOOTH` - Mặc định): Giữ đà lăn liên tục và tự động bơm gia tốc mạnh khi lệch ra mắt 2/4 hoặc mắt 1/5.
     - `🎯 Nhấp Phanh & Lùi Chỉnh Đầu` (`STEP`): Băm nhịp tiến ngắn kết hợp xoay chỉnh hướng gắt.
2. **Khối Giám Sát 5 Mắt Cảm Biến TCRT5000 (`S1 -> S5`):**
   - Hiển thị trực tiếp mắt nào đang nhìn thấy vạch đen (`1` - sáng màu vàng) hoặc nền trắng (`0` - màu xám).
   - Hiển thị **Sai số vị trí (`Error` từ `-4` đến `+4`)** và **Tốc độ xuất ra 2 bánh (`Bánh Trái`, `Bánh Phải`)**.
   - *Mẹo:* Khi cho xe chạy chính thức và không cần nhìn màn hình, bạn có thể bỏ tích ô `☑ Tự cập nhật` để giảm tải truyền thông Wi-Fi cho ESP32.
3. **Khối Lái Thử Động Cơ (`Manual Test`):**
   - Các nút `▲ TIẾN`, `▼ LÙI`, `◀ TRÁI`, `PHẢI ▶`, `■ DỪNG` dùng để kiểm tra nhanh chiều quay của 2 động cơ và độ khỏe của Pin trước khi đặt xe vào vạch.
4. **Khối Tinh Chỉnh Tốc Độ & PID Trực Tiếp (Live Tuning):**
   - Cho phép thay đổi nóng `Tốc độ cơ sở (%)`, `Kp`, `Ki`, `Kd` và bấm **`💾 CẬP NHẬT THÔNG SỐ`** ngay khi xe đang ở trên sân mà không cần cắm lại cáp USB.
