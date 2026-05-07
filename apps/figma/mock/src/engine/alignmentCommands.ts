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

// ─── Tidy up ──────────────────────────────────────────────────────────
//
// Helper spec: app-docs/helper/extracted/features/alignment/tidy-up.md.
// Detects whether the selection is 1D (single row / column with overlapping
// perpendicular extents) or 2D (grid clustered on both axes), then equalizes
// spacing using the **mode** of observed gaps (mean fallback if all unique).
// No-op when neither layout qualifies, when fewer than 2 layers are selected,
// or when the resolved positions don't actually move any layer.

type WorldRect = { x: number; y: number; w: number; h: number };
type LayerWithRect = { layer: Layer; wr: WorldRect };

function commonRangeExists(rects: WorldRect[], axis: "x" | "y"): boolean {
  let maxStart = -Infinity;
  let minEnd = Infinity;
  for (const r of rects) {
    const start = axis === "x" ? r.x : r.y;
    const size = axis === "x" ? r.w : r.h;
    if (start > maxStart) maxStart = start;
    if (start + size < minEnd) minEnd = start + size;
  }
  return maxStart < minEnd;
}

function computeSpacing(gaps: number[], tolerance: number): number {
  if (gaps.length === 0) return 0;
  // Bucket gaps within `tolerance` of an existing bucket's running mean; the
  // bucket with the most members wins (mode). Falls back to overall mean when
  // every gap is unique.
  const buckets: Array<{ value: number; count: number }> = [];
  for (const g of gaps) {
    const hit = buckets.find((b) => Math.abs(b.value - g) <= tolerance);
    if (hit) {
      hit.value = (hit.value * hit.count + g) / (hit.count + 1);
      hit.count += 1;
    } else {
      buckets.push({ value: g, count: 1 });
    }
  }
  buckets.sort((a, b) => b.count - a.count);
  if (buckets[0].count > 1) return buckets[0].value;
  return gaps.reduce((s, g) => s + g, 0) / gaps.length;
}

function tryClusterAsGrid(items: LayerWithRect[]): LayerWithRect[][] | null {
  if (items.length < 4) return null; // Grid needs at least 2x2.
  const sorted = [...items].sort(
    (a, b) => a.wr.y + a.wr.h / 2 - (b.wr.y + b.wr.h / 2),
  );
  const rows: LayerWithRect[][] = [];
  for (const it of sorted) {
    const cy = it.wr.y + it.wr.h / 2;
    const tol = Math.max(8, it.wr.h / 4);
    let placed = false;
    for (const row of rows) {
      const refCy = row[0].wr.y + row[0].wr.h / 2;
      const rowTol = Math.max(tol, row[0].wr.h / 4);
      if (Math.abs(cy - refCy) <= rowTol) {
        row.push(it);
        placed = true;
        break;
      }
    }
    if (!placed) rows.push([it]);
  }
  if (rows.length < 2) return null;
  // Every row must have the same number of items to qualify as a grid.
  const cols = rows[0].length;
  if (cols < 2) return null;
  if (rows.some((r) => r.length !== cols)) return null;
  for (const r of rows) {
    r.sort((a, b) => a.wr.x + a.wr.w / 2 - (b.wr.x + b.wr.w / 2));
  }
  return rows;
}

function detectTidyDimension(
  items: LayerWithRect[],
):
  | { kind: "1d_horizontal" }
  | { kind: "1d_vertical" }
  | { kind: "2d"; rows: LayerWithRect[][] }
  | null {
  if (items.length < 2) return null;
  const rects = items.map((i) => i.wr);

  if (items.length === 2) {
    // 2 layers: only 1D ever qualifies.
    const yOverlap = commonRangeExists(rects, "y");
    const xOverlap = commonRangeExists(rects, "x");
    if (yOverlap && !xOverlap) return { kind: "1d_horizontal" };
    if (xOverlap && !yOverlap) return { kind: "1d_vertical" };
    if (yOverlap && xOverlap) {
      // Layers overlap on both axes (e.g. stacked); pick the axis with the
      // larger center-to-center span so the tidy is meaningful.
      const dx = Math.abs(
        rects[0].x + rects[0].w / 2 - (rects[1].x + rects[1].w / 2),
      );
      const dy = Math.abs(
        rects[0].y + rects[0].h / 2 - (rects[1].y + rects[1].h / 2),
      );
      return dx >= dy ? { kind: "1d_horizontal" } : { kind: "1d_vertical" };
    }
    return null;
  }

  // 3+ layers: try 2D grid FIRST. A grid where adjacent rows happen to share
  // a y-range (e.g. tall cards with slight overlap) would otherwise be
  // misclassified as 1D horizontal and collapsed onto a single row.
  const grid = tryClusterAsGrid(items);
  if (grid) return { kind: "2d", rows: grid };

  const yOverlap = commonRangeExists(rects, "y");
  const xOverlap = commonRangeExists(rects, "x");
  if (yOverlap) return { kind: "1d_horizontal" };
  if (xOverlap) return { kind: "1d_vertical" };
  return null;
}

