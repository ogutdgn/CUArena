// Alignment + distribution commands.
//
// Bounds and target positions are computed in WORLD space so a selection can
// safely span multiple parents (e.g. a top-level layer + a frame child).
// Final per-layer x/y are converted back to each layer's own parent-local
// space before dispatching set_transform, matching the parent-local convention
// the document uses everywhere else.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "./selectors";
import type { TransformMap } from "@/types/ops";
import type { Layer, Page } from "@/types/scene";
import type { AppState } from "./store";
import { worldRectOfLayer, worldToParentLocal } from "./coordinates";

export type AlignAxis = "left" | "center-x" | "right" | "top" | "center-y" | "bottom";
export type DistributeAxis = "horizontal" | "vertical";

// Figma parity: when a single non-top-level layer is selected, its align
// buttons act against the parent container (frame / group / section). Returns
// the container layer or null if the parent is the page or otherwise not
// alignment-eligible. Shared with the UI so the button-disabled state and the
// engine guard agree on what counts as a single-child alignment context.
export function getSingleSelectionAlignmentContainer(
  state: AppState,
  layers: Layer[],
): Layer | null {
  if (layers.length !== 1) return null;
  const layer = layers[0];
  const parent = state.nodesById[layer.parentId] as Layer | Page | undefined;
  if (!parent || (parent as Page).type === "page") return null;
  const parentLayer = parent as Layer;
  if (
    parentLayer.type !== "frame" &&
    parentLayer.type !== "group" &&
    parentLayer.type !== "section"
  ) {
    return null;
  }
  return parentLayer;
}

export function alignSelection(axis: AlignAxis): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;

  // Single-child case: align inside the parent container's world rect.
  if (layers.length === 1) {
    const container = getSingleSelectionAlignmentContainer(s, layers);
    if (!container) return; // page-level single layer: nothing to align against.
    const layer = layers[0];
    const wr = worldRectOfLayer(s, layer);
    const cr = worldRectOfLayer(s, container);

    let wx = wr.x;
    let wy = wr.y;
    if (axis === "left") wx = cr.x;
    else if (axis === "right") wx = cr.x + cr.w - wr.w;
    else if (axis === "center-x") wx = cr.x + cr.w / 2 - wr.w / 2;
    else if (axis === "top") wy = cr.y;
    else if (axis === "bottom") wy = cr.y + cr.h - wr.h;
    else if (axis === "center-y") wy = cr.y + cr.h / 2 - wr.h / 2;

    const local = worldToParentLocal(s, layer.parentId, { x: wx, y: wy });
    const t = { x: layer.x, y: layer.y, w: layer.w, h: layer.h, rotation: layer.rotation, scaleX: layer.scaleX, scaleY: layer.scaleY };
    if (local.x === t.x && local.y === t.y) return; // no-op: already aligned.

    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_transform",
      pageId: s.activePageId,
      ids: [layer.id],
      before: { [layer.id]: t },
      after: { [layer.id]: { ...t, x: local.x, y: local.y } },
    });
    emitSemantic({
      name: "align_layers",
      layerIds: [layer.id],
      axis,
      trigger: "panel_button",
    } as never);
    return;
  }

  // 2+ layers: bounds from the selection itself.
  if (layers.length < 2) return;

  // World-space rect per layer + selection bounds in world space.
  const worldRects = layers.map((l) => ({ layer: l, wr: worldRectOfLayer(s, l) }));
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const { wr } of worldRects) {
    if (wr.x < minX) minX = wr.x;
    if (wr.y < minY) minY = wr.y;
    if (wr.x + wr.w > maxX) maxX = wr.x + wr.w;
    if (wr.y + wr.h > maxY) maxY = wr.y + wr.h;
  }
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;

  const before: TransformMap = {};
  const after: TransformMap = {};
  for (const { layer: l, wr } of worldRects) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;

    let wx = wr.x;
    let wy = wr.y;
    if (axis === "left") wx = minX;
    else if (axis === "right") wx = maxX - wr.w;
    else if (axis === "center-x") wx = cx - wr.w / 2;
    else if (axis === "top") wy = minY;
    else if (axis === "bottom") wy = maxY - wr.h;
    else if (axis === "center-y") wy = cy - wr.h / 2;

    const local = worldToParentLocal(s, l.parentId, { x: wx, y: wy });
    after[l.id] = { ...t, x: local.x, y: local.y };
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

  // World-space rect per layer; sort by world position along the chosen axis.
  const enriched = layers.map((l) => ({ layer: l, wr: worldRectOfLayer(s, l) }));
  enriched.sort((a, b) => (axis === "horizontal" ? a.wr.x - b.wr.x : a.wr.y - b.wr.y));
  const first = enriched[0].wr;
  const last = enriched[enriched.length - 1].wr;
  let totalSize = 0;
  for (const { wr } of enriched) totalSize += axis === "horizontal" ? wr.w : wr.h;
  const span =
    axis === "horizontal"
      ? last.x + last.w - first.x
      : last.y + last.h - first.y;
  const gap = (span - totalSize) / (enriched.length - 1);

  const before: TransformMap = {};
  const after: TransformMap = {};
  let cursor = axis === "horizontal" ? first.x : first.y;
  for (const { layer: l, wr } of enriched) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;
    let wx = wr.x;
    let wy = wr.y;
    if (axis === "horizontal") {
      wx = cursor;
      cursor += wr.w + gap;
    } else {
      wy = cursor;
      cursor += wr.h + gap;
    }
    const local = worldToParentLocal(s, l.parentId, { x: wx, y: wy });
    after[l.id] = { ...t, x: local.x, y: local.y };
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
