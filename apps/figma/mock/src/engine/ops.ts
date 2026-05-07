// Op apply + inverse. Slice 0 implements the subset listed in ARCHITECTURE.md §9;
// other op kinds throw at apply time so the surface is explicit.
// Source: .analysis/engine-report.md §2.
//
// Designed to mutate Immer drafts — `state.nodesById` is a Record (not Map),
// `children` arrays mutate in place, etc.

import type {
  Op,
  CreateNodeOp,
  DeleteNodesOp,
  SetPropertyOp,
  SetTransformOp,
  SetSelectionOp,
  SetViewportOp,
  SetToolOp,
  SetEditModeOp,
  SetClipboardOp,
  ReparentOp,
  ReorderZOp,
  SetFocusContextOp,
  CreatePageOp,
  DeletePageOp,
  SwitchPageOp,
  MutateTextRunsOp,
  MutateVectorNetworkOp,
} from "@/types/ops";
import type { AppState } from "./store";
import type { Layer, Page } from "@/types/scene";
import { isContainer } from "@/types/scene";
import { worldOffsetOfParent } from "./coordinates";

function findNodeInLayers(layers: Layer[], id: string): Layer | null {
  for (const l of layers) {
    if (l.id === id) return l;
    if (isContainer(l)) {
      const hit = findNodeInLayers(l.children, id);
      if (hit) return hit;
    }
  }
  return null;
}

function findNodeInDocument(state: AppState, id: string): Layer | Page | null {
  for (const p of state.document.pages) {
    if (p.id === id) return p;
    const hit = findNodeInLayers(p.children, id);
    if (hit) return hit;
  }
  return null;
}

function reindexNodes(state: AppState): void {
  const next: Record<string, Layer | Page> = {};
  for (const p of state.document.pages) {
    next[p.id] = p;
    const stack = [...p.children];
    while (stack.length > 0) {
      const cur = stack.pop()!;
      next[cur.id] = cur;
      if (isContainer(cur)) {
        for (let i = cur.children.length - 1; i >= 0; i--) {
          stack.push(cur.children[i]);
        }
      }
    }
  }
  state.nodesById = next;
}

function getChildren(state: AppState, parentId: string): Layer[] | null {
  const node = findNodeInDocument(state, parentId);
  if (!node) return null;
  if ((node as Page).type === "page") return (node as Page).children;
  if (isContainer(node as Layer)) return (node as Layer & { children: Layer[] }).children;
  return null;
}

function indexById(arr: { id: string }[], id: string): number {
  return arr.findIndex((n) => n.id === id);
}

function walkUnindex(state: AppState, layer: Layer) {
  if (isContainer(layer)) {
    for (const c of layer.children) {
      delete state.nodesById[c.id];
      walkUnindex(state, c);
    }
  }
}

function walkIndex(state: AppState, layer: Layer) {
  state.nodesById[layer.id] = layer;
  if (isContainer(layer)) {
    for (const c of layer.children) walkIndex(state, c);
  }
}

function collectLayerIds(layer: Layer, out: Set<string>) {
  out.add(layer.id);
  if (isContainer(layer)) {
    for (const c of layer.children) collectLayerIds(c, out);
  }
}

function removeFromTree(state: AppState, id: string): {
  node: Layer;
  parentId: string;
  indexInParent: number;
} | null {
  const found = findNodeInDocument(state, id);
  if (!found || (found as Page).type === "page") return null;
  const layer = found as Layer;
  const children = getChildren(state, layer.parentId);
  if (!children) return null;
  const idx = indexById(children, id);
  if (idx === -1) return null;
  children.splice(idx, 1);
  delete state.nodesById[id];
  if (isContainer(layer)) walkUnindex(state, layer);
  return { node: layer, parentId: layer.parentId, indexInParent: idx };
}

