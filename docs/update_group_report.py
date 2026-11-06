# -*- coding: utf-8 -*-
"""
Script cập nhật các sơ đồ khối và hình ảnh kiến trúc vào
Báo Cáo Nhóm: docs/Bao_Cao_Xe_Do_Line_ESP32_Nhom.docx
(Văn phong cô đọng, súc tích, chuẩn học thuật)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def update_group_report():
    doc_path = "docs/Bao_Cao_Xe_Do_Line_ESP32_Nhom.docx"
    if not os.path.exists(doc_path):
        print(f"Không tìm thấy file: {doc_path}")
        return

    doc = docx.Document(doc_path)

    # 1. Chèn ảnh và mô tả Kiến trúc tổng thể 2.2.1
    img_arch = "docs/images/Kien truc tong the he thong.png"
    p_arch = None
    for p in doc.paragraphs:
        if "Gợi ý: Đưa vào sơ đồ kiến trúc tổng thể" in p.text:
            p_arch = p
            break

    if p_arch and os.path.exists(img_arch):
        p_desc = p_arch.insert_paragraph_before(
            "Hệ thống xe dò line tự hành điều khiển vi sai gồm 6 khối chức năng chính được mô hình hóa trong Hình 2.1:"
        )
        p_desc.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_desc.paragraph_format.line_spacing = 1.3
        p_desc.paragraph_format.first_line_indent = Cm(1.0)
        p_desc.paragraph_format.space_after = Pt(4)
        for r in p_desc.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(13)

        p_img = p_arch.insert_paragraph_before()
        p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        p_img.paragraph_format.first_line_indent = Cm(0)
        r_img = p_img.add_run()
        r_img.add_picture(img_arch, width=Cm(16.0))

        p_cap = p_arch.insert_paragraph_before()
        p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        p_cap.paragraph_format.first_line_indent = Cm(0)
        r_cap = p_cap.add_run("Hình 2.1. Sơ đồ khối kiến trúc tổng thể hệ thống xe dò line tự hành ESP32")
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(11)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(30, 41, 59)

        bullets = [
            ("Khối cảm biến dò line (TCRT5000): ", "5 kênh hồng ngoại Active-Low (đen = 0V, trắng = 3.3V) đặt cách mặt đường 5–10mm, cung cấp dữ liệu quang học thời gian thực."),
            ("Khối xử lý trung tâm (ESP32): ", "Thực thi firmware MicroPython OOP: giải thuật nén bitmask, lọc số học, vòng lặp PID 100Hz và phát xung PWM."),
            ("Khối công suất (TB6612FNG): ", "Cầu H Dual-MOSFET nhận 4 kênh PWM 1kHz lái động cơ với dòng liên tục 1.2A, thay thế L298N nhằm tối ưu hiệu suất và giảm nhiệt."),
            ("Cơ cấu chấp hành: ", "2 động cơ DC giảm tốc TT (1:48) dẫn động vi sai 2 bánh kèm 1 bánh đa hướng Omni."),
            ("Khối nguồn: ", "Bộ 2 cell pin 18650 (7.4V–8.4V), tách nguồn động lực VM và ổn áp 5V nuôi ESP32 và cảm biến."),
            ("Khối giám sát (Web / Ngrok): ", "Máy chủ HTTP Non-blocking tích hợp đường hầm Ngrok HTTPS phục vụ giám sát và cấu hình PID qua Internet.")
        ]
        for bold_t, norm_t in bullets:
            p_b = p_arch.insert_paragraph_before()
            p_b.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_b.paragraph_format.line_spacing = 1.3
            p_b.paragraph_format.first_line_indent = Cm(0)
            p_b.paragraph_format.left_indent = Cm(0.8)
            p_b.paragraph_format.space_after = Pt(3)
            
            r_bullet = p_b.add_run("• ")
            r_bullet.bold = True
            r_bullet.font.name = "Times New Roman"
            r_bullet.font.size = Pt(13)
            r_bullet.font.color.rgb = RGBColor(15, 76, 129)

            r_bt = p_b.add_run(bold_t)
            r_bt.bold = True
            r_bt.font.name = "Times New Roman"
            r_bt.font.size = Pt(13)

            r_nt = p_b.add_run(norm_t)
            r_nt.font.name = "Times New Roman"
            r_nt.font.size = Pt(13)

        p_arch.text = ""

    # 2. Chèn Sơ đồ đấu nối chân ESP32 vào Mục 3.1.0
    img_pinout = "docs/images/So do dau noi chan esp32.png"
    p_hw = None
    for p in doc.paragraphs:
        if "Hình [số]. [Sơ đồ đấu nối phần cứng]" in p.text:
            p_hw = p
            break

    if p_hw and os.path.exists(img_pinout):
        p_img_hw = p_hw.insert_paragraph_before()
        p_img_hw.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img_hw.paragraph_format.space_before = Pt(8)
        p_img_hw.paragraph_format.space_after = Pt(3)
        p_img_hw.paragraph_format.first_line_indent = Cm(0)
        r_img_hw = p_img_hw.add_run()
        r_img_hw.add_picture(img_pinout, width=Cm(16.0))

        p_hw.text = "Hình 3.1. Sơ đồ nguyên lý đấu nối chân chi tiết vi điều khiển ESP32 với mảng cảm biến TCRT5000 và mạch công suất TB6612FNG"
        p_hw.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hw.paragraph_format.space_before = Pt(2)
        p_hw.paragraph_format.space_after = Pt(8)
        p_hw.paragraph_format.first_line_indent = Cm(0)
        for r in p_hw.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.font.italic = True
            r.font.color.rgb = RGBColor(30, 41, 59)

    # 3. Chèn Lưu đồ thuật toán vào Mục 3.2
    img_flow = "docs/images/[3.2.5] Lưu đồ thuật toán.drawio.png"
    p_flow = None
    for p in doc.paragraphs:
        if "Hình [số]. [Lưu đồ thuật toán]" in p.text:
            p_flow = p
            break

    if p_flow and os.path.exists(img_flow):
        p_img_fl = p_flow.insert_paragraph_before()
        p_img_fl.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img_fl.paragraph_format.space_before = Pt(8)
        p_img_fl.paragraph_format.space_after = Pt(3)
        p_img_fl.paragraph_format.first_line_indent = Cm(0)
        r_img_fl = p_img_fl.add_run()
        r_img_fl.add_picture(img_flow, width=Cm(16.0))

        p_flow.text = "Hình 3.2. Lưu đồ thuật toán điều phối toàn cục vòng lặp điều khiển thời gian thực 100Hz (main.py)"
        p_flow.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_flow.paragraph_format.space_before = Pt(2)
        p_flow.paragraph_format.space_after = Pt(8)
        p_flow.paragraph_format.first_line_indent = Cm(0)
        for r in p_flow.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.font.italic = True
            r.font.color.rgb = RGBColor(30, 41, 59)

    doc.save(doc_path)
    print(f"Cập nhật thành công Báo cáo nhóm: {doc_path}")

if __name__ == "__main__":
    update_group_report()
