/* ─── Office Drawing ─── */
const PAL = {
  floor: "#3d3522", floorLight: "#4a4030",
  wall: "#2d2640", wallAccent: "#3a3355",
  desk: "#5c4a32", deskTop: "#6b5a3e",
  monitor: "#1e1e2e", monitorScreen: "#4ade80",
  chair: "#4a3728",
  plant: "#22c55e", plantDark: "#16a34a", pot: "#8b6914",
  book1: "#ef4444", book2: "#3b82f6", book3: "#f59e0b", book4: "#8b5cf6",
  coffee: "#8b6914", coffeeLiquid: "#5c3a11",
  whiteboard: "#e8e8e8", whiteboardFrame: "#9ca3af",
  rug: "#6b21a8", rugLight: "#7c3aed",
  window: "#60a5fa", windowFrame: "#4b5563",
  curtain: "#7c3aed", lamp: "#fbbf24",
};

const TILE = 16, SCALE = 2, CW = 800, CH = 560;
// Room / corridor geometry (mirror pathfinding constants in agents.js)
const WT = 7;            // wall thickness
const ROOM_Y1 = 32, ROOM_Y2 = 268;
const COR_Y1 = 268, COR_Y2 = 320;
const BREAK_Y1 = 320;
const ROOM_DEFS = [
  { x1: 10,  x2: 258, doorCx: 134, label: "RESEARCH" },
  { x1: 268, x2: 532, doorCx: 400, label: "DEV" },
  { x1: 542, x2: 790, doorCx: 666, label: "MEETING" },
];
const DOOR_HW = 26; // door half-width

/* ─── Drawing helpers ─── */
function drawDesk(ctx, x, y, colorIdx) {
  const mc = ["#4ade80","#60a5fa","#fbbf24"][colorIdx % 3];
  drawRect(ctx, x, y, 120, 50, PAL.desk);
  drawRect(ctx, x+4, y+2, 112, 4, PAL.deskTop);
  drawRect(ctx, x+4, y+46, 6, 16, PAL.desk);
  drawRect(ctx, x+110, y+46, 6, 16, PAL.desk);
  drawRect(ctx, x+30, y-30, 60, 34, PAL.monitor);
  drawRect(ctx, x+34, y-27, 52, 26, mc);
  drawRect(ctx, x+55, y+3, 10, 6, PAL.monitor);
  drawRect(ctx, x+45, y+8, 30, 3, PAL.monitor);
  drawRect(ctx, x+35, y+14, 50, 10, "#374151");
  drawRect(ctx, x+37, y+15, 46, 8, "#4b5563");
  drawRect(ctx, x+40, y+55, 40, 30, PAL.chair);
  drawRect(ctx, x+38, y+52, 44, 6, PAL.chair);
  drawRect(ctx, x+42, y+84, 6, 10, "#374151");
  drawRect(ctx, x+72, y+84, 6, 10, "#374151");
  for (let l = 0; l < 3; l++)
    drawRect(ctx, x+38, y-23+l*6, 20+(colorIdx*13+l*7)%24, 2, "#1a1a2e");
}

function drawWhiteboard(ctx, x, y) {
  drawRect(ctx, x, y, 148, 66, PAL.whiteboardFrame);
  drawRect(ctx, x+4, y+4, 140, 54, PAL.whiteboard);
  drawRect(ctx, x+10, y+14, 40, 2, "#ef4444");
  drawRect(ctx, x+10, y+22, 60, 2, "#3b82f6");
  drawRect(ctx, x+10, y+30, 25, 2, "#22c55e");
  drawRect(ctx, x+50, y+38, 50, 2, "#f59e0b");
  drawRect(ctx, x+4, y+58, 140, 8, "#9ca3af");
}

