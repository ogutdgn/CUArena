import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
// Dev-only relay: mock POSTs the current log here; run_task.py GETs it.
function devLogRelayPlugin() {
    // Bounded LRU cache of session logs keyed by sessionId so concurrent rollouts
    // can be retrieved deterministically by id.
    var MAX_SESSIONS = 4096;
    var logsBySession = new Map();
    var latestSessionId = null;
    var postCount = 0;
    var getCount = 0;
    var lastPostedAtGlobal = null;
    function touchSession(sessionId, record) {
        logsBySession.delete(sessionId);
        logsBySession.set(sessionId, record);
        while (logsBySession.size > MAX_SESSIONS) {
            var first = logsBySession.keys().next().value;
            if (!first)
                break;
            logsBySession.delete(first);
        }
    }
    function parseSessionId(payload) {
        try {
            var parsed = JSON.parse(payload);
            var sessionId = parsed.sessionId;
            return typeof sessionId === "string" ? sessionId : null;
        }
        catch (_a) {
            return null;
        }
    }
    return {
        name: "dev-log-relay",
        apply: "serve",
        configureServer: function (server) {
            server.middlewares.use("/dev-log", function (req, res) {
                var _a, _b, _c, _d;
                var requestUrl = new URL((_a = req.url) !== null && _a !== void 0 ? _a : "/", "http://dev-log.local");
                var pathname = requestUrl.pathname;
                var sessionIdParam = requestUrl.searchParams.get("sessionId");
                res.setHeader("Access-Control-Allow-Origin", "*");
                if (req.method === "GET" && pathname === "/status") {
                    var selectedSessionId = sessionIdParam || latestSessionId;
                    var selected = selectedSessionId ? (_b = logsBySession.get(selectedSessionId)) !== null && _b !== void 0 ? _b : null : null;
                    var body = JSON.stringify({
                        hasLog: !!selected,
                        requestedSessionId: sessionIdParam,
                        selectedSessionId: selectedSessionId,
                        sessionCount: logsBySession.size,
                        postCount: postCount,
                        getCount: getCount,
                        lastPostedAt: (_c = selected === null || selected === void 0 ? void 0 : selected.postedAt) !== null && _c !== void 0 ? _c : null,
                        lastPostedAtGlobal: lastPostedAtGlobal,
                        lastSessionId: latestSessionId,
                        sessionPostCount: (_d = selected === null || selected === void 0 ? void 0 : selected.postCount) !== null && _d !== void 0 ? _d : 0,
                    });
                    res.writeHead(200, { "Content-Type": "application/json" }).end(body);
                    return;
                }
                if (req.method === "POST" && pathname === "/") {
                    var chunks_1 = [];
                    req.on("data", function (c) { return chunks_1.push(c); });
                    req.on("end", function () {
                        var _a;
                        var payload = Buffer.concat(chunks_1).toString();
                        var sessionId = parseSessionId(payload);
                        if (!sessionId) {
                            res.writeHead(400).end("missing sessionId");
                            return;
                        }
                        var now = Date.now();
                        var prev = logsBySession.get(sessionId);
                        touchSession(sessionId, {
                            payload: payload,
                            postedAt: now,
                            postCount: ((_a = prev === null || prev === void 0 ? void 0 : prev.postCount) !== null && _a !== void 0 ? _a : 0) + 1,
                            bytes: payload.length,
                        });
                        latestSessionId = sessionId;
                        postCount += 1;
                        lastPostedAtGlobal = now;
                        res.writeHead(200).end("ok");
                    });
                }
                else {
                    getCount += 1;
                    var targetSessionId = sessionIdParam || latestSessionId;
                    if (!targetSessionId) {
                        res.writeHead(404).end("no log yet — start a session first");
                        return;
                    }
                    var record = logsBySession.get(targetSessionId);
                    if (!record) {
                        res.writeHead(404).end("no log for sessionId=".concat(targetSessionId));
                    }
                    else {
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