function insertIntoTree(state: AppState, layer: Layer, parentId: string, index: number) {
  const children = getChildren(state, parentId);
  if (!children) throw new Error(`insertIntoTree: parent ${parentId} has no children`);
  const safeIndex = Math.max(0, Math.min(children.length, index));
  layer.parentId = parentId;
  children.splice(safeIndex, 0, layer);
  walkIndex(state, layer);
}

// ---- apply ----

export function applyCreateNode(state: AppState, op: CreateNodeOp): void {
  insertIntoTree(state, op.node, op.parentId, op.indexInParent);
}

export function applyDeleteNodes(state: AppState, op: DeleteNodesOp): void {
  const sorted = [...op.ids]
    .map((id) => {
      const n = findNodeInDocument(state, id);
      if (!n || (n as Page).type === "page") return null;
      const layer = n as Layer;
      const children = getChildren(state, layer.parentId);
      if (!children) return null;
      return { id, idx: indexById(children, id) };
    })
    .filter((v): v is { id: string; idx: number } => !!v)
    .sort((a, b) => b.idx - a.idx);

  const snapshot: Array<{ node: Layer; parentId: string; indexInParent: number }> = [];
  for (const { id } of sorted) {
    const removed = removeFromTree(state, id);
    if (removed) snapshot.unshift(removed);
  }
  op.snapshot = snapshot;

  // Clean stale selection/focus references if deleted ids were selected/focused.
  const removedIds = new Set<string>();
  for (const s of snapshot) collectLayerIds(s.node, removedIds);

  for (const pageId of Object.keys(state.selectionByPage)) {
    const sel = state.selectionByPage[pageId] ?? [];
    const next = sel.filter((id) => !removedIds.has(id));
    if (next.length !== sel.length) state.selectionByPage[pageId] = next;
  }
  for (const pageId of Object.keys(state.focusContextByPage)) {
    const fc = state.focusContextByPage[pageId];
    if (fc && removedIds.has(fc)) state.focusContextByPage[pageId] = null;
  }

  // Drop any prototype flows / connections that referenced deleted nodes, and
  // snapshot the original arrays so undo restores them. Without this the
  // exported `outcome.document` keeps stale flows / connections pointing at
  // ids that no longer exist (visible to verifiers and replay tooling).
  const protoSnap: NonNullable<DeleteNodesOp["prototypeSnapshot"]> = [];
  for (const page of state.document.pages) {
    let entry: { pageId: string; flowsBefore?: unknown[]; connectionsBefore?: unknown[] } | null = null;
    if (page.prototypeFlows && page.prototypeFlows.length > 0) {
      const filtered = page.prototypeFlows.filter((f) => !removedIds.has(f.frameId));
      if (filtered.length !== page.prototypeFlows.length) {
        entry = entry ?? { pageId: page.id };
        entry.flowsBefore = [...page.prototypeFlows];
        page.prototypeFlows = filtered;
      }
    }
    if (page.prototypeConnections && page.prototypeConnections.length > 0) {
      const filtered = page.prototypeConnections.filter(
        (c) =>
          !removedIds.has(c.sourceLayerId) &&
          !(c.destinationFrameId && removedIds.has(c.destinationFrameId)),
      );
      if (filtered.length !== page.prototypeConnections.length) {
        entry = entry ?? { pageId: page.id };
        entry.connectionsBefore = [...page.prototypeConnections];
        page.prototypeConnections = filtered;
      }
    }
    if (entry) protoSnap.push(entry);
  }
  if (protoSnap.length > 0) op.prototypeSnapshot = protoSnap;
}

export function applySetProperty(state: AppState, op: SetPropertyOp): void {
  for (const id of op.ids) {
    const node = findNodeInDocument(state, id);
    if (!node) continue;
    const after = op.after[id];
    if (after === undefined) continue;
    setByPath(node as unknown as Record<string, unknown>, op.path, after);
  }
}