function drawBookshelf(ctx, x, y) {
  drawRect(ctx, x, y, 100, 110, PAL.desk);
  for (let s = 0; s < 3; s++) {
    drawRect(ctx, x+4, y+4+s*34, 92, 3, PAL.deskTop);
    [PAL.book1,PAL.book2,PAL.book3,PAL.book4,PAL.book1,PAL.book3].forEach((bc,bi) =>
      drawRect(ctx, x+6+bi*14, y+8+s*34, 10, 25, bc));
  }
}

function drawPlant(ctx, px, py) {
  drawRect(ctx, px+6, py+12, 16, 18, PAL.pot);
  drawRect(ctx, px+4, py+10, 20, 4, PAL.pot);
  drawRect(ctx, px+10, py-4, 8, 16, PAL.plant);
  drawRect(ctx, px+4, py-2, 8, 10, PAL.plantDark);
  drawRect(ctx, px+16, py, 6, 10, PAL.plantDark);
  drawRect(ctx, px+8, py-10, 4, 8, PAL.plant);
}

function drawWindow(ctx, cx) {
  drawRect(ctx, cx-34, 0, 68, 30, "#1e2a3a");
  drawRect(ctx, cx-34, 0, 68, 3, PAL.windowFrame);
  drawRect(ctx, cx-2, 3, 4, 27, PAL.windowFrame);
  drawRect(ctx, cx-34, 15, 68, 3, PAL.windowFrame);
  ctx.fillStyle = "#60a5fa33"; ctx.fillRect(cx-34, 3, 68, 12);
  ctx.fillStyle = "#60a5fa1a"; ctx.fillRect(cx-34, 18, 68, 9);
  drawRect(ctx, cx-42, 0, 8, 30, PAL.curtain);
  drawRect(ctx, cx+34, 0, 8, 30, PAL.curtain);
}

