/* ─── Agent Definitions (loaded from /team) ─── */
const SKIN_COLORS  = ["#fcd5b5", "#e8c4a0", "#f5d6b8", "#deb896", "#fde68a", "#c8a882", "#f0c8a0"];
const HAIR_COLORS  = ["#4a3728", "#1a1a2e", "#92400e", "#1e293b", "#78350f", "#2d1b69", "#374151"];
const PANTS_COLORS = ["#374151", "#1f2937", "#374151", "#1e293b", "#374151", "#1f2937", "#374151"];

const ACTIVITIES = {
  writing:     ["Drafting report...", "Editing document", "Writing summary", "Composing email"],
  coding:      ["Fixing bug #42", "Writing tests", "Code review", "Refactoring..."],
  researching: ["Reading papers", "Analyzing data", "Web search...", "Deep research"],
  thinking:    ["Brainstorming", "Processing...", "Evaluating...", "Reasoning..."],
  idle:        ["Coffee break!", "Stretching...", "Chatting", "Taking a break"],
  planning:    ["Roadmap review", "Sprint plan", "Architecture", "Diagramming"],
};

/* ─── Pathfinding ─── */
// Room boundaries
const ROOM_BOUNDS = {
  research: { x1: 10,  x2: 258 },
  dev:      { x1: 268, x2: 532 },
  meeting:  { x1: 542, x2: 790 },
};
const ROOM_DOOR_X  = { research: 134, dev: 400, meeting: 666 };
const ZONE_ROOM    = { desk1: "research", desk2: "dev", desk3: "dev", whiteboard: "meeting", breakroom: "breakroom" };
const DOOR_INNER_Y = 254;  // just inside room before door
const DOOR_OUTER_Y = 284;  // just in corridor after door
const CORRIDOR_Y   = 295;  // corridor centre
const BREAK_TOP_Y  = 330;  // top of break room

function getAgentRoom(x, y) {
  if (y >= 320) return "breakroom";
  if (y >= 270) return "corridor";
  if (x < 258)  return "research";
  if (x < 542)  return "dev";
  return "meeting";
}

function buildPath(fromX, fromY, zoneName) {
  const zone = ZONES[zoneName];
  if (!zone) return [];
  const fromRoom = getAgentRoom(fromX, fromY);
  const toRoom   = ZONE_ROOM[zoneName];
  if (fromRoom === toRoom) return [{ x: zone.x, y: zone.y }];

  const path = [];
  // ── exit current room ──
  if (fromRoom === "research" || fromRoom === "dev" || fromRoom === "meeting") {
    const dx = ROOM_DOOR_X[fromRoom];
    path.push({ x: dx, y: DOOR_INNER_Y });
    path.push({ x: dx, y: DOOR_OUTER_Y });
  } else if (fromRoom === "breakroom") {
    path.push({ x: fromX, y: BREAK_TOP_Y });
  }
  // ── navigate corridor then enter target ──
  if (toRoom === "breakroom") {
    path.push({ x: zone.x, y: CORRIDOR_Y });
    path.push({ x: zone.x, y: BREAK_TOP_Y });
  } else {
    const dx = ROOM_DOOR_X[toRoom];
    path.push({ x: dx, y: CORRIDOR_Y });
    path.push({ x: dx, y: DOOR_OUTER_Y });
    path.push({ x: dx, y: DOOR_INNER_Y });
  }
  path.push({ x: zone.x, y: zone.y });
  return path;
}

/* ─── Runtime Agent State ─── */
let agents = [];

async function loadAgentsFromServer() {
  try {
    const res = await fetch("/team");
    const teamConfig = await res.json();
    agents = Object.entries(teamConfig).map(([id, cfg], i) => ({
      id,
      name: cfg.name,
      role: cfg.role,
      color: cfg.color || "#9ca3af",
      skinColor:  SKIN_COLORS[i % SKIN_COLORS.length],
      hairColor:  HAIR_COLORS[i % HAIR_COLORS.length],
      shirtColor: cfg.color || "#9ca3af",
      pantsColor: PANTS_COLORS[i % PANTS_COLORS.length],
      x: 100 + i * Math.floor(700 / Math.max(Object.keys(teamConfig).length, 1)),
      y: 430,
      waypoints: [],
      status: "idle",
      detail: "",
      output: "",
      facing: "right",
      isWalking: false,
      bubbleText: "",
      bubbleTimer: 0,
    }));
  } catch (e) {
    console.warn("[agents] ไม่สามารถโหลด team config ได้:", e);
  }
}

let selectedAgentId = null;
let activityLogs = [];

/* ─── Pixel Character Drawing ─── */
const S = 2; // pixel scale

function drawRect(ctx, x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(Math.floor(x), Math.floor(y), w, h);
}