function applyLayerTransform(
  layer: Layer,
  t: { x: number; y: number; w: number; h: number; rotation: number; scaleX: 1 | -1; scaleY: 1 | -1 },
): void {
  const prevW = Math.max(1, layer.w);
  const prevH = Math.max(1, layer.h);
  const nextW = Math.max(1, t.w);
  const nextH = Math.max(1, t.h);

  if (layer.type === "line" || layer.type === "arrow") {
    const sx = nextW / prevW;
    const sy = nextH / prevH;
    layer.p1 = { x: layer.p1.x * sx, y: layer.p1.y * sy };
    layer.p2 = { x: layer.p2.x * sx, y: layer.p2.y * sy };
  }
  if (layer.type === "vector") {
    const sx = nextW / prevW;
    const sy = nextH / prevH;
    layer.network = {
      ...layer.network,
      vertices: layer.network.vertices.map((v) => ({
        ...v,
        x: v.x * sx,
        y: v.y * sy,
      })),
      segments: layer.network.segments.map((seg) => ({
        ...seg,
        handleFrom: seg.handleFrom
          ? { dx: seg.handleFrom.dx * sx, dy: seg.handleFrom.dy * sy }
          : null,
        handleTo: seg.handleTo
          ? { dx: seg.handleTo.dx * sx, dy: seg.handleTo.dy * sy }
          : null,
      })),
    };
  }
  layer.x = t.x;
  layer.y = t.y;
  layer.w = nextW;
  layer.h = nextH;
  layer.rotation = t.rotation;
  layer.scaleX = t.scaleX;
  layer.scaleY = t.scaleY;
}

function applyConstrainedAxis(
  pos: number,
  size: number,
  prevSize: number,
  nextSize: number,
  mode: "left" | "right" | "center" | "stretch" | "scale" | "top" | "bottom",
): { pos: number; size: number } {
  const safePrev = Math.max(1, prevSize);
  const rightOrBottom = safePrev - (pos + size);
  switch (mode) {
    case "left":
    case "top":
      return { pos, size };
    case "right":
    case "bottom":
      return { pos: nextSize - rightOrBottom - size, size };
    case "center": {
      const centerOffset = pos + size / 2 - safePrev / 2;
      return { pos: nextSize / 2 + centerOffset - size / 2, size };
    }
    case "stretch": {
      const stretched = Math.max(1, nextSize - pos - rightOrBottom);
      return { pos, size: stretched };
    }
    case "scale": {
      const f = nextSize / safePrev;
      return { pos: pos * f, size: Math.max(1, size * f) };
    }
    default:
      return { pos, size };
  }
}

function reflowFrameChildren(
  frame: Extract<Layer, { type: "frame" }>,
  prevW: number,
  prevH: number,
): void {
  const nextW = Math.max(1, frame.w);
  const nextH = Math.max(1, frame.h);
  for (const child of frame.children) {
    const h = applyConstrainedAxis(
      child.x,
      child.w,
      prevW,
      nextW,
      child.constraints.horizontal,
    );
    const v = applyConstrainedAxis(
      child.y,
      child.h,
      prevH,
      nextH,
      child.constraints.vertical,
    );

    const childPrevW = Math.max(1, child.w);
    const childPrevH = Math.max(1, child.h);
    applyLayerTransform(child, {
      x: h.pos,
      y: v.pos,
      w: h.size,
      h: v.size,
      rotation: child.rotation,
      scaleX: child.scaleX,
      scaleY: child.scaleY,
    });
    if (child.type === "frame") {
      const childNextW = Math.max(1, child.w);
      const childNextH = Math.max(1, child.h);
      if (childPrevW !== childNextW || childPrevH !== childNextH) {
        reflowFrameChildren(child, childPrevW, childPrevH);
      }
    }
  }
}

export function applySetTransform(state: AppState, op: SetTransformOp): void {
  for (const id of op.ids) {
    const node = findNodeInDocument(state, id);
    if (!node || (node as Page).type === "page") continue;
    const t = op.after[id];
    if (!t) continue;
    const layer = node as Layer;
    const prevW = Math.max(1, layer.w);
    const prevH = Math.max(1, layer.h);
    applyLayerTransform(layer, t);
    if (layer.type === "frame") {
      const nextW = Math.max(1, layer.w);
      const nextH = Math.max(1, layer.h);
      if (prevW !== nextW || prevH !== nextH) {
        reflowFrameChildren(layer, prevW, prevH);
      }
    }
  }
}