/* ─── Main office layout ─── */
function drawOffice(ctx) {
  // ── full canvas floor ──
  drawRect(ctx, 0, 0, CW, CH, PAL.floor);
  for (let tx = 0; tx < CW; tx += TILE*SCALE)
    for (let ty = 0; ty < CH; ty += TILE*SCALE)
      if ((tx/(TILE*SCALE) + ty/(TILE*SCALE)) % 2 === 0)
        drawRect(ctx, tx, ty, TILE*SCALE, TILE*SCALE, PAL.floorLight);

  // ── work-room floors (warmer tint) ──
  ROOM_DEFS.forEach(r => {
    drawRect(ctx, r.x1, ROOM_Y1, r.x2 - r.x1, ROOM_Y2 - ROOM_Y1, "#3e3826");
    for (let tx = r.x1; tx < r.x2; tx += TILE*SCALE)
      for (let ty = ROOM_Y1; ty < ROOM_Y2; ty += TILE*SCALE)
        if ((Math.floor(tx/(TILE*SCALE)) + Math.floor(ty/(TILE*SCALE))) % 2 === 0)
          drawRect(ctx, tx, ty, Math.min(TILE*SCALE, r.x2-tx), Math.min(TILE*SCALE, ROOM_Y2-ty), "#4a4230");
  });

  // ── corridor floor ──
  drawRect(ctx, 10, COR_Y1, 780, COR_Y2 - COR_Y1, "#28252e");
  for (let cx = 30; cx < 780; cx += 52) drawRect(ctx, cx, 291, 38, 3, "#3a3355");

  // ── break room floor + rug ──
  drawRect(ctx, 10, BREAK_Y1, 780, 232, "#2a2536");
  drawRect(ctx, 180, 368, 430, 156, PAL.rug);
  drawRect(ctx, 188, 376, 414, 140, PAL.rugLight);
  drawRect(ctx, 196, 384, 398, 124, PAL.rug);

  // ── ceiling / top wall ──
  drawRect(ctx, 0, 0, CW, ROOM_Y1, PAL.wall);
  drawRect(ctx, 0, ROOM_Y1 - 4, CW, 6, PAL.wallAccent);

  // ── outer side walls ──
  drawRect(ctx, 0, 0, WT, CH, PAL.wallAccent);
  drawRect(ctx, CW - WT, 0, WT, CH, PAL.wallAccent);
  drawRect(ctx, 0, CH - WT, CW, WT, PAL.wallAccent);

  // ── room divider walls (vertical, between rooms) ──
  [258, 532].forEach(vx => {
    drawRect(ctx, vx, ROOM_Y1, WT, ROOM_Y2 - ROOM_Y1, PAL.wallAccent);
    // pillar stub into corridor
    drawRect(ctx, vx, COR_Y1, WT, COR_Y2 - COR_Y1, PAL.wallAccent + "88");
  });

  // ── bottom walls of work rooms (with door gaps) ──
  ROOM_DEFS.forEach(r => {
    const wallY = ROOM_Y2 - WT;
    // left segment
    drawRect(ctx, r.x1, wallY, r.doorCx - DOOR_HW - r.x1, WT, PAL.wallAccent);
    // right segment
    drawRect(ctx, r.doorCx + DOOR_HW, wallY, r.x2 - (r.doorCx + DOOR_HW), WT, PAL.wallAccent);
    // door frame (wood)
    drawRect(ctx, r.doorCx - DOOR_HW - 4, wallY - 6, 4, WT + 10, "#6b5a3e");
    drawRect(ctx, r.doorCx + DOOR_HW,     wallY - 6, 4, WT + 10, "#6b5a3e");
    // door threshold line
    drawRect(ctx, r.doorCx - DOOR_HW, ROOM_Y2 - 1, DOOR_HW * 2, 2, "#5c4a3244");
  });

  // ── top wall of break room (open corridor→break transition) ──
  drawRect(ctx, WT, BREAK_Y1, CW - WT*2, 3, PAL.wallAccent + "55");

  // ── windows ──
  [134, 400, 666].forEach(drawWindow.bind(null, ctx));

  // ── room labels ──
  ctx.font = "7px 'Press Start 2P', monospace";
  ctx.textAlign = "center";
  ROOM_DEFS.forEach(r => {
    ctx.fillStyle = "rgba(255,255,255,0.13)";
    ctx.fillText(r.label, (r.x1 + r.x2) / 2, ROOM_Y1 + 16);
  });

  // ── RESEARCH ROOM ──
  drawBookshelf(ctx, 15, 78);
  drawDesk(ctx, 78, 148, 0);
  drawPlant(ctx, 224, 130);

  // ── DEV ROOM ──
  drawDesk(ctx, 283, 148, 1);
  drawDesk(ctx, 403, 148, 2);

  // ── MEETING ROOM ──
  drawWhiteboard(ctx, 594, 52);
  // meeting table + chairs
  drawRect(ctx, 598, 160, 148, 54, PAL.desk);
  drawRect(ctx, 602, 162, 140, 4, PAL.deskTop);
  [[610,150],[710,150],[610,212],[710,212]].forEach(([cx,cy]) => {
    drawRect(ctx, cx, cy, 28, 12, PAL.chair);
  });
  drawPlant(ctx, 756, 130);

  // ── BREAK ROOM ──
  drawBookshelf(ctx, 15, 350);
  // coffee machine
  drawRect(ctx, 690, 350, 52, 62, "#4b5563");
  drawRect(ctx, 694, 354, 42, 30, "#1e1e2e");
  drawRect(ctx, 700, 362, 10, 10, "#ef4444");
  drawRect(ctx, 716, 362, 10, 10, "#22c55e");
  drawRect(ctx, 698, 393, 16, 16, PAL.coffee);
  drawRect(ctx, 700, 395, 12, 12, PAL.coffeeLiquid);
  // couch
  drawRect(ctx, 490, 460, 120, 42, "#6b21a8");
  drawRect(ctx, 488, 455, 124, 8, "#7c3aed");
  drawRect(ctx, 486, 450, 12, 52, "#6b21a8");
  drawRect(ctx, 600, 450, 12, 52, "#6b21a8");
  // small table
  drawRect(ctx, 430, 462, 48, 28, "#5c4a32");
  drawRect(ctx, 432, 460, 44, 4, "#6b5a3e");
  // plants
  drawPlant(ctx, 760, 346);
  drawPlant(ctx, 15, 494);

  // ── ceiling lights ──
  [134, 400, 666, 290, 510].forEach(lx => {
    drawRect(ctx, lx-12, ROOM_Y1, 24, 4, "#4b5563");
    drawRect(ctx, lx-2, ROOM_Y1+2, 4, 12, "#4b5563");
    drawRect(ctx, lx-9, ROOM_Y1+12, 18, 5, PAL.lamp);
    ctx.fillStyle = "rgba(251,191,36,0.05)";
    ctx.beginPath(); ctx.ellipse(lx, 80, 52, 36, 0, 0, Math.PI*2); ctx.fill();
  });
}

