import type { AppState } from "./store";
import type { TransformMap } from "@/types/ops";
import type { Layer, Page } from "@/types/scene";
import type { HandleDir } from "@/ui/overlays/SelectionOverlay";
import type { Point } from "@/util/geometry";
import { localPointToWorld, worldPointToLayerLocal, worldToParentLocal } from "./coordinates";

export function resizeSingleTransformedLayer(
  s: AppState,
  layerIds: string[],
  startTransforms: TransformMap,
  dir: HandleDir,
  world: Point,
): TransformMap | null {
  if (layerIds.length !== 1) return null;
  const id = layerIds[0];
  const liveLayer = s.nodesById[id] as Layer | undefined;
  const start = startTransforms[id];
  if (!liveLayer || (liveLayer as unknown as Page).type === "page" || !start) return null;
  if (start.rotation === 0 && start.scaleX === 1 && start.scaleY === 1) return null;

  const startLayer = { ...liveLayer, ...start } as Layer;
  const local = worldPointToLayerLocal(s, startLayer, world);
  let left = 0;
  let top = 0;
  let right = start.w;
  let bottom = start.h;
  if (dir.includes("w")) left = local.x;
  if (dir.includes("e")) right = local.x;
  if (dir.includes("n")) top = local.y;
  if (dir.includes("s")) bottom = local.y;
  if (right < left) [left, right] = [right, left];
  if (bottom < top) [top, bottom] = [bottom, top];

  const nextW = Math.max(1, right - left);
  const nextH = Math.max(1, bottom - top);
  const anchorWorld = localPointToWorld(s, startLayer, { x: left, y: top });
  const anchorParent = worldToParentLocal(s, liveLayer.parentId, anchorWorld);
  const originOffset = transformedLocalPoint({ x: 0, y: 0 }, nextW, nextH, start.rotation, start.scaleX, start.scaleY);

  return {
    [id]: {
      ...start,
      x: anchorParent.x - originOffset.x,
      y: anchorParent.y - originOffset.y,
      w: nextW,
      h: nextH,
    },
  };
}

function transformedLocalPoint(p: Point, w: number, h: number, rotation: number, scaleX: 1 | -1, scaleY: 1 | -1): Point {
  const cx = w / 2;
  const cy = h / 2;
  let x = cx + (p.x - cx) * scaleX;
  let y = cy + (p.y - cy) * scaleY;
  if (rotation !== 0) {
    const rad = (rotation * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const dx = x - cx;
    const dy = y - cy;
    x = cx + dx * cos - dy * sin;
    y = cy + dx * sin + dy * cos;
  }
  return { x, y };
}
