# ==============================================================================
# NAP_CODE_ESP32.PY – CÔNG CỤ TỰ ĐỘNG DÒ CỔNG COM VÀ NẠP CODE SIÊU TỐC VÀO ESP32
# ==============================================================================

import sys
import time
import binascii
from pathlib import Path
import serial
import serial.tools.list_ports

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_PORT = "COM3"
BAUD = 115200


def send_raw(ser, data, wait=0.1):
    ser.write(data)
    time.sleep(wait)


def enter_raw_repl(ser):
    print("-> Đang đồng bộ và dừng chương trình cũ trên ESP32...", end=" ", flush=True)
    t0 = time.time()
    while time.time() - t0 < 6:
        ser.write(b"\r\x03")
        time.sleep(0.2)
        resp = ser.read_all()
        if b">>>" in resp or b"raw REPL" in resp:
            break

    for _ in range(5):
        ser.write(b"\r\x01")
        time.sleep(0.25)
        resp = ser.read_all()
        if b"raw REPL" in resp:
            print("[OK] Đã vào chế độ Raw REPL.")
            return True
        ser.write(b"\r\x02\r\x03")
        time.sleep(0.2)
    return False


def exec_raw(ser, code_str):
    payload = code_str.encode("utf-8") + b"\x04"
    ser.write(payload)
    out = b""
    t0 = time.time()
    while time.time() - t0 < 4.0:
        if ser.in_waiting > 0:
            out += ser.read(ser.in_waiting)
            if out.count(b"\x04") >= 2:
                break
        time.sleep(0.01)
    return out


def upload_file(ser, local_path, remote_path):
    print(f"-> Đang nạp: {remote_path:<26} ...", end=" ", flush=True)
    content = Path(local_path).read_bytes()
    exec_raw(ser, f"import ubinascii\nf = open('{remote_path}', 'wb')\n")

    chunk_size = 512
    for i in range(0, len(content), chunk_size):
        chunk = content[i : i + chunk_size]
        b64_str = binascii.b2a_base64(chunk).decode("ascii").strip()
        exec_raw(ser, f"f.write(ubinascii.a2b_base64('{b64_str}'))\n")

    exec_raw(ser, "f.close()\n")
    print("XONG!")


def detect_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    available = [p.device for p in ports]
    if DEFAULT_PORT in available:
        return DEFAULT_PORT, available
    for p in ports:
        desc = (p.description or "").lower()
        if any(k in desc for k in ["ch340", "cp210", "usb", "serial", "uart"]):
            return p.device, available
    if available:
        return available[0], available
    return None, []


def main():
    target_port, _ = detect_esp32_port()
    if not target_port:
        print("[LỖI] Không tìm thấy cổng COM nào! Hãy kiểm tra cáp USB cắm vào ESP32.")
        return

    print(f"[Serial] Đang kết nối tới ESP32 tại cổng {target_port} (Baud={BAUD})...")
    try:
        ser = serial.Serial(target_port, BAUD, timeout=1)
    except Exception as e:
        print(f"[LỖI] Không thể mở cổng {target_port}: {e}")
        print("-> Hãy đóng các cửa sổ nạp code cũ đang mở để giải phóng cổng COM3!")
        return

    ser.dtr = False
    ser.rts = False
    time.sleep(1.0)

    if not enter_raw_repl(ser):
        print("\n[LỖI] Không thể vào Raw REPL trên ESP32!")
        ser.close()
        return

    # Tạo thư mục modules và network trên ESP32
    exec_raw(
        ser,
        "import os\nfor d in ('modules', 'network'):\n try:\n  os.mkdir(d)\n except:\n  pass\n",
    )

    base = Path(__file__).resolve().parent
    files_to_upload = [
        (base / "config.py", "config.py"),
        (base / "modules" / "line_sensor.py", "modules/line_sensor.py"),
        (base / "modules" / "motor_driver.py", "modules/motor_driver.py"),
        (base / "modules" / "line_tracker.py", "modules/line_tracker.py"),
        (base / "network" / "wifi_ap.py", "network/wifi_ap.py"),
        (base / "network" / "web_server.py", "network/web_server.py"),
        (base / "network" / "index.html", "network/index.html"),
        (base / "network" / "style.css", "network/style.css"),
        (base / "network" / "app.js", "network/app.js"),
        (base / "boot.py", "boot.py"),
        (base / "main.py", "main.py"),
    ]

    for local_file, remote_file in files_to_upload:
        upload_file(ser, local_file, remote_file)

    print("\n[OK] ĐÃ NẠP THÀNH CÔNG TOÀN BỘ CODE DÒ LINE VÀO ESP32!")
    print("[ESP32] Đang khởi động lại ESP32 để tự động kết nối Wi-Fi 'Sune'...\n" + "=" * 56)

    # Thoát về Normal REPL (Ctrl+B) và Soft Reset (Ctrl+D)
    send_raw(ser, b"\x02", 0.15)
    send_raw(ser, b"\x04", 0.3)

    # Đọc log khởi động và chờ ESP32 in ra địa chỉ IP của Wi-Fi 'Sune'
    start = time.time()
    while time.time() - start < 9.0:
        if ser.in_waiting > 0:
            line = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(line, end="")
            if "SẴN SÀNG!" in line:
                break
        time.sleep(0.05)

    ser.close()


if __name__ == "__main__":
    main()