/* ─── Main Loop ─── */
const canvas = document.getElementById("office");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

let frame = 0;

function render() {
  frame++;

  // Move agents along waypoint path
  agents.forEach(a => {
    if (a.waypoints && a.waypoints.length > 0) {
      const wp = a.waypoints[0];
      const dx = wp.x - a.x, dy = wp.y - a.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 4) {
        a.x = wp.x; a.y = wp.y;
        a.waypoints.shift();
        a.isWalking = a.waypoints.length > 0;
      } else {
        a.x += (dx/dist) * 2;
        a.y += (dy/dist) * 2;
        a.isWalking = true;
        a.facing = dx > 0 ? "right" : "left";
      }
    } else {
      a.isWalking = false;
    }
    a.bubbleTimer = Math.max(0, a.bubbleTimer - 1);
  });

  // Draw
  ctx.clearRect(0, 0, CW, CH);
  drawOffice(ctx);

  // Agents sorted by Y (depth)
  const sorted = [...agents].sort((a,b) => a.y - b.y);
  sorted.forEach(a => {
    drawPixelChar(ctx, a, a.x, a.y, frame);
    if (a.bubbleTimer > 0 && a.bubbleText) {
      ctx.globalAlpha = a.bubbleTimer < 30 ? a.bubbleTimer/30 : 1;
      drawBubble(ctx, a.x, a.y, a.bubbleText, a.color);
      ctx.globalAlpha = 1;
    }
    // Status icon
    const icon = STATUS_ICONS[a.status] || "❓";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(icon, a.x, a.y - 28*S + Math.sin(frame*0.08+a.x)*3);
  });

  requestAnimationFrame(render);
}

/* ─── Poll Server Status ─── */
let serverOnline = false;

async function fetchStatus() {
  try {
    const res = await fetch("/status");
    if (res.ok) {
      const data = await res.json();
      serverOnline = true;
      applyServerState(data);
    }
  } catch (e) {
    serverOnline = false;
  }
}

/* ─── Demo Mode (only when server is offline) ─── */
function demoTick() {
  if (serverOnline) return;
  const statuses = Object.keys(STATUS_TO_ZONE);
  agents.forEach(a => {
    if (Math.random() < 0.15) {
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
      const zone = ZONES[STATUS_TO_ZONE[newStatus]];
      const msgs = ACTIVITIES[newStatus] || ACTIVITIES.idle;
      const msg = msgs[Math.floor(Math.random() * msgs.length)];
      const jitter = () => (Math.random()-0.5)*24;
      const zoneName = STATUS_TO_ZONE[newStatus];
      const path = buildPath(a.x, a.y, zoneName);
      if (path.length > 0) path[path.length-1] = { x: zone.x + jitter(), y: zone.y + jitter() };
      a.status = newStatus;
      a.detail = msg;
      a.waypoints = path;
      a.bubbleText = msg;
      a.bubbleTimer = 180;

      activityLogs.unshift({
        time: new Date(), agent: a.name, color: a.color, status: newStatus, detail: msg
      });
      if (activityLogs.length > 30) activityLogs.pop();
    }
  });
}

