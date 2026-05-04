import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// Dev-only relay: test-app POSTs the current log here; export_log.py GETs it.
function devLogRelayPlugin(): Plugin {
  let latestLog: string | null = null;
  return {
    name: "dev-log-relay",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use("/dev-log", (req, res) => {
        res.setHeader("Access-Control-Allow-Origin", "*");
        if (req.method === "POST") {
          const chunks: Buffer[] = [];
          req.on("data", (c: Buffer) => chunks.push(c));
          req.on("end", () => {
            latestLog = Buffer.concat(chunks).toString();
            res.writeHead(200).end("ok");
          });
        } else {
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
