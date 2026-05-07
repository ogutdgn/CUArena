// Derived selectors over store state. Pure functions over AppState.

import type { AppState } from "./store";
import type { Layer, Page, ContainerLayer } from "@/types/scene";
import type { Rect } from "@/util/geometry";
import { worldOffsetOfLayer, worldRectOfLayer, worldPointToLayerLocal } from "./coordinates";
import { isContainer } from "@/types/scene";

export function getActivePage(s: AppState): Page | null {
  return s.document.pages.find((p) => p.id === s.activePageId) ?? null;
}

export function getSelection(s: AppState): string[] {
  return s.selectionByPage[s.activePageId] ?? [];
}

export function getSelectedLayers(s: AppState): Layer[] {
  const ids = getSelection(s);
  const out: Layer[] = [];
  for (const id of ids) {
    const n = s.nodesById[id];
    if (n && (n as Page).type !== "page") out.push(n as Layer);
  }
  return out;
}

export function selectionBbox(s: AppState): Rect | null {
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return null;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  // Intentionally NOT transform-aware: the resize math in `move.ts` consumes
  // `selectionBbox` together with each layer's `worldRectOfLayer` (also
  // untransformed) and assumes the two are in the same coordinate space.
  // Per-layer transformed AABBs are used by `HoverOutline` and
  // `ParentBoundsOverlay` for visual feedback that follows rotation/flip;
  // upgrading the resize path to inverse-transform pointer deltas is a
  // separate follow-up.
  for (const l of layers) {
    const r = worldRectOfLayer(s, l);
    if (r.x < minX) minX = r.x;
    if (r.y < minY) minY = r.y;
    if (r.x + r.w > maxX) maxX = r.x + r.w;
    if (r.y + r.h > maxY) maxY = r.y + r.h;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function hitTest(s: AppState, x: number, y: number): Layer | null {
  const page = getActivePage(s);
  if (!page) return null;
  // Zoom is needed so line/arrow hit padding stays constant in screen space
  // (a pixel of slack means the same thing at 25% as at 400% zoom).
  const zoom = (s.viewportByPage[s.activePageId] ?? { zoom: 1 }).zoom;
  const focusId = s.focusContextByPage[s.activePageId] ?? null;
  if (focusId) {
    const node = s.nodesById[focusId];
    if (node && (node as Page).type !== "page" && isContainer(node as Layer)) {
      const scope = node as ContainerLayer;
      const origin = worldOffsetOfLayer(s, scope);
      return hitTestArr(scope.children, x, y, origin.x, origin.y, zoom, s);
    }
  }
  return hitTestArr(page.children, x, y, 0, 0, zoom, s);
}

function hitTestArr(layers: Layer[], x: number, y: number, ox: number, oy: number, zoom: number, state: AppState): Layer | null {
  for (let i = layers.length - 1; i >= 0; i--) {
    const l = layers[i];
    if (l.locked || !l.visible) continue;
    const wx = ox + l.x;
    const wy = oy + l.y;
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      const hit = hitTestArr(l.children, x, y, wx, wy, zoom, state);
      if (hit) return hit;
      if (l.type !== "group" && containsTransformed(l, x, y, zoom, state)) return l;
      continue;
    }
    if (containsTransformed(l, x, y, zoom, state)) return l;
  }
  return null;
}

// Hit-test threshold for line/arrow segments — keeps thin lines selectable
// without making clicks 50px away from the line register. Stroke weight gets
// added so heavier strokes have a proportionally bigger hit area.
const LINE_HIT_PADDING_PX = 4;

// Transform-aware containment. For line/arrow we apply the layer's local
// scale + rotation to the endpoints and test point-to-segment distance with a
// stroke-weight + zoom-aware threshold. For everything else we inverse-map the
// world point into the layer's local coordinate space and test against the
// un-rotated 0..w / 0..h rect — that way clicks land on the visibly rotated
// or flipped layer rather than its stored un-transformed AABB.
function containsTransformed(l: Layer, x: number, y: number, zoom: number, state: AppState): boolean {
  if (l.type === "line" || l.type === "arrow") {
    const sw = (l.strokes[0]?.weight ?? 1);
    const threshold = sw / 2 + LINE_HIT_PADDING_PX / Math.max(0.0001, zoom);
    const ancestor = worldOffsetOfLayer(state, l);
    const a = applyLayerLocalTransform(l, l.p1.x, l.p1.y, ancestor.x, ancestor.y);
    const b = applyLayerLocalTransform(l, l.p2.x, l.p2.y, ancestor.x, ancestor.y);
    return pointToSegmentDistance(x, y, a.x, a.y, b.x, b.y) <= threshold;
  }
  const local = worldPointToLayerLocal(state, l, { x, y });
  return local.x >= 0 && local.x <= l.w && local.y >= 0 && local.y <= l.h;
}

// Apply scale-around-center then rotate-around-center then translate-to-world,
// matching `commonTransform` in NodeRenderer. Used by line/arrow endpoint
// hit-testing and SelectionOverlay endpoint placement.
function applyLayerLocalTransform(
  l: Layer,
  lx: number,
  ly: number,
  wx: number,
  wy: number,
): { x: number; y: number } {
  const cx = l.w / 2;
  const cy = l.h / 2;
  let px = lx;
  let py = ly;
  if (l.scaleX !== 1 || l.scaleY !== 1) {
    px = cx + (px - cx) * l.scaleX;
    py = cy + (py - cy) * l.scaleY;
  }
  if (l.rotation !== 0) {
    const rad = (l.rotation * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const dx = px - cx;
    const dy = py - cy;
    px = cx + dx * cos - dy * sin;
    py = cy + dx * sin + dy * cos;
  }
  return { x: wx + px, y: wy + py };
}

function pointToSegmentDistance(px: number, py: number, ax: number, ay: number, bx: number, by: number): number {
  const dx = bx - ax;
  const dy = by - ay;
  const len2 = dx * dx + dy * dy;
  if (len2 === 0) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  const cx = ax + dx * t;
  const cy = ay + dy * t;
  return Math.hypot(px - cx, py - cy);
}
