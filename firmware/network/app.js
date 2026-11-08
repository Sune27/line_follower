// =============================================================================
// APP.JS – CONTROLLER & TELEMETRY SYNC FOR ESP32 LINE FOLLOWER ROBOT
// =============================================================================

let busy = false;
let isCarRunning = false;
let lastPidEditTime = 0;
let lastArmEditTime = 0;
let armDebounceTimer = null;

const ARM_MAP = {
  b: { input: "angBase", label: "angBaseVal" },
  s: { input: "angShoulder", label: "angShoulderVal" },
  e: { input: "angElbow", label: "angElbowVal" },
  g: { input: "angGripper", label: "angGripperVal" },
};

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

  // 5. Cập nhật thông số PID từ xe chỉ khi người dùng không vừa bấm chỉnh sửa (trong 10 giây qua)
  const now = Date.now();
  if (now - lastPidEditTime > 10000) {
    if (d.spd !== undefined) document.getElementById("inSpd").value = d.spd;
    if (d.kp !== undefined) document.getElementById("inKp").value = d.kp;
    if (d.ki !== undefined) document.getElementById("inKi").value = d.ki;
    if (d.kd !== undefined) document.getElementById("inKd").value = d.kd;
  }

  // 6. Cập nhật góc cánh tay Robot từ xe nếu người dùng không đang giữ lái
  if (d.arm && !isDrivingArm && (now - lastArmEditTime > 800)) {
    for (const k in d.arm) {
      const info = ARM_MAP[k];
      if (info) {
        const inp = document.getElementById(info.input);
        const lbl = document.getElementById(info.label);
        if (inp && document.activeElement !== inp) inp.value = d.arm[k];
        if (lbl) lbl.innerText = d.arm[k] + "°";
      }
    }
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


// =============================================================================
// ROBOTIC ARM CONTROLLER FUNCTIONS
// =============================================================================
function onArmSlider(joint, val) {
  lastArmEditTime = Date.now();
  val = parseInt(val, 10);
  const info = ARM_MAP[joint];
  if (info) {
    const lbl = document.getElementById(info.label);
    if (lbl) lbl.innerText = val + "°";
  }
  clearTimeout(armDebounceTimer);
  armDebounceTimer = setTimeout(() => {
    sendApi("/api/arm?" + joint + "=" + val);
  }, 50);
}

function setJoint(joint, val) {
  lastArmEditTime = Date.now();
  val = parseInt(val, 10);
  const info = ARM_MAP[joint];
  if (info) {
    const inp = document.getElementById(info.input);
    const lbl = document.getElementById(info.label);
    if (inp) inp.value = val;
    if (lbl) lbl.innerText = val + "°";
  }
  sendApi("/api/arm?" + joint + "=" + val);
}

function stepArm(joint, delta) {
  lastArmEditTime = Date.now();
  const info = ARM_MAP[joint];
  if (!info) return;
  const inp = document.getElementById(info.input);
  if (!inp) return;
  let val = Math.max(0, Math.min(180, (parseInt(inp.value, 10) || 90) + delta));
  inp.value = val;
  const lbl = document.getElementById(info.label);
  if (lbl) lbl.innerText = val + "°";
  clearTimeout(armDebounceTimer);
  armDebounceTimer = setTimeout(() => {
    sendApi("/api/arm?" + joint + "=" + val);
  }, 40);
}

let isDrivingArm = false;

function startDrive(joint, dir) {
  isDrivingArm = true;
  sendApi("/api/arm?j=" + joint + "&dir=" + dir);
}

function stopDrive(joint) {
  if (!isDrivingArm) return;
  isDrivingArm = false;
  sendApi("/api/arm?j=" + joint + "&dir=0");
}

function rotateBase(dir) {
  const targetAngle = dir === "left" ? 180 : 0;
  setJoint("b", targetAngle);
}

function sendArmPreset(presetName) {
  lastArmEditTime = 0;
  sendApi("/api/arm?p=" + presetName);
}

window.addEventListener("DOMContentLoaded", () => {
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
