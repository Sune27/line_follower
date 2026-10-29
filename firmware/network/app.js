// =============================================================================
// APP.JS – LOGIC GIAO DIỆN ĐIỀU KHIỂN & ĐỒNG BỘ TRẠNG THÁI XE DÒ LINE ESP32
// =============================================================================

let busy = false;

function updateUI(d) {
  if (!d) return;

  document.getElementById("actTxt").innerText = d.act || "STANDBY";

  const b = document.getElementById("modeBadge");
  if (d.run) {
    b.className = "badge b-run";
    b.innerText = "ĐANG DÒ LINE";
  } else {
    b.className = "badge b-stop";
    b.innerText = "ĐANG DỪNG";
  }

  if (d.s) {
    for (let i = 0; i < 5; i++) {
      const el = document.getElementById("s" + i);
      if (el) {
        el.innerText = d.s[i];
        el.className = d.s[i] ? "dot black" : "dot";
      }
    }
  }

  document.getElementById("errVal").innerText = d.err !== undefined ? d.err : 0;
  document.getElementById("spdL").innerText = (d.l || 0) + "%";
  document.getElementById("spdR").innerText = (d.r || 0) + "%";

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
  document.getElementById("actTxt").innerText = "ĐANG GỬI...";
  const sep = path.indexOf("?") > -1 ? "&" : "?";
  fetch(path + sep + "t=" + Date.now())
    .then((r) => r.json())
    .then((d) => updateUI(d))
    .catch(() => {
      document.getElementById("actTxt").innerText = "THỬ LẠI...";
    });
}

function manual(l, r) {
  sendApi("/api/manual?l=" + l + "&r=" + r);
}

function savePid() {
  const spd = document.getElementById("inSpd").value;
  const kp = document.getElementById("inKp").value;
  const ki = document.getElementById("inKi").value;
  const kd = document.getElementById("inKd").value;
  sendApi("/api/pid?spd=" + spd + "&kp=" + kp + "&ki=" + ki + "&kd=" + kd);
}

window.addEventListener("DOMContentLoaded", () => {
  sendApi("/api/status");
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
      });
  }, 500);
});
