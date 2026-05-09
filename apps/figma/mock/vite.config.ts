import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// Dev-only relay: mock POSTs the current log here; run_task.py GETs it.
function devLogRelayPlugin(): Plugin {
  type SessionLogRecord = {
    payload: string;
    postedAt: number;
    postCount: number;
    bytes: number;
  };

  // Bounded LRU cache of session logs keyed by sessionId so concurrent rollouts
  // can be retrieved deterministically by id.
  const MAX_SESSIONS = 4096;
  const logsBySession = new Map<string, SessionLogRecord>();

  let latestSessionId: string | null = null;
  let postCount = 0;
  let getCount = 0;
  let lastPostedAtGlobal: number | null = null;

  function touchSession(sessionId: string, record: SessionLogRecord): void {
    logsBySession.delete(sessionId);
    logsBySession.set(sessionId, record);
    while (logsBySession.size > MAX_SESSIONS) {
      const first = logsBySession.keys().next().value as string | undefined;
      if (!first) break;
      logsBySession.delete(first);
    }
  }

  function parseSessionId(payload: string): string | null {
    try {
      const parsed = JSON.parse(payload);
      const sessionId = (parsed as { sessionId?: unknown }).sessionId;
      return typeof sessionId === "string" ? sessionId : null;
    } catch {
      return null;
    }
  }

  return {
    name: "dev-log-relay",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use("/dev-log", (req, res) => {
        const requestUrl = new URL(req.url ?? "/", "http://dev-log.local");
        const pathname = requestUrl.pathname;
        const sessionIdParam = requestUrl.searchParams.get("sessionId");

        res.setHeader("Access-Control-Allow-Origin", "*");
        if (req.method === "GET" && pathname === "/status") {
          const selectedSessionId = sessionIdParam || latestSessionId;
          const selected = selectedSessionId ? logsBySession.get(selectedSessionId) ?? null : null;
          const body = JSON.stringify({
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
          res.writeHead(200, { "Content-Type": "application/json" }).end(body);
          return;
        }
        if (req.method === "POST" && pathname === "/") {
          const chunks: Buffer[] = [];
          req.on("data", (c: Buffer) => chunks.push(c));
          req.on("end", () => {
            const payload = Buffer.concat(chunks).toString();
            const sessionId = parseSessionId(payload);
            if (!sessionId) {
              res.writeHead(400).end("missing sessionId");
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
            res.writeHead(200).end("ok");
          });
        } else {
          getCount += 1;
          const targetSessionId = sessionIdParam || latestSessionId;
          if (!targetSessionId) {
            res.writeHead(404).end("no log yet — start a session first");
            return;
          }
          const record = logsBySession.get(targetSessionId);
          if (!record) {
            res.writeHead(404).end(`no log for sessionId=${targetSessionId}`);
          } else {
            // Touch on read to keep active rollout sessions resident longer.
            touchSession(targetSessionId, record);
            res.writeHead(200, { "Content-Type": "application/json" }).end(record.payload);
          }
        }
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), devLogRelayPlugin()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    strictPort: false,
  },
});
