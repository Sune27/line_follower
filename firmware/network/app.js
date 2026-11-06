// =============================================================================
// APP.JS – CONTROLLER & TELEMETRY SYNC FOR ESP32 LINE FOLLOWER ROBOT
// =============================================================================

let busy = false;
let isCarRunning = false;

function setConnectionStatus(online) {
  const pill = document.getElementById("livePill");
  const txt = document.getElementById("connTxt");
  if (!pill || !txt) return;
  if (online) {
    pill.className = "live-pill online";
    txt.innerText = "ONLINE";
  } else {
    pill.className = "live-pill offline";
    txt.innerText = "MẤT KẾT NỐI";
  }
}

function updateUI(d) {
  if (!d) return;
  setConnectionStatus(true);

  isCarRunning = Boolean(d.run);

  // 1. Cập nhật hành động & Chế độ
  const actEl = document.getElementById("actTxt");
  if (actEl) actEl.innerText = d.act || "STANDBY";

  const b = document.getElementById("modeBadge");
  if (b) {
    if (d.run) {
      b.className = "badge badge-run";
      b.innerText = "ĐANG DÒ LINE";
    } else {
      b.className = "badge badge-stop";
      b.innerText = "ĐANG DỪNG";
    }
  }

  // Cập nhật trạng thái nút tròn STAND-BY (Sáng rực xanh Neon khi xe chạy)
  const stbyBtn = document.getElementById("btnStandby");
  if (stbyBtn) {
    stbyBtn.classList.toggle("active", isCarRunning);
  }

  // 2. Cập nhật 5 mắt cảm biến (0 = Nền trắng, 1 = Vạch đen)
  if (d.s && Array.isArray(d.s)) {
    for (let i = 0; i < 5; i++) {
      const el = document.getElementById("s" + i);
      if (el) {
        el.innerText = d.s[i];
        el.className = d.s[i] ? "sensor-diode black" : "sensor-diode";
      }
    }
  }

  // 3. Cập nhật Sai số vị trí & Thước đo độ lệch
  const errNum = d.err !== undefined ? parseFloat(d.err) : 0.0;
  carLateralError = errNum;
  currentMotorSpeed = Math.abs((d.l || 0) + (d.r || 0)) / 2;

  // Kiểm tra qua Vạch Ngang Xuất Phát / Đích để đồng bộ vị trí
  const isCross = (d.act && d.act.indexOf("CROSS") > -1) || 
                  (d.s && d.s.length === 5 && d.s.every((v) => v === 1));
  if (isCross && trackProgress > 0.35) {
    triggerCheckpoint();
  }
  const errEl = document.getElementById("errVal");
  if (errEl) errEl.innerText = errNum.toFixed(1);

  const cursor = document.getElementById("gaugeCursor");
  if (cursor) {
    // Quy đổi sai số (-4.0 .. +4.0) sang vị trí % (6% .. 94%)
    const clampedErr = Math.max(-4.0, Math.min(4.0, errNum));
    const leftPct = 50 + (clampedErr / 4.0) * 44;
    cursor.style.left = leftPct + "%";
  }

  // 4. Cập nhật vận tốc 2 bánh & Thanh đo tốc độ
  const spdL = d.l || 0;
  const spdR = d.r || 0;
  const spdLEl = document.getElementById("spdL");
  const spdREl = document.getElementById("spdR");
  if (spdLEl) spdLEl.innerText = spdL + "%";
  if (spdREl) spdREl.innerText = spdR + "%";

  const barL = document.getElementById("barL");
  const barR = document.getElementById("barR");
  if (barL) barL.style.width = Math.min(100, Math.abs(spdL)) + "%";
  if (barR) barR.style.width = Math.min(100, Math.abs(spdR)) + "%";

  // 5. Cập nhật thông số PID vào ô Input nếu người dùng không đang gõ
  const ae = document.activeElement;
  if (d.spd !== undefined && ae !== document.getElementById("inSpd")) {
    document.getElementById("inSpd").value = d.spd;
  }
  if (d.kp !== undefined && ae !== document.getElementById("inKp")) {
    document.getElementById("inKp").value = d.kp;
  }
  if (d.ki !== undefined && ae !== document.getElementById("inKi")) {
    document.getElementById("inKi").value = d.ki;
  }
  if (d.kd !== undefined && ae !== document.getElementById("inKd")) {
    document.getElementById("inKd").value = d.kd;
  }
}

