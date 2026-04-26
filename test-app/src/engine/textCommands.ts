// Text creation + edit + commit. Slice 5: simple plain content (no per-run
// formatting). Coalescing window is the entire edit session (open → blur).

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { setSelection } from "./commands";
import { uid } from "@/util/id";
import type { Text as TextLayer, Page, Layer } from "@/types/scene";
import { resolveCreationParentId, worldToParentLocal } from "./coordinates";

interface TextSnapshot {
  content: string;
  runs: unknown[];
  fontFamily: string;
  fontWeight: number;
  fontSize: number;
}

export function createTextAt(world: { x: number; y: number }, mode: "auto_width" | "fixed", widthHint?: number, heightHint?: number): string | null {
  const s = useStore.getState();
  const pageId = s.activePageId;
  const parentId = resolveCreationParentId(s, world);
  const local = worldToParentLocal(s, parentId, world);
  const pageParent = s.document.pages.find((p) => p.id === parentId);
  const indexedParent = s.nodesById[parentId];
  const childCount = pageParent
    ? pageParent.children.length
    : indexedParent && "children" in indexedParent && Array.isArray((indexedParent as { children?: unknown[] }).children)
    ? ((indexedParent as { children: unknown[] }).children).length
    : 0;
  const w = mode === "fixed" ? widthHint ?? 200 : 100;
  const h = mode === "fixed" ? heightHint ?? 24 : 24;
  const layer: TextLayer = {
    id: uid("text"),
    type: "text",
    name: "Text",
    parentId,
    x: local.x,
    y: local.y,
    w,
    h,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
    content: "",
    runs: [],
    fontFamily: "Inter",
    fontWeight: 400,
    fontSize: 16,
    lineHeight: { type: "auto" },
    letterSpacing: { type: "px", value: 0 },
    hAlign: "left",
    vAlign: "top",
    fills: [{ kind: "solid", color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    resizingMode: mode,
  };

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "create_node",
    pageId,
    parentId,
    indexInParent: childCount,
    node: layer,
  });
  setSelection([layer.id], "implicit_after_create");
  emitSemantic({
    name: "create_text",
    layerId: layer.id,
    x: layer.x,
    y: layer.y,
    w: layer.w,
    h: layer.h,
    parentId,
    resizingMode: mode,
    trigger: "shortcut_T",
  });
  enterTextEdit(layer.id);
  return layer.id;
}

export function enterTextEdit(layerId: string): void {
  const before = useStore.getState().editMode;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_edit_mode",
    before,
    after: { kind: "text", layerId },
  });
  emitSemantic({ name: "mode_change", before: before.kind, after: "text" });
}

export function exitTextEdit(): void {
  const before = useStore.getState().editMode;
  if (before.kind !== "text") return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_edit_mode",
    before,
    after: { kind: "none" },
  });
  emitSemantic({ name: "mode_change", before: "text", after: "none" });
}

export function commitText(layerId: string, snapshot: TextSnapshot, after: TextSnapshot): void {
  const s = useStore.getState();
  // If content didn't change since open, don't push undo entry.
  const same =
    snapshot.content === after.content &&
    snapshot.fontFamily === after.fontFamily &&
    snapshot.fontWeight === after.fontWeight &&
    snapshot.fontSize === after.fontSize;
  if (!same) {
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "mutate_text_runs",
      pageId: s.activePageId,
      layerId,
      before: snapshot,
      after,
    });
  }
  // If content is empty, delete the layer.
  if (after.content.trim() === "") {
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "delete_nodes",
      pageId: s.activePageId,
      ids: [layerId],
    });
  }
  exitTextEdit();
  emitSemantic({ name: "commit_text", layerId, content: after.content });
}

export function setTextProperty(field: "fontFamily" | "fontSize" | "fontWeight" | "hAlign", value: unknown): void {
  const s = useStore.getState();
  const ids = s.selectionByPage[s.activePageId] ?? [];
  const layers = ids
    .map((id) => s.nodesById[id])
    .filter((n): n is Layer => !!n && (n as Page).type !== "page" && (n as Layer).type === "text") as Layer[];
  if (layers.length === 0) return;
  const before: Record<string, unknown> = {};
  const after: Record<string, unknown> = {};
  for (const l of layers) {
    before[l.id] = (l as unknown as Record<string, unknown>)[field];
    after[l.id] = value;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    path: field,
    before,
    after,
  });
  emitSemantic({
    name: "set_property",
    layerIds: layers.map((l) => l.id),
    path: field,
    before,
    after,
    trigger: "panel_input",
  });
}

export function snapshotText(layerId: string): TextSnapshot | null {
  const s = useStore.getState();
  const node = s.nodesById[layerId];
  if (!node) return null;
  const t = node as TextLayer;
  if (t.type !== "text") return null;
  return {
    content: t.content,
    runs: t.runs,
    fontFamily: t.fontFamily,
    fontWeight: t.fontWeight,
    fontSize: t.fontSize,
  };
}
