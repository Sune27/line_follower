import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_full_member3_report():
    doc = docx.Document()

    # Thiết lập lề trang A4 chuẩn UET: Trên 2cm, Dưới 2cm, Trái 3cm, Phải 2cm
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    # Helper format màu ô
    def set_cell_background(cell, fill_hex):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    # Helper padding lề ô
    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
            node = OxmlElement(m)
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    # Helper viền ô bảng
    def set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="none", right="none"):
        tcPr = cell._tc.get_or_add_tcPr()
        b_top = f'<w:top {nsdecls("w")} w:val="single" w:sz="4" w:space="0" w:color="{top}"/>' if top != "none" else f'<w:top {nsdecls("w")} w:val="none"/>'
        b_bot = f'<w:bottom {nsdecls("w")} w:val="single" w:sz="4" w:space="0" w:color="{bottom}"/>' if bottom != "none" else f'<w:bottom {nsdecls("w")} w:val="none"/>'
        b_l = f'<w:left {nsdecls("w")} w:val="single" w:sz="4" w:space="0" w:color="{left}"/>' if left != "none" else f'<w:left {nsdecls("w")} w:val="none"/>'
        b_r = f'<w:right {nsdecls("w")} w:val="single" w:sz="4" w:space="0" w:color="{right}"/>' if right != "none" else f'<w:right {nsdecls("w")} w:val="none"/>'
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>{b_top}{b_l}{b_bot}{b_r}</w:tcBorders>')
        tcPr.append(borders)

    # Helper thêm đoạn văn bản chuẩn UET
    def add_p(text, bold_prefix="", italic_prefix="", indent=True):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Cm(1.0) if indent else Cm(0)

        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(13)
            run_b.bold = True
            run_b.font.color.rgb = RGBColor(15, 23, 42)
        if italic_prefix:
            run_i = p.add_run(italic_prefix)
            run_i.font.name = 'Times New Roman'
            run_i.font.size = Pt(13)
            run_i.italic = True
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.bold = True
        run.font.color.rgb = RGBColor(15, 76, 129)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13.5)
        run.bold = True
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_caption_table(table_num, title):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.first_line_indent = Cm(0)
        run_b = p.add_run(f"Bảng {table_num}. ")
        run_b.font.name = 'Times New Roman'
        run_b.font.size = Pt(12)
        run_b.bold = True
        run_b.font.color.rgb = RGBColor(15, 76, 129)
        run_t = p.add_run(title)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(12)
        run_t.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0.8)
        
        run_bullet = p.add_run("• ")
        run_bullet.font.name = 'Times New Roman'
        run_bullet.font.size = Pt(13)
        run_bullet.bold = True
        run_bullet.font.color.rgb = RGBColor(15, 76, 129)

        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(13)
            run_b.bold = True
            run_b.font.color.rgb = RGBColor(15, 23, 42)
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_fig(image_path, fig_num, caption, width_cm=16.0):
        if os.path.exists(image_path):
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run()
            run.add_picture(image_path, width=Cm(width_cm))

            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            p_cap.paragraph_format.first_line_indent = Cm(0)
            r_cap = p_cap.add_run(f"Hình {fig_num}. {caption}")
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(11)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(30, 41, 59)

    def add_code_block(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Cm(16.0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                <w:left w:val="single" w:sz="16" w:space="0" w:color="0284C7"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(code_text.strip())
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(15, 23, 42)

    def add_formula_block(formula_text, formula_num):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c_left = tbl.cell(0, 0)
        c_right = tbl.cell(0, 1)
        c_left.width = Cm(14.5)
        c_right.width = Cm(1.5)
        for c in (c_left, c_right):
            tcPr = c._tc.get_or_add_tcPr()
            borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
            tcPr.append(borders)
        p_left = c_left.paragraphs[0]
        p_left.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_left.paragraph_format.space_before = Pt(3)
        p_left.paragraph_format.space_after = Pt(3)
        p_left.paragraph_format.first_line_indent = Cm(0)
        run_f = p_left.add_run(formula_text)
        run_f.font.name = 'Times New Roman'
        run_f.font.size = Pt(12.5)
        run_f.italic = True
        p_right = c_right.paragraphs[0]
        p_right.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_right.paragraph_format.space_before = Pt(3)
        p_right.paragraph_format.space_after = Pt(3)
        p_right.paragraph_format.first_line_indent = Cm(0)
        run_n = p_right.add_run(f"({formula_num})")
        run_n.font.name = 'Times New Roman'
        run_n.font.size = Pt(12)

    # -------------------------------------------------------------
    # BẮT ĐẦU TẠO NỘI DUNG BÁO CÁO
    # -------------------------------------------------------------
    p_banner = doc.add_paragraph()
    p_banner.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_banner.paragraph_format.first_line_indent = Cm(0)
    p_banner.paragraph_format.space_after = Pt(14)
    r_ban = p_banner.add_run("BÁO CÁO TIỂU LUẬN / ĐỒ ÁN MÔN HỌC HỆ THỐNG NHÚNG & ROBOTICS\nPHẦN 3: ĐẶC TẢ BỘ ĐIỀU KHIỂN TRUNG TÂM & LẬP TRÌNH NHÚNG PID\n(Thành viên 3: Nguyễn Ngọc Sơn phụ trách)")
    r_ban.font.name = 'Times New Roman'
    r_ban.font.size = Pt(13)
    r_ban.bold = True
    r_ban.font.color.rgb = RGBColor(15, 76, 129)

    # =============================================================
    # MỤC 2.2.1. KIẾN TRÚC TỔNG THỂ HỆ THỐNG
    # =============================================================
    add_h2("2.2.1. Kiến trúc tổng thể hệ thống xe dò line tự hành")
    add_p(
        "Hệ thống xe dò line tự hành điều khiển vi sai gồm 6 khối chức năng chính được mô hình hóa trong Hình 2.1:"
    )
    if os.path.exists("docs/images/Kien truc tong the he thong.png"):
        add_fig("docs/images/Kien truc tong the he thong.png", "2.1", "Sơ đồ khối kiến trúc tổng thể hệ thống xe dò line tự hành ESP32", width_cm=16.0)

    add_bullet("Khối cảm biến dò line (TCRT5000): ", "5 kênh hồng ngoại Active-Low (đen = 0V, trắng = 3.3V) đặt cách mặt đường 5–10mm, cung cấp dữ liệu quang học thời gian thực.")
    add_bullet("Khối xử lý trung tâm (ESP32): ", "Thực thi firmware MicroPython OOP: giải thuật nén bitmask, lọc số học, vòng lặp PID 100Hz và phát xung PWM.")
    add_bullet("Khối công suất (TB6612FNG): ", "Cầu H Dual-MOSFET nhận 4 kênh PWM 1kHz lái động cơ với dòng liên tục 1.2A, thay thế L298N nhằm tối ưu hiệu suất và giảm nhiệt.")
    add_bullet("Cơ cấu chấp hành: ", "2 động cơ DC giảm tốc TT (1:48) dẫn động vi sai 2 bánh kèm 1 bánh đa hướng Omni.")
    add_bullet("Khối nguồn: ", "Bộ 2 cell pin 18650 (7.4V–8.4V), tách nguồn động lực VM và ổn áp 5V nuôi ESP32 và cảm biến.")
    add_bullet("Khối giám sát (Web / Ngrok): ", "Máy chủ HTTP Non-blocking tích hợp đường hầm Ngrok HTTPS phục vụ giám sát và cấu hình PID qua Internet.")

    # =============================================================
    # MỤC 2.2.2. ĐẶC TẢ BỘ ĐIỀU KHIỂN TRUNG TÂM (ESP32)
    # =============================================================
    add_h2("2.2.2. Đặc tả Bộ điều khiển trung tâm (ESP32)")
    add_p(
        "Hệ thống sử dụng module ESP32 NodeMCU-32S (30 chân) kết hợp Shield mở rộng S-V-G, đảm nhiệm đồng thời hai chức năng: thực thi vòng lặp PID 100Hz và duy trì máy chủ Web giám sát qua Wi-Fi."
    )

    # Chèn ảnh linh kiện ESP32 nếu có
    if os.path.exists("linh kiện/esp32.png"):
        add_fig("linh kiện/esp32.png", "2.2", "Module vi điều khiển ESP32 NodeMCU-32S (Bản 30 chân) và sơ đồ chân thực tế", width_cm=11.0)

    # Bảng 2.1: Thông số kỹ thuật phần cứng
    add_caption_table("2.1", "Thông số kỹ thuật phần cứng vi điều khiển ESP32 NodeMCU-32S")
    tbl_esp = doc.add_table(rows=7, cols=3)
    tbl_esp.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_esp = [Cm(3.5), Cm(4.5), Cm(8.0)]
    
    headers_esp = ["Thành phần", "Thông số phần cứng", "Vai trò trong hệ thống xe dò line"]
    for c_idx, h_text in enumerate(headers_esp):
        c = tbl_esp.cell(0, c_idx)
        c.width = col_w_esp[c_idx]
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    data_esp = [
        ("Lõi xử lý (CPU)", "Tensilica Xtensa Dual-Core 32-bit LX6, xung nhịp 240 MHz", "Thực thi song song: Core 1 tính toán PID chu kỳ 10ms, Core 0 phục vụ Web Server Non-blocking"),
        ("Bộ nhớ RAM / Flash", "520 KB SRAM nội, 4 MB Flash SPI ngoài", "Lưu trữ mã nguồn MicroPython, lưu bộ nhớ đệm giao diện Web (HTML/CSS/JS) để phản hồi tức thì"),
        ("Bộ phát xung (PWM)", "16 kênh PWM phần cứng LEDC, tần số 1.000 Hz, độ phân giải 10-bit (0..1023)", "Lái 4 kênh công suất TB6612FNG; tần số 1kHz triệt tiêu tiếng rít tần số thấp của động cơ DC TT"),
        ("Chân đệm an toàn", "GPIO 14 đấu song song dự phòng cho GPIO 12", "Ngăn chặn lỗi boot loop do GPIO 12 là chân cấu hình điện áp flash lúc khởi động (Strapping Pin)"),
        ("Đèn LED trạng thái", "GPIO 2 (LED xanh dương Onboard)", "Chỉ thị trạng thái Wi-Fi: nhấp nháy khi dò Hotspot và sáng đứng cố định khi đã cấp phát IP"),
        ("Truyền thông không dây", "Wi-Fi 802.11 b/g/n (2.4 GHz), băng thông 150 Mbps", "Hoạt động ở Station Mode kết nối Hotspot 'Sune', truyền nhận JSON Telemetry và qua đường hầm Ngrok")
    ]

    for r_idx, r_data in enumerate(data_esp, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, text_val in enumerate(r_data):
            c = tbl_esp.cell(r_idx, c_idx)
            c.width = col_w_esp[c_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 90, 90)
            set_cell_borders(c, top="E2E8F0", bottom="E2E8F0", left="none", right="none")
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text_val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(15, 23, 42)

    # Đoạn dẫn nhập Bảng 2.2
    add_p(
        "Toàn bộ chân GPIO và cổng kết nối được phân bổ chi tiết trong Bảng 2.2:"
    )

    # Bảng 2.2: Bảng phân bổ chân GPIO chuẩn chỉ
    add_caption_table("2.2", "Bảng phân bổ chân GPIO và cấu hình ngoại vi của vi điều khiển ESP32")
    tbl_gpio = doc.add_table(rows=13, cols=6)
    tbl_gpio.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_gpio = [Cm(1.0), Cm(2.4), Cm(2.4), Cm(2.8), Cm(3.4), Cm(4.0)]

    headers_gpio = ["STT", "Chân ESP32", "Cọc Shield", "Hướng / Chế độ", "Ngoại vi kết nối", "Chức năng kỹ thuật & Vai trò"]
    for c_idx, h_text in enumerate(headers_gpio):
        c = tbl_gpio.cell(0, c_idx)
        c.width = col_w_gpio[c_idx]
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 90, 90, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)

    data_gpio = [
        ("1", "GPIO 21", "D21 (Cột S)", "INPUT (Pull-up)", "TCRT5000 - S1", "Mắt 1 (Ngoài Trái): Sai số -4.0, kích hoạt bơm cua gắt trái"),
        ("2", "GPIO 19", "D19 (Cột S)", "INPUT (Pull-up)", "TCRT5000 - S2", "Mắt 2 (Giữa Trái): Sai số -2.0, bẻ lái cua vừa trái"),
        ("3", "GPIO 18", "D18 (Cột S)", "INPUT (Pull-up)", "TCRT5000 - S3", "Mắt 3 (Chính Giữa): Sai số 0.0, xe chạy thẳng bám tâm line"),
        ("4", "GPIO 5",  "D5 (Cột S)",  "INPUT (Pull-up)", "TCRT5000 - S4", "Mắt 4 (Giữa Phải): Sai số +2.0, bẻ lái cua vừa phải"),
        ("5", "GPIO 17", "D17 (Cột S)", "INPUT (Pull-up)", "TCRT5000 - S5", "Mắt 5 (Ngoài Phải): Sai số +4.0, kích hoạt bơm cua gắt phải"),
        ("6", "GPIO 13", "D13 (Cột S)", "OUTPUT (PWM)", "TB6612 - AIN1", "Điều khiển Bánh Trái chiều thuận (PWM 1000Hz, 10-bit)"),
        ("7", "GPIO 14/12", "D14 / D12", "OUTPUT (PWM)", "TB6612 - AIN2", "Điều khiển Bánh Trái chiều ngược (Ánh xạ kép chống boot loop)"),
        ("8", "GPIO 27", "D27 (Cột S)", "OUTPUT (PWM)", "TB6612 - BIN1", "Điều khiển Bánh Phải chiều thuận (PWM 1000Hz, 10-bit)"),
        ("9", "GPIO 26", "D26 (Cột S)", "OUTPUT (PWM)", "TB6612 - BIN2", "Điều khiển Bánh Phải chiều ngược (PWM 1000Hz, 10-bit)"),
        ("10", "GPIO 2", "D2 Onboard", "OUTPUT (Digital)", "LED trạng thái", "Báo trạng thái kết nối mạng Wi-Fi và ngắt dừng khẩn cấp"),
        ("11", "VIN / 5V", "Khung 5V", "POWER IN", "Đế Shield (AMS1117)", "Nhận nguồn 5V ổn áp từ pin 2S cấp nuôi mạch logic vi điều khiển"),
        ("12", "GND", "Khung GND", "POWER GROUND", "Mass chung toàn xe", "Đấu chung mass giữa Pin 2S, TB6612FNG, TCRT5000 và ESP32")
    ]

    for r_idx, r_data in enumerate(data_gpio, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, text_val in enumerate(r_data):
            c = tbl_gpio.cell(r_idx, c_idx)
            c.width = col_w_gpio[c_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 70, 70)
            set_cell_borders(c, top="E2E8F0", bottom="E2E8F0", left="none", right="none")
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1, 2] else (WD_ALIGN_PARAGRAPH.LEFT if c_idx in [4, 5] else WD_ALIGN_PARAGRAPH.CENTER)
            run = p.add_run(text_val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            if c_idx == 1:
                run.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)

    # Phân tích kỹ thuật các chân đặc biệt
    add_p(
        "Thiết kế mạch tuân thủ 3 nguyên tắc kỹ thuật:",
        bold_prefix="Nguyên tắc phân bổ chân: "
    )
    add_p(
        "1. Tránh Boot Loop (Strapping Pin GPIO 12/14): GPIO 12 quyết định điện áp flash khi khởi động; hệ thống chuyển sang GPIO 14 an toàn và kéo LOW cả hai chân ngay khi boot.",
        indent=True
    )
    add_p(
        "2. Chống nhiễu ngõ vào (Active-Low Pull-up): 5 chân cảm biến (GPIO 21, 19, 18, 5, 17) bật trở kéo lên nội; vạch đen kéo chân về 0V, triệt tiêu nhiễu sụt áp nguồn.",
        indent=True
    )
    add_p(
        "3. PWM phần cứng 1.000 Hz: 4 kênh LEDC 10-bit (0..1023) ở tần số 1kHz, loại bỏ tiếng rít và dao động cơ khí của động cơ TT.",
        indent=True
    )

    # Chèn ảnh Sơ đồ đấu nối chân ESP32 với cảm biến và driver
    if os.path.exists("docs/images/So do dau noi chan esp32.png"):
        add_fig("docs/images/So do dau noi chan esp32.png", "2.3", "Sơ đồ nguyên lý đấu nối chân chi tiết vi điều khiển ESP32 với mảng cảm biến TCRT5000 và mạch công suất TB6612FNG", width_cm=16.0)

    add_p(
        "Firmware được lập trình bằng MicroPython v1.29.0, hỗ trợ mô hình hướng đối tượng (OOP) và xử lý mạng socket bất đồng bộ."
    )

    # =============================================================
    # MỤC 3.2. LẬP TRÌNH HỆ THỐNG NHÚNG
    # =============================================================
    add_h1("3.2. Lập trình hệ thống nhúng (Embedded Firmware)")

    # 3.2.1. Cấu trúc phần mềm OOP
    add_h2("3.2.1. Kiến trúc phần mềm và Thiết kế Hướng đối tượng (OOP)")
    add_p(
        "Firmware được module hóa thành 2 package hướng đối tượng độc lập:",
        bold_prefix="Kiến trúc OOP: "
    )
    add_bullet("firmware/modules/: ", "Trừu tượng hóa phần cứng và thuật toán chuyển động: LineFollowerSensor (cảm biến), MotorDriver (driver động cơ), LineTracker (bộ tính toán PID).")
    add_bullet("firmware/network/: ", "Quản lý truyền thông: WiFiStationClient (kết nối Wi-Fi Hotspot) và WebControlServer (máy chủ HTTP/REST API).")

    add_caption_table("3.1", "Tóm tắt trách nhiệm và phương thức của các lớp OOP trong hệ thống nhúng")
    tbl_oop = doc.add_table(rows=4, cols=4)
    tbl_oop.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_oop = [Cm(3.2), Cm(3.3), Cm(5.5), Cm(4.0)]
    
    headers_oop = ["Tên Lớp (Class)", "File mã nguồn", "Trách nhiệm chính (Responsibility)", "Phương thức tiêu biểu"]
    for c_idx, h_text in enumerate(headers_oop):
        c = tbl_oop.cell(0, c_idx)
        c.width = col_w_oop[c_idx]
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 90, 90, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    data_oop = [
        ("LineFollowerSensor", "line_sensor.py", "Quản lý 5 chân cảm biến hồng ngoại, xử lý đảo bit active_low, ép nhị phân bitmask và tính sai số độ lệch vạch e.", "read_all_raw()\ncalculate_error()\nread_status()"),
        ("MotorDriver", "motor_driver.py", "Lái 4 kênh PWM mạch cầu H TB6612FNG, điều khiển vi sai 2 bánh, thực thi thuật toán Xung mồi Kickstart chống ma sát nghỉ.", "set_differential(l, r)\nstop()\n_apply_kickstart()"),
        ("LineTracker", "line_tracker.py", "Bộ não tính toán PID mượt, bộ lọc thông thấp, thuật toán Bơm gia tốc cua gắt (Corner Boost) và cứu vạch khi lọt khe.", "update(sensors, now)\nstart(speed)\nstop()\nset_params()")
    ]

    for r_idx, r_data in enumerate(data_oop, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(r_data):
            c = tbl_oop.cell(r_idx, c_idx)
            c.width = col_w_oop[c_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 80, 80)
            set_cell_borders(c, top="E2E8F0", bottom="E2E8F0", left="none", right="none")
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            if c_idx == 0:
                run.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)

    # Chèn các hình lưu đồ giải thuật cho từng Class
    add_p(
        "Lưu đồ giải thuật chi tiết của từng lớp trong kiến trúc OOP được mô hình hóa trong các Hình từ 3.1 đến 3.5:"
    )

    if os.path.exists("docs/images/LineFollowerSensor.png"):
        add_fig("docs/images/LineFollowerSensor.png", "3.1", "Lưu đồ thuật toán xử lý dữ liệu 5 mắt cảm biến và tính sai số vị trí (LineFollowerSensor)", width_cm=16.0)

    if os.path.exists("docs/images/MotorDriver.png"):
        add_fig("docs/images/MotorDriver.png", "3.2", "Lưu đồ thuật toán phát xung PWM và cơ chế Xung mồi Kickstart chống ma sát nghỉ (MotorDriver)", width_cm=16.0)

    if os.path.exists("docs/images/LineTracker.png"):
        add_fig("docs/images/LineTracker.png", "3.3", "Lưu đồ thuật toán lọc số học, giải thuật PID mượt và Bơm gia tốc cua gắt (LineTracker)", width_cm=16.0)

    if os.path.exists("docs/images/WebControlServer.png"):
        add_fig("docs/images/WebControlServer.png", "3.4", "Lưu đồ thuật toán máy chủ Web Server và tiếp nhận REST API bất đồng bộ (WebControlServer)", width_cm=16.0)

    if os.path.exists("docs/images/WiFiStationClient.png"):
        add_fig("docs/images/WiFiStationClient.png", "3.5", "Lưu đồ thuật toán kết nối và duy trì mạng Wi-Fi Hotspot Station Mode (WiFiStationClient)", width_cm=16.0)

    # 3.2.2. Error Mapping
    add_h2("3.2.2. Bảng quy đổi sai số vị trí mảng 5 mắt cảm biến (Error Mapping)")
    add_p(
        "Mảng 5 mắt TCRT5000 xuất tín hiệu Active-Low (đen = 0, trắng = 1). Lớp LineFollowerSensor đảo bit và đóng gói thành bitmask 5-bit theo Công thức (3.1):"
    )
    add_formula_block("bitmask = (S_1 << 4) | (S_2 << 3) | (S_3 << 2) | (S_4 << 1) | S_5", "3.1")
    add_p(
        "Từ bitmask thu được, hệ thống tra bảng xác định sai số vị trí e thuộc [-4.0, +4.0] (e = 0.0 chuẩn tâm, e < 0 lệch trái, e > 0 lệch phải) như trình bày trong Bảng 3.2:"
    )

    add_caption_table("3.2", "Bảng tra cứu sai số vị trí độ lệch vạch và hành vi điều khiển vi sai")
    tbl_err = doc.add_table(rows=12, cols=4)
    tbl_err.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_err = [Cm(3.0), Cm(2.2), Cm(5.8), Cm(5.0)]

    headers_err = ["Bitmask (S1..S5)", "Sai số e", "Vị trí thực tế của vạch đen", "Hành động điều khiển vi sai"]
    for c_idx, h_text in enumerate(headers_err):
        c = tbl_err.cell(0, c_idx)
        c.width = col_w_err[c_idx]
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 90, 90, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    data_err = [
        ("0b10000", "-4.0", "Lệch tối đa sang trái (chỉ S1 thấy vạch)", "Bơm cua gắt Trái (Phải: +90%, Trái: -65%)"),
        ("0b11000", "-3.2", "Lệch nhiều sang trái (S1 và S2 cùng thấy)", "Bơm cua mạnh Trái (Phải: +85%, Trái: -40%)"),
        ("0b01000", "-2.0", "Lệch vừa sang trái (chỉ S2 thấy vạch)", "Bẻ lái PID vừa Trái (Điều chỉnh vi sai)"),
        ("0b01100", "-1.0", "Lệch nhẹ sang trái (S2 và S3 cùng thấy)", "Bẻ lái PID nhẹ Trái"),
        ("0b00100", " 0.0", "Chính giữa vạch line (chỉ S3 thấy vạch)", "Đi thẳng cân bằng (Trái = Phải = Base)"),
        ("0b00110", "+1.0", "Lệch nhẹ sang phải (S3 và S4 cùng thấy)", "Bẻ lái PID nhẹ Phải"),
        ("0b00010", "+2.0", "Lệch vừa sang phải (chỉ S4 thấy vạch)", "Bẻ lái PID vừa Phải (Điều chỉnh vi sai)"),
        ("0b00011", "+3.2", "Lệch nhiều sang phải (S4 và S5 cùng thấy)", "Bơm cua mạnh Phải (Trái: +85%, Phải: -40%)"),
        ("0b00001", "+4.0", "Lệch tối đa sang phải (chỉ S5 thấy vạch)", "Bơm cua gắt Phải (Trái: +90%, Phải: -65%)"),
        ("0b00000", "e_last", "Mất vạch hoàn toàn / Lọt khe giữa 2 mắt", "Cứu vạch: Giữ nguyên hướng bẻ lái gần nhất"),
        ("0b11111", "0.0", "Vạch ngang dừng xe / Vạch đích (Finish)", "Hãm dừng xe hoặc tăng tốc vượt qua vạch đích")
    ]

    for r_idx, r_data in enumerate(data_err, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(r_data):
            c = tbl_err.cell(r_idx, c_idx)
            c.width = col_w_err[c_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 70, 70)
            set_cell_borders(c, top="E2E8F0", bottom="E2E8F0", left="none", right="none")
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Consolas' if c_idx == 0 else 'Times New Roman'
            run.font.size = Pt(10)
            if c_idx == 1:
                run.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)

    # 3.2.3. Kickstart Anti-Stiction
    add_h2("3.2.3. Cơ chế Xung mồi thắng ma sát nghỉ (Kickstart Anti-Stiction)")
    add_p(
        "Do ma sát nghỉ của hộp số nhựa và lốp xe, động cơ DC thường bị kẹt ở dải PWM thấp (vùng chết Deadband). Lớp MotorDriver giải quyết triệt để bằng cơ chế Xung mồi Kickstart: khi bánh xe bắt đầu quay từ vận tốc 0 hoặc đảo chiều, hệ thống xuất xung 98% duty cycle trong 70ms để phá vỡ ma sát tĩnh, sau đó tự động hạ mượt về tốc độ mục tiêu của bộ điều khiển PID."
    )
    add_code_block('''def _apply_kickstart(self, target_pct, prev_dir, kick_until, now_ms):
    if target_pct == 0:
        return 0, 0, 0
    cur_dir = 1 if target_pct > 0 else -1
    # Bánh xe vừa khởi hành từ trạng thái đứng yên hoặc đảo chiều quay
    if prev_dir != cur_dir:
        kick_until = now_ms + self.kickstart_ms  # Kích hoạt cửa sổ 70ms

    if time.ticks_diff(kick_until, now_ms) > 0:
        boosted = max(abs(target_pct), self.kickstart_speed)  # Phóng xung 98%
        actual_pct = boosted if cur_dir > 0 else -boosted
    else:
        actual_pct = target_pct  # Hết 70ms: hạ mượt về tốc độ mục tiêu
    return actual_pct, cur_dir, kick_until''')

    # 3.2.4. PID & Corner Boost
    add_h2("3.2.4. Thuật toán điều khiển vi sai PID rời rạc & Bơm gia tốc cua (Corner Boost)")
    add_p(
        "Hệ thống làm mịn sai số bằng bộ lọc thông thấp bậc nhất (alpha = 0.85) nhằm triệt tiêu nhiễu ánh sáng và rung lắc cơ khí:"
    )
    add_formula_block("e_smooth(t) = alpha * e_raw(t) + (1 - alpha) * e_smooth(t - dt)", "3.2")
    add_p(
        "Tín hiệu điều khiển bù vi sai u(t) được tính toán theo thuật toán PID rời rạc:"
    )
    add_formula_block("u(t) = P(t) + I(t) + D(t) = Kp * e(t) + Ki * sum(e*dt) + Kd * (e(t) - e(t-dt))/dt", "3.3")
    add_p(
        "1. Khâu Tỉ lệ (Kp = 7.5): Tạo phản ứng bẻ lái tức thời tỷ lệ với sai số lệch vạch.",
        indent=True
    )
    add_p(
        "2. Khâu Tích phân (Ki = 0.04): Triệt tiêu sai số xác lập; tích hợp Zero-Crossing Reset (tự động xóa tích phân về 0 khi |e| < 0.1 hoặc đổi dấu) để chống bão hòa tích phân (Anti-windup).",
        indent=True
    )
    add_p(
        "3. Khâu Đạo hàm (Kd = 4.5): Đóng vai trò bộ giảm chấn động học, hãm quán tính và chống văng đuôi xe khi bẻ lái.",
        indent=True
    )
    add_p(
        "Khi vào khúc cua gắt (|e| >= 3.2), lớp LineTracker tự động kích hoạt chế độ Bơm cua (Corner Boost): ép bánh ngoài tăng tốc lên 90% công suất, bánh trong quay lùi -65%, tạo ngẫu lực bẻ gập hướng cực nhanh mà không văng khỏi line.",
        bold_prefix="Bơm gia tốc cua gắt (Corner Boost): "
    )

    # 3.2.5. Chương trình thời gian thực
    add_h2("3.2.5. Chương trình điều khiển thời gian thực và Lưu đồ thuật toán (main.py)")
    add_p(
        "Vòng lặp chính trong main.py hoạt động ở tần số cố định 100Hz (chu kỳ 10ms) sử dụng hàm time.ticks_diff() để chống trôi thời gian, phân chia độ ưu tiên như Bảng 3.3 và Lưu đồ Hình 3.6:"
    )

    add_caption_table("3.3", "Phân bổ độ ưu tiên và chu kỳ thực thi tác vụ trong vòng lặp chính")
    tbl_task = doc.add_table(rows=3, cols=3)
    tbl_task.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_task = [Cm(4.5), Cm(4.0), Cm(7.5)]

    headers_task = ["Tác vụ (Task)", "Chu kỳ thực thi", "Nhiệm vụ chi tiết trong vòng lặp"]
    for c_idx, h_text in enumerate(headers_task):
        c = tbl_task.cell(0, c_idx)
        c.width = col_w_task[c_idx]
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 90, 90, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    data_task = [
        ("ƯU TIÊN 1: Điều khiển PID", "Cố định 10ms (100 Hz)\n(Ticks diff check)", "Đọc 5 mắt cảm biến -> Tính sai số e -> Lọc số học -> Tính P, I, D -> Phân vùng bẻ lái -> Xuất PWM 4 kênh qua MotorDriver."),
        ("ƯU TIÊN 2: Mạng Web Server", "Bất đồng bộ (Non-blocking)\n(Mỗi vòng lặp)", "Lắng nghe socket accept() -> Nhận HTTP Request -> Giải mã lệnh /api/start, /api/stop, /api/pid -> Đóng gói JSON trạng thái 5 mắt gửi lên Web.")
    ]

    for r_idx, r_data in enumerate(data_task, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(r_data):
            c = tbl_task.cell(r_idx, c_idx)
            c.width = col_w_task[c_idx]
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 80, 80)
            set_cell_borders(c, top="E2E8F0", bottom="E2E8F0", left="none", right="none")
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            if c_idx == 0:
                run.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)

    # Chèn ảnh Lưu đồ thuật toán điều phối toàn cục
    flowchart_img = "docs/images/[3.2.5] Lưu đồ thuật toán.drawio.png"
    if os.path.exists(flowchart_img):
        add_fig(flowchart_img, "3.6", "Lưu đồ thuật toán điều phối toàn cục vòng lặp điều khiển thời gian thực 100Hz (main.py)", width_cm=16.0)

    # Lưu đồ thuật toán dạng Text Flowchart
    add_p(
        "Lưu đồ thuật toán điều phối toàn cục của hệ thống nhúng trong main.py được trực quan hóa tuần tự như sau:",
        bold_prefix="Lưu đồ thuật toán vòng lặp chính: "
    )
    add_code_block('''[BẮT ĐẦU NGUỒN PIN (7.4V - 8.4V)]
         │
         ▼
[Kéo 4 chân Motor về LOW (0V) để giữ xe đứng im]
         │
         ▼
[Khởi tạo WiFiStationClient -> Quét & Kết nối Hotspot 'Sune' (STA_IF)]
         │
         ├──> Nếu kết nối thành công: LED D2 sáng đứng, in địa chỉ IP ra Terminal
         │
         ▼
[Khởi tạo MotorDriver, LineFollowerSensor, LineTracker, WebControlServer]
         │
         ▼
[VÒNG LẶP CHÍNH THỜI GIAN THỰC (while True)]
         │
         ├──> [Kiểm tra thời gian: Đủ chu kỳ 10ms (100Hz) & Xe đang Bật?]
         │         │
         │         ├── [CÓ]: 1. Đọc thô 5 mắt cảm biến TCRT5000 (read_all_raw)
         │         │         2. Nén thành Bitmask 5-bit (0b00000 .. 0b11111)
         │         │         3. Quy đổi sai số vị trí e thuộc [-4.0, +4.0]
         │         │         4. Lọc thông thấp: e_smooth = 0.85*e + 0.15*e_prev
         │         │         5. Tính toán các khâu P, I, D (kèm Zero-Crossing reset)
         │         │         6. Phân vùng bẻ lái (|e| <= 1.2 -> Tâm; 1.2..2.6 -> Vừa; > 2.6 -> Gắt)
         │         │         7. Áp dụng Xung mồi Kickstart (98% trong 70ms) nếu đổi chiều
         │         │         8. Xuất PWM 4 kênh điều khiển 2 bánh xe qua TB6612FNG
         │         │
         │         └── [KHÔNG]: Bỏ qua, duy trì xe ở chế độ chờ
         │
         ├──> [Lắng nghe kết nối mạng Web Server (Non-blocking poll)]
         │         │
         │         └── Có yêu cầu từ Client? 
         │                   ├── /api/start  -> Kích hoạt cờ is_active = True
         │                   ├── /api/stop   -> Dừng xe, tắt PWM
         │                   ├── /api/pid    -> Cập nhật nóng Kp, Ki, Kd
         │                   └── /api/status -> Đóng gói JSON gửi dữ liệu 5 mắt lên Web
         │
         └──> [Nghỉ 1 mili-giây: time.sleep_ms(1)] -> Lặp lại chu trình''')

    output_path = "docs/Bao_Cao_Phan_3_Thanh_Vien_3_Firmware_PID.docx"
    doc.save(output_path)
    print(f"Hoàn thành tạo mới tài liệu: {output_path}")

if __name__ == "__main__":
    create_full_member3_report()