/* ─── UI Updates ─── */
function updateUI() {
  // Clock
  document.getElementById("clock").textContent =
    new Date().toLocaleTimeString("en", {hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false});

  // Agent cards
  const cards = document.getElementById("agent-cards");
  const isBusy = a => !["idle","error"].includes(a.status);
  cards.innerHTML = agents.map(a => `
    <div class="agent-card ${selectedAgentId===a.id?'selected':''}"
         style="--agent-color:${a.color}; ${selectedAgentId===a.id?`border-color:${a.color};background:${a.color}11`:''}"
         onclick="selectAgent('${a.id}')">
      <span class="agent-dot" style="background:${STATUS_COLORS[a.status]||'#6b7280'};
        box-shadow:0 0 6px ${STATUS_COLORS[a.status]||'#6b7280'}"></span>
      <span style="color:${a.color}">${a.name.split(' ')[1]}</span>
      <span style="color:#6b7280">${STATUS_ICONS[a.status]||''} ${a.status}</span>
      ${isBusy(a) ? `<button class="stop-agent-btn" title="หยุดงาน"
        onclick="event.stopPropagation();stopAgent('${a.id}')">■</button>` : ''}
    </div>
  `).join("");

  // Agent detail
  const detailEl = document.getElementById("agent-detail");
  if (selectedAgentId) {
    const a = agents.find(ag => ag.id === selectedAgentId);
    if (a) {
      detailEl.classList.add("visible");
      detailEl.innerHTML = `
        <div class="name" style="color:${a.color}">${a.name}</div>
        <div class="role">${a.role}</div>
        <div class="status-line">
          <span class="agent-dot" style="width:6px;height:6px;background:${STATUS_COLORS[a.status]}"></span>
          ${STATUS_ICONS[a.status]||''} ${a.status}
        </div>
        ${a.detail ? `<div class="detail">"${a.detail}"</div>` : ''}
      `;
    }
  } else {
    detailEl.classList.remove("visible");
  }

  // Activity log
  const logEl = document.getElementById("activity-log");
  logEl.innerHTML = activityLogs.map((log, i) => `
    <div class="log-entry" style="opacity:${i>15?0.4:1}">
      <span class="time">${log.time.toLocaleTimeString("en",{hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false})}</span>
      <span class="agent" style="color:${log.color}">${log.agent.split(' ')[1]}</span>
      <span class="status-tag" style="color:${STATUS_COLORS[log.status]};background:${STATUS_COLORS[log.status]}15">${log.status}</span>
      <div class="detail">${log.detail}</div>
    </div>
  `).join("") || '<div style="color:#4b5563;padding:10px;text-align:center">Waiting for activity...</div>';

  // Action target
  const targetEl = document.getElementById("action-target");
  if (selectedAgentId) {
    const a = agents.find(ag => ag.id === selectedAgentId);
    targetEl.textContent = `→ ${a ? a.name : "Agent"}`;
  } else {
    targetEl.textContent = "→ All agents";
  }
}

function selectAgent(id) {
  selectedAgentId = selectedAgentId === id ? null : id;
}

function setStatus(status) {
  const zoneName = STATUS_TO_ZONE[status];
  const zone = ZONES[zoneName];
  const msgs = ACTIVITIES[status] || ACTIVITIES.idle;
  const msg = msgs[Math.floor(Math.random() * msgs.length)];

  agents.forEach(a => {
    if (selectedAgentId && a.id !== selectedAgentId) return;
    const jitter = () => (Math.random()-0.5)*24;
    const path = buildPath(a.x, a.y, zoneName);
    if (path.length > 0) path[path.length-1] = { x: zone.x + jitter(), y: zone.y + jitter() };
    a.status = status;
    a.detail = msg;
    a.waypoints = path;
    a.bubbleText = msg;
    a.bubbleTimer = 180;

    activityLogs.unshift({ time: new Date(), agent: a.name, color: a.color, status, detail: msg });
  });
  if (activityLogs.length > 30) activityLogs.length = 30;
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  const btn = document.getElementById("btn-sidebar");
  sb.classList.toggle("hidden");
  btn.textContent = sb.classList.contains("hidden") ? "▶ Panel" : "◀ Panel";
}