export function tidySelection(
  trigger: "panel_button" | "context_menu" | "shortcut",
): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length < 2) return;

  const items: LayerWithRect[] = layers.map((l) => ({ layer: l, wr: worldRectOfLayer(s, l) }));
  const detection = detectTidyDimension(items);
  if (!detection) return; // No qualifying 1D or 2D layout — no-op.

  const before: TransformMap = {};
  const after: TransformMap = {};
  const tEpsilon = 0.5; // sub-pixel positions don't count as "changed".
  let changed = false;

  function recordTarget(layer: Layer, worldX: number, worldY: number) {
    const local = worldToParentLocal(s, layer.parentId, { x: worldX, y: worldY });
    const t = { x: layer.x, y: layer.y, w: layer.w, h: layer.h, rotation: layer.rotation, scaleX: layer.scaleX, scaleY: layer.scaleY };
    before[layer.id] = t;
    after[layer.id] = { ...t, x: local.x, y: local.y };
    if (Math.abs(local.x - layer.x) > tEpsilon || Math.abs(local.y - layer.y) > tEpsilon) {
      changed = true;
    }
  }

  let computedSpacing: { x?: number; y?: number } = {};

  if (detection.kind === "1d_horizontal" || detection.kind === "1d_vertical") {
    const horizontal = detection.kind === "1d_horizontal";
    const sorted = [...items].sort((a, b) =>
      horizontal
        ? a.wr.x + a.wr.w / 2 - (b.wr.x + b.wr.w / 2)
        : a.wr.y + a.wr.h / 2 - (b.wr.y + b.wr.h / 2),
    );
    const gaps: number[] = [];
    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1].wr;
      const cur = sorted[i].wr;
      gaps.push(
        horizontal ? cur.x - (prev.x + prev.w) : cur.y - (prev.y + prev.h),
      );
    }
    const spacing = computeSpacing(gaps, 2);
    if (horizontal) computedSpacing = { x: spacing };
    else computedSpacing = { y: spacing };

    // Perpendicular axis: align all layers to the average current center on that axis.
    const perpCenters = sorted.map((it) =>
      horizontal ? it.wr.y + it.wr.h / 2 : it.wr.x + it.wr.w / 2,
    );
    const perpAvg = perpCenters.reduce((a, b) => a + b, 0) / perpCenters.length;

    let cursor = horizontal ? sorted[0].wr.x : sorted[0].wr.y;
    for (const it of sorted) {
      const wx = horizontal ? cursor : perpAvg - it.wr.w / 2;
      const wy = horizontal ? perpAvg - it.wr.h / 2 : cursor;
      recordTarget(it.layer, wx, wy);
      cursor += (horizontal ? it.wr.w : it.wr.h) + spacing;
    }
  } else {
    // 2D grid
    const rows = detection.rows;
    const cols = rows[0].length;
    const anchorX = Math.min(...items.map((i) => i.wr.x));
    const anchorY = Math.min(...items.map((i) => i.wr.y));

    // Row gaps: gap between rows (max-bottom of row N → top of row N+1).
    const rowGaps: number[] = [];
    for (let r = 1; r < rows.length; r++) {
      const prevBottom = Math.max(...rows[r - 1].map((c) => c.wr.y + c.wr.h));
      const curTop = Math.min(...rows[r].map((c) => c.wr.y));
      rowGaps.push(curTop - prevBottom);
    }
    // Col gaps aggregated across EVERY row so a single outlier in the first
    // row can't force the whole grid to inherit a bad spacing.
    const colGaps: number[] = [];
    for (const row of rows) {
      for (let c = 1; c < row.length; c++) {
        const prev = row[c - 1].wr;
        const cur = row[c].wr;
        colGaps.push(cur.x - (prev.x + prev.w));
      }
    }
    const ySpacing = computeSpacing(rowGaps, 2);
    const xSpacing = computeSpacing(colGaps, 2);
    computedSpacing = { x: xSpacing, y: ySpacing };

    // For variable-width grids: each column gets a fixed width = max width
    // observed in that column across all rows. Then column anchors are shared
    // by every row, so columns line up vertically even when items differ in
    // width row-to-row. Items are centered within their column slot.
    const colWidths: number[] = [];
    for (let c = 0; c < cols; c++) {
      let maxW = 0;
      for (const row of rows) {
        if (row[c].wr.w > maxW) maxW = row[c].wr.w;
      }
      colWidths.push(maxW);
    }
    const colXAnchors: number[] = [];
    {
      let cur = anchorX;
      for (let c = 0; c < cols; c++) {
        colXAnchors.push(cur);
        cur += colWidths[c] + xSpacing;
      }
    }

    let yCursor = anchorY;
    for (const row of rows) {
      const rowH = Math.max(...row.map((c) => c.wr.h));
      for (let c = 0; c < cols; c++) {
        const it = row[c];
        const colW = colWidths[c];
        const wx = colXAnchors[c] + (colW - it.wr.w) / 2;
        const wy = yCursor + (rowH - it.wr.h) / 2;
        recordTarget(it.layer, wx, wy);
      }
      yCursor += rowH + ySpacing;
    }
  }

  if (!changed) return; // Already tidy — don't burn an undo entry.

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: items.map((i) => i.layer.id),
    before,
    after,
  });
  emitSemantic({
    name: "tidy_up",
    layerIds: items.map((i) => i.layer.id),
    dimension:
      detection.kind === "1d_horizontal"
        ? "1d_horizontal"
        : detection.kind === "1d_vertical"
        ? "1d_vertical"
        : "2d",
    computedSpacing,
    trigger,
  });
}
