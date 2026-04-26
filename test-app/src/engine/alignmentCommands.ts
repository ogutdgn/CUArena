// Alignment + distribution commands.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "./selectors";
import type { TransformMap } from "@/types/ops";

export type AlignAxis = "left" | "center-x" | "right" | "top" | "center-y" | "bottom";
export type DistributeAxis = "horizontal" | "vertical";

export function alignSelection(axis: AlignAxis): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length < 2) return;

  // Compute selection bounding box
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const l of layers) {
    if (l.x < minX) minX = l.x;
    if (l.y < minY) minY = l.y;
    if (l.x + l.w > maxX) maxX = l.x + l.w;
    if (l.y + l.h > maxY) maxY = l.y + l.h;
  }
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;

  const before: TransformMap = {};
  const after: TransformMap = {};
  for (const l of layers) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;
    let nx = t.x;
    let ny = t.y;
    if (axis === "left") nx = minX;
    else if (axis === "right") nx = maxX - t.w;
    else if (axis === "center-x") nx = cx - t.w / 2;
    else if (axis === "top") ny = minY;
    else if (axis === "bottom") ny = maxY - t.h;
    else if (axis === "center-y") ny = cy - t.h / 2;
    after[l.id] = { ...t, x: nx, y: ny };
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  });
  emitSemantic({
    name: "align_layers",
    layerIds: layers.map((l) => l.id),
    axis,
    trigger: "panel_button",
  } as never);
}

export function distributeSelection(axis: DistributeAxis): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length < 3) return;

  // Sort by axis position
  const sorted = [...layers].sort((a, b) => (axis === "horizontal" ? a.x - b.x : a.y - b.y));
  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  let totalSize = 0;
  for (const l of sorted) totalSize += axis === "horizontal" ? l.w : l.h;
  const span =
    axis === "horizontal"
      ? last.x + last.w - first.x
      : last.y + last.h - first.y;
  const gap = (span - totalSize) / (sorted.length - 1);

  const before: TransformMap = {};
  const after: TransformMap = {};
  let cursor = axis === "horizontal" ? first.x : first.y;
  for (const l of sorted) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;
    if (axis === "horizontal") {
      after[l.id] = { ...t, x: cursor };
      cursor += l.w + gap;
    } else {
      after[l.id] = { ...t, y: cursor };
      cursor += l.h + gap;
    }
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  });
  emitSemantic({
    name: "distribute_layers",
    layerIds: layers.map((l) => l.id),
    axis,
    trigger: "panel_button",
  } as never);
}
