# 🤖 Dự Án Xe Dò Line Tự Hành ESP32 (TCRT5000 5 Mắt + TB6612FNG)

Hệ thống điều khiển xe dò line cơ điện tử sử dụng **ESP32 (MicroPython)**, mảng cảm biến hồng ngoại **TCRT5000 5 mắt** và mạch công suất **TB6612FNG**, tích hợp giao diện điều khiển trực tiếp qua **Wi-Fi trên Điện thoại & Máy tính**.

---

## 📚 Tài Liệu Hướng Dẫn Chi Tiết (`docs/`)

Toàn bộ tài liệu hướng dẫn đấu nối, vận hành và tinh chỉnh thuật toán được lưu trữ trong thư mục [`docs/`](./docs):

1. 🔌 **[01_huong_dan_dau_noi_phan_cung.md](./docs/01_huong_dan_dau_noi_phan_cung.md)**: Hướng dẫn đấu nối chi tiết ESP32 Shield 30-Pin với TB6612FNG, TCRT5000 5 mắt và cách cân chỉnh biến trở độ nhạy.
2. 🚀 **[02_huong_dan_nap_code_va_van_hanh.md](./docs/02_huong_dan_nap_code_va_van_hanh.md)**: Hướng dẫn nạp code 1-Click (`nap_code_esp32.bat`), kết nối Wi-Fi Hotspot `Sune` và sử dụng giao diện điều khiển trên Điện thoại / Máy tính.
3. 🧠 **[03_nguyen_ly_thuat_toan_va_tinh_chinh_pid.md](./docs/03_nguyen_ly_thuat_toan_va_tinh_chinh_pid.md)**: Giải thích nguyên lý tính sai số 5 mắt, cơ chế Xung mồi `Kickstart`, Bơm gia tốc cua ở Mắt 1 & 5, xử lý vạch lọt khe và bảng hướng dẫn chỉnh thông số `Kp, Ki, Kd`.
4. 📄 **[huong_dan_noi_chan_tcrt5000_5mat_va_tb6612fng.txt](./docs/huong_dan_noi_chan_tcrt5000_5mat_va_tb6612fng.txt)**: Bản sơ đồ nối chân gốc dạng văn bản thuần (Text).

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
line_follower/
├── README.md                                          # Trang tổng quan dự án
├── nap_code_esp32.bat                                 # Công cụ nạp code 1-Click vào ESP32
├── chay_ngrok_dieu_khien_xe.bat                       # Cầu nối ngrok điều khiển xe từ xa qua Internet
├── docs/                                              # Thư mục lưu trữ toàn bộ tài liệu hướng dẫn (.md, .txt)
│   ├── 01_huong_dan_dau_noi_phan_cung.md
│   ├── 02_huong_dan_nap_code_va_van_hanh.md
│   ├── 03_nguyen_ly_thuat_toan_va_tinh_chinh_pid.md
│   ├── ke_hoach_phan_cong_viet_bao_cao.md             # Kế hoạch & phân công viết báo cáo 5 người
│   ├── quy_tac_dinh_dang_bao_cao.md                   # Quy chuẩn định dạng Word (font, lề, ảnh, bảng, công thức)
│   ├── Bao_Cao_Phan_3_Thanh_Vien_3_Firmware_PID.docx  # Bản thảo Word mẫu hoàn chỉnh Phần 3 (Thành viên 3)
│   ├── classes/                                       # Phân tích chi tiết các Class OOP
│   │   └── LineFollowerSensor.md                      # Tác dụng từng method trong class đọc cảm biến
│   └── huong_dan_noi_chan_tcrt5000_5mat_va_tb6612fng.txt
└── firmware/                                          # Mã nguồn MicroPython nạp lên ESP32
    ├── config.py                                      # Cấu hình Wi-Fi, chân GPIO, thông số tốc độ & PID
    ├── boot.py                                        # Khởi động tự động khi cấp nguồn Pin
    ├── main.py                                        # Vòng lặp chính thời gian thực (100Hz)
    ├── nap_code_esp32.py                              # Script tự động dò cổng COM và nạp firmware
    ├── modules/                                       # Khối Phần cứng & Điều khiển xe (OOP)
    │   ├── line_sensor.py                             # Đọc 5 mắt TCRT5000 & tính toán sai số (-4 .. +4)
    │   ├── motor_driver.py                            # Điều khiển PWM 4 kênh TB6612FNG + Xung mồi Kickstart
    │   └── line_tracker.py                            # Thuật toán dò line mượt PID + Bơm gia tốc cua
    └── network/                                       # Khối Truyền thông Wi-Fi & Giao diện Web
        ├── wifi_ap.py                                 # Module tự động tìm và kết nối Wi-Fi (Hotspot "Sune")
        ├── web_server.py                              # Web Server HTTP Non-blocking xử lý API điều khiển
        ├── index.html                                 # Giao diện HTML bảng điều khiển
        ├── style.css                                  # Định dạng giao diện CSS (Dark Mode)
        └── app.js                                     # Logic JavaScript gửi lệnh và đồng bộ trạng thái
```

---

## ⚡ Bắt Đầu Nhanh (Quick Start)

1. **Nạp code:** Cắm cáp USB từ ESP32 vào máy tính và nhấp đúp chạy `nap_code_esp32.bat`.
2. **Bật Wi-Fi Hotspot:** Bật điểm phát sóng cá nhân (2.4 GHz) trên điện thoại với tên **`Sune`** (mật khẩu: `mouse_love_rice`). Đèn LED xanh trên ESP32 sẽ **sáng đứng** khi kết nối thành công.
3. **Điều khiển mạng nội bộ (Local Wi-Fi):** Mở trình duyệt Chrome trên điện thoại hoặc máy tính và truy cập `http://10.174.162.159` (hoặc IP in ra khi nạp code) để bắt đầu chạy xe!

---

## 🌐 Điều Khiển Trực Tuyến Qua Internet (Ngrok Public Link)

Dự án đã tích hợp đường link ngrok tĩnh cố định cho tài khoản của bạn, cho phép theo dõi cảm biến và điều khiển xe từ xa qua mạng Internet (sử dụng 4G/5G từ bất kỳ đâu):

- 🔗 **Link Web Điều Khiển Online:** **[https://saturday-sarcasm-quarrel.ngrok-free.dev](https://saturday-sarcasm-quarrel.ngrok-free.dev)**
- 🚀 **Cách kích hoạt:**
  1. Đảm bảo xe và máy tính cùng kết nối vào mạng Wi-Fi Hotspot **`Sune`**.
  2. Nhấp đúp chuột vào file **`chay_ngrok_dieu_khien_xe.bat`** trên máy tính (bấm Enter để nhận IP mặc định `10.174.162.159`).
  3. Mở đường link trên trên bất kỳ điện thoại, máy tính bảng hay laptop nào có kết nối Internet để điều khiển xe trực tiếp!
