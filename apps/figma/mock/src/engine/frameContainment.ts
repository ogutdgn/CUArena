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
  options: { frames?: FrameContainmentFrame[]; exitRatio?: number; orderIds?: string[] } = {},
): void {
  const moves = getFrameContainmentMoves(state, layerIds, options);
  if (moves.length > 0) {
    applyReparent(state, {
      id: `frame-containment-${moves.map((move) => move.id).join("-")}`,
      timestamp: 0,
      kind: "reparent",
      pageId: state.activePageId,
      moves,
    });
  }
}

export function getFrameContainmentMoves(
  state: AppState,
  layerIds: string[],
  options: { frames?: FrameContainmentFrame[]; exitRatio?: number; orderIds?: string[] } = {},
): ReparentOp["moves"] {
  const movedSet = new Set(layerIds);
  const frames = options.frames ?? collectFrameContainmentFrames(state, movedSet);
  const exitRatio = options.exitRatio ?? FRAME_NEST_EXIT_RATIO;
  const orderRank = orderRankForContainment(state, options.orderIds ?? null, layerIds);
  const rootIds = rootMovedLayerIds(state, layerIds, movedSet);
  if (rootIds.length > 1) {
    const atomicMoves = getAtomicFrameContainmentMoves(state, rootIds, movedSet, frames, exitRatio, orderRank);
    if (atomicMoves) return atomicMoves;
  }
  const moves = rootIds
    .map((id) => getFrameContainmentMove(state, id, movedSet, frames, exitRatio, orderRank))
    .filter((move): move is ReparentOp["moves"][number] => move !== null);
  return normalizeBatchInsertionOrder(state, moves, orderRank);
}

function getAtomicFrameContainmentMoves(
  state: AppState,
  rootIds: string[],
  movedSet: Set<string>,
  frames: FrameContainmentFrame[],
  exitRatio: number,
  orderRank: Map<string, number>,
): ReparentOp["moves"] | null {
  const layers = rootIds
    .map((id) => state.nodesById[id] as Layer | undefined)
    .filter((layer): layer is Layer => !!layer && (layer as unknown as Page).type !== "page");
  if (layers.length !== rootIds.length) return null;

  const commonParentId = layers[0].parentId;
  if (!layers.every((layer) => layer.parentId === commonParentId)) return null;

  const wr = unionRects(layers.map((layer) => worldAABBOfLayer(state, layer)));
  if (!wr) return [];
  const area = Math.max(1, wr.w * wr.h);
  const currentParent = state.nodesById[commonParentId] as Layer | Page | undefined;
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
    if (movedSet.has(frame.id)) continue;
    if (rootIds.some((id) => id === frame.id || isAncestor(state, id, frame.id))) continue;
    const ratio = overlapRatio(wr, frame.rect, area);
    if (ratio < FRAME_NEST_ENTER_RATIO) continue;
    const depth = depthOf(state, frame.id);
    if (depth > bestDepth || (depth === bestDepth && ratio > bestRatio)) {
      bestDepth = depth;
      bestRatio = ratio;
      bestFrameId = frame.id;
    }
  }

  let toParentId = commonParentId;
  if (bestFrameId) {
    toParentId = bestFrameId;
  } else if (currentFrameParent && currentOverlap < exitRatio) {
    toParentId = currentFrameParent.parentId;
  }
  if (toParentId === commonParentId) return [];

  const fromArr = childrenOf(state, commonParentId);
  const toArr = childrenOf(state, toParentId);
  if (!fromArr || !toArr) return [];
  let fallbackToIndex = toArr.length;
  if (currentFrameParent && toParentId === currentFrameParent.parentId) {
    const frameIndex = toArr.findIndex((child) => child.id === currentFrameParent.id);
    if (frameIndex >= 0) fallbackToIndex = frameIndex + 1;
  }

  const moves = layers.map((layer) => {
    const fromIndex = fromArr.findIndex((child) => child.id === layer.id);
    return {
      id: layer.id,
      fromParentId: commonParentId,
      fromIndex,
      toParentId,
      toIndex: insertionIndexForSelectionOrder(toArr, layer.id, fallbackToIndex, orderRank),
    };
  }).filter((move) => move.fromIndex >= 0);
  return normalizeBatchInsertionOrder(state, moves, orderRank);
}

function getFrameContainmentMove(
  state: AppState,
  id: string,
  movedSet: Set<string>,
  frames: FrameContainmentFrame[],
  exitRatio: number,
  orderRank: Map<string, number>,
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
  toIndex = insertionIndexForSelectionOrder(toArr, id, toIndex, orderRank);

  return { id, fromParentId: layer.parentId, fromIndex, toParentId, toIndex };
}

