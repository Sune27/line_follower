# ==============================================================================
# WEB_SERVER.PY – MÁY CHỦ WEB HTTP NON-BLOCKING ĐIỀU KHIỂN XE QUA ĐIỆN THOẠI
# ==============================================================================
# Đọc giao diện từ các file tách rời trong thư mục network/:
#   - network/index.html
#   - network/style.css
#   - network/app.js
# ==============================================================================

import gc
import time
import ujson
try:
    import usocket as socket
except ImportError:
    import socket


class WebControlServer:
    def __init__(self, line_sensor, motor, tracker, port=80, web_dir="network"):
        self.line_sensor = line_sensor
        self.motor = motor
        self.tracker = tracker
        self.port = port
        self.web_dir = web_dir
        self.server_sock = None

        self.html_bytes = b""
        self.css_bytes = b""
        self.js_bytes = b""
        self._load_web_assets()
        self._start_server()

    def _read_text_file(self, filename):
        path = f"{self.web_dir}/{filename}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[WebServer] Không đọc được file {path}:", e)
            return ""

    def _load_web_assets(self):
        """
        Đọc các file index.html, style.css, app.js vào bộ nhớ đệm RAM lúc khởi động
        để phản hồi cực nhanh mà không cần truy xuất Flash trong lúc xe đang chạy.
        """
        html_str = self._read_text_file("index.html")
        css_str = self._read_text_file("style.css")
        js_str = self._read_text_file("app.js")

        self.css_bytes = css_str.encode("utf-8")
        self.js_bytes = js_str.encode("utf-8")

        # Ghép sẵn CSS và JS vào HTML trong RAM để trình duyệt tải gọn trong 1 gói tin
        if css_str:
            html_str = html_str.replace(
                '<link rel="stylesheet" href="style.css">',
                f"<style>\n{css_str}\n</style>",
            )
        if js_str:
            html_str = html_str.replace(
                '<script src="app.js"></script>',
                f"<script>\n{js_str}\n</script>",
            )

        self.html_bytes = html_str.encode("utf-8")

    def _start_server(self):
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(("0.0.0.0", self.port))
            self.server_sock.listen(5)
            self.server_sock.setblocking(False)
            print(f"[WebServer] 🌐 Đã mở cổng HTTP điều khiển tại cổng {self.port}")
        except Exception as e:
            print("[WebServer] Lỗi khởi tạo socket:", e)
            self.server_sock = None

    def _parse_query(self, query_str):
        params = {}
        if not query_str:
            return params
        for pair in query_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v
        return params

    def _build_status_dict(self):
        raw = self.line_sensor.read_all_raw()
        err = self.line_sensor.calculate_error(raw)
        return {
            "run": self.tracker.is_active,
            "act": self.tracker.last_action,
            "s": raw,
            "err": err,
            "l": self.motor.current_speed_left,
            "r": self.motor.current_speed_right,
            "spd": self.tracker.base_speed,
            "kp": self.tracker.kp,
            "ki": self.tracker.ki,
            "kd": self.tracker.kd,
        }

    def _write_all(self, cl, data_bytes):
        total = len(data_bytes)
        sent = 0
        while sent < total:
            try:
                n = cl.send(data_bytes[sent : sent + 1024])
                if not n:
                    break
                sent += n
            except OSError as e:
                if e.args and e.args[0] in (11, 110):
                    time.sleep_ms(5)
                    continue
                break

    def _send_response(self, cl, body_bytes, content_type):
        hdr = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            "Cache-Control: no-store, no-cache\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")
        self._write_all(cl, hdr)
        self._write_all(cl, body_bytes)

    def _send_json(self, cl, data_dict):
        body = ujson.dumps(data_dict).encode("utf-8")
        self._send_response(cl, body, "application/json")

    def _read_request(self, cl):
        cl.settimeout(0.3)
        data = b""
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < 300:
            try:
                chunk = cl.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data or len(data) > 2048:
                    break
            except OSError:
                break
        return data

    def poll(self):
        if not self.server_sock:
            return

        for _ in range(2):
            try:
                cl, _ = self.server_sock.accept()
            except OSError:
                return

            try:
                req = self._read_request(cl)
                if not req:
                    cl.close()
                    continue

                first_line = req.decode("utf-8", "ignore").split("\r\n")[0]
                parts = first_line.split(" ")
                path_full = parts[1] if len(parts) > 1 else "/"

                if "?" in path_full:
                    path, query_str = path_full.split("?", 1)
                else:
                    path, query_str = path_full, ""

                params = self._parse_query(query_str)

                if path == "/api/start":
                    spd = params.get("spd")
                    self.tracker.start(int(spd) if spd else None)
                    print("[Web] ▶ LỆNH: BẮT ĐẦU DÒ LINE")
                    self._send_json(cl, self._build_status_dict())

                elif path == "/api/stop":
                    self.tracker.stop()
                    print("[Web] ⏹ LỆNH: DỪNG XE")
                    self._send_json(cl, self._build_status_dict())

                elif path == "/api/manual":
                    self.tracker.stop()
                    l_spd = int(params.get("l", 0))
                    r_spd = int(params.get("r", 0))
                    self.motor.set_differential(l_spd, r_spd)
                    self.tracker.last_action = f"MANUAL ({l_spd},{r_spd})"
                    self._send_json(cl, self._build_status_dict())

                elif path == "/api/pid":
                    self.tracker.set_params(
                        base_speed=params.get("spd"),
                        kp=params.get("kp"),
                        ki=params.get("ki"),
                        kd=params.get("kd"),
                    )
                    self._send_json(cl, self._build_status_dict())

                elif path == "/api/status":
                    self._send_json(cl, self._build_status_dict())

                elif path == "/style.css":
                    self._send_response(cl, self.css_bytes, "text/css; charset=utf-8")

                elif path == "/app.js":
                    self._send_response(cl, self.js_bytes, "application/javascript; charset=utf-8")

                elif path == "/favicon.ico":
                    self._write_all(cl, b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")

                else:
                    self._send_response(cl, self.html_bytes, "text/html; charset=utf-8")
                    gc.collect()

                time.sleep_ms(3)
            except Exception as e:
                print("[WebServer Error]:", e)
            finally:
                try:
                    cl.close()
                except Exception:
                    pass
