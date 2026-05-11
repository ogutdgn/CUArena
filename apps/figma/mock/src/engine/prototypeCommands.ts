// Prototype-document commands. Wrap each prototype-related document mutation
// in a `set_property` op + a specific semantic event, so prototype edits go
// through the same dispatch / undo / log pipeline as every other mutation.
//
// All mutations write whole arrays (prototypeConnections) or whole objects
// (prototypeSettings) so undo restores the exact prior state without
// depending on element-level paths.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import type {
  Page,
  PrototypeAction,
  PrototypeAnimation,
  PrototypeConnection,
  PrototypeSettings,
  PrototypeTrigger,
} from "@/types/scene";

const DEFAULT_SETTINGS: PrototypeSettings = {
  device: null,
  backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 },
};

function findPage(pageId: string): Page | null {
  return useStore.getState().document.pages.find((p) => p.id === pageId) ?? null;
}

function dispatchPageProperty(
  pageId: string,
  path: string,
  beforeValue: unknown,
  afterValue: unknown,
  opts: { skipUndo?: boolean } = {},
): void {
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_property",
      pageId,
      ids: [pageId],
      path,
      before: { [pageId]: beforeValue },
      after: { [pageId]: afterValue },
    },
    opts,
  );
}

// ─── prototype settings ───────────────────────────────────────────────

export function setPrototypeDevice(pageId: string, device: string | null): void {
  const page = findPage(pageId);
  if (!page) return;
  const beforeSettings: PrototypeSettings = page.prototypeSettings ?? DEFAULT_SETTINGS;
  if (beforeSettings.device === device) return;
  const afterSettings: PrototypeSettings = { ...beforeSettings, device };
  dispatchPageProperty(pageId, "prototypeSettings", beforeSettings, afterSettings);
  emitSemantic({ name: "set_prototype_device", before: beforeSettings.device, after: device });
}

// ─── connections ──────────────────────────────────────────────────────

export function createPrototypeConnection(
  pageId: string,
  conn: PrototypeConnection,
): void {
  const page = findPage(pageId);
  if (!page) return;
  const before: PrototypeConnection[] = [...(page.prototypeConnections ?? [])];
  const after: PrototypeConnection[] = [...before, conn];
  dispatchPageProperty(pageId, "prototypeConnections", before, after);
  emitSemantic({
    name: "create_prototype_connection",
    connectionId: conn.id,
    sourceLayerId: conn.sourceLayerId,
    trigger: conn.trigger,
    action: conn.action,
  });
}

export function updatePrototypeConnection(
  pageId: string,
  connId: string,
  patch: Partial<Omit<PrototypeConnection, "id" | "sourceLayerId">>,
): void {
  const page = findPage(pageId);
  if (!page) return;
  const before: PrototypeConnection[] = [...(page.prototypeConnections ?? [])];
  const target = before.find((c) => c.id === connId);
  if (!target) return;
  const updated: PrototypeConnection = { ...target, ...patch };

  // Diff the relevant fields first. If nothing actually changed, do not
  // dispatch — otherwise the no-op set_property would consume an undo slot
  // and swallow the user's previous real edit.
  type Field = "trigger" | "action" | "destinationFrameId" | "animation" | "delayMs" | "url";
  const fields: Field[] = ["trigger", "action", "destinationFrameId", "animation", "delayMs", "url"];
  const changedFields: Field[] = [];
  for (const f of fields) {
    const a = (target as unknown as Record<string, unknown>)[f];
    const b = (updated as unknown as Record<string, unknown>)[f];
    if (a !== b) changedFields.push(f);
  }
  if (changedFields.length === 0) return;

  const after: PrototypeConnection[] = before.map((c) => (c.id === connId ? updated : c));
  dispatchPageProperty(pageId, "prototypeConnections", before, after);

  for (const f of changedFields) {
    const a = (target as unknown as Record<string, unknown>)[f];
    const b = (updated as unknown as Record<string, unknown>)[f];
    emitSemantic({
      name: "update_prototype_connection",
      connectionId: connId,
      field: f,
      before: a == null ? null : String(a),
      after: b == null ? null : String(b),
    });
  }
}

export function deletePrototypeConnection(pageId: string, connId: string): void {
  const page = findPage(pageId);
  if (!page) return;
  const before: PrototypeConnection[] = [...(page.prototypeConnections ?? [])];
  const removed = before.find((c) => c.id === connId);
  if (!removed) return;
  const after: PrototypeConnection[] = before.filter((c) => c.id !== connId);
  dispatchPageProperty(pageId, "prototypeConnections", before, after);
  emitSemantic({
    name: "delete_prototype_connection",
    connectionId: connId,
    sourceLayerId: removed.sourceLayerId,
  });
}

// Re-export type aliases used by callers (avoids unused-imports lint).
export type {
  PrototypeAction,
  PrototypeAnimation,
  PrototypeConnection,
  PrototypeSettings,
  PrototypeTrigger,
};