function normalizeBatchInsertionOrder(
  state: AppState,
  moves: ReparentOp["moves"],
  orderRank: Map<string, number>,
): ReparentOp["moves"] {
  if (moves.length <= 1) return moves;
  const byParent = new Map<string, ReparentOp["moves"]>();
  for (const move of moves) {
    const group = byParent.get(move.toParentId);
    if (group) group.push(move);
    else byParent.set(move.toParentId, [move]);
  }

  const normalized = moves.map((move) => ({ ...move }));
  const byId = new Map(normalized.map((move) => [move.id, move]));
  const originalOrder = new Map(normalized.map((move, index) => [move.id, index]));
  const leavingByParent = new Map<string, Set<string>>();
  for (const move of normalized) {
    const set = leavingByParent.get(move.fromParentId);
    if (set) set.add(move.id);
    else leavingByParent.set(move.fromParentId, new Set([move.id]));
  }
  for (const [parentId, group] of byParent) {
    const leaving = leavingByParent.get(parentId);
    if (group.length <= 1 && !leaving) continue;
    const currentChildren = [...(childrenOf(state, parentId) ?? [])];
    const virtualChildren = currentChildren.filter((child) => !leaving?.has(child.id));
    const sorted = [...group].sort((a, b) => compareContainmentOrder(state, a.id, b.id, orderRank));
    for (const move of sorted) {
      const target = byId.get(move.id);
      const virtualIndex = insertionIndexForSelectionOrder(virtualChildren, move.id, move.toIndex, orderRank);
      const toIndex = currentIndexForVirtualInsert(currentChildren, virtualIndex, leaving);
      if (target) target.toIndex = toIndex;
      const layer = state.nodesById[move.id] as Layer | undefined;
      virtualChildren.splice(Math.max(0, Math.min(virtualChildren.length, virtualIndex)), 0, layer ?? ({ id: move.id } as Layer));
      currentChildren.splice(Math.max(0, Math.min(currentChildren.length, toIndex)), 0, layer ?? ({ id: move.id } as Layer));
    }
  }
  return normalized.sort((a, b) => {
    const dependency = frameEnterBeforeExitOrder(state, a, b);
    if (dependency !== 0) return dependency;
    if (a.toParentId === b.toParentId && a.toIndex !== b.toIndex) return a.toIndex - b.toIndex;
    return (originalOrder.get(a.id) ?? 0) - (originalOrder.get(b.id) ?? 0);
  });
}

function frameEnterBeforeExitOrder(
  state: AppState,
  a: ReparentOp["moves"][number],
  b: ReparentOp["moves"][number],
): number {
  if (a.toParentId === b.fromParentId && isFrameParent(state, a.toParentId)) return -1;
  if (b.toParentId === a.fromParentId && isFrameParent(state, b.toParentId)) return 1;
  return 0;
}

function isFrameParent(state: AppState, parentId: string): boolean {
  const parent = state.nodesById[parentId] as Layer | Page | undefined;
  return !!parent && (parent as Page).type !== "page" && (parent as Layer).type === "frame";
}

function currentIndexForVirtualInsert(
  currentChildren: Layer[],
  virtualIndex: number,
  leaving: Set<string> | undefined,
): number {
  if (virtualIndex <= 0) return 0;
  let kept = 0;
  for (let i = 0; i < currentChildren.length; i++) {
    if (leaving?.has(currentChildren[i].id)) continue;
    kept += 1;
    if (kept === virtualIndex) return i + 1;
  }
  return currentChildren.length;
}

function insertionIndexForSelectionOrder(
  toArr: Layer[],
  id: string,
  fallback: number,
  orderRank: Map<string, number>,
): number {
  const rank = orderRank.get(id);
  if (rank == null) return fallback;

  let target = fallback;
  for (let i = 0; i < toArr.length; i++) {
    const siblingRank = orderRank.get(toArr[i].id);
    if (siblingRank == null) continue;
    if (siblingRank > rank && i < target) target = i;
    if (siblingRank < rank && i >= target) target = i + 1;
  }
  return target;
}

function compareContainmentOrder(
  state: AppState,
  aId: string,
  bId: string,
  orderRank: Map<string, number>,
): number {
  const ar = orderRank.get(aId);
  const br = orderRank.get(bId);
  if (ar != null && br != null && ar !== br) return ar - br;
  return compareSceneOrder(state, aId, bId);
}

function compareSceneOrder(state: AppState, aId: string, bId: string): number {
  const aPath = sceneOrderPath(state, aId);
  const bPath = sceneOrderPath(state, bId);
  const n = Math.min(aPath.length, bPath.length);
  for (let i = 0; i < n; i++) {
    if (aPath[i] !== bPath[i]) return aPath[i] - bPath[i];
  }
  return aPath.length - bPath.length;
}

function orderRankFromIds(ids: string[]): Map<string, number> {
  const ranks = new Map<string, number>();
  ids.forEach((id, index) => {
    if (!ranks.has(id)) ranks.set(id, index);
  });
  return ranks;
}

function orderRankForContainment(
  state: AppState,
  orderIds: string[] | null,
  layerIds: string[],
): Map<string, number> {
  if (orderIds) return orderRankFromIds(orderIds);
  return orderRankFromIds([...layerIds].sort((a, b) => compareSceneOrder(state, a, b)));
}

function sceneOrderPath(state: AppState, id: string): number[] {
  const path: number[] = [];
  let cur = state.nodesById[id] as Layer | Page | undefined;
  while (cur && (cur as Page).type !== "page") {
    const layer = cur as Layer;
    const siblings = childrenOf(state, layer.parentId);
    path.unshift(siblings ? siblings.findIndex((child) => child.id === layer.id) : -1);
    cur = state.nodesById[layer.parentId] as Layer | Page | undefined;
  }
  return path;
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

function unionRects(rects: { x: number; y: number; w: number; h: number }[]): { x: number; y: number; w: number; h: number } | null {
  if (rects.length === 0) return null;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const r of rects) {
    minX = Math.min(minX, r.x);
    minY = Math.min(minY, r.y);
    maxX = Math.max(maxX, r.x + r.w);
    maxY = Math.max(maxY, r.y + r.h);
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
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
