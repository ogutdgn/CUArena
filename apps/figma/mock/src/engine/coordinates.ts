import type { AppState } from "./store";
import type { Layer, Page } from "@/types/scene";

export interface XY {
  x: number;
  y: number;
}

export interface RectLike extends XY {
  w: number;
  h: number;
}

function asLayer(node: Layer | Page | undefined): Layer | null {
  if (!node) return null;
  if ((node as Page).type === "page") return null;
  return node as Layer;
}

export function getNodeById(state: AppState, id: string): Layer | Page | undefined {
  return state.nodesById[id];
}

export function getParentNode(state: AppState, layer: Layer): Layer | Page | null {
  return state.nodesById[layer.parentId] ?? null;
}

export function worldOffsetOfParent(state: AppState, parentId: string): XY {
  const parent = state.nodesById[parentId];
  if (!parent || (parent as Page).type === "page") {
    return { x: 0, y: 0 };
  }
  return worldOffsetOfLayer(state, parent as Layer);
}

export function worldOffsetOfLayer(state: AppState, layer: Layer): XY {
  let x = layer.x;
  let y = layer.y;
  let cur: Layer | null = layer;
  while (cur) {
    const parent = getParentNode(state, cur);
    const pLayer = asLayer(parent ?? undefined);
    if (!pLayer) break;
    x += pLayer.x;
    y += pLayer.y;
    cur = pLayer;
  }
  return { x, y };
}

export function worldRectOfLayer(state: AppState, layer: Layer): RectLike {
  const p = worldOffsetOfLayer(state, layer);
  return { x: p.x, y: p.y, w: layer.w, h: layer.h };
}

export function worldToParentLocal(state: AppState, parentId: string, world: XY): XY {
  const p = worldOffsetOfParent(state, parentId);
  return { x: world.x - p.x, y: world.y - p.y };
}

export function worldRectToParentLocal(state: AppState, parentId: string, rect: RectLike): RectLike {
  const p = worldOffsetOfParent(state, parentId);
  return { x: rect.x - p.x, y: rect.y - p.y, w: rect.w, h: rect.h };
}

export function localToWorld(state: AppState, parentId: string, local: XY): XY {
  const p = worldOffsetOfParent(state, parentId);
  return { x: local.x + p.x, y: local.y + p.y };
}

export function resolveCreationParentId(state: AppState, world: XY): string {
  const pageId = state.activePageId;
  const focusId = state.focusContextByPage[pageId] ?? null;
  // 1) If a focus context is set and the cursor is inside it, parent there.
  if (focusId) {
    const node = state.nodesById[focusId];
    if (node && (node as Page).type !== "page") {
      const layer = node as Layer;
      if (layer.type === "frame" || layer.type === "section" || layer.type === "group") {
        const wr = worldRectOfLayer(state, layer);
        if (world.x >= wr.x && world.x <= wr.x + wr.w && world.y >= wr.y && world.y <= wr.y + wr.h) {
          return focusId;
        }
      }
    }
  }
  // 2) Otherwise auto-parent into the deepest visible/unlocked container under
  // the cursor. Fixes #12: drawing inside an unfocused frame previously fell
  // through to the page and required a follow-up drag-into-frame.
  const page = state.document.pages.find((p) => p.id === pageId);
  if (page) {
    const deep = deepestContainerAt(page.children, world, 0, 0);
    if (deep) return deep;
  }
  return pageId;
}

// Walks the layer tree top-down (z-order, last-in-array wins) and returns the
// id of the deepest visible/unlocked frame|section|group that contains the
// world point. Locked or hidden containers are skipped.
function deepestContainerAt(layers: Layer[], world: XY, ox: number, oy: number): string | null {
  for (let i = layers.length - 1; i >= 0; i--) {
    const l = layers[i];
    if (l.locked || !l.visible) continue;
    if (l.type !== "frame" && l.type !== "section" && l.type !== "group") continue;
    const wx = ox + l.x;
    const wy = oy + l.y;
    const inside =
      world.x >= wx && world.x <= wx + l.w && world.y >= wy && world.y <= wy + l.h;
    if (!inside) continue;
    const deeper = deepestContainerAt(l.children, world, wx, wy);
    if (deeper) return deeper;
    return l.id;
  }
  return null;
}
