# 📐 Quy Chuẩn & Quy Tắc Định Dạng Báo Cáo Kỹ Thuật (Format Guide)

> **Dành cho:** Toàn bộ 5 thành viên tham gia viết báo cáo dự án xe dò line ESP32.  
> **Mục tiêu:** Đảm bảo toàn bộ tài liệu sau khi ghép nối đạt tính nhất quán, chuyên nghiệp theo đúng chuẩn học thuật của **Trường Đại học Công nghệ – ĐHQGHN (UET - VNU)**.

---

## 📄 1. Khổ Giấy, Căn Lề & Đánh Số Trang

### 1.1. Căn lề trang văn bản (Page Margins)
Cấu hình trong Word: thẻ **Layout $\to$ Margins $\to$ Custom Margins**:
- **Khổ giấy:** `A4` ($210 \times 297\text{ mm}$), hướng giấy đứng (`Portrait`).
- **Lề trên (Top):** `2.0 cm` – `2.5 cm`.
- **Lề dưới (Bottom):** `2.0 cm` – `2.5 cm`.
- **Lề trái (Left):** `3.0 cm` – `3.5 cm` *(rộng hơn để chừa gáy đóng bìa/dập ghim)*.
- **Lề phải (Right):** `2.0 cm`.

### 1.2. Đánh số trang (Page Numbering)
- Vị trí: Góc dưới cùng bên phải (`Bottom Right`) hoặc ở giữa chân trang (`Bottom Center`).
- **Phần đầu** (Trang bìa, Tóm tắt, Mục lục, Lịch sử tài liệu): Đánh số La Mã chữ thường (`i, ii, iii...`) — *Trang bìa không hiện số*.
- **Phần nội dung chính** (Bắt đầu từ *Chương 1* đến hết *Chương 5* và Phụ lục): Đánh số Ả Rập (`1, 2, 3...`) bắt đầu từ trang `1`.

---

## 🔤 2. Quy Chuẩn Font Chữ & Giãn Dòng (Typography)

Tất cả thành viên **bắt buộc sử dụng Style có sẵn trong file Word** (`Normal`, `Heading 1`, `Heading 2`...), không tự chỉnh tay từng đoạn để tránh lệch định dạng.

| Thành Phần | Font Chữ | Cỡ Chữ (Size) | Kiểu (Style) | Căn Lề (Alignment) | Giãn Dòng & Giãn Đoạn |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Đoạn văn thông thường (Body Text)** | **Times New Roman** | **13 pt** *(hoặc 12 pt)* | Thường (Regular) | **Căn đều hai bên (Justified)** | - Giãn dòng: `1.3 lines` (hoặc `1.5 lines`)<br>- Giãn đoạn: `Before 3 pt`, `After 3 pt`<br>- Thụt đầu dòng: `First Line 1.0 cm` *(1 tab chuẩn)* |
| **Tiêu đề Chương (Heading 1)** | Times New Roman | **15 – 16 pt** | **IN HOA, ĐẬM** | Căn trái (hoặc Giữa) | - `Before 12 pt`, `After 6 pt`<br>- Ngắt trang mới trước mỗi chương |
| **Mục cấp 1 (Heading 2)** | Times New Roman | **13 – 14 pt** | **In đậm** | Căn trái | - `Before 9 pt`, `After 4 pt`<br>- Ví dụ: **1.1. Động lực (Motivation)** |
| **Mục cấp 2 (Heading 3)** | Times New Roman | **13 pt** | **In đậm** | Căn trái | - `Before 6 pt`, `After 3 pt`<br>- Ví dụ: **2.2.1. Kiến trúc tổng thể** |
| **Mục cấp 3 (Heading 4)** | Times New Roman | **13 pt** | *In nghiêng* | Căn trái | - `Before 4 pt`, `After 2 pt` |

> ⚠️ **LƯU Ý CỰC KỲ QUAN TRỌNG:**
> - Tuyệt đối **KHÔNG dùng phím Space (cách) liên tiếp** để thụt đầu dòng. Hãy dùng tính năng `First Line Indent: 1.0 cm` của Word.
> - Tuyệt đối **KHÔNG chia mục quá 4 cấp** (ví dụ: tối đa là `3.2.1.1`, không được chia `3.2.1.1.1`).

---

## 🖼️ 3. Quy Chuẩn Hình Ảnh, Sơ Đồ & Đồ Thị (Figures)

