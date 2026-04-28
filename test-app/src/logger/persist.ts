// Mirrors the in-memory ring buffers to sessionStorage on a 250ms throttle.
// Keys: `${YYYY-MM-DD}_${sessionId}_raw_data` and `${YYYY-MM-DD}_${sessionId}_semantic_data`.

import { logger } from "./buffer";
import { useStore } from "@/engine/store";

const FLUSH_INTERVAL_MS = 250;

let installed = false;
let dirty = false;
let timer: ReturnType<typeof setTimeout> | null = null;
let rawKey = "";
let semanticKey = "";

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
  try {
    sessionStorage.setItem(rawKey, JSON.stringify(logger.rawEvents.toArray()));
    sessionStorage.setItem(semanticKey, JSON.stringify(logger.semanticEvents.toArray()));
  } catch {
    // Quota exceeded or storage unavailable: drop this flush silently.
    // Ring-buffer caps keep the next attempt the same size, so it'll keep failing
    // — that's the deliberate behaviour for "storage full".
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

export function installPersist(): void {
  if (installed) return;
  installed = true;

  const sessionId = useStore.getState().sessionId;
  const date = ymd(new Date());
  rawKey = `${date}_${sessionId}_raw_data`;
  semanticKey = `${date}_${sessionId}_semantic_data`;

  // Seed empty arrays so the keys exist immediately.
  try {
    sessionStorage.setItem(rawKey, "[]");
    sessionStorage.setItem(semanticKey, "[]");
  } catch {
    // ignore
  }

  logger.subscribe(schedule);
  window.addEventListener("beforeunload", flushNow);
}