/* ─── Mode Switching ─── */
function switchMode(mode) {
  document.getElementById("mode-manual").classList.toggle("hidden", mode !== "manual");
  document.getElementById("mode-auto").classList.toggle("hidden", mode !== "auto");
  document.getElementById("tab-manual").classList.toggle("active", mode === "manual");
  document.getElementById("tab-auto").classList.toggle("active", mode === "auto");
}

/* ─── Brainstorm (AUTO mode) ─── */
function handleBrainstormKey(event) {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    doBrainstorm();
  }
}

async function doBrainstorm() {
  const input = document.getElementById("brainstorm-input");
  const task = input.value.trim();
  if (!task) return;

  const btn = document.getElementById("brainstorm-btn");
  const badge = document.getElementById("task-running-badge");
  const planEl = document.getElementById("brainstorm-plan");

  btn.disabled = true;
  btn.textContent = "⏳ Boss thinking...";
  badge.classList.remove("hidden");
  planEl.classList.add("hidden");
  setBrainstormFeedback("✦ Boss กำลังวิเคราะห์งาน...", "#fbbf24");

  // ส่ง agents ทุกตัวไป whiteboard
  agents.forEach(a => {
    const path = buildPath(a.x, a.y, "whiteboard");
    const zone = ZONES["whiteboard"];
    const jitter = () => (Math.random() - 0.5) * 28;
    if (path.length > 0) path[path.length - 1] = { x: zone.x + jitter(), y: zone.y + jitter() };
    a.status = "thinking";
    a.detail = "Boss กำลังวิเคราะห์...";
    a.waypoints = path;
    a.bubbleText = "🧠";
    a.bubbleTimer = 300;
  });

  try {
    const res = await fetch("/brainstorm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      setBrainstormFeedback(`✗ ${err.error || "Server error"}`, "#ef4444");
      agents.forEach(a => { a.status = "idle"; a.waypoints = buildPath(a.x, a.y, "breakroom"); });
      return;
    }

    const data = await res.json();
    renderBrainstormPlan(data);

    const assignedIds = new Set(data.assignments.map(a => a.agent_id));
    agents.forEach(a => {
      if (assignedIds.has(a.id)) {
        a.bubbleText = "📋 รับงานแล้ว!";
        a.bubbleTimer = 200;
      } else {
        a.status = "idle";
        a.detail = "พักระหว่างรอทีม...";
        a.waypoints = buildPath(a.x, a.y, "breakroom");
        a.bubbleText = "☕";
        a.bubbleTimer = 180;
      }
    });

    const names = data.assignments.map(a => a.agent_id.replace("claude-", "")).join(", ");
    setBrainstormFeedback(`✓ แบ่งงานให้: ${names}`, "#4ade80");

    // log
    data.assignments.forEach(({ agent_id, task: subtask }) => {
      const a = agents.find(ag => ag.id === agent_id);
      if (a) activityLogs.unshift({ time: new Date(), agent: a.name, color: a.color, status: "planning", detail: subtask });
    });
    if (activityLogs.length > 30) activityLogs.length = 30;

  } catch (e) {
    setBrainstormFeedback("✗ ไม่สามารถเชื่อมต่อ server", "#f59e0b");
    agents.forEach(a => { a.status = "idle"; a.waypoints = buildPath(a.x, a.y, "breakroom"); });
  } finally {
    btn.disabled = false;
    btn.textContent = "✦ BRAINSTORM";
    setTimeout(() => {
      badge.classList.add("hidden");
      setBrainstormFeedback("", "#6b7280");
    }, 6000);
  }
}