### 3.1. Kích thước & Vị trí ảnh
- **Chất lượng:** Ảnh chụp mạch, sơ đồ khối phải rõ nét, độ phân giải cao, chữ trong ảnh đọc được dễ dàng. Không chụp màn hình IDE bị mờ hoặc nền đen quá tối.
- **Tỷ lệ ảnh:** Tuyệt đối giữ đúng tỷ lệ khung hình (Aspect Ratio), không kéo méo dẹp hoặc kéo dài ảnh.
- **Kích thước:**
  - Chiều rộng ảnh (Width) khuyên dùng: **`10 cm` – `14 cm`** (chiếm khoảng 60% – 85% chiều rộng trang giấy).
  - Không để ảnh tràn ra ngoài lề trang văn bản.
- **Căn lề:** Luôn đặt ảnh ở chế độ **`In Line with Text`** và **Căn giữa trang (Center)**.

### 3.2. Chú thích hình (Figure Caption)
- **Vị trí chú thích:** Luôn nằm **PHÍA DƯỚI** hình ảnh.
- **Căn lề:** Căn giữa (`Center`).
- **Font & Size:** Times New Roman, cỡ **`11 pt`** hoặc **`12 pt`**, in nghiêng.
- **Cú pháp đặt tên:**
  $$\text{Hình [Số chương].[Số thứ tự hình]. [Tên mô tả hình ngắn gọn, rõ nghĩa]}$$
- **Ví dụ chuẩn:**
  - *Hình 2.1. Sơ đồ kiến trúc tổng thể các khối trong hệ thống xe dò line.*
  - *Hình 3.2. Sơ đồ đấu nối chân giữa ESP32 Shield, TB6612FNG và mảng TCRT5000.*
  - *Hình 4.3. Giao diện Web điều khiển thời gian thực trên trình duyệt điện thoại.*
- **Nguyên tắc dẫn chiếu:** Trước khi xuất hiện hình, trong đoạn văn bản phải có ít nhất một câu nhắc tới hình đó (ví dụ: *"Sơ đồ nguyên lý đấu nối phần cứng được thể hiện chi tiết tại Hình 3.2"*). Không được thả hình mồ côi mà không có lời dẫn.

---

## 📊 4. Quy Chuẩn Bảng Biểu (Tables)

### 4.1. Vị trí & Căn lề
- Toàn bộ bảng phải được **Căn giữa trang (Center)**.
- Độ rộng các cột nên cân đối vừa vặn với nội dung, không để một từ bị bẻ dòng vô lý (ví dụ: không để chữ `"Thành"` một dòng và `"viên"` xuống dòng tiếp theo).

### 4.2. Chú thích bảng (Table Caption)
- **Vị trí chú thích:** Nằm **PHÍA TRÊN** bảng (ngược lại với hình ảnh).
- **Căn lề:** Căn trái (`Left`) hoặc Căn giữa (`Center`).
- **Font & Size:** Times New Roman, cỡ **`12 pt`**, in đậm phần nhãn.
- **Cú pháp:**
  $$\text{\textbf{Bảng [Số chương].[Số thứ tự].} [Tên mô tả bảng]}$$
- **Ví dụ chuẩn:**
  - **Bảng 3.1.** Danh mục linh kiện phần cứng sử dụng trong dự án.
  - **Bảng 3.2.** Bảng quy đổi bitmask 5 mắt cảm biến sang sai số vị trí $e(t)$.
  - **Bảng 4.1.** Kết quả thực nghiệm các kịch bản kiểm thử góc cua và bám vạch.

### 4.3. Màu sắc & Định dạng ô trong bảng
- **Hàng tiêu đề (Header Row):**
  - Chữ in đậm (**Bold**), căn giữa ô.
  - Nền hàng tiêu đề (Shading): Màu xám nhạt (`#E2E8F0` hoặc `#F1F5F9`) hoặc để trắng viền đậm. Không dùng màu nền tối đen hoặc màu neon chói mắt.
- **Nội dung các ô:**
  - Ô chứa chữ/văn bản: Căn lề trái (`Left`).
  - Ô chứa số liệu, số thứ tự, đơn vị, trạng thái Đạt/Chưa đạt: Căn giữa (`Center`).
  - Cỡ chữ trong bảng: **`11 pt` – `12 pt`**, giãn dòng đơn (`Single` hoặc `1.15 lines`).

---

## 🧮 5. Quy Chuẩn Công Thức Toán Học & Ký Hiệu (Equations)

- Công thức toán học bắt buộc phải soạn thảo bằng công cụ **Equation** tích hợp trong Word (phím tắt `Alt + =`) hoặc MathType. Tuyệt đối **không chụp ảnh công thức** rồi dán vào.
- **Công thức quan trọng:** Đặt trên một dòng riêng, căn giữa trang, có đánh số thứ tự ở mép phải trong dấu ngoặc tròn:
  $$u(t) = K_p \cdot e(t) + K_i \sum e(t)\Delta t + K_d \frac{e(t) - e(t-\Delta t)}{\Delta t} \qquad (3.1)$$
