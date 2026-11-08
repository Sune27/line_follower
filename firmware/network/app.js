// =============================================================================
// APP.JS – CONTROLLER & TELEMETRY SYNC FOR ESP32 SUPERCAR LINE FOLLOWER
// High-Tech Automotive Cockpit Interface • 100% Native Vanilla JS
// =============================================================================

let busy = false;
let isCarRunning = false;
let lastPidEditTime = 0;

// =============================================================================
// 1. TRẠNG THÁI KẾT NỐI & ĐỒNG BỘ TELEMETRY
// =============================================================================

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
  if (actEl) actEl.innerText = d.act || (isCarRunning ? "AUTONOMOUS TRACKING" : "STANDBY");

  const b = document.getElementById("modeBadge");
  const sub = document.getElementById("modeSubtitle");
  if (b) {
    if (d.run) {
      b.className = "badge badge-run";
      b.innerText = "ĐANG DÒ LINE";
      if (sub) sub.innerText = "SPORT AUTONOMOUS ACTIVE";
    } else {
      b.className = "badge badge-stop";
      b.innerText = "ĐANG DỪNG";
      if (sub) sub.innerText = "PARKING / STANDBY MODE";
    }
  }

  // 2. Cập nhật nút bấm START / STOP ENGINE & Trạng thái Cockpit
  const stbyBtn = document.getElementById("btnStandby");
  const lockIcon = document.getElementById("cockpitLockIcon");
  const holoText = document.getElementById("cockpitStatusText");
  const brakeStat = document.getElementById("hudBrakeStat");

  if (stbyBtn) {
    stbyBtn.classList.toggle("active", isCarRunning);
    const topTxt = stbyBtn.querySelector(".engine-text-top");
    const botTxt = stbyBtn.querySelector(".engine-text-bot");
    if (topTxt && botTxt) {
      if (isCarRunning) {
        topTxt.innerText = "STOP";
        botTxt.innerText = "ENGINE";
      } else {
        topTxt.innerText = "START";
        botTxt.innerText = "ENGINE";
      }
    }
  }

  if (holoText) {
    if (isCarRunning) {
      holoText.innerText = "ACTIVE";
      holoText.className = "status-hologram-text active";
    } else {
      holoText.innerText = "STANDBY";
      holoText.className = "status-hologram-text";
    }
  }

  if (lockIcon) {
    lockIcon.classList.toggle("active", isCarRunning);
  }

  if (brakeStat) {
    brakeStat.innerText = isCarRunning ? "RUNNING" : "HOLD";
    brakeStat.className = isCarRunning ? "pill-val text-green" : "pill-val";
  }

  // 3. Cập nhật 5 mắt cảm biến TCRT5000 (0 = Trắng, 1 = Đen)
  let activeSensorCount = 0;
  if (d.s && Array.isArray(d.s)) {
    for (let i = 0; i < 5; i++) {
      const el = document.getElementById("s" + i);
      if (el) {
        el.innerText = d.s[i];
        el.className = d.s[i] ? "sensor-diode black" : "sensor-diode";
        if (d.s[i]) activeSensorCount++;
      }
    }
  }

  // Cập nhật số cảnh báo trên chuông
  const alertEl = document.getElementById("alertCount");
  if (alertEl) {
    alertEl.innerText = activeSensorCount === 0 && isCarRunning ? "!" : activeSensorCount;
  }

  // 4. Cập nhật Sai số vị trí & Thước đo độ lệch quỹ đạo (Gauge)
  const errNum = d.err !== undefined ? parseFloat(d.err) : 0.0;
  const errEl = document.getElementById("errVal");
  const errTab = document.getElementById("errValTab");
  const hudErr = document.getElementById("hudErrVal");
  if (errEl) errEl.innerText = errNum.toFixed(1);
  if (errTab) errTab.innerText = errNum.toFixed(1);
  if (hudErr) hudErr.innerText = errNum.toFixed(1);

  const cursor = document.getElementById("gaugeCursor");
  if (cursor) {
    // Quy đổi sai số (-4.0 .. +4.0) sang vị trí % (6% .. 94%)
    const clampedErr = Math.max(-4.0, Math.min(4.0, errNum));
    const leftPct = 50 + (clampedErr / 4.0) * 44;
    cursor.style.left = leftPct + "%";
  }

  // 5. Cập nhật vận tốc 2 bánh (Left / Right Wheels)
  const spdL = d.l || 0;
  const spdR = d.r || 0;
  const spdLEl = document.getElementById("spdL");
  const spdREl = document.getElementById("spdR");
  const spdLTab = document.getElementById("spdLTab");
  const spdRTab = document.getElementById("spdRTab");
  if (spdLEl) spdLEl.innerText = spdL + "%";
  if (spdREl) spdREl.innerText = spdR + "%";
  if (spdLTab) spdLTab.innerText = spdL + "%";
  if (spdRTab) spdRTab.innerText = spdR + "%";

  const barL = document.getElementById("barL");
  const barR = document.getElementById("barR");
  if (barL) barL.style.width = Math.min(100, Math.abs(spdL)) + "%";
  if (barR) barR.style.width = Math.min(100, Math.abs(spdR)) + "%";

  // 6. Cập nhật tốc độ cơ sở hiển thị ở Pod phải
  const baseSpdEl = document.getElementById("hudBaseSpd");
  if (baseSpdEl && d.spd !== undefined) {
    baseSpdEl.innerText = d.spd + "%";
  }

  // 7. Cập nhật thông số PID từ xe chỉ khi người dùng không vừa bấm chỉnh sửa (trong 10 giây qua)
  const now = Date.now();
  if (now - lastPidEditTime > 10000) {
    if (d.spd !== undefined) document.getElementById("inSpd").value = d.spd;
    if (d.kp !== undefined) document.getElementById("inKp").value = d.kp;
    if (d.ki !== undefined) document.getElementById("inKi").value = d.ki;
    if (d.kd !== undefined) document.getElementById("inKd").value = d.kd;
  }
}

