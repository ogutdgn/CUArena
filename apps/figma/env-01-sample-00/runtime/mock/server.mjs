import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import http from "node:http";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, "dist");
const tasksDir = process.env.TASKS_DIR
  ? path.resolve(process.env.TASKS_DIR)
  : path.resolve(__dirname, "..", "..");
const devLogDir = process.env.DEVLOG_DIR
  ? path.resolve(process.env.DEVLOG_DIR)
  : path.resolve(__dirname, "dev-logs");
const port = Number(process.env.PORT || 5173);

const MAX_SESSIONS = 4096;
const logsBySession = new Map();
let latestSessionId = null;
let postCount = 0;
let getCount = 0;
let lastPostedAtGlobal = null;

try {
  fs.mkdirSync(devLogDir, { recursive: true });
} catch {}

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".map": "application/json; charset=utf-8",
};

function touchSession(sessionId, record) {
  logsBySession.delete(sessionId);
  logsBySession.set(sessionId, record);
  while (logsBySession.size > MAX_SESSIONS) {
    const first = logsBySession.keys().next().value;
    if (!first) break;
    logsBySession.delete(first);
  }
}

function parseSessionId(payload) {
  try {
    const parsed = JSON.parse(payload);
    return typeof parsed.sessionId === "string" ? parsed.sessionId : null;
  } catch {
    return null;
  }
}

function sendJson(res, status, bodyObj) {
  const body = JSON.stringify(bodyObj);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Access-Control-Allow-Origin": "*",
  });
  res.end(body);
}

function sendText(res, status, text) {
  res.writeHead(status, {
    "Content-Type": "text/plain; charset=utf-8",
    "Content-Length": Buffer.byteLength(text),
    "Access-Control-Allow-Origin": "*",
  });
  res.end(text);
}

function handleDevLog(req, res, urlObj) {
  const sessionIdParam = urlObj.searchParams.get("sessionId");
  const pathname = urlObj.pathname;

  if (req.method === "GET" && pathname === "/dev-log/status") {
    const selectedSessionId = sessionIdParam || latestSessionId;
    const selected = selectedSessionId ? logsBySession.get(selectedSessionId) ?? null : null;
    sendJson(res, 200, {
      hasLog: !!selected,
      requestedSessionId: sessionIdParam,
      selectedSessionId,
      sessionCount: logsBySession.size,
      postCount,
      getCount,
      lastPostedAt: selected?.postedAt ?? null,
      lastPostedAtGlobal,
      lastSessionId: latestSessionId,
      sessionPostCount: selected?.postCount ?? 0,
    });
    return true;
  }

  if (req.method === "POST" && pathname === "/dev-log") {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      const payload = Buffer.concat(chunks).toString("utf-8");
      const sessionId = parseSessionId(payload);
      if (!sessionId) {
        sendText(res, 400, "missing sessionId");
        return;
      }
      const now = Date.now();
      const prev = logsBySession.get(sessionId);
      touchSession(sessionId, {
        payload,
        postedAt: now,
        postCount: (prev?.postCount ?? 0) + 1,
        bytes: payload.length,
      });
      latestSessionId = sessionId;
      postCount += 1;
      lastPostedAtGlobal = now;
      try {
        fs.writeFileSync(path.join(devLogDir, `${sessionId}.json`), payload, "utf-8");
      } catch {}
      sendText(res, 200, "ok");
    });
    return true;
  }

  if (req.method === "GET" && pathname === "/dev-log") {
    getCount += 1;
    const targetSessionId = sessionIdParam || latestSessionId;
    if (!targetSessionId) {
      sendText(res, 404, "no log yet — start a session first");
      return true;
    }
    const record = logsBySession.get(targetSessionId);
    if (!record) {
      sendText(res, 404, `no log for sessionId=${targetSessionId}`);
      return true;
    }
    touchSession(targetSessionId, record);
    res.writeHead(200, {
      "Content-Type": "application/json; charset=utf-8",
      "Content-Length": Buffer.byteLength(record.payload),
      "Access-Control-Allow-Origin": "*",
    });
    res.end(record.payload);
    return true;
  }

  return false;
}

