# 🤖 Dự Án Xe Dò Line Tự Hành ESP32 (TCRT5000 5 Mắt + TB6612FNG)

Hệ thống điều khiển xe dò line cơ điện tử sử dụng **ESP32 (MicroPython)**, mảng cảm biến hồng ngoại **TCRT5000 5 mắt** và mạch công suất **TB6612FNG**, tích hợp giao diện điều khiển trực tiếp qua **Wi-Fi trên Điện thoại & Máy tính**.

---

## 1. Cấu trúc thư mục dự án

```text
line_follower/
├── huong_dan_noi_chan_tcrt5000_5mat_va_tb6612fng.txt  # Sơ đồ đấu nối phần cứng chi tiết
├── nap_code_esp32.bat                                 # Công cụ nạp code 1-Click vào ESP32
└── firmware/
    ├── config.py                                      # Cấu hình Wi-Fi, chân GPIO, thông số tốc độ & PID
    ├── boot.py                                        # Khởi động tự động khi cấp nguồn Pin
    ├── main.py                                        # Vòng lặp chính thời gian thực (100Hz)
    ├── nap_code_esp32.py                              # Script tự động dò cổng COM và nạp firmware
    └── modules/
        ├── wifi_ap.py                                 # Module tự động tìm và kết nối Wi-Fi (Hotspot)
        ├── web_server.py                              # Web Server Non-blocking điều khiển qua trình duyệt
        ├── line_sensor.py                             # Đọc 5 mắt TCRT5000 & tính toán sai số (-4 .. +4)
        ├── motor_driver.py                            # Điều khiển PWM 4 kênh TB6612FNG + Xung mồi Kickstart
        └── line_tracker.py                            # Thuật toán dò line (Chế độ SMOOTH PID & STEP)
```

---

## 2. Sơ đồ chân kết nối (ESP32 Shield 30-Pin)

| Linh kiện | Chân Module | Chân ESP32 Shield | Ghi chú |
| :--- | :--- | :--- | :--- |
| **TB6612FNG** | `AIN1`, `AIN2` | `D13`, `D12` (hoặc `D14`) | Động cơ Bánh Trái (PWM) |
| **TB6612FNG** | `BIN1`, `BIN2` | `D27`, `D26` | Động cơ Bánh Phải (PWM) |
| **TB6612FNG** | `VM`, `STBY`, `GND` | `5V`, `3V/5V`, `GND` | Nguồn động cơ & kích hoạt IC |
| **TCRT5000 (5 mắt)** | `OUT1` .. `OUT5` | `D21, D19, D18, D5, D17` | 5 cọc liền kề hàng bên phải |
| **TCRT5000 (5 mắt)** | `VCC`, `GND` | `3V`, `GND` | Cấp nguồn 3.3V chuẩn logic ESP32 |

---

## 3. Hướng dẫn nạp code & Vận hành

1. **Nạp code vào ESP32:**
   - Cắm cáp USB kết nối ESP32 với máy tính.
   - Nhấp đúp vào file `nap_code_esp32.bat` để tự động nạp toàn bộ mã nguồn.
2. **Kết nối Wi-Fi & Điều khiển:**
   - Bật điểm phát sóng cá nhân (Hotspot 2.4GHz) trên điện thoại với tên **`Sune`** (mật khẩu: `mouse_love_rice`) — có thể thay đổi trong `firmware/config.py`.
   - Khi ESP32 kết nối thành công, đèn LED xanh trên mạch sẽ **sáng đứng**.
   - Mở trình duyệt trên điện thoại hoặc máy tính và truy cập địa chỉ IP của ESP32 (ví dụ: `http://10.174.162.159`) để điều khiển xe và tinh chỉnh thông số trực tiếp.
