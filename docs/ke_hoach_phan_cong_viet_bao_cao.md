# 📋 Kế Hoạch & Bảng Phân Công Nhiệm Vụ Viết Báo Cáo Dự Án (5 Thành Viên)

> **Đề tài:** THIẾT KẾ VÀ CHẾ TẠO XE DÒ LINE TỰ HÀNH SỬ DỤNG VI ĐIỀU KHIỂN ESP32 (MICROPYTHON), CẢM BIẾN TCRT5000 5 MẮT, MẠCH CẦU H TB6612FNG VÀ GIÁM SÁT QUA WEB / NGROK  
> **Mẫu chuẩn:** Dựa theo cấu trúc `docs/baocaogk_thamkhao.docx` (Trường ĐH Công nghệ - ĐHQGHN)

---

## 👥 1. Bảng Phân Công Nhiệm Vụ 5 Thành Viên

| STT | Thành Viên | Vai Trò Chuyên Môn | Nội Dung Phụ Trách Trong Báo Cáo | % Đóng Góp Dự Kiến | Tài Liệu & Code Cần Tham Khảo |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | **Nguyễn Trung Tùng (Trưởng nhóm)** | **Kiến trúc Tổng thể & Tổng hợp** | - Bìa, Tóm tắt (Abstract), Từ khóa<br>- **Chương 1:** Giới thiệu (Động lực, Mục tiêu, Bố cục)<br>- **Mục 2.1:** Yêu cầu chung & Sơ đồ luồng hoạt động<br>- **Mục 2.2.1:** Kiến trúc tổng thể hệ thống<br>- Biên tập, định dạng, gộp file Word hoàn chỉnh | 20% | `README.md` |
| **2** | **Đỗ Bá Hưng** | **Phần cứng, Mạch & Nguồn điện** | - **Mục 2.2.7:** Yêu cầu phi chức năng (nguồn, tản nhiệt)<br>- **Mục 3.1:** Kiến trúc phần cứng<br>  + 3.1.0: Bảng linh kiện & Sơ đồ nối chân chi tiết<br>  + 3.1.1: Khối vi điều khiển ESP32<br>  + 3.1.2: Mảng cảm biến TCRT5000 5 mắt<br>  + 3.1.3: Mạch cầu H TB6612FNG & Động cơ DC TT | 20% | - `docs/01_huong_dan_dau_noi_phan_cung.md`<br>- `docs/huong_dan_noi_chan_tcrt5000_5mat_va_tb6612fng.txt`<br>- `firmware/config.py` |
| **3** | **Nguyễn Ngọc Sơn** | **Firmware Nhúng & Thuật Toán PID** | - **Mục 2.2.2:** Đặc tả Bộ điều khiển trung tâm ESP32<br>- **Mục 3.2:** Lập trình hệ thống nhúng (MicroPython)<br>  + Cấu trúc OOP: `LineFollowerSensor`, `MotorDriver`, `LineTracker`<br>  + Thuật toán PID sai số 5 mắt (Error -4..+4)<br>  + Cơ chế Xung mồi Kickstart (98% trong 70ms)<br>  + Bơm gia tốc cua Mắt 1 & 5 và xử lý lọt khe (00000)<br>  + Lưu đồ thuật toán vòng lặp 100Hz (`main.py`) | 20% | - `docs/03_nguyen_ly_thuat_toan_va_tinh_chinh_pid.md`<br>- `firmware/modules/line_sensor.py`<br>- `firmware/modules/motor_driver.py`<br>- `firmware/modules/line_tracker.py`<br>- `firmware/main.py` |
| **4** | **Phạm Minh Quân** | **Truyền Thông, Web Server & Ngrok** | - **Mục 2.2.3 & 2.2.6:** Đặc tả hệ thống truyền thông Wi-Fi, gói tin JSON API<br>- **Mục 2.2.5 & 3.3:** Lập trình Giao diện Web & Server<br>  + Kết nối Wi-Fi Station Mode (`wifi_ap.py`)<br>  + Web Server Non-blocking HTTP (`web_server.py`)<br>  + Tách lớp Frontend: `index.html`, `style.css`, `app.js`<br>  + Cầu nối Ngrok qua Internet (Link tĩnh `saturday-sarcasm-quarrel.ngrok-free.dev`) | 20% | - `docs/02_huong_dan_nap_code_va_van_hanh.md`<br>- `firmware/network/wifi_ap.py`<br>- `firmware/network/web_server.py`<br>- `firmware/network/index.html`<br>- `chay_ngrok_dieu_khien_xe.bat` |
| **5** | **Trương Hữu Nghĩa** | **Thực Nghiệm, Đánh Giá & Video** | - **Chương 4:** Kiểm chứng (Validation)<br>  + Bảng kịch bản test (Đi thẳng, Cua cong, Cua gắt 90 độ, Lọt khe giữa 2 mắt, Trễ Web qua Wi-Fi/Ngrok)<br>  + Bảng kết quả Đạt/Chưa đạt, biểu đồ đánh giá<br>  + Quay/cắt video demo, đăng YouTube/Drive và lấy link<br>- **Chương 5:** Kết luận & Hướng phát triển | 20% | - Chạy thử nghiệm xe trên sân thực tế<br>- Quay video thao tác trên Web & trên đường đua |

