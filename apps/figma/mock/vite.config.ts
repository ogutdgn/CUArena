import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// Dev-only relay: mock POSTs the current log here; run_task.py GETs it.
function devLogRelayPlugin(): Plugin {
  let latestLog: string | null = null;
  let postCount = 0;
  let getCount = 0;
  let lastPostedAt: number | null = null;
  let lastSessionId: string | null = null;

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
        res.setHeader("Access-Control-Allow-Origin", "*");
        if (req.method === "GET" && (req.url === "/status" || req.url?.startsWith("/status?"))) {
          const body = JSON.stringify({
            hasLog: !!latestLog,
            postCount,
            getCount,
            lastPostedAt,
            lastSessionId,
          });
          res.writeHead(200, { "Content-Type": "application/json" }).end(body);
          return;
        }
        if (req.method === "POST") {
          const chunks: Buffer[] = [];
          req.on("data", (c: Buffer) => chunks.push(c));
          req.on("end", () => {
            latestLog = Buffer.concat(chunks).toString();
            postCount += 1;
            lastPostedAt = Date.now();
            lastSessionId = parseSessionId(latestLog);
            res.writeHead(200).end("ok");
          });
        } else {
          getCount += 1;
          if (!latestLog) {
            res.writeHead(404).end("no log yet — start a session first");
          } else {
            res.writeHead(200, { "Content-Type": "application/json" }).end(latestLog);
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
