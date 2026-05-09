// Mirrors the in-memory ring buffers + the current document snapshot to
// sessionStorage on a 250ms throttle. Three keys per session:
//   `${YYYY-MM-DD}_raw_${sessionId}_data`
//   `${YYYY-MM-DD}_semantic_${sessionId}_data`
//   `${YYYY-MM-DD}_outcome_${sessionId}_data`

import { logger } from "./buffer";
import type { RawEvent, SemanticEvent } from "@/types/events";
import { hydrateStoreFromSnapshot, useStore } from "@/engine/store";
import { buildOutcomeSnapshot } from "./outcome";

const FLUSH_INTERVAL_MS = 250;
const LOG_KEY_TAIL = "_data";
type StreamName = "raw" | "semantic" | "outcome";

let installed = false;
let dirty = false;
let timer: ReturnType<typeof setTimeout> | null = null;
let restoredOnInstall = false;
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

function parseJsonArray<T>(raw: string | null): T[] | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as T[]) : null;
  } catch {
    return null;
  }
}

function readStorageItem(key: string): string | null {
  try {
    return sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function readRawOutcome(seedKey: string): {
  sessionId: string;
  activePageId?: string;
  document: unknown;
} | null {
  try {
    const raw = readStorageItem(seedKey);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as {
      sessionId?: unknown;
      activePageId?: unknown;
      document?: unknown;
    };
    if (typeof parsed.sessionId !== "string") return null;
    if (parsed.activePageId != null && typeof parsed.activePageId !== "string") return null;
    if (typeof parsed.document !== "object" || parsed.document === null) return null;
    return {
      sessionId: parsed.sessionId,
      activePageId: parsed.activePageId as string | undefined,
      document: parsed.document,
    };
  } catch {
    return null;
  }
}

function findExistingKey(stream: StreamName, sessionId: string): string | null {
  const suffix = `_${stream}_${sessionId}${LOG_KEY_TAIL}`;
  let found: string | null = null;
  try {
    for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i);
      if (!k || !k.endsWith(suffix)) continue;
      if (!found || k > found) found = k;
    }
  } catch {
    return null;
  }
  return found;
}

function makeDefaultKey(stream: StreamName, sessionId: string, date: string): string {
  return `${date}_${stream}_${sessionId}${LOG_KEY_TAIL}`;
}

function tryRestore(): boolean {
  const rawEvents = parseJsonArray<RawEvent>(readStorageItem(rawKey));
  const semanticEvents = parseJsonArray<SemanticEvent>(readStorageItem(semanticKey));
  const hasStoredLogs = rawEvents != null || semanticEvents != null;
  if (hasStoredLogs) {
    logger.hydrate(rawEvents ?? [], semanticEvents ?? []);
  }

  const parsedOutcome = readRawOutcome(outcomeKey);
  if (!parsedOutcome || parsedOutcome.sessionId !== _sessionId) {
    return hasStoredLogs;
  }
  const restored = hydrateStoreFromSnapshot({
    sessionId: parsedOutcome.sessionId,
    activePageId: parsedOutcome.activePageId,
    document: parsedOutcome.document,
  });
  return restored || hasStoredLogs;
}

function onVisibilityChange(): void {
  if (document.visibilityState === "hidden") flushNow();
}

export function installPersist(): { restored: boolean; sessionId: string } {
  if (installed) return { restored: restoredOnInstall, sessionId: _sessionId };
  installed = true;

  _sessionId = useStore.getState().sessionId;
  const date = ymd(new Date());
  rawKey = findExistingKey("raw", _sessionId) ?? makeDefaultKey("raw", _sessionId, date);
  semanticKey = findExistingKey("semantic", _sessionId) ?? makeDefaultKey("semantic", _sessionId, date);
  outcomeKey = findExistingKey("outcome", _sessionId) ?? makeDefaultKey("outcome", _sessionId, date);

  restoredOnInstall = tryRestore();

  logger.subscribe(schedule);
  window.addEventListener("beforeunload", flushNow);
  window.addEventListener("pagehide", flushNow);
  document.addEventListener("visibilitychange", onVisibilityChange);

  // Ensure both storage and /dev-log relay have a payload even before the next
  // interaction, so verifier fetches can still resolve after a refresh.
  dirty = true;
  flush();

  return { restored: restoredOnInstall, sessionId: _sessionId };
}
