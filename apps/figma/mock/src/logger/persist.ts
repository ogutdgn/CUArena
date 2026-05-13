// Mirrors the in-memory ring buffers + the current document snapshot to
// durable browser storage on a 250ms throttle. Three keys per session:
//   `${YYYY-MM-DD}_raw_${sessionId}_data`
//   `${YYYY-MM-DD}_semantic_${sessionId}_data`
//   `${YYYY-MM-DD}_outcome_${sessionId}_data`

import { logger } from "./buffer";
import type { RawEvent, SemanticEvent } from "@/types/events";
import { hydrateStoreFromSnapshot } from "@/engine/store";
import { buildOutcomeSnapshot } from "./outcome";
import { resolveSessionInfo } from "@/util/session";

const FLUSH_INTERVAL_MS = 250;
const LOG_KEY_TAIL = "_data";
const MAX_PERSIST_RAW_EVENTS = 1500;
const MAX_PERSIST_SEMANTIC_EVENTS = 3000;
type StreamName = "raw" | "semantic" | "outcome";

let installed = false;
let dirty = false;
let timer: ReturnType<typeof setTimeout> | null = null;
let restoredOnInstall = false;
let rawKey = "";
let semanticKey = "";
let outcomeKey = "";
let _sessionId = "";
let selectedStorage: Storage | null | undefined;

function ymd(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function resolveStorage(): Storage | null {
  if (selectedStorage !== undefined) return selectedStorage;
  if (typeof window === "undefined") {
    selectedStorage = null;
    return selectedStorage;
  }
  const probe = "__figma_mock_storage_probe";
  try {
    sessionStorage.setItem(probe, "1");
    sessionStorage.removeItem(probe);
    selectedStorage = sessionStorage;
    return selectedStorage;
  } catch {
    // fall through to localStorage
  }
  try {
    localStorage.setItem(probe, "1");
    localStorage.removeItem(probe);
    selectedStorage = localStorage;
    return selectedStorage;
  } catch {
    selectedStorage = null;
    return selectedStorage;
  }
}

function isPersistLogKey(key: string): boolean {
  return (
    key.endsWith(LOG_KEY_TAIL) &&
    (key.includes("_raw_") || key.includes("_semantic_") || key.includes("_outcome_"))
  );
}

function evictPersistLogKeys(st: Storage, protectedKeys: Set<string>, maxToRemove = 12): void {
  const candidates: string[] = [];
  try {
    for (let i = 0; i < st.length; i++) {
      const key = st.key(i);
      if (!key) continue;
      if (protectedKeys.has(key)) continue;
      if (!isPersistLogKey(key)) continue;
      candidates.push(key);
    }
  } catch {
    return;
  }
  candidates.sort(); // older YYYY-MM-DD prefixed keys first
  for (const key of candidates.slice(0, maxToRemove)) {
    try {
      st.removeItem(key);
    } catch {
      // best effort
    }
  }
}

function flush(): void {
  timer = null;
  if (!dirty) return;
  dirty = false;
  const raw = logger.rawEvents.toArray();
  const semantic = logger.semanticEvents.toArray();
  const rawForStorage =
    raw.length > MAX_PERSIST_RAW_EVENTS ? raw.slice(raw.length - MAX_PERSIST_RAW_EVENTS) : raw;
  const semanticForStorage =
    semantic.length > MAX_PERSIST_SEMANTIC_EVENTS
      ? semantic.slice(semantic.length - MAX_PERSIST_SEMANTIC_EVENTS)
      : semantic;
  const outcome = buildOutcomeSnapshot();
  const st = resolveStorage();
  if (st) {
    try {
      st.setItem(rawKey, JSON.stringify(rawForStorage));
      st.setItem(semanticKey, JSON.stringify(semanticForStorage));
      st.setItem(outcomeKey, JSON.stringify(outcome));
    } catch {
      // Quota exceeded: evict old persisted logs from other sessions and retry once.
      evictPersistLogKeys(st, new Set([rawKey, semanticKey, outcomeKey]));
      try {
        st.setItem(rawKey, JSON.stringify(rawForStorage));
        st.setItem(semanticKey, JSON.stringify(semanticForStorage));
        st.setItem(outcomeKey, JSON.stringify(outcome));
      } catch {
        // Storage still full/unavailable: keep running without local persistence.
      }
    }
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
  const st = resolveStorage();
  if (!st) return null;
  try {
    return st.getItem(key);
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
  const st = resolveStorage();
  if (!st) return null;
  const suffix = `_${stream}_${sessionId}${LOG_KEY_TAIL}`;
  let found: string | null = null;
  try {
    for (let i = 0; i < st.length; i++) {
      const k = st.key(i);
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

function tryRestore(candidates: string[]): boolean {
  for (const candidateId of candidates) {
    const candidateRawKey = findExistingKey("raw", candidateId);
    const candidateSemanticKey = findExistingKey("semantic", candidateId);
    const candidateOutcomeKey = findExistingKey("outcome", candidateId);
    const rawEvents = parseJsonArray<RawEvent>(
      candidateRawKey ? readStorageItem(candidateRawKey) : null,
    );
    const semanticEvents = parseJsonArray<SemanticEvent>(
      candidateSemanticKey ? readStorageItem(candidateSemanticKey) : null,
    );
    const hasStoredLogs = rawEvents != null || semanticEvents != null;
    if (hasStoredLogs) {
      logger.hydrate(rawEvents ?? [], semanticEvents ?? []);
    }

    const parsedOutcome = candidateOutcomeKey
      ? readRawOutcome(candidateOutcomeKey)
      : null;
    if (!parsedOutcome || parsedOutcome.sessionId !== candidateId) {
      if (hasStoredLogs) return true;
      continue;
    }
    const restored = hydrateStoreFromSnapshot({
      sessionId: _sessionId,
      activePageId: parsedOutcome.activePageId,
      document: parsedOutcome.document,
    });
    if (restored || hasStoredLogs) return true;
  }
  return false;
}

function onVisibilityChange(): void {
  if (document.visibilityState === "hidden") flushNow();
}

export function installPersist(): { restored: boolean; sessionId: string } {
  if (installed) return { restored: restoredOnInstall, sessionId: _sessionId };
  installed = true;

  const sessionInfo = resolveSessionInfo();
  _sessionId = sessionInfo.sessionId;
  const date = ymd(new Date());
  rawKey = findExistingKey("raw", _sessionId) ?? makeDefaultKey("raw", _sessionId, date);
  semanticKey = findExistingKey("semantic", _sessionId) ?? makeDefaultKey("semantic", _sessionId, date);
  outcomeKey = findExistingKey("outcome", _sessionId) ?? makeDefaultKey("outcome", _sessionId, date);

  const restoreCandidates = [_sessionId];
  if (
    sessionInfo.requestedSessionId &&
    !restoreCandidates.includes(sessionInfo.requestedSessionId)
  ) {
    // If this tab became a diverged session (session-1, session-2...), seed
    // from the requested base id before writing into the diverged stream.
    restoreCandidates.push(sessionInfo.requestedSessionId);
  }
  restoredOnInstall = tryRestore(restoreCandidates);

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