function setBrainstormFeedback(text, color) {
  const el = document.getElementById("brainstorm-feedback");
  if (el) { el.textContent = text; el.style.color = color; }
}

function renderBrainstormPlan(data) {
  const planEl = document.getElementById("brainstorm-plan");
  document.getElementById("plan-text").textContent = `Boss: ${data.plan}`;

  const assignedMap = Object.fromEntries(data.assignments.map(a => [a.agent_id, a.task]));
  document.getElementById("plan-assignments").innerHTML = agents.map(a => {
    const task = assignedMap[a.id];
    if (task) {
      return `<div class="plan-row">
        <span class="plan-dot" style="background:${a.color};box-shadow:0 0 4px ${a.color}"></span>
        <span class="plan-name" style="color:${a.color}">${a.name.split(" ")[1]}</span>
        <span class="plan-task">${task}</span>
      </div>`;
    }
    return `<div class="plan-row idle">
      <span class="plan-dot" style="background:#374151"></span>
      <span class="plan-name" style="color:#4b5563">${a.name.split(" ")[1]}</span>
      <span class="plan-task">☕ idle</span>
    </div>`;
  }).join("");

  planEl.classList.remove("hidden");
}

/* ─── Task Dispatch Panel ─── */
const TASK_DEFAULTS = {
  "claude-opus":   "วิเคราะห์แนวโน้ม AI ปี 2026...",
  "claude-sonnet": "ออกแบบ REST API สำหรับ...",
  "claude-haiku":  "สรุปข่าวเทคโนโลยีวันนี้...",
  "claude-code":   "เขียน unit test สำหรับ...",
};

function initTaskPanel() {
  const grid = document.getElementById("task-inputs-grid");
  grid.innerHTML = agents.map(a => {
    const glow = a.color + "33";
    return `
      <div class="task-card" style="--agent-color:${a.color};--agent-glow:${glow}">
        <div class="task-card-header">
          <span class="agent-dot" style="background:${a.color};box-shadow:0 0 5px ${a.color};width:8px;height:8px;border-radius:50%;flex-shrink:0"></span>
          <div>
            <div class="task-card-name" style="color:${a.color}">${a.name}</div>
            <div class="task-card-role">${a.role}</div>
          </div>
        </div>
        <textarea
          class="task-input"
          id="task-input-${a.id}"
          placeholder="${TASK_DEFAULTS[a.id] || 'พิมพ์ task...'}"
          style="--agent-color:${a.color}"
          onkeydown="handleTaskKey(event,'${a.id}')"
        ></textarea>
        <button class="task-run-btn" id="run-btn-${a.id}"
                style="--agent-color:${a.color};--agent-glow:${glow}"
                onclick="dispatchAgent('${a.id}')">
          ▶ RUN
        </button>
      </div>
    `;
  }).join("");
}

function handleTaskKey(event, agentId) {
  // Ctrl+Enter หรือ Cmd+Enter = dispatch agent นั้น
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    dispatchAgent(agentId);
  }
}

async function dispatchAgent(agentId) {
  const input = document.getElementById(`task-input-${agentId}`);
  const task = input.value.trim() || input.placeholder;
  if (!task) return;

  const btn = document.getElementById(`run-btn-${agentId}`);
  btn.disabled = true;
  btn.textContent = "⏳";
  await sendTasks({ [agentId]: task });
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = "▶ RUN";
  }, 3000);
}

async function dispatchAll() {
  const tasks = {};
  agents.forEach(a => {
    const input = document.getElementById(`task-input-${a.id}`);
    if (!input) return;
    const task = input.value.trim() || input.placeholder;
    if (task) tasks[a.id] = task;
  });
  if (Object.keys(tasks).length === 0) return;
  await sendTasks(tasks);
}

