# ==============================================================================
# WEB_SERVER.PY – MÁY CHỦ WEB HTTP NON-BLOCKING ĐIỀU KHIỂN XE QUA ĐIỆN THOẠI
# ==============================================================================

import gc
import time
import ujson
try:
    import usocket as socket
except ImportError:
    import socket


MOBILE_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Điều Khiển Xe Dò Line ESP32</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;user-select:none;-webkit-tap-highlight-color:transparent}
body{background:#0f172a;color:#f8fafc;padding:10px;max-width:460px;margin:0 auto}
.card{background:#1e293b;border-radius:14px;padding:12px;margin-bottom:10px;border:1px solid #334155}
h1{font-size:17px;text-align:center;color:#38bdf8;margin-bottom:2px}
.sub{font-size:11px;text-align:center;color:#94a3b8;margin-bottom:8px}
.status-bar{display:flex;justify-content:space-between;align-items:center;background:#0f172a;padding:8px 12px;border-radius:10px;font-size:13px;margin-bottom:10px}
.badge{padding:3px 10px;border-radius:99px;font-weight:700;font-size:11px}
.b-run{background:#16a34a;color:#fff}
.b-stop{background:#475569;color:#e2e8f0}
.btn-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px}
.mode-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}
button{border:none;border-radius:12px;padding:14px 8px;font-size:15px;font-weight:700;cursor:pointer;transition:transform .08s,opacity .08s}
button:active{transform:scale(0.95);opacity:0.85}
.btn-start{background:#22c55e;color:#052e16;box-shadow:0 4px 12px rgba(34,197,94,.35)}
.btn-stop{background:#ef4444;color:#fff;box-shadow:0 4px 12px rgba(239,68,68,.35)}
.btn-mode{background:#334155;color:#cbd5e1;padding:10px 6px;font-size:12px;border:2px solid transparent}
.btn-mode.active{background:#0369a1;color:#fff;border-color:#38bdf8}
.sec-title{font-size:12px;font-weight:700;color:#94a3b8;margin-bottom:8px;text-transform:uppercase;display:flex;justify-content:space-between;align-items:center}
.sensors{display:flex;justify-content:space-around;padding:6px 0}
.eye{display:flex;flex-direction:column;align-items:center;gap:4px}
.dot{width:36px;height:36px;border-radius:50%;background:#334155;border:3px solid #64748b;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.dot.black{background:#f59e0b;border-color:#fde047;color:#0f172a;box-shadow:0 0 10px #f59e0b}
.eye span{font-size:10px;color:#94a3b8}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;text-align:center;margin-top:6px}
.m-box{background:#0f172a;padding:6px;border-radius:8px}
.m-lbl{font-size:10px;color:#94a3b8}
.m-val{font-size:15px;font-weight:700;color:#38bdf8;margin-top:2px}
.dpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:250px;margin:0 auto}
.dpad button{background:#334155;color:#f8fafc;padding:13px 0;font-size:13px}
.dpad .d-stop{background:#dc2626}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.inp-grp{display:flex;flex-direction:column;gap:2px}
.inp-grp label{font-size:11px;color:#cbd5e1}
.inp-grp input{background:#0f172a;border:1px solid #475569;color:#fff;padding:7px;border-radius:8px;font-size:14px;text-align:center}
.btn-save{width:100%;background:#0284c7;color:#fff;padding:11px;font-size:14px}
</style>
<script>
let busy=false;
function updateUI(d){
  if(!d)return;
  document.getElementById('actTxt').innerText=d.act||'STANDBY';
  const b=document.getElementById('modeBadge');
  if(d.run){b.className='badge b-run';b.innerText='ĐANG DÒ LINE';}
  else{b.className='badge b-stop';b.innerText='ĐANG DỪNG';}
  if(d.mode){
    document.getElementById('mStep').className=d.mode==='STEP'?'btn-mode active':'btn-mode';
    document.getElementById('mSmooth').className=d.mode==='SMOOTH'?'btn-mode active':'btn-mode';
  }
  if(d.s){
    for(let i=0;i<5;i++){
      const el=document.getElementById('s'+i);
      if(el){el.innerText=d.s[i];el.className=d.s[i]?'dot black':'dot';}
    }
  }
  document.getElementById('errVal').innerText=d.err!==undefined?d.err:0;
  document.getElementById('spdL').innerText=(d.l||0)+'%';
  document.getElementById('spdR').innerText=(d.r||0)+'%';
  const ae=document.activeElement;
  if(d.spd!==undefined&&ae!==document.getElementById('inSpd'))document.getElementById('inSpd').value=d.spd;
  if(d.kp!==undefined&&ae!==document.getElementById('inKp'))document.getElementById('inKp').value=d.kp;
  if(d.ki!==undefined&&ae!==document.getElementById('inKi'))document.getElementById('inKi').value=d.ki;
  if(d.kd!==undefined&&ae!==document.getElementById('inKd'))document.getElementById('inKd').value=d.kd;
}
function sendApi(path){
  document.getElementById('actTxt').innerText='ĐANG GỬI...';
  const sep=path.indexOf('?')>-1?'&':'?';
  fetch(path+sep+'t='+Date.now()).then(r=>r.json()).then(d=>updateUI(d)).catch(e=>{
    document.getElementById('actTxt').innerText='THỬ LẠI...';
  });
}
function setMode(m){sendApi('/api/mode?m='+m);}
function manual(l,r){sendApi('/api/manual?l='+l+'&r='+r);}
function savePid(){
  const spd=document.getElementById('inSpd').value;
  const kp=document.getElementById('inKp').value;
  const ki=document.getElementById('inKi').value;
  const kd=document.getElementById('inKd').value;
  sendApi('/api/pid?spd='+spd+'&kp='+kp+'&ki='+ki+'&kd='+kd);
}
window.addEventListener('DOMContentLoaded',()=>{
  sendApi('/api/status');
  setInterval(()=>{
    const chk=document.getElementById('liveChk');
    if(!chk||!chk.checked||busy)return;
    busy=true;
    fetch('/api/status?t='+Date.now()).then(r=>r.json()).then(d=>{updateUI(d);busy=false;}).catch(e=>{busy=false;});
  },500);
});
</script>
</head>
<body>
<div class="card">
  <h1>🤖 XE DÒ LINE ESP32</h1>
  <div class="sub">TCRT5000 (5 Mắt) + TB6612FNG • 192.168.4.1</div>
  <div class="status-bar">
    <span>Trạng thái: <b id="actTxt">SẴN SÀNG</b></span>
    <span id="modeBadge" class="badge b-stop">ĐANG DỪNG</span>
  </div>
  <div class="btn-row">
    <button type="button" class="btn-start" onclick="sendApi('/api/start')">▶ BẮT ĐẦU DÒ</button>
    <button type="button" class="btn-stop" onclick="sendApi('/api/stop')">⏹ DỪNG XE</button>
  </div>
  <div class="sec-title" style="margin-top:6px;margin-bottom:4px"><span>Kiểu Chạy Dò Line:</span></div>
  <div class="mode-row">
    <button type="button" id="mStep" class="btn-mode active" onclick="setMode('STEP')">🎯 Nhấp Phanh & Lùi Chỉnh Đầu</button>
    <button type="button" id="mSmooth" class="btn-mode" onclick="setMode('SMOOTH')">🌊 Chạy PID Mượt Liên Tục</button>
  </div>
</div>

<div class="card">
  <div class="sec-title">
    <span>5 Mắt Cảm Biến TCRT5000</span>
    <label style="font-size:11px;text-transform:none"><input type="checkbox" id="liveChk" checked> Tự cập nhật</label>
  </div>
  <div class="sensors">
    <div class="eye"><div id="s0" class="dot">0</div><span>S1 (D21)</span></div>
    <div class="eye"><div id="s1" class="dot">0</div><span>S2 (D19)</span></div>
    <div class="eye"><div id="s2" class="dot">0</div><span>S3 (D18)</span></div>
    <div class="eye"><div id="s3" class="dot">0</div><span>S4 (D5)</span></div>
    <div class="eye"><div id="s4" class="dot">0</div><span>S5 (D17)</span></div>
  </div>
  <div class="metrics">
    <div class="m-box"><div class="m-lbl">Sai số (Error)</div><div id="errVal" class="m-val">0</div></div>
    <div class="m-box"><div class="m-lbl">Bánh Trái</div><div id="spdL" class="m-val">0%</div></div>
    <div class="m-box"><div class="m-lbl">Bánh Phải</div><div id="spdR" class="m-val">0%</div></div>
  </div>
</div>

<div class="card">
  <div class="sec-title"><span>Lái Thử Động Cơ (Manual Test)</span></div>
  <div class="dpad">
    <div></div>
    <button type="button" onclick="manual(65,65)">▲ TIẾN</button>
    <div></div>
    <button type="button" onclick="manual(-50,50)">◀ TRÁI</button>
    <button type="button" class="d-stop" onclick="sendApi('/api/stop')">■ DỪNG</button>
    <button type="button" onclick="manual(50,-50)">PHẢI ▶</button>
    <div></div>
    <button type="button" onclick="manual(-60,-60)">▼ LÙI</button>
    <div></div>
  </div>
</div>

<div class="card">
  <div class="sec-title"><span>Tinh Chỉnh Tốc Độ & PID</span></div>
  <div class="form-grid">
    <div class="inp-grp"><label>Tốc độ cơ sở (%)</label><input id="inSpd" type="number" value="62"></div>
    <div class="inp-grp"><label>Hệ số Kp</label><input id="inKp" type="number" step="0.1" value="6.0"></div>
    <div class="inp-grp"><label>Hệ số Ki</label><input id="inKi" type="number" step="0.01" value="0.04"></div>
    <div class="inp-grp"><label>Hệ số Kd</label><input id="inKd" type="number" step="0.1" value="4.2"></div>
  </div>
  <button type="button" class="btn-save" onclick="savePid()">💾 CẬP NHẬT THÔNG SỐ</button>
</div>
</body>
</html>
"""

HTML_BYTES = MOBILE_HTML.encode("utf-8")


class WebControlServer:
    def __init__(self, line_sensor, motor, tracker, port=80):
        self.line_sensor = line_sensor
        self.motor = motor
        self.tracker = tracker
        self.port = port
        self.server_sock = None
        self._start_server()

    def _start_server(self):
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(("0.0.0.0", self.port))
            self.server_sock.listen(5)
            self.server_sock.setblocking(False)
            print(f"[WebServer] 🌐 Đã mở cổng HTTP điều khiển tại http://192.168.4.1:{self.port}")
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
            "mode": self.tracker.drive_mode,
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

    def _send_json(self, cl, data_dict):
        body = ujson.dumps(data_dict).encode("utf-8")
        hdr = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Cache-Control: no-store, no-cache\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")
        self._write_all(cl, hdr + body)

    def _send_html(self, cl):
        hdr = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(HTML_BYTES)}\r\n"
            "Cache-Control: no-store\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")
        self._write_all(cl, hdr)
        self._write_all(cl, HTML_BYTES)

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

                elif path == "/api/mode":
                    m = params.get("m", "STEP")
                    self.tracker.set_mode(m)
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

                elif path == "/favicon.ico":
                    self._write_all(cl, b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")

                else:
                    self._send_html(cl)
                    gc.collect()

                time.sleep_ms(3)
            except Exception as e:
                print("[WebServer Error]:", e)
            finally:
                try:
                    cl.close()
                except Exception:
                    pass