// =============================================================================
// 2. GIAO TIẾP VỚI ESP32 REST API
// =============================================================================

function sendApi(path) {
  const actEl = document.getElementById("actTxt");
  if (actEl) actEl.innerText = "TRANSMITTING...";

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
  lastPidEditTime = Date.now();
  const el = document.getElementById(inputId);
  if (!el) return;
  let val = parseFloat(el.value) || 0;
  val = Math.round((val + delta) * 100) / 100;
  if (minVal !== undefined && val < minVal) val = minVal;
  if (maxVal !== undefined && val > maxVal) val = maxVal;
  el.value = val;
}

function savePid() {
  lastPidEditTime = 0;
  const btn = document.getElementById("btnSavePid");
  const spd = document.getElementById("inSpd").value;
  const kp = document.getElementById("inKp").value;
  const ki = document.getElementById("inKi").value;
  const kd = document.getElementById("inKd").value;

  if (btn) {
    btn.innerHTML = '<span>⏳ ĐANG NẠP THÔNG SỐ VÀO XE...</span>';
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

function applyPreset(spd, kp, ki, kd) {
  lastPidEditTime = Date.now();
  document.getElementById("inSpd").value = spd;
  document.getElementById("inKp").value = kp;
  document.getElementById("inKi").value = ki;
  document.getElementById("inKd").value = kd;
  savePid();
}

// =============================================================================
// 3. ĐIỀU HƯỚNG TABS & DRAWER MENU
// =============================================================================

function switchTab(tabId) {
  const isWidescreen = window.innerWidth >= 768;

  if (!isWidescreen) {
    const sections = document.querySelectorAll(".hud-view-section");
    sections.forEach((sec) => sec.classList.remove("active"));

    const target = document.getElementById(tabId);
    if (target) target.classList.add("active");
  } else {
    // Trên máy tính / tablet: cuộn mượt và làm sáng nổi bật Card tương ứng
    const target = document.getElementById(tabId);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "nearest" });
      target.classList.add("highlight-card");
      setTimeout(() => target.classList.remove("highlight-card"), 1000);
    }
  }

  // Cập nhật trạng thái active trên Bottom Dock
  const dockMap = {
    tabCockpit: "dockCockpit",
    tabSensors: "dockSensors",
    tabManual: "dockManual",
    tabTuning: "dockTuning",
  };
  document.querySelectorAll(".dock-item").forEach((btn) => btn.classList.remove("active"));
  const activeDockBtn = document.getElementById(dockMap[tabId]);
  if (activeDockBtn) activeDockBtn.classList.add("active");

  // Cập nhật pod buttons
  const podButtons = document.querySelectorAll(".side-control-pod .pod-btn");
  podButtons.forEach((btn) => btn.classList.remove("active"));
}

function toggleDrawer() {
  const drawer = document.getElementById("sideDrawer");
  const backdrop = document.getElementById("sideDrawerBackdrop");
  if (!drawer || !backdrop) return;
  drawer.classList.toggle("show");
  backdrop.classList.toggle("show");
}

function updateClock() {
  const clockEl = document.getElementById("liveClock");
  if (!clockEl) return;
  const d = new Date();
  const h = String(d.getHours()).padStart(2, "0");
  const m = String(d.getMinutes()).padStart(2, "0");
  clockEl.innerText = `${h}:${m}`;
}

// =============================================================================
// 4. KHỞI TẠO ỨNG DỤNG
// =============================================================================

window.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 10000);

  sendApi("/api/status");

  ["inSpd", "inKp", "inKi", "inKd"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => { lastPidEditTime = Date.now(); });
      el.addEventListener("focus", () => { lastPidEditTime = Date.now(); });
    }
  });

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