---

## 📝 2. Hướng Dẫn Chi Tiết Từng Phần Cho Từng Thành Viên

### 👤 Nguyễn Trung Tùng: Trưởng nhóm – Kiến trúc tổng thể & Tổng hợp
- **Trang bìa & Tóm tắt:** Điền tên đề tài, bảng thông tin 5 thành viên (Họ tên, MSV, link GitHub). Viết phần Tóm tắt (150–250 từ) tóm lược bài toán xe tự hành, giải pháp điều khiển PID trên ESP32 và giám sát qua Web/Ngrok.
- **1. Giới thiệu:**
  - *1.1. Động lực:* Ứng dụng AGV vận chuyển trong nhà máy thông minh, bài toán tự hành trong robotics.
  - *1.2. Mục tiêu:* Xây dựng mô hình robot bám line ổn định ở tốc độ cao, điều khiển và tinh chỉnh tham số PID thời gian thực không dây.
  - *1.3. Nội dung chính:* Tóm tắt ngắn gọn 5 chương của báo cáo.
- **2.1 & 2.2.1:** Vẽ sơ đồ kiến trúc tổng thể gồm 4 khối: Khối cảm biến (TCRT5000) $\to$ Khối vi điều khiển (ESP32) $\to$ Khối chấp hành (TB6612FNG + DC Motor) $\leftrightarrow$ Khối điều khiển/Giám sát (Web Dashboard / Ngrok).
- **Trách nhiệm cuối:** Định dạng font chữ (Times New Roman), căn lề, mục lục tự động và xuất bản file PDF/Word nộp giảng viên.

---

### 👤 Đỗ Bá Hưng: Phần cứng & Mạch công suất
- **3.1.0. Danh sách linh kiện:** Lập bảng gồm: ESP32 NodeMCU 30-Pin + Shield mở rộng, Mảng cảm biến TCRT5000 5 kênh, Driver TB6612FNG (bản 4 dây PWM), Khung xe 2 bánh kèm động cơ DC TT (tỷ số truyền 1:48), 2 Cell Pin 18650 (7.4V - 8.4V).
- **Sơ đồ đấu nối (Wiring Diagram):**
  - Chèn bảng nối chân chi tiết từ file `docs/01_huong_dan_dau_noi_phan_cung.md`.
  - Nêu rõ giải pháp ánh xạ kép cho chân `D12` (chân strapping pin của ESP32) sang chân `D14` để đảm bảo an toàn khi khởi động.
- **3.1.1, 3.1.2, 3.1.3:**
  - Giải thích nguyên lý mảng hồng ngoại 5 mắt (Active-Low: Đen=0, Trắng=1) và cách xoay biến trở để độ nhạy đồng đều.
  - Giải thích mạch cầu H TB6612FNG điều khiển động cơ bằng PWM 4 kênh trực tiếp không qua chân Enable.
- **2.2.7. Yêu cầu phi chức năng:** Phân tích mức tiêu thụ dòng của động cơ, cách ly nguồn Logic và nguồn Động cơ (VM) để tránh sụt áp gây reset ESP32.

---

### 👤 Nguyễn Ngọc Sơn: Firmware Nhúng & Thuật Toán PID
- **3.2. Lập trình hệ thống nhúng (MicroPython):**
  - Giới thiệu cấu trúc lập trình hướng đối tượng (OOP) của các lớp trong `firmware/modules/`:
    - `LineFollowerSensor`: Đọc bitmask 5 mắt và quy đổi ra sai số $e \in [-4.0, +4.0]$.
    - `MotorDriver`: Phát xung PWM 1kHz và tự động kích hoạt **Kickstart (98% trong 70ms)** khi bánh xe bắt đầu chuyển động từ trạng thái nghỉ để thắng ma sát tĩnh.
    - `LineTracker`: Tính toán giải thuật PID và bộ bơm gia tốc cua.
- **Công thức điều khiển:**
  - Công thức PID rời rạc:
    $$u(t) = K_p \cdot e(t) + K_i \sum e(t)\Delta t + K_d \frac{e(t) - e(t-\Delta t)}{\Delta t}$$
  - Cơ chế **Bơm gia tốc cua gắt (Corner Boost):** Khi lệch ra mắt $S_1$ hoặc $S_5$, bánh ngoài được bơm lên 90%, bánh trong lùi -65% để tạo ngẫu lực bẻ lái không bị kẹt bánh.
  - Cơ chế **Nội suy lọt khe:** Xử lý trường hợp vạch đen lọt vào khe giữa 2 đèn (`00000`).
- **Lưu đồ thuật toán:** Vẽ lưu đồ cho hàm `main()` với chu kỳ điều khiển cố định 10ms (100Hz).

