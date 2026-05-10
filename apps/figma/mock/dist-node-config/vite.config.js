import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
// Dev-only relay: mock POSTs the current log here; run_task.py GETs it.
function devLogRelayPlugin() {
    var latestLog = null;
    return {
        name: "dev-log-relay",
        apply: "serve",
        configureServer: function (server) {
            server.middlewares.use("/dev-log", function (req, res) {
                res.setHeader("Access-Control-Allow-Origin", "*");
                if (req.method === "POST") {
                    var chunks_1 = [];
                    req.on("data", function (c) { return chunks_1.push(c); });
                    req.on("end", function () {
                        latestLog = Buffer.concat(chunks_1).toString();
                        res.writeHead(200).end("ok");
                    });
                }
                else {
                    if (!latestLog) {
                        res.writeHead(404).end("no log yet — start a session first");
                    }
                    else {
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