export function applySetSelection(state: AppState, op: SetSelectionOp): void {
  state.selectionByPage[op.pageId] = [...op.after];
}

export function applySetViewport(state: AppState, op: SetViewportOp): void {
  state.viewportByPage[op.pageId] = { ...op.after };
}

export function applySetTool(state: AppState, op: SetToolOp): void {
  state.activeTool = op.after;
}

export function applySetEditMode(state: AppState, op: SetEditModeOp): void {
  state.editMode = { ...op.after };
}

export function applySetClipboard(state: AppState, op: SetClipboardOp): void {
  state.clipboard = op.after ? { ...op.after } : null;
}

export function applyReparent(state: AppState, op: ReparentOp): void {
  // Apply moves in order. For each, remove from current parent, insert into
  // new — and re-express x/y from the OLD parent's coordinate space into the
  // NEW parent's coordinate space so the layer's world position is preserved.
  // Without this, grouping/ungrouping or any cross-parent reparent visually
  // shifts layers (and corrupts geometry that verifiers read from
  // `outcome.document`).
  for (const m of op.moves) {
    const layer = findNodeInDocument(state, m.id) as Layer | undefined;
    if (!layer || (layer as unknown as Page).type === "page") continue;
    const fromArr = getChildren(state, m.fromParentId);
    if (!fromArr) continue;
    const idx = fromArr.findIndex((c) => c.id === m.id);
    if (idx === -1) continue;

    const oldOffset = worldOffsetOfParent(state, m.fromParentId);
    const worldX = layer.x + oldOffset.x;
    const worldY = layer.y + oldOffset.y;

    fromArr.splice(idx, 1);
    insertIntoTree(state, layer, m.toParentId, m.toIndex);

    const newOffset = worldOffsetOfParent(state, m.toParentId);
    layer.x = worldX - newOffset.x;
    layer.y = worldY - newOffset.y;
  }
}

export function applyReorderZ(state: AppState, op: ReorderZOp): void {
  const arr = getChildren(state, op.parentId);
  if (!arr) return;
  // Pull out the listed ids preserving their relative order.
  const items = op.ids
    .map((id) => arr.find((c) => c.id === id))
    .filter((c): c is Layer => !!c);
  for (const it of items) {
    const i = arr.indexOf(it);
    if (i !== -1) arr.splice(i, 1);
  }
  const target = Math.max(0, Math.min(arr.length, op.toIndex));
  arr.splice(target, 0, ...items);
}

export function applySetFocusContext(state: AppState, op: SetFocusContextOp): void {
  state.focusContextByPage[op.pageId] = op.after;
}

export function applyCreatePage(state: AppState, op: CreatePageOp): void {
  const safe = Math.max(0, Math.min(state.document.pages.length, op.pageIndex));
  state.document.pages.splice(safe, 0, op.page);
  state.nodesById[op.page.id] = op.page;
  for (const c of op.page.children) {
    state.nodesById[c.id] = c;
    if (c.type === "frame" || c.type === "section" || c.type === "group") {
      walkIndex(state, c);
    }
  }
  if (!state.viewportByPage[op.page.id]) state.viewportByPage[op.page.id] = { x: 0, y: 0, zoom: 1 };
  if (!state.selectionByPage[op.page.id]) state.selectionByPage[op.page.id] = [];
  if (!(op.page.id in state.focusContextByPage)) state.focusContextByPage[op.page.id] = null;
}

