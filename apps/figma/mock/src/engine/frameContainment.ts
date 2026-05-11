import type { Layer, Page } from "@/types/scene";
import type { ReparentOp } from "@/types/ops";
import { applyReparent } from "./ops";
import { getActivePage } from "./selectors";
import type { AppState } from "./store";
import { worldAABBOfLayer } from "./coordinates";

const FRAME_NEST_ENTER_RATIO = 0.6;
const FRAME_NEST_EXIT_RATIO = 0.4;

export interface FrameContainmentFrame {
  id: string;
  rect: { x: number; y: number; w: number; h: number };
}

export function collectFrameContainmentFrames(
  state: AppState,
  movingIds: Set<string>,
): FrameContainmentFrame[] {
  const page = getActivePage(state);
  if (!page) return [];
  const frames: FrameContainmentFrame[] = [];
  const collect = (layers: Layer[]) => {
    for (const layer of layers) {
      if (movingIds.has(layer.id)) continue;
      if (!layer.visible) continue;
      if (layer.type === "frame") {
        frames.push({ id: layer.id, rect: worldAABBOfLayer(state, layer) });
      }
      if (layer.type === "frame" || layer.type === "section" || layer.type === "group") {
        collect(layer.children);
      }
    }
  };
  collect(page.children);
  return frames;
}

export function applyFrameContainmentForLayers(
  state: AppState,
  layerIds: string[],
  options: { frames?: FrameContainmentFrame[]; exitRatio?: number } = {},
): void {
  const movedSet = new Set(layerIds);
  const frames = options.frames ?? collectFrameContainmentFrames(state, movedSet);
  for (const id of rootMovedLayerIds(state, layerIds, movedSet)) {
    const move = getFrameContainmentMove(state, id, movedSet, frames, options.exitRatio ?? FRAME_NEST_EXIT_RATIO);
    if (!move) continue;
    applyReparent(state, {
      id: `frame-containment-${id}`,
      timestamp: 0,
      kind: "reparent",
      pageId: state.activePageId,
      moves: [move],
    });
  }
}

export function getFrameContainmentMoves(
  state: AppState,
  layerIds: string[],
  options: { frames?: FrameContainmentFrame[]; exitRatio?: number } = {},
): ReparentOp["moves"] {
  const movedSet = new Set(layerIds);
  const frames = options.frames ?? collectFrameContainmentFrames(state, movedSet);
  const exitRatio = options.exitRatio ?? FRAME_NEST_EXIT_RATIO;
  return rootMovedLayerIds(state, layerIds, movedSet)
    .map((id) => getFrameContainmentMove(state, id, movedSet, frames, exitRatio))
    .filter((move): move is ReparentOp["moves"][number] => move !== null);
}

function getFrameContainmentMove(
  state: AppState,
  id: string,
  movedSet: Set<string>,
  frames: FrameContainmentFrame[],
  exitRatio: number,
): { id: string; fromParentId: string; fromIndex: number; toParentId: string; toIndex: number } | null {
  const layer = state.nodesById[id] as Layer | undefined;
  if (!layer || (layer as unknown as Page).type === "page") return null;

  const wr = worldAABBOfLayer(state, layer);
  const area = Math.max(1, wr.w * wr.h);

  const currentParent = state.nodesById[layer.parentId] as Layer | Page | undefined;
  const currentFrameParent =
    currentParent &&
    (currentParent as Page).type !== "page" &&
    (currentParent as Layer).type === "frame"
      ? (currentParent as Layer)
      : null;
  const currentOverlap =
    currentFrameParent != null
      ? overlapRatio(wr, worldAABBOfLayer(state, currentFrameParent), area)
      : 0;

  let bestFrameId: string | null = null;
  let bestDepth = -1;
  let bestRatio = 0;

  for (const frame of frames) {
    if (frame.id === id) continue;
    if (isAncestor(state, id, frame.id)) continue;
    if (movedSet.has(frame.id)) continue;

    const ratio = overlapRatio(wr, frame.rect, area);
    if (ratio < FRAME_NEST_ENTER_RATIO) continue;
    const depth = depthOf(state, frame.id);
    if (depth > bestDepth || (depth === bestDepth && ratio > bestRatio)) {
      bestDepth = depth;
      bestRatio = ratio;
      bestFrameId = frame.id;
    }
  }

  let toParentId = layer.parentId;
  if (bestFrameId) {
    toParentId = bestFrameId;
  } else if (currentFrameParent && currentOverlap < exitRatio) {
    toParentId = currentFrameParent.parentId;
  }
  if (toParentId === layer.parentId) return null;

  const fromArr = childrenOf(state, layer.parentId);
  const toArr = childrenOf(state, toParentId);
  if (!fromArr || !toArr) return null;
  const fromIndex = fromArr.findIndex((c) => c.id === id);
  if (fromIndex < 0) return null;

  let toIndex = toArr.length;
  if (currentFrameParent && toParentId === currentFrameParent.parentId) {
    const frameIndex = toArr.findIndex((c) => c.id === currentFrameParent.id);
    if (frameIndex >= 0) toIndex = frameIndex + 1;
  }

  return { id, fromParentId: layer.parentId, fromIndex, toParentId, toIndex };
}

function rootMovedLayerIds(state: AppState, layerIds: string[], movedSet: Set<string>): string[] {
  return layerIds.filter((id) => {
    let cur = state.nodesById[id] as Layer | undefined;
    while (cur && (cur as unknown as Page).type !== "page") {
      const parent = state.nodesById[cur.parentId] as Layer | Page | undefined;
      if (!parent || (parent as Page).type === "page") break;
      if (movedSet.has((parent as Layer).id)) return false;
      cur = parent as Layer;
    }
    return true;
  });
}

function childrenOf(state: AppState, parentId: string): Layer[] | null {
  const p = state.nodesById[parentId] as Layer | Page | undefined;
  if (!p) return null;
  if ((p as Page).type === "page") return (p as Page).children;
  if ("children" in (p as object)) {
    return ((p as Layer & { children?: Layer[] }).children ?? null);
  }
  return null;
}

function overlapRatio(
  a: { x: number; y: number; w: number; h: number },
  b: { x: number; y: number; w: number; h: number },
  aArea: number,
): number {
  const x1 = Math.max(a.x, b.x);
  const y1 = Math.max(a.y, b.y);
  const x2 = Math.min(a.x + a.w, b.x + b.w);
  const y2 = Math.min(a.y + a.h, b.y + b.h);
  const w = Math.max(0, x2 - x1);
  const h = Math.max(0, y2 - y1);
  return (w * h) / Math.max(1, aArea);
}

function depthOf(state: AppState, id: string): number {
  let d = 0;
  let cur = state.nodesById[id] as Layer | Page | undefined;
  while (cur && (cur as Page).type !== "page") {
    const parent = state.nodesById[(cur as Layer).parentId] as Layer | Page | undefined;
    if (!parent || (parent as Page).type === "page") break;
    d += 1;
    cur = parent;
  }
  return d;
}

function isAncestor(state: AppState, ancestorId: string, nodeId: string): boolean {
  let cur = state.nodesById[nodeId] as Layer | Page | undefined;
  while (cur && (cur as Page).type !== "page") {
    if ((cur as Layer).id === ancestorId) return true;
    cur = state.nodesById[(cur as Layer).parentId] as Layer | Page | undefined;
  }
  return false;
}