function drawPixelChar(ctx, agent, x, y, frame) {
  const bobY = Math.sin(frame * 0.15) * 1.5;
  const legFrame = agent.isWalking ? Math.floor(frame * 0.2) % 4 : 0;
  const facing = agent.facing;

  // Shadow
  ctx.fillStyle = "rgba(0,0,0,0.15)";
  ctx.beginPath();
  ctx.ellipse(x, y + 18 * S, 5 * S, 2 * S, 0, 0, Math.PI * 2);
  ctx.fill();

  // Legs
  const legOff = [[0,0],[-1,1],[0,0],[1,-1]];
  const [lO, rO] = [legOff[legFrame], legOff[(legFrame+2)%4]];
  drawRect(ctx, x-3*S, y+10*S+lO[0], 2*S, 8*S, agent.pantsColor);
  drawRect(ctx, x+1*S, y+10*S+rO[0], 2*S, 8*S, agent.pantsColor);
  drawRect(ctx, x-3*S, y+17*S+lO[0], 3*S, 2*S, "#1a1a2e");
  drawRect(ctx, x+1*S, y+17*S+rO[0], 3*S, 2*S, "#1a1a2e");

  // Body
  drawRect(ctx, x-4*S, y+2*S+bobY, 8*S, 9*S, agent.shirtColor);
  const armBob = agent.isWalking ? Math.sin(frame*0.2)*2 : 0;
  drawRect(ctx, x-6*S, y+3*S+bobY+armBob, 2*S, 6*S, agent.shirtColor);
  drawRect(ctx, x+4*S, y+3*S+bobY-armBob, 2*S, 6*S, agent.shirtColor);
  drawRect(ctx, x-6*S, y+8*S+bobY+armBob, 2*S, 2*S, agent.skinColor);
  drawRect(ctx, x+4*S, y+8*S+bobY-armBob, 2*S, 2*S, agent.skinColor);

  // Head
  drawRect(ctx, x-4*S, y-7*S+bobY, 8*S, 9*S, agent.skinColor);
  drawRect(ctx, x-4*S, y-8*S+bobY, 8*S, 4*S, agent.hairColor);
  if (facing === "left") {
    drawRect(ctx, x-5*S, y-7*S+bobY, 2*S, 6*S, agent.hairColor);
  } else {
    drawRect(ctx, x+4*S, y-7*S+bobY, 2*S, 6*S, agent.hairColor);
  }

  // Eyes
  const eX = facing === "left" ? -2 : 1;
  drawRect(ctx, x+(eX-1)*S, y-3*S+bobY, 1.5*S, 2*S, "#1a1a2e");
  drawRect(ctx, x+(eX+2)*S, y-3*S+bobY, 1.5*S, 2*S, "#1a1a2e");
  drawRect(ctx, x+(eX-0.5)*S, y-3*S+bobY, 0.8*S, 0.8*S, "#fff");
  drawRect(ctx, x+(eX+2.5)*S, y-3*S+bobY, 0.8*S, 0.8*S, "#fff");

  // Name
  ctx.fillStyle = agent.color;
  ctx.font = "bold 10px 'Press Start 2P', monospace";
  ctx.textAlign = "center";
  ctx.fillText(agent.name.split(" ")[1] || agent.name, x, y - 14*S + bobY);
}

function drawBubble(ctx, x, y, text, color) {
  const pad = 8;
  ctx.font = "9px 'Press Start 2P', monospace";
  const tw = ctx.measureText(text).width;
  const bw = tw + pad*2;
  const bh = 22;
  const bx = x - bw/2;
  const by = y - 50;

  ctx.fillStyle = "rgba(0,0,0,0.7)";
  ctx.beginPath(); ctx.roundRect(bx-1, by-1, bw+2, bh+2, 4); ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 3); ctx.fill();

  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.moveTo(x-4, by+bh); ctx.lineTo(x, by+bh+6); ctx.lineTo(x+4, by+bh);
  ctx.fill();

  ctx.fillStyle = color || "#1a1a2e";
  ctx.textAlign = "center";
  ctx.fillText(text, x, by + 15);
}

/* ─── Update Agent from Server ─── */
function applyServerState(serverState) {
  if (!serverState || !serverState.agents) return;

  for (const [agentId, data] of Object.entries(serverState.agents)) {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) continue;

    const oldStatus = agent.status;
    agent.status = data.status || "idle";
    agent.detail = data.detail || "";
    if (data.output !== undefined) agent.output = data.output;

    // ถ้าสถานะเปลี่ยน → เดินไปโซนใหม่
    if (oldStatus !== agent.status) {
      const zoneName = STATUS_TO_ZONE[agent.status] || "breakroom";
      const zone = ZONES[zoneName];
      if (zone) {
        const jitter = () => (Math.random() - 0.5) * 24;
        const path = buildPath(agent.x, agent.y, zoneName);
        if (path.length > 0) path[path.length - 1] = { x: zone.x + jitter(), y: zone.y + jitter() };
        agent.waypoints = path;
        agent.bubbleText = agent.detail || agent.status;
        agent.bubbleTimer = 180;
      }

      activityLogs.unshift({
        time: new Date(),
        agent: agent.name,
        color: agent.color,
        status: agent.status,
        detail: agent.detail,
      });
      if (activityLogs.length > 30) activityLogs.pop();
    }
  }
}