function sendApi(path) {
  const actEl = document.getElementById("actTxt");
  if (actEl) actEl.innerText = "ĐANG TRUYỀN...";

  const sep = path.indexOf("?") > -1 ? "&" : "?";
  fetch(path + sep + "t=" + Date.now())
    .then((r) => {
      if (!r.ok) throw new Error("HTTP error " + r.status);
      return r.json();
    })
    .then((d) => updateUI(d))
    .catch(() => {
      setConnectionStatus(false);
      if (actEl) actEl.innerText = "LỖI KẾT NỐI!";
    });
}

function toggleRun() {
  if (isCarRunning) {
    sendApi("/api/stop");
  } else {
    sendApi("/api/start");
  }
}

function manual(l, r) {
  sendApi("/api/manual?l=" + l + "&r=" + r);
}

function stepVal(inputId, delta, minVal, maxVal) {
  const el = document.getElementById(inputId);
  if (!el) return;
  let val = parseFloat(el.value) || 0;
  val = Math.round((val + delta) * 100) / 100;
  if (minVal !== undefined && val < minVal) val = minVal;
  if (maxVal !== undefined && val > maxVal) val = maxVal;
  el.value = val;
}

function savePid() {
  const btn = document.getElementById("btnSavePid");
  const spd = document.getElementById("inSpd").value;
  const kp = document.getElementById("inKp").value;
  const ki = document.getElementById("inKi").value;
  const kd = document.getElementById("inKd").value;

  if (btn) {
    btn.innerText = "⏳ ĐANG LƯU...";
    btn.style.filter = "brightness(0.85)";
  }

  sendApi("/api/pid?spd=" + spd + "&kp=" + kp + "&ki=" + ki + "&kd=" + kd);

  setTimeout(() => {
    if (btn) {
      btn.innerHTML = '<span class="btn-icon">💾</span><span>CẬP NHẬT THÔNG SỐ VÀO XE</span>';
      btn.style.filter = "none";
    }
  }, 600);
}

window.addEventListener("DOMContentLoaded", () => {
  sendApi("/api/status");
  initCanvasLoop();

  // Vòng lặp đồng bộ trạng thái xe mỗi 500ms
  setInterval(() => {
    const chk = document.getElementById("liveChk");
    if (!chk || !chk.checked || busy) return;
    busy = true;

    fetch("/api/status?t=" + Date.now())
      .then((r) => r.json())
      .then((d) => {
        updateUI(d);
        busy = false;
      })
      .catch(() => {
        busy = false;
        setConnectionStatus(false);
      });
  }, 500);
});

// =============================================================================
// REALTIME TRACK CANVAS ENGINE
// =============================================================================
let trackPreset = "oval";
let trackProgress = 0.0;
let lapCycleSec = 10;
let lapCount = 0;
let lastFrameTime = performance.now();
let checkpointTimeout = null;

function changeTrackPreset(val) {
  trackPreset = val;
  trackProgress = 0.0;
  updateTrackUI();
}

function adjustLapCycle(delta) {
  lapCycleSec = Math.max(3, Math.min(60, lapCycleSec + delta));
  const el = document.getElementById("lapCycleVal");
  if (el) el.innerText = lapCycleSec + "s";
}

function resetTrackPosition() {
  trackProgress = 0.0;
  lapCount = 0;
  updateTrackUI();
}

function triggerCheckpoint() {
  trackProgress = 0.0;
  lapCount++;
  updateTrackUI();
  const alertEl = document.getElementById("checkpointAlert");
  if (alertEl) {
    alertEl.classList.add("show");
    clearTimeout(checkpointTimeout);
    checkpointTimeout = setTimeout(() => {
      alertEl.classList.remove("show");
    }, 1200);
  }
}

