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

function drawOffice(ctx) {
  // Floor tiles
  drawRect(ctx, 0, 0, CW, CH, PAL.floor);
  for (let tx = 0; tx < CW; tx += TILE*SCALE)
    for (let ty = 0; ty < CH; ty += TILE*SCALE)
      if ((tx/(TILE*SCALE) + ty/(TILE*SCALE)) % 2 === 0)
        drawRect(ctx, tx, ty, TILE*SCALE, TILE*SCALE, PAL.floorLight);

  // Wall
  drawRect(ctx, 0, 0, CW, 60, PAL.wall);
  drawRect(ctx, 0, 55, CW, 10, PAL.wallAccent);

  // Rug
  drawRect(ctx, 300, 320, 200, 120, PAL.rug);
  drawRect(ctx, 308, 328, 184, 104, PAL.rugLight);
  drawRect(ctx, 316, 336, 168, 88, PAL.rug);

  // Windows
  [150, 350, 550].forEach(wx => {
    drawRect(ctx, wx-2, 8, 84, 44, PAL.windowFrame);
    drawRect(ctx, wx, 10, 80, 40, PAL.window);
    drawRect(ctx, wx+38, 10, 4, 40, PAL.windowFrame);
    drawRect(ctx, wx, 28, 80, 4, PAL.windowFrame);
    drawRect(ctx, wx-6, 6, 8, 48, PAL.curtain);
    drawRect(ctx, wx+78, 6, 8, 48, PAL.curtain);
  });

  // Desks
  [{x:80,y:150},{x:280,y:150},{x:480,y:150}].forEach((d, i) => {
    drawRect(ctx, d.x, d.y, 120, 50, PAL.desk);
    drawRect(ctx, d.x+4, d.y+2, 112, 4, PAL.deskTop);
    drawRect(ctx, d.x+4, d.y+46, 6, 16, PAL.desk);
    drawRect(ctx, d.x+110, d.y+46, 6, 16, PAL.desk);
    // Monitor
    drawRect(ctx, d.x+30, d.y-30, 60, 34, PAL.monitor);
    const colors = ["#4ade80","#60a5fa","#fbbf24"];
    drawRect(ctx, d.x+34, d.y-27, 52, 26, colors[i]);
    drawRect(ctx, d.x+55, d.y+3, 10, 6, PAL.monitor);
    drawRect(ctx, d.x+45, d.y+8, 30, 3, PAL.monitor);
    // Keyboard
    drawRect(ctx, d.x+35, d.y+14, 50, 10, "#374151");
    drawRect(ctx, d.x+37, d.y+15, 46, 8, "#4b5563");
    // Chair
    drawRect(ctx, d.x+40, d.y+55, 40, 30, PAL.chair);
    drawRect(ctx, d.x+38, d.y+52, 44, 6, PAL.chair);
    drawRect(ctx, d.x+42, d.y+84, 6, 10, "#374151");
    drawRect(ctx, d.x+72, d.y+84, 6, 10, "#374151");
    // Screen lines (deterministic width per desk/line)
    for (let l = 0; l < 3; l++)
      drawRect(ctx, d.x+38, d.y-23+l*6, 20+(i*13+l*7)%24, 2, "#1a1a2e");
  });

  // Whiteboard
  drawRect(ctx, 340, 62, 120, 50, PAL.whiteboardFrame);
  drawRect(ctx, 344, 66, 112, 42, PAL.whiteboard);
  drawRect(ctx, 350, 74, 30, 2, "#ef4444");
  drawRect(ctx, 350, 80, 50, 2, "#3b82f6");
  drawRect(ctx, 350, 86, 20, 2, "#22c55e");
  drawRect(ctx, 390, 92, 40, 2, "#f59e0b");

  // Bookshelf
  drawRect(ctx, 30, 340, 100, 120, PAL.desk);
  for (let s = 0; s < 3; s++) {
    drawRect(ctx, 34, 345+s*38, 92, 4, PAL.deskTop);
    [PAL.book1,PAL.book2,PAL.book3,PAL.book4,PAL.book1,PAL.book3].forEach((bc,bi) =>
      drawRect(ctx, 38+bi*14, 350+s*38, 10, 32, bc));
  }

  // Coffee machine
  drawRect(ctx, 680, 360, 50, 60, "#4b5563");
  drawRect(ctx, 684, 364, 42, 30, "#1e1e2e");
  drawRect(ctx, 690, 370, 10, 10, "#ef4444");
  drawRect(ctx, 706, 370, 10, 10, "#22c55e");
  drawRect(ctx, 688, 400, 16, 16, PAL.coffee);
  drawRect(ctx, 690, 402, 12, 12, PAL.coffeeLiquid);

  // Couch
  drawRect(ctx, 620, 430, 100, 40, "#6b21a8");
  drawRect(ctx, 618, 426, 104, 8, "#7c3aed");
  drawRect(ctx, 616, 420, 10, 50, "#6b21a8");
  drawRect(ctx, 718, 420, 10, 50, "#6b21a8");

  // Plants
  [[20,130],[740,130],[620,340]].forEach(([px,py]) => {
    drawRect(ctx, px+6, py+12, 16, 18, PAL.pot);
    drawRect(ctx, px+4, py+10, 20, 4, PAL.pot);
    drawRect(ctx, px+10, py-4, 8, 16, PAL.plant);
    drawRect(ctx, px+4, py-2, 8, 10, PAL.plantDark);
    drawRect(ctx, px+16, py, 6, 10, PAL.plantDark);
    drawRect(ctx, px+8, py-10, 4, 8, PAL.plant);
  });

  // Ceiling lights
  [200,400,600].forEach(lx => {
    drawRect(ctx, lx-15, 0, 30, 4, "#4b5563");
    drawRect(ctx, lx-3, 2, 6, 14, "#4b5563");
    drawRect(ctx, lx-10, 14, 20, 6, PAL.lamp);
    ctx.fillStyle = "rgba(251,191,36,0.08)";
    ctx.beginPath();
    ctx.ellipse(lx, 60, 60, 40, 0, 0, Math.PI*2);
    ctx.fill();
  });
}

