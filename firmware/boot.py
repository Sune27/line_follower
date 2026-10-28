# ==============================================================================
# BOOT.PY – TỰ ĐỘNG BẬT ĐÈN XANH & CHẠY MAIN NGAY KHI CẤP NGUỒN PIN ESP32
# ==============================================================================
from machine import Pin

# Bật sáng ngay đèn LED xanh (GPIO 2) ở mili-giây đầu tiên để báo hiệu chip đã Boot
try:
    Pin(2, Pin.OUT, value=1)
except Exception:
    pass

try:
    import main
    if hasattr(main, "run"):
        main.run()
    elif hasattr(main, "main"):
        main.main()
except KeyboardInterrupt:
    print("[Boot] Đã dừng vòng lặp.")
except Exception as e:
    print("[Boot Error]:", e)
