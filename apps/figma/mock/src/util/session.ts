import { createSessionId, randomUuidV4 } from "@/util/id";

const INSTANCE_ID_KEY = "__figma_mock_instance_id";
const LEASE_PREFIX = "__figma_mock_lease_";
const DIVERGE_COUNTER_PREFIX = "__figma_mock_diverge_counter_";
const LEASE_TTL_MS = 12_000;
const LEASE_HEARTBEAT_MS = 4_000;
const ID_PATTERN = /^[A-Za-z0-9._:-]{3,128}$/;

type LeaseRecord = { instanceId: string; updatedAt: number };

let heartbeat: ReturnType<typeof setInterval> | null = null;
let resolved: ResolvedSessionInfo | null = null;

export interface ResolvedSessionInfo {
  sessionId: string;
  requestedSessionId: string | null;
  isDiverged: boolean;
}

function storage(): Storage | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage;
  } catch {
    return null;
  }
}

function readLease(key: string, st: Storage): LeaseRecord | null {
  const raw = st.getItem(key);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as { instanceId?: unknown; updatedAt?: unknown };
    if (typeof parsed.instanceId !== "string" || typeof parsed.updatedAt !== "number") return null;
    return { instanceId: parsed.instanceId, updatedAt: parsed.updatedAt };
  } catch {
    return null;
  }
}

function writeLease(key: string, st: Storage, instanceId: string): void {
  const lease: LeaseRecord = { instanceId, updatedAt: Date.now() };
  st.setItem(key, JSON.stringify(lease));
}

function isLeaseAlive(lease: LeaseRecord | null): boolean {
  if (!lease) return false;
  return Date.now() - lease.updatedAt <= LEASE_TTL_MS;
}

function getOrCreateInstanceId(): string {
  try {
    const existing = sessionStorage.getItem(INSTANCE_ID_KEY);
    if (existing) return existing;
    const fresh = `instance_${randomUuidV4()}`;
    sessionStorage.setItem(INSTANCE_ID_KEY, fresh);
    return fresh;
  } catch {
    return `instance_${randomUuidV4()}`;
  }
}

function sanitizeSessionId(id: string | null): string | null {
  if (!id) return null;
  const clean = decodeURIComponent(id).trim();
  if (!ID_PATTERN.test(clean)) return null;
  return clean;
}

function parsePathSessionId(pathname: string): string | null {
  const m = pathname.match(/\/id=([^/?#]+)/i);
  if (!m) return null;
  return sanitizeSessionId(m[1]);
}

export function parseRequestedSessionId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const url = new URL(window.location.href);
    const fromQuery = sanitizeSessionId(url.searchParams.get("id"));
    if (fromQuery) return fromQuery;
    const fromPath = parsePathSessionId(url.pathname);
    if (fromPath) return fromPath;
  } catch {
    return null;
  }
  return null;
}

function startLeaseHeartbeat(st: Storage, leaseKey: string, instanceId: string): void {
  const touch = () => {
    const current = readLease(leaseKey, st);
    if (current && current.instanceId !== instanceId && isLeaseAlive(current)) {
      // Another tab has taken this lease; stop touching this one.
      if (heartbeat) {
        clearInterval(heartbeat);
        heartbeat = null;
      }
      return;
    }
    writeLease(leaseKey, st, instanceId);
  };

  touch();
  if (heartbeat) clearInterval(heartbeat);
  heartbeat = setInterval(touch, LEASE_HEARTBEAT_MS);

  const release = () => {
    try {
      const current = readLease(leaseKey, st);
      if (current?.instanceId === instanceId) st.removeItem(leaseKey);
    } catch {
      // best-effort only
    }
  };
  window.addEventListener("beforeunload", release);
  window.addEventListener("pagehide", release);
}

function allocateDivergedId(st: Storage, baseId: string): string {
  const key = `${DIVERGE_COUNTER_PREFIX}${baseId}`;
  let n = 0;
  try {
    n = Number.parseInt(st.getItem(key) ?? "0", 10);
    if (!Number.isFinite(n) || n < 0) n = 0;
  } catch {
    n = 0;
  }
  n += 1;
  try {
    st.setItem(key, String(n));
  } catch {
    // fallback below if write fails
  }
  return `${baseId}-${n}`;
}

export function resolveSessionInfo(): ResolvedSessionInfo {
  if (resolved) return resolved;
  const requested = parseRequestedSessionId();
  const st = storage();
  if (!requested || !st) {
    resolved = {
      sessionId: createSessionId(),
      requestedSessionId: requested,
      isDiverged: false,
    };
    return resolved;
  }

  const instanceId = getOrCreateInstanceId();
  const primaryLeaseKey = `${LEASE_PREFIX}${requested}`;
  const existing = readLease(primaryLeaseKey, st);
  if (!isLeaseAlive(existing) || existing?.instanceId === instanceId) {
    startLeaseHeartbeat(st, primaryLeaseKey, instanceId);
    resolved = {
      sessionId: requested,
      requestedSessionId: requested,
      isDiverged: false,
    };
    return resolved;
  }

  const diverged = allocateDivergedId(st, requested);
  const divergedLeaseKey = `${LEASE_PREFIX}${diverged}`;
  startLeaseHeartbeat(st, divergedLeaseKey, instanceId);
  resolved = {
    sessionId: diverged,
    requestedSessionId: requested,
    isDiverged: true,
  };
  return resolved;
}
