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
  if (!focusId) return pageId;
  const node = state.nodesById[focusId];
  if (!node || (node as Page).type === "page") return pageId;
  const layer = node as Layer;
  if (layer.type !== "frame" && layer.type !== "section" && layer.type !== "group") return pageId;
  const wr = worldRectOfLayer(state, layer);
  if (world.x >= wr.x && world.x <= wr.x + wr.w && world.y >= wr.y && world.y <= wr.y + wr.h) {
    return focusId;
  }
  return pageId;
}