---

### 👤 Phạm Minh Quân: Truyền Thông, Web Server & Ngrok
- **3.3. Lập trình Website/App & Truyền thông:**
  - Mô tả mô hình kết nối: ESP32 cấu hình ở chế độ `STA_IF` tự động kết nối vào Hotspot điện thoại `Sune` (băng tần 2.4GHz), hoàn toàn tắt chế độ `AP_IF` để tiết kiệm năng lượng và tránh nóng chip.
  - Giải thích máy chủ Web Non-blocking HTTP trên cổng 80 trong `firmware/network/web_server.py`: Xử lý bắt tay TCP, cơ chế buffer tránh lỗi `TCP RST` trên điện thoại Android.
  - Kiến trúc phân tách giao diện: `index.html` (cấu trúc Dark Mode), `style.css` (giao diện hiện đại), `app.js` (gửi request RESTful API qua `fetch()`, tự động đồng bộ trạng thái xe mỗi 500ms).
- **Mở rộng Internet qua Ngrok:**
  - Giải thích giải pháp đường hầm (Reverse Tunnel) qua máy tính trung gian bằng lệnh:
    `ngrok http http://10.174.162.159:80 --domain=saturday-sarcasm-quarrel.ngrok-free.dev --host-header=rewrite`
  - Giúp xe có thể nhận lệnh điều khiển và giám sát từ bất kỳ đâu qua mạng 4G/Internet với tên miền tĩnh cố định.

---

### 👤 Trương Hữu Nghĩa: Thực Nghiệm, Đánh Giá & Video
- **4.1. Bảng kịch bản kiểm chứng:**
  - *Bài test 1: Đi thẳng ổn định* (Tốc độ cơ sở 62%, sai số dao động quanh $0 \pm 0.5$).
  - *Bài test 2: Vào cua góc tù và góc vuông* (Kiểm chứng lực bơm bánh ngoài 90% và lùi bánh trong -65%).
  - *Bài test 3: Kiểm chứng xung mồi Kickstart* (Xe khởi hành êm ái, không bị ì hoặc đứng bánh).
  - *Bài test 4: Điều khiển từ xa qua Ngrok* (Đo độ trễ phản hồi khi bấm nút Bắt đầu/Dừng qua mạng 4G).
  - Lập bảng tổng hợp: [Chức năng | Điều kiện thử | Kết quả mong đợi | Kết quả thực tế | Đánh giá Đạt/Chưa đạt].
- **4.2. Video minh chứng:**
  - Quay clip ngắn (2-3 phút) bao gồm: Xe chạy trên sa bàn, màn hình điện thoại cập nhật trạng thái 5 mắt cảm biến, thao tác bấm nút Dừng/Chạy.
  - Tải lên YouTube (chế độ Không công khai hoặc Công khai) hoặc Google Drive, dán link vào báo cáo.
- **5. Kết luận:**
  - Đánh giá những gì đã làm được và các giới hạn còn tồn tại (ví dụ: sa bàn có ánh sáng mạnh có thể ảnh hưởng mắt hồng ngoại).
  - Hướng phát triển: Thêm cảm biến siêu âm tránh vật cản, cảm biến đo điện áp pin tự động bù ga, tích hợp camera nhận diện làn đường.

---

## 📅 3. Kế Hoạch Tiến Độ Đề Xuất (3 Giai Đoạn)

```text
GIAI ĐOẠN 1 (Ngày 1 - Ngày 3): VIẾT BẢN THẢO THÔ
├── Nguyễn Trung Tùng: Hoàn thành Khung báo cáo, Chương 1 và Mục 2.1, 2.2.1
├── Đỗ Bá Hưng: Điền Bảng linh kiện và vẽ Sơ đồ đấu dây chi tiết
├── Nguyễn Ngọc Sơn: Soạn công thức PID, cơ chế Kickstart, vẽ Lưu đồ thuật toán
├── Phạm Minh Quân: Chụp ảnh giao diện Web, giải thích API và cấu hình Ngrok
└── Trương Hữu Nghĩa: Lập danh sách kịch bản test và chuẩn bị sân chạy

GIAI ĐOẠN 2 (Ngày 4 - Ngày 5): CHẠY TEST & THU THẬP MINH CHỨNG
├── Toàn nhóm: Cho xe chạy trên sa bàn thực tế
├── Trương Hữu Nghĩa: Ghi lại số liệu thực nghiệm (bảng 4.1), quay và dựng Video demo
└── Các Đỗ Bá Hưng, Nguyễn Ngọc Sơn, Phạm Minh Quân: Bổ sung hình ảnh thực tế mạch, cảm biến và đồ thị vào phần của mình

GIAI ĐOẠN 3 (Ngày 6): TỔNG HỢP & HOÀN THIỆN
├── Nguyễn Trung Tùng: Ghép nối các phần vào file Word chính thức, chuẩn hóa font và mục lục
└── Toàn nhóm: Review chéo để đảm bảo tính nhất quán số liệu trước khi nộp
```