async function sendTasks(tasks) {
  const btn = document.getElementById("dispatch-all-btn");
  const badge = document.getElementById("task-running-badge");

  btn.disabled = true;
  badge.classList.remove("hidden");
  setFeedback("⏳ Dispatching to agents...", "#9ca3af");

  try {
    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks }),
    });

    if (res.ok) {
      const data = await res.json();
      const names = data.started.map(id => id.replace("claude-","")).join(", ");
      setFeedback(`✓ Started: ${names}`, "#4ade80");
    } else {
      setFeedback("✗ Server error — is the server running?", "#ef4444");
    }
  } catch (e) {
    setFeedback("✗ Cannot reach server (demo mode)", "#f59e0b");
  }

  setTimeout(() => {
    btn.disabled = false;
    badge.classList.add("hidden");
    setFeedback("", "#6b7280");
  }, 5000);
}

function setFeedback(text, color) {
  const el = document.getElementById("dispatch-feedback");
  el.textContent = text;
  el.style.color = color;
}

/* ─── Stop Agents ─── */
async function stopAgent(agentId) {
  try {
    await fetch("/stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId }),
    });
    // อัพเดต local state ทันที ไม่รอ poll
    const a = agents.find(ag => ag.id === agentId);
    if (a) {
      a.status = "idle";
      a.detail = "หยุดโดยผู้ใช้";
      a.waypoints = buildPath(a.x, a.y, "breakroom");
      a.bubbleText = "☕ หยุดพัก...";
      a.bubbleTimer = 120;
      activityLogs.unshift({ time: new Date(), agent: a.name, color: a.color, status: "idle", detail: "หยุดโดยผู้ใช้" });
      if (activityLogs.length > 30) activityLogs.pop();
    }
  } catch (e) {
    // demo mode — อัพเดตแค่ local
    const a = agents.find(ag => ag.id === agentId);
    if (a) { a.status = "idle"; a.detail = ""; a.waypoints = buildPath(a.x, a.y, "breakroom"); }
  }
}

async function stopAll() {
  const busy = agents.filter(a => !["idle","error"].includes(a.status));
  if (busy.length === 0) return;
  await Promise.all(busy.map(a => stopAgent(a.id)));
  setFeedback(`■ หยุด: ${busy.map(a => a.name.split(" ")[1]).join(", ")}`, "#f87171");
  setTimeout(() => setFeedback("", "#6b7280"), 3000);
}

function toggleTaskPanel() {
  const body = document.getElementById("task-panel-body");
  const toggle = document.getElementById("task-panel-toggle");
  body.classList.toggle("hidden");
  toggle.textContent = body.classList.contains("hidden") ? "▼" : "▲";
}

/* ─── Init ─── */
(function init() {
  // Zone labels
  const labelsEl = document.getElementById("zone-labels");
  for (const [, zone] of Object.entries(ZONES)) {
    const el = document.createElement("div");
    el.className = "zone-label";
    el.style.left = `${(zone.x/CW)*100}%`;
    el.style.top = `${((zone.y-20)/CH)*100}%`;
    el.textContent = zone.label;
    labelsEl.appendChild(el);
  }

  // Action buttons
  const actionsEl = document.getElementById("action-buttons");
  ["writing","coding","researching","thinking","idle","planning"].forEach(status => {
    const btn = document.createElement("button");
    btn.className = "action-btn";
    btn.style.background = `${STATUS_COLORS[status]}20`;
    btn.style.border = `1px solid ${STATUS_COLORS[status]}40`;
    btn.style.color = STATUS_COLORS[status];
    btn.textContent = `${STATUS_ICONS[status]} ${status}`;
    btn.onclick = () => setStatus(status);
    actionsEl.appendChild(btn);
  });

  // Task dispatch panel
  initTaskPanel();

  // Start render loop
  requestAnimationFrame(render);

  // Poll server every 2s
  setInterval(fetchStatus, 2000);
  fetchStatus();

  // Demo mode fallback (if no server)
  setInterval(demoTick, 3000);

  // UI update
  setInterval(updateUI, 200);
  updateUI();
})();