- **Ký hiệu biến số:**
  - Biến số, hàm số: Viết nghiêng ($e, u, t, K_p, K_i, K_d$).
  - Số học, tên hàm chuẩn, đơn vị đo: Viết đứng ($2, \pi, \sin, \cos, \text{Hz}, \text{ms}, \text{V}, \text{cm}$).
  - Giải thích rõ các đại lượng ngay bên dưới công thức:  
    *Trong đó: $e(t)$ là sai số vị trí tại thời điểm $t$; $K_p, K_i, K_d$ lần lượt là các hệ số Tỷ lệ, Tích phân và Đạo hàm.*

---

## 💻 6. Quy Chuẩn Trích Dẫn Mã Nguồn Code (Code Snippets)

Khi trích dẫn các đoạn code quan trọng (như thuật toán PID, hàm ngắt, API socket):
- **Font chữ code:** Dùng font đơn cách (**Monospace**): `Consolas`, `Courier New` hoặc `Cascadia Code`.
- **Cỡ chữ:** **`10 pt` – `11 pt`**.
- **Cách trình bày:**
  - Đặt code trong bảng 1 ô (hoặc khung Textbox) có đường viền xám mỏng và nền màu xám nhạt (`#F8FAFC`).
  - Có đánh số dòng hoặc chú thích code rõ ràng.
  - Không chèn code quá dài (trên 1 trang). Chỉ trích dẫn các đoạn hàm cốt lõi; toàn bộ mã nguồn đẩy lên link GitHub và ghi rõ đường dẫn ở trang bìa.

```python
# Ví dụ định dạng trích dẫn hàm tính sai số trong báo cáo:
def calculate_error(self, raw_list=None):
    s1, s2, s3, s4, s5 = raw_list
    bitmask = (s1 << 4) | (s2 << 3) | (s3 << 2) | (s4 << 1) | s5
    return self.MAP_ERROR.get(bitmask, self.last_valid_error)
```

---

## 🎨 7. Bảng Màu Sắc Chuẩn (Color Palette)

Để báo cáo vừa đẹp mắt, vừa nghiêm túc khi in màu hoặc in đen trắng nộp hội đồng:
- **Màu chữ chính:** Màu đen thuần (`#000000`) hoặc xám đậm (`#1E293B`). Tuyệt đối không dùng chữ màu xám nhạt khó đọc.
- **Màu nhấn (Primary Accent):** Xanh dương đậm (`Dark Blue - #0F4C81` hoặc `#1E40AF`) dành cho các đường phân cách hoặc tiêu đề lớn nếu muốn dùng màu.
- **Màu nền bảng biểu:** Xám nhạt dịu mắt (`#F1F5F9`).
- **Màu sơ đồ khối:** Khuyên dùng các tông màu Pastel nhạt, chữ đen rõ ràng, viền nét mảnh (`1 pt`).

---

## ✅ 8. Checklist Kiểm Tra Trước Khi Nộp Bài (Dành Cho Trưởng Nhóm)

- [ ] **1. Font chữ đồng nhất:** Toàn bài chỉ dùng duy nhất font `Times New Roman` (trừ các khối code dùng `Consolas`). Không sót font `Calibri` hay `Arial`.
- [ ] **2. Căn lề:** Toàn bộ văn bản đã căn đều 2 bên (`Justify`), không bị so le mép phải.
- [ ] **3. Vị trí chú thích:** Tất cả **Hình ảnh có chú thích ở DƯỚI**; tất cả **Bảng biểu có chú thích ở TRÊN**.
- [ ] **4. Lời dẫn chiếu:** Mọi Hình và Bảng đều được nhắc đến trong đoạn văn phía trước (`Hình X.X`, `Bảng X.X`).
- [ ] **5. Đánh số trang:** Trang bìa không đánh số; bắt đầu số 1 từ Chương 1.
- [ ] **6. Mục lục tự động:** Đã bấm `Update Table` cho cả **Mục Lục Nội Dung**, **Danh Mục Hình Ảnh** và **Danh Mục Bảng Biểu**.
- [ ] **7. Kiểm tra chính tả:** Không bị lỗi gõ tiếng Việt (như telex lỗi: `ddieefu khieenr`), không dính chữ.
- [ ] **8. Xuất file PDF:** Mở file PDF kiểm tra lại lần cuối để đảm bảo các công thức toán và sơ đồ không bị nhảy trang hoặc đè chữ.