function updateTrackUI() {
  const pEl = document.getElementById("lapProgress");
  if (pEl) pEl.innerText = Math.round(trackProgress * 100) + "%";
  const lEl = document.getElementById("lapCount");
  if (lEl) lEl.innerText = lapCount;
}

// Hàm tính tọa độ trên đường cong tham số [0..1)
function getTrackPoint(p) {
  p = ((p % 1) + 1) % 1;
  const W = 420, H = 230;
  const pad = 38;
  const cx = W / 2, cy = H / 2;

  if (trackPreset === "oval") {
    // Đường Bo Góc Oval (2 đoạn thẳng + 2 nửa đường tròn)
    const r = (H - 2 * pad) / 2;
    const straightL = W - 2 * pad - 2 * r;
    const halfCirc = Math.PI * r;
    const totalL = 2 * straightL + 2 * halfCirc;
    const dist = p * totalL;

    if (dist < straightL) {
      const t = dist / straightL;
      return { x: pad + r + t * straightL, y: pad };
    } else if (dist < straightL + halfCirc) {
      const ang = -Math.PI / 2 + ((dist - straightL) / halfCirc) * Math.PI;
      return { x: cx + straightL / 2 + r * Math.cos(ang), y: cy + r * Math.sin(ang) };
    } else if (dist < 2 * straightL + halfCirc) {
      const t = (dist - straightL - halfCirc) / straightL;
      return { x: cx + straightL / 2 - t * straightL, y: H - pad };
    } else {
      const ang = Math.PI / 2 + ((dist - 2 * straightL - halfCirc) / halfCirc) * Math.PI;
      return { x: cx - straightL / 2 - r * Math.cos(ang), y: cy + r * Math.sin(ang) };
    }
  } else if (trackPreset === "figure8") {
    // Đường số 8 (Lemniscate of Gerono)
    const a = (W - 2 * pad) / 2.3;
    const b = (H - 2 * pad) / 1.15;
    const ang = p * 2 * Math.PI;
    return {
      x: cx + a * Math.sin(ang),
      y: cy + (b / 2) * Math.sin(2 * ang)
    };
  } else {
    // Đường đua F1 hỗn hợp (Circuit với cua gấp & ziczac)
    const pts = [
      { x: 70, y: 48 }, { x: 210, y: 48 }, { x: 350, y: 48 },
      { x: 365, y: 115 }, { x: 320, y: 182 }, { x: 230, y: 130 },
      { x: 175, y: 182 }, { x: 70, y: 182 }, { x: 55, y: 115 }
    ];
    const n = pts.length;
    const idxFloat = p * n;
    const i = Math.floor(idxFloat) % n;
    const nextI = (i + 1) % n;
    const t = idxFloat - Math.floor(idxFloat);
    return {
      x: pts[i].x + (pts[nextI].x - pts[i].x) * t,
      y: pts[i].y + (pts[nextI].y - pts[i].y) * t
    };
  }
}

// Đạo hàm số học tính góc tiếp tuyến (Heading direction)
function getTrackHeading(p) {
  const eps = 0.005;
  const p1 = getTrackPoint(p - eps);
  const p2 = getTrackPoint(p + eps);
  return Math.atan2(p2.y - p1.y, p2.x - p1.x);
}