export function applyDeletePage(state: AppState, op: DeletePageOp): void {
  if (state.document.pages.length <= 1) return; // last page protected
  const idx = state.document.pages.findIndex((p) => p.id === op.pageId);
  if (idx === -1) return;
  const page = state.document.pages[idx];
  state.document.pages.splice(idx, 1);
  // Unindex nodes
  delete state.nodesById[page.id];
  for (const c of page.children) {
    delete state.nodesById[c.id];
    if (c.type === "frame" || c.type === "section" || c.type === "group") walkUnindex(state, c);
  }
  delete state.viewportByPage[page.id];
  delete state.selectionByPage[page.id];
  delete state.focusContextByPage[page.id];
  if (state.activePageId === op.pageId) {
    const fallback = state.document.pages[Math.max(0, idx - 1)] ?? state.document.pages[0];
    state.activePageId = fallback.id;
  }
}

export function applySwitchPage(state: AppState, op: SwitchPageOp): void {
  state.activePageId = op.after.pageId;
}

export function applyMutateTextRuns(state: AppState, op: MutateTextRunsOp): void {
  const node = findNodeInDocument(state, op.layerId);
  if (!node) return;
  const t = node as unknown as Record<string, unknown>;
  t.content = op.after.content;
  t.runs = op.after.runs;
  t.fontFamily = op.after.fontFamily;
  t.fontWeight = op.after.fontWeight;
  t.fontSize = op.after.fontSize;
}

export function applyMutateVectorNetwork(state: AppState, op: MutateVectorNetworkOp): void {
  const node = findNodeInDocument(state, op.layerId);
  if (!node) return;
  (node as unknown as Record<string, unknown>).network = op.after;
}

// ---- inverse ----

export function applyInverse(state: AppState, op: Op): void {
  switch (op.kind) {
    case "create_node":
      applyDeleteNodes(state, {
        id: op.id + ":inv",
        timestamp: Date.now(),
        kind: "delete_nodes",
        pageId: op.pageId,
        ids: [op.node.id],
      });
      break;
    case "delete_nodes":
      if (op.snapshot) {
        for (const s of op.snapshot) {
          insertIntoTree(state, s.node, s.parentId, s.indexInParent);
        }
      }
      if (op.prototypeSnapshot) {
        for (const entry of op.prototypeSnapshot) {
          const page = state.document.pages.find((p) => p.id === entry.pageId);
          if (!page) continue;
          if (entry.flowsBefore !== undefined) {
            page.prototypeFlows = entry.flowsBefore as typeof page.prototypeFlows;
          }
          if (entry.connectionsBefore !== undefined) {
            page.prototypeConnections = entry.connectionsBefore as typeof page.prototypeConnections;
          }
        }
      }
      break;
    case "set_property":
      for (const id of op.ids) {
        const node = state.nodesById[id];
        if (!node) continue;
        const before = op.before[id];
        if (before === undefined) continue;
        setByPath(node as unknown as Record<string, unknown>, op.path, before);
      }
      break;
    case "set_transform":
      applySetTransform(state, {
        ...op,
        after: op.before,
        before: op.after,
      });
      break;
    case "set_selection":
      state.selectionByPage[op.pageId] = [...op.before];
      break;
    case "set_viewport":
      state.viewportByPage[op.pageId] = { ...op.before };
      break;
    case "set_tool":
      state.activeTool = op.before;
      break;
    case "set_edit_mode":
      state.editMode = { ...op.before };
      break;
    case "set_clipboard":
      state.clipboard = op.before ? { ...op.before } : null;
      break;
    case "reparent": {
      // Reverse each move
      const reverse: ReparentOp = {
        ...op,
        moves: [...op.moves].reverse().map((m) => ({
          id: m.id,
          fromParentId: m.toParentId,
          fromIndex: m.toIndex,
          toParentId: m.fromParentId,
          toIndex: m.fromIndex,
        })),
      };
      applyReparent(state, reverse);
      break;
    }
    case "reorder_z": {
      // Restore original positions one at a time.
      const arr = getChildren(state, op.parentId);
      if (!arr) break;
      const items = op.ids
        .map((id) => arr.find((c) => c.id === id))
        .filter((c): c is Layer => !!c);
      for (const it of items) {
        const i = arr.indexOf(it);
        if (i !== -1) arr.splice(i, 1);
      }
      // Re-insert each at its before index, smallest first, respecting shifts.
      const restore = items
        .map((it, i) => ({ it, idx: op.before[i] }))
        .sort((a, b) => a.idx - b.idx);
      for (const { it, idx } of restore) {
        const target = Math.max(0, Math.min(arr.length, idx));
        arr.splice(target, 0, it);
      }
      break;
    }
    case "set_focus_context":
      state.focusContextByPage[op.pageId] = op.before;
      break;
    case "create_page":
      applyDeletePage(state, {
        id: op.id + ":inv",
        timestamp: Date.now(),
        kind: "delete_page",
        pageId: op.page.id,
        before: { pageIndex: op.pageIndex, page: op.page, wasActive: false, fallbackPageId: null },
      });
      break;
    case "delete_page":
      applyCreatePage(state, {
        id: op.id + ":inv",
        timestamp: Date.now(),
        kind: "create_page",
        pageIndex: op.before.pageIndex,
        page: op.before.page,
      });
      if (op.before.wasActive) state.activePageId = op.before.page.id;
      break;
    case "switch_page":
      state.activePageId = op.before.pageId;
      break;
    case "mutate_text_runs":
      applyMutateTextRuns(state, { ...op, before: op.after, after: op.before });
      break;
    case "mutate_vector_network":
      applyMutateVectorNetwork(state, { ...op, before: op.after, after: op.before });
      break;
    default: {
      // Slice-deferred ops (scale_uniform, mutate_text_runs, mutate_vector_network)
      // — no inverse implementation yet.
      void op;
      break;
    }
  }
  reindexNodes(state);
}

