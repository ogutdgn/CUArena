// Smart-snap solver. Given a moving bounding box and a set of candidate bboxes,
// returns adjusted dx/dy and a list of guide lines + distance measurements.

import type { Rect } from "@/util/geometry";

const SNAP_PX = 6;

export type SnapLine =
  | { axis: "x"; x: number; yMin: number; yMax: number }
  | { axis: "y"; y: number; xMin: number; xMax: number };

export interface DistanceMeasure {
  // Endpoints in world coords; label rendered between them.
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  axis: "x" | "y";
  value: number;
}

export interface SnapResult {
  dx: number;
  dy: number;
  lines: SnapLine[];
  measures: DistanceMeasure[];
}

interface XEdge { kind: "left" | "right" | "centerX"; value: number; rect: Rect }
interface YEdge { kind: "top" | "bottom" | "centerY"; value: number; rect: Rect }

function xEdges(r: Rect): XEdge[] {
  return [
    { kind: "left", value: r.x, rect: r },
    { kind: "right", value: r.x + r.w, rect: r },
    { kind: "centerX", value: r.x + r.w / 2, rect: r },
  ];
}
function yEdges(r: Rect): YEdge[] {
  return [
    { kind: "top", value: r.y, rect: r },
    { kind: "bottom", value: r.y + r.h, rect: r },
    { kind: "centerY", value: r.y + r.h / 2, rect: r },
  ];
}

export function computeSnap(
  movingBboxBefore: Rect,
  proposedDx: number,
  proposedDy: number,
  candidates: Rect[],
  zoom: number,
): SnapResult {
  const threshold = SNAP_PX / Math.max(0.0001, zoom);
  const proposed: Rect = {
    x: movingBboxBefore.x + proposedDx,
    y: movingBboxBefore.y + proposedDy,
    w: movingBboxBefore.w,
    h: movingBboxBefore.h,
  };
  const movingX = xEdges(proposed);
  const movingY = yEdges(proposed);

  let bestX: { delta: number; movingValue: number; candidate: Rect } | null = null;
  let bestY: { delta: number; movingValue: number; candidate: Rect } | null = null;

  for (const c of candidates) {
    const cxs = xEdges(c);
    const cys = yEdges(c);
    for (const me of movingX) {
      for (const ce of cxs) {
        const d = ce.value - me.value;
        if (Math.abs(d) <= threshold) {
          if (!bestX || Math.abs(d) < Math.abs(bestX.delta)) {
            bestX = { delta: d, movingValue: ce.value, candidate: c };
          }
        }
      }
    }
    for (const me of movingY) {
      for (const ce of cys) {
        const d = ce.value - me.value;
        if (Math.abs(d) <= threshold) {
          if (!bestY || Math.abs(d) < Math.abs(bestY.delta)) {
            bestY = { delta: d, movingValue: ce.value, candidate: c };
          }
        }
      }
    }
  }

  let dx = proposedDx;
  let dy = proposedDy;
  const lines: SnapLine[] = [];
  const measures: DistanceMeasure[] = [];

  if (bestX) {
    dx = proposedDx + bestX.delta;
    const snappedRect: Rect = { ...proposed, x: movingBboxBefore.x + dx };
    const yMin = Math.min(snappedRect.y, bestX.candidate.y);
    const yMax = Math.max(snappedRect.y + snappedRect.h, bestX.candidate.y + bestX.candidate.h);
    lines.push({ axis: "x", x: bestX.movingValue, yMin, yMax });
    // Distance label: vertical gap between snapped rect and candidate.
    const gap = candidateGap(snappedRect, bestX.candidate, "y");
    if (gap) {
      measures.push({
        axis: "y",
        x1: bestX.movingValue,
        y1: gap.from,
        x2: bestX.movingValue,
        y2: gap.to,
        value: Math.abs(gap.to - gap.from),
      });
    }
  }
  if (bestY) {
    dy = proposedDy + bestY.delta;
    const snappedRect: Rect = { ...proposed, y: movingBboxBefore.y + dy };
    const xMin = Math.min(snappedRect.x, bestY.candidate.x);
    const xMax = Math.max(snappedRect.x + snappedRect.w, bestY.candidate.x + bestY.candidate.w);
    lines.push({ axis: "y", y: bestY.movingValue, xMin, xMax });
    const gap = candidateGap(snappedRect, bestY.candidate, "x");
    if (gap) {
      measures.push({
        axis: "x",
        x1: gap.from,
        y1: bestY.movingValue,
        x2: gap.to,
        y2: bestY.movingValue,
        value: Math.abs(gap.to - gap.from),
      });
    }
  }

  return { dx, dy, lines, measures };
}

// Compute the gap (clear distance) between two rectangles along a given axis.
// Returns from/to coords on that axis where the gap label should be drawn,
// or null if the rects overlap on that axis.
function candidateGap(a: Rect, b: Rect, axis: "x" | "y"): { from: number; to: number } | null {
  if (axis === "y") {
    // Vertical gap (between top/bottom edges)
    const aTop = a.y;
    const aBot = a.y + a.h;
    const bTop = b.y;
    const bBot = b.y + b.h;
    if (bBot <= aTop) return { from: bBot, to: aTop }; // b is above a
    if (aBot <= bTop) return { from: aBot, to: bTop }; // a is above b
    return null;
  }
  // axis === "x"
  const aLeft = a.x;
  const aRight = a.x + a.w;
  const bLeft = b.x;
  const bRight = b.x + b.w;
  if (bRight <= aLeft) return { from: bRight, to: aLeft };
  if (aRight <= bLeft) return { from: aRight, to: bLeft };
  return null;
}