// Vòng lặp vẽ đồ họa thời gian thực
function initCanvasLoop() {
  const canvas = document.getElementById("trackCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function drawTrack(now) {
    const dt = (now - lastFrameTime) / 1000;
    lastFrameTime = now;

    // Tính tiến độ di chuyển dựa theo tốc độ động cơ và chu kỳ vòng
    if (isCarRunning && lapCycleSec > 0) {
      const speedFactor = currentMotorSpeed > 0 ? (currentMotorSpeed / 62) : 1.0;
      trackProgress += (dt / lapCycleSec) * speedFactor;
      if (trackProgress >= 1.0) {
        trackProgress = trackProgress % 1.0;
        lapCount++;
      }
      updateTrackUI();
    }

    const W = canvas.width;
    const H = canvas.height;

    // 1. Xóa nền & Vẽ lưới radar tọa độ
    ctx.clearRect(0, 0, W, H);

    ctx.strokeStyle = "rgba(56, 189, 248, 0.05)";
    ctx.lineWidth = 1;
    const step = 28;
    for (let x = 0; x < W; x += step) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += step) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    // 2. Vẽ nền đường nhựa Asphalt
    const samples = 140;
    ctx.beginPath();
    for (let i = 0; i <= samples; i++) {
      const pt = getTrackPoint(i / samples);
      if (i === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    }
    ctx.closePath();
    ctx.lineWidth = 26;
    ctx.strokeStyle = "#131d2e";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();

    // 3. Vẽ vạch đen dẫn đường (Black Line)
    ctx.lineWidth = 8;
    ctx.strokeStyle = "#05080f";
    ctx.stroke();

    // 4. Vẽ vạch chỉ hướng dạ quang
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
    ctx.setLineDash([4, 6]);
    ctx.stroke();
    ctx.setLineDash([]);

    // 5. Vẽ Vạch Xuất Phát / Đích (Finish Checkpoint)
    const startPt = getTrackPoint(0.0);
    const startAng = getTrackHeading(0.0);
    const normX = -Math.sin(startAng);
    const normY = Math.cos(startAng);
    ctx.beginPath();
    ctx.moveTo(startPt.x - normX * 13, startPt.y - normY * 13);
    ctx.lineTo(startPt.x + normX * 13, startPt.y + normY * 13);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#10b981";
    ctx.stroke();

    ctx.font = "bold 9px monospace";
    ctx.fillStyle = "#34d399";
    ctx.fillText("FINISH", startPt.x - 14, startPt.y - 16);

    // 6. Tính vị trí xe thời gian thực + Độ lắc ngang từ 5 mắt TCRT5000
    const rawPt = getTrackPoint(trackProgress);
    const heading = getTrackHeading(trackProgress);
    const latNormX = -Math.sin(heading);
    const latNormY = Math.cos(heading);

    // Sai số lệch ngang: khi xe lệch trái/phải, xe trên bản đồ cũng lệch theo tim vạch
    const latOffset = Math.max(-4, Math.min(4, carLateralError)) * 2.2;
    const carX = rawPt.x + latNormX * latOffset;
    const carY = rawPt.y + latNormY * latOffset;

    // 7. Sóng Radar phát xạ khi xe đang chạy
    if (isCarRunning) {
      const pulseR = 12 + Math.sin(now / 150) * 4;
      ctx.beginPath();
      ctx.arc(carX, carY, pulseR, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(56, 189, 248, 0.5)";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // 8. Vẽ Robot Dò Line (Chassis) xoay theo hướng chuyển động
    ctx.save();
    ctx.translate(carX, carY);
    ctx.rotate(heading);

    // Thân xe bo tròn
    ctx.fillStyle = isCarRunning ? "#0284c7" : "#475569";
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(-10, -7, 20, 14, 4);
    } else {
      ctx.rect(-10, -7, 20, 14);
    }
    ctx.fill();
    ctx.strokeStyle = isCarRunning ? "#38bdf8" : "#94a3b8";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 2 Đèn pha trước
    ctx.fillStyle = isCarRunning ? "#fef08a" : "#cbd5e1";
    ctx.fillRect(8, -5, 3, 3);
    ctx.fillRect(8, 2, 3, 3);

    // 2 Bánh xe cao su
    ctx.fillStyle = "#020617";
    ctx.fillRect(-6, -9, 12, 3);
    ctx.fillRect(-6, 6, 12, 3);

    ctx.restore();

    requestAnimationFrame(drawTrack);
  }

  requestAnimationFrame(drawTrack);
}