// ---- apply dispatch ----

export function applyOp(state: AppState, op: Op): void {
  switch (op.kind) {
    case "create_node":
      applyCreateNode(state, op);
      break;
    case "delete_nodes":
      applyDeleteNodes(state, op);
      break;
    case "set_property":
      applySetProperty(state, op);
      break;
    case "set_transform":
      applySetTransform(state, op);
      break;
    case "set_selection":
      applySetSelection(state, op);
      break;
    case "set_viewport":
      applySetViewport(state, op);
      break;
    case "set_tool":
      applySetTool(state, op);
      break;
    case "set_edit_mode":
      applySetEditMode(state, op);
      break;
    case "set_clipboard":
      applySetClipboard(state, op);
      break;
    case "reparent":
      applyReparent(state, op);
      break;
    case "reorder_z":
      applyReorderZ(state, op);
      break;
    case "set_focus_context":
      applySetFocusContext(state, op);
      break;
    case "create_page":
      applyCreatePage(state, op);
      break;
    case "delete_page":
      applyDeletePage(state, op);
      break;
    case "switch_page":
      applySwitchPage(state, op);
      break;
    case "mutate_text_runs":
      applyMutateTextRuns(state, op);
      break;
    case "mutate_vector_network":
      applyMutateVectorNetwork(state, op);
      break;
    default: {
      // Op union is exhaustively covered above; this branch is unreachable in
      // well-typed code. Throwing a non-typed error keeps it surfaced if a new
      // op kind is added without an apply handler.
      const u = op as { kind?: string };
      throw new Error(`applyOp: unimplemented op kind "${u.kind ?? "unknown"}"`);
    }
  }
  reindexNodes(state);
}

// ---- path helpers ----

function setByPath(target: Record<string, unknown>, path: string, value: unknown): void {
  if (path === "") return;
  const parts = path.split("/");
  let cur: Record<string, unknown> = target;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = parts[i];
    const next = cur[k];
    if (next == null || typeof next !== "object") return;
    cur = next as Record<string, unknown>;
  }
  cur[parts[parts.length - 1]] = value;
}

export function getByPath(target: Record<string, unknown>, path: string): unknown {
  if (path === "") return target;
  const parts = path.split("/");
  let cur: unknown = target;
  for (const k of parts) {
    if (cur == null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[k];
  }
  return cur;
}
