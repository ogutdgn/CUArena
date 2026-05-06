// Mirrors the in-memory ring buffers + the current document snapshot to
// sessionStorage on a 250ms throttle. Three keys per session:
//   `${YYYY-MM-DD}_raw_${sessionId}_data`
//   `${YYYY-MM-DD}_semantic_${sessionId}_data`
//   `${YYYY-MM-DD}_outcome_${sessionId}_data`

import { logger } from "./buffer";
import { useStore } from "@/engine/store";
import { buildOutcomeSnapshot } from "./outcome";

const FLUSH_INTERVAL_MS = 250;
const LOG_STREAM_MARKERS = ["_raw_", "_semantic_", "_outcome_"] as const;
const LOG_KEY_TAIL = "_data";

let installed = false;
let dirty = false;
let timer: ReturnType<typeof setTimeout> | null = null;
let rawKey = "";
let semanticKey = "";
let outcomeKey = "";
let _sessionId = "";

function ymd(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function flush(): void {
  timer = null;
  if (!dirty) return;
  dirty = false;
  const raw = logger.rawEvents.toArray();
  const semantic = logger.semanticEvents.toArray();
  const outcome = buildOutcomeSnapshot();
  try {
    sessionStorage.setItem(rawKey, JSON.stringify(raw));
    sessionStorage.setItem(semanticKey, JSON.stringify(semantic));
    sessionStorage.setItem(outcomeKey, JSON.stringify(outcome));
  } catch {
    // Quota exceeded or storage unavailable: drop this flush silently.
  }
  if (import.meta.env.DEV) {
    const body = JSON.stringify({
      schemaVersion: 1,
      sessionId: _sessionId,
      exportedAt: Date.now(),
      raw,
      semantic,
      outcome,
    });
    fetch("/dev-log", { method: "POST", body, headers: { "Content-Type": "application/json" } }).catch(() => {});
  }
}

function schedule(): void {
  dirty = true;
  if (timer != null) return;
  timer = setTimeout(flush, FLUSH_INTERVAL_MS);
}

function flushNow(): void {
  if (timer != null) {
    clearTimeout(timer);
    timer = null;
  }
  dirty = true;
  flush();
}

// sessionStorage survives a page refresh, but `sessionId` regenerates on every
// reload — without this sweep, each refresh leaves the previous run's keys
// behind and accumulates one pair per refresh until the tab closes.
function clearPreviousLogs(): void {
  try {
    const keysToRemove: string[] = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i);
      if (
        k &&
        k.endsWith(LOG_KEY_TAIL) &&
        LOG_STREAM_MARKERS.some((marker) => k.includes(marker))
      ) {
        keysToRemove.push(k);
      }
    }
    for (const k of keysToRemove) sessionStorage.removeItem(k);
  } catch {
    // ignore
  }
}

export function installPersist(): void {
  if (installed) return;
  installed = true;

  clearPreviousLogs();

  _sessionId = useStore.getState().sessionId;
  const date = ymd(new Date());
  rawKey = `${date}_raw_${_sessionId}_data`;
  semanticKey = `${date}_semantic_${_sessionId}_data`;
  outcomeKey = `${date}_outcome_${_sessionId}_data`;

  // Seed each key so they exist immediately. Outcome gets the initial document
  // state, raw + semantic start as empty arrays.
  try {
    sessionStorage.setItem(rawKey, "[]");
    sessionStorage.setItem(semanticKey, "[]");
    sessionStorage.setItem(outcomeKey, JSON.stringify(buildOutcomeSnapshot()));
  } catch {
    // ignore
  }

  logger.subscribe(schedule);
  window.addEventListener("beforeunload", flushNow);
}
