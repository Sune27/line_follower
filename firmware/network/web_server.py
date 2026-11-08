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
    def __init__(self, line_sensor, motor, tracker, arm=None, port=80, web_dir="network"):
        self.line_sensor = line_sensor
        self.motor = motor
        self.tracker = tracker
        self.arm = arm
        self.port = port
        self.web_dir = web_dir
        self.server_sock = None
        self._buf = bytearray(1024)
        self._start_server()

    def _send_file(self, cl, filename, content_type, cache_sec=86400):
        """Gửi file trực tiếp từ bộ nhớ Flash theo từng gói nhỏ để tiết kiệm RAM tối đa."""
        path = f"{self.web_dir}/{filename}"
        try:
            import os
            size = os.stat(path)[6]
            cache_hdr = "Cache-Control: no-store, no-cache, must-revalidate\r\nPragma: no-cache\r\nExpires: 0\r\n"
            hdr = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {size}\r\n"
                f"{cache_hdr}"
                "Access-Control-Allow-Origin: *\r\n"
                "Connection: close\r\n\r\n"
            ).encode("utf-8")
            self._write_all(cl, hdr)

            with open(path, "rb") as f:
                while True:
                    n = f.readinto(self._buf)
                    if not n:
                        break
                    self._write_all(cl, memoryview(self._buf)[:n])
        except Exception as e:
            print(f"[WebServer] Lỗi gửi file {path}:", e)
            self._write_all(cl, b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")

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
        res = {
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
        if self.arm:
            res["arm"] = self.arm.get_angles()
        return res

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

                elif path == "/api/arm":
                    if self.arm:
                        drive_dir = params.get("dir")
                        if drive_dir is not None:
                            joint = params.get("j", "b")
                            self.arm.drive_joint(joint, int(drive_dir))
                        else:
                            preset = params.get("p")
                            if preset == "home":
                                self.arm.pose_home()
                            elif preset in ("rest", "park"):
                                self.arm.pose_park()
                            elif preset == "grab":
                                self.arm.pose_grab()
                            elif preset == "grip":
                                self.arm.grip(True)
                            elif preset == "open":
                                self.arm.grip(False)
                            elif preset == "stop_all":
                                self.arm.stop_all()
                            else:
                                b = params.get("b")
                                s = params.get("s")
                                e = params.get("e")
                                g = params.get("g")
                                self.arm.set_angles(
                                    base=int(b) if b is not None else None,
                                    shoulder=int(s) if s is not None else None,
                                    elbow=int(e) if e is not None else None,
                                    gripper=int(g) if g is not None else None,
                                )
                    self._send_json(cl, self._build_status_dict())

                elif path == "/style.css":
                    self._send_file(cl, "style.css", "text/css; charset=utf-8", cache_sec=0)

                elif path == "/app.js":
                    self._send_file(cl, "app.js", "application/javascript; charset=utf-8", cache_sec=0)

                elif path == "/favicon.ico":
                    self._write_all(cl, b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")

                else:
                    self._send_file(cl, "index.html", "text/html; charset=utf-8", cache_sec=0)

                time.sleep_ms(3)
            except Exception as e:
                print("[WebServer Error]:", e)
            finally:
                try:
                    cl.close()
                except Exception:
                    pass