function handlePrompt(req, res, urlObj) {
  if (req.method !== "GET") return false;
  const m = urlObj.pathname.match(/^\/task\/(task_\d{2})\/prompt$/i);
  if (!m) return false;
  const taskId = m[1].toLowerCase();
  const promptPath = path.join(tasksDir, taskId, "prompt.md");
  if (!promptPath.startsWith(tasksDir) || !fs.existsSync(promptPath)) {
    sendText(res, 404, `prompt not found for ${taskId}`);
    return true;
  }
  const body = fs.readFileSync(promptPath, "utf-8");
  res.writeHead(200, {
    "Content-Type": "text/markdown; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Access-Control-Allow-Origin": "*",
  });
  res.end(body);
  return true;
}

function handleFixture(req, res, urlObj) {
  if (req.method !== "GET") return false;
  const m = urlObj.pathname.match(/^\/task\/(task_\d{2})\/fixture$/i);
  if (!m) return false;
  const taskId = m[1].toLowerCase();
  const fixturePath = path.join(tasksDir, taskId, "fixture.json");
  if (!fixturePath.startsWith(tasksDir) || !fs.existsSync(fixturePath)) {
    sendText(res, 404, `fixture not found for ${taskId}`);
    return true;
  }
  const body = fs.readFileSync(fixturePath, "utf-8");
  res.writeHead(200, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Access-Control-Allow-Origin": "*",
  });
  res.end(body);
  return true;
}

function handleTaskBootstrap(req, res, urlObj) {
  if (req.method !== "GET" || urlObj.pathname !== "/task-bootstrap.js") return false;
  const body = `(() => {
  try {
    const params = new URLSearchParams(window.location.search);
    const task = params.get("task");
    if (!task) return;
    const normalized = /^task_\\d{2}$/i.test(task)
      ? task.toLowerCase()
      : /^\\d+$/.test(task)
        ? \`task_\${task.padStart(2, "0")}\`
        : null;
    if (!normalized) return;
    fetch(\`/task/\${normalized}/fixture\`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((fixture) => {
        if (!fixture) return;
        let tries = 0;
        const maxTries = 50;
        const timer = setInterval(() => {
          tries += 1;
          if (typeof window.__loadFixture === "function") {
            try { window.__loadFixture(fixture); } catch {}
            clearInterval(timer);
            return;
          }
          if (tries >= maxTries) clearInterval(timer);
        }, 100);
      })
      .catch(() => {});
  } catch {}
})();`;
  res.writeHead(200, {
    "Content-Type": "text/javascript; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Access-Control-Allow-Origin": "*",
  });
  res.end(body);
  return true;
}

function serveStatic(req, res, urlObj) {
  let pathname = decodeURIComponent(urlObj.pathname);
  if (pathname === "/") pathname = "/index.html";

  let filePath = path.join(distDir, pathname);
  if (!filePath.startsWith(distDir)) {
    sendText(res, 403, "forbidden");
    return;
  }
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, "index.html");
  }
  if (!fs.existsSync(filePath)) {
    filePath = path.join(distDir, "index.html");
  }
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME[ext] || "application/octet-stream";

  fs.readFile(filePath, (err, data) => {
    if (err) {
      sendText(res, 500, "server error");
      return;
    }
    if (filePath.endsWith("index.html")) {
      let html = data.toString("utf-8");
      if (!html.includes("/task-bootstrap.js")) {
        html = html.replace("</head>", '  <script src="/task-bootstrap.js"></script>\n</head>');
      }
      const out = Buffer.from(html, "utf-8");
      res.writeHead(200, {
        "Content-Type": contentType,
        "Content-Length": out.length,
      });
      res.end(out);
      return;
    }
    res.writeHead(200, {
      "Content-Type": contentType,
      "Content-Length": data.length,
    });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  if (!req.url) {
    sendText(res, 400, "bad request");
    return;
  }
  const urlObj = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (urlObj.pathname.startsWith("/dev-log")) {
    const handled = handleDevLog(req, res, urlObj);
    if (!handled) sendText(res, 405, "method not allowed");
    return;
  }
  if (urlObj.pathname === "/task-bootstrap.js") {
    const handled = handleTaskBootstrap(req, res, urlObj);
    if (handled) return;
  }
  if (urlObj.pathname.startsWith("/task/")) {
    const handled = handlePrompt(req, res, urlObj) || handleFixture(req, res, urlObj);
    if (handled) return;
  }
  serveStatic(req, res, urlObj);
});

server.listen(port, "0.0.0.0", () => {
  console.log(`[mock-runtime] listening on 0.0.0.0:${port}`);
});