/* ─── Main Loop ─── */
const canvas = document.getElementById("office");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

let frame = 0;

function render() {
  frame++;

  // Move agents toward targets
  agents.forEach(a => {
    const dx = a.targetX - a.x;
    const dy = a.targetY - a.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > 3) {
      a.x += (dx/dist) * 1.5;
      a.y += (dy/dist) * 1.5;
      a.isWalking = true;
      a.facing = dx > 0 ? "right" : "left";
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
async function fetchStatus() {
  try {
    const res = await fetch("/status");
    if (res.ok) {
      const data = await res.json();
      applyServerState(data);
    }
  } catch (e) {
    // Server ไม่พร้อม — ใช้ demo mode
  }
}

/* ─── Demo Mode (auto-simulate when no server) ─── */
function demoTick() {
  const statuses = Object.keys(STATUS_TO_ZONE);
  agents.forEach(a => {
    if (Math.random() < 0.15) {
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
      const zone = ZONES[STATUS_TO_ZONE[newStatus]];
      const msgs = ACTIVITIES[newStatus] || ACTIVITIES.idle;
      const msg = msgs[Math.floor(Math.random() * msgs.length)];
      const jitter = () => (Math.random()-0.5)*60;

      a.status = newStatus;
      a.detail = msg;
      a.targetX = zone.x + jitter();
      a.targetY = zone.y + jitter() + 40;
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
  cards.innerHTML = agents.map(a => `
    <button class="agent-card ${selectedAgentId===a.id?'selected':''}"
            style="--agent-color:${a.color}; ${selectedAgentId===a.id?`border-color:${a.color};background:${a.color}11`:''}"
            onclick="selectAgent('${a.id}')">
      <span class="agent-dot" style="background:${STATUS_COLORS[a.status]||'#6b7280'};
        box-shadow:0 0 6px ${STATUS_COLORS[a.status]||'#6b7280'}"></span>
      <span style="color:${a.color}">${a.name.split(' ')[1]}</span>
      <span style="color:#6b7280">${STATUS_ICONS[a.status]||''} ${a.status}</span>
    </button>
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
  const zone = ZONES[STATUS_TO_ZONE[status]];
  const msgs = ACTIVITIES[status] || ACTIVITIES.idle;
  const msg = msgs[Math.floor(Math.random() * msgs.length)];

  agents.forEach(a => {
    if (selectedAgentId && a.id !== selectedAgentId) return;
    const jitter = () => (Math.random()-0.5)*60;
    a.status = status;
    a.detail = msg;
    a.targetX = zone.x + jitter();
    a.targetY = zone.y + jitter() + 40;
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

/* ─── Init ─── */
(function init() {
  // Zone labels
  const labelsEl = document.getElementById("zone-labels");
  for (const [key, zone] of Object.entries(ZONES)) {
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
