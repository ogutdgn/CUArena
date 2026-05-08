import type { AppState } from "./store";
import type { Layer, Page, VectorNetwork } from "@/types/scene";
import type { TransformTuple } from "@/types/ops";

export interface XY {
  x: number;
  y: number;
}

export interface RectLike extends XY {
  w: number;
  h: number;
}

export interface Matrix {
  a: number;
  b: number;
  c: number;
  d: number;
  e: number;
  f: number;
}

const IDENTITY: Matrix = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };

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

export function multiplyMatrices(left: Matrix, right: Matrix): Matrix {
  return {
    a: left.a * right.a + left.c * right.b,
    b: left.b * right.a + left.d * right.b,
    c: left.a * right.c + left.c * right.d,
    d: left.b * right.c + left.d * right.d,
    e: left.a * right.e + left.c * right.f + left.e,
    f: left.b * right.e + left.d * right.f + left.f,
  };
}

function translate(x: number, y: number): Matrix {
  return { a: 1, b: 0, c: 0, d: 1, e: x, f: y };
}

function rotate(deg: number): Matrix {
  const rad = (deg * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  return { a: cos, b: sin, c: -sin, d: cos, e: 0, f: 0 };
}

function scale(x: number, y: number): Matrix {
  return { a: x, b: 0, c: 0, d: y, e: 0, f: 0 };
}

function around(cx: number, cy: number, inner: Matrix): Matrix {
  return multiplyMatrices(multiplyMatrices(translate(cx, cy), inner), translate(-cx, -cy));
}

function applyMatrix(m: Matrix, p: XY): XY {
  return { x: m.a * p.x + m.c * p.y + m.e, y: m.b * p.x + m.d * p.y + m.f };
}

function invert(m: Matrix): Matrix {
  const det = m.a * m.d - m.b * m.c;
  if (Math.abs(det) < 1e-9) return IDENTITY;
  return {
    a: m.d / det,
    b: -m.b / det,
    c: -m.c / det,
    d: m.a / det,
    e: (m.c * m.f - m.d * m.e) / det,
    f: (m.b * m.e - m.a * m.f) / det,
  };
}

function layerLocalMatrix(layer: Layer): Matrix {
  const cx = layer.w / 2;
  const cy = layer.h / 2;
  let m = translate(layer.x, layer.y);
  if (layer.rotation !== 0) m = multiplyMatrices(m, around(cx, cy, rotate(layer.rotation)));
  if (layer.scaleX !== 1 || layer.scaleY !== 1) m = multiplyMatrices(m, around(cx, cy, scale(layer.scaleX, layer.scaleY)));
  return m;
}

function pathFromRoot(state: AppState, layer: Layer): Layer[] {
  const out: Layer[] = [];
  let cur: Layer | null = layer;
  while (cur) {
    out.unshift(cur);
    const parent = getParentNode(state, cur);
    cur = asLayer(parent ?? undefined);
  }
  return out;
}

export function layerToWorldMatrix(state: AppState, layer: Layer): Matrix {
  let m = IDENTITY;
  for (const item of pathFromRoot(state, layer)) m = multiplyMatrices(m, layerLocalMatrix(item));
  return m;
}

export function parentToWorldMatrix(state: AppState, parentId: string): Matrix {
  const parent = state.nodesById[parentId];
  if (!parent || (parent as Page).type === "page") return IDENTITY;
  return layerToWorldMatrix(state, parent as Layer);
}

export function invertMatrix(m: Matrix): Matrix {
  return invert(m);
}

export function applyMatrixToPoint(m: Matrix, p: XY): XY {
  return applyMatrix(m, p);
}

export function transformFromLocalMatrix(layer: Pick<Layer, "w" | "h">, matrix: Matrix): TransformTuple {
  const det = matrix.a * matrix.d - matrix.b * matrix.c;
  const scaleX: 1 | -1 = det < 0 ? -1 : 1;
  const scaleY: 1 | -1 = 1;
  const rotation = normalizeRotation((Math.atan2(matrix.b / scaleX, matrix.a / scaleX) * 180) / Math.PI);
  const originOffset = transformedOriginOffset(layer.w, layer.h, rotation, scaleX, scaleY);
  return {
    x: matrix.e - originOffset.x,
    y: matrix.f - originOffset.y,
    w: layer.w,
    h: layer.h,
    rotation,
    scaleX,
    scaleY,
  };
}

function transformedOriginOffset(w: number, h: number, rotation: number, scaleX: 1 | -1, scaleY: 1 | -1): XY {
  const cx = w / 2;
  const cy = h / 2;
  const rad = (rotation * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const scaled = {
    x: cx + (0 - cx) * scaleX,
    y: cy + (0 - cy) * scaleY,
  };
  const dx = scaled.x - cx;
  const dy = scaled.y - cy;
  return {
    x: cx + dx * cos - dy * sin,
    y: cy + dx * sin + dy * cos,
  };
}

function normalizeRotation(deg: number): number {
  const rounded = Math.abs(deg) < 1e-9 ? 0 : deg;
  return ((rounded % 360) + 360) % 360;
}

// Apply the layer's local point through the same nested transform chain used
// by the SVG renderer: translate, rotate around center, then scale/flip around
// center for the layer and every transformed ancestor.
export function localPointToWorld(state: AppState, layer: Layer, local: XY): XY {
  return applyMatrix(layerToWorldMatrix(state, layer), local);
}

// Inverse of localPointToWorld: take a world point and express it in the
// layer's local coordinate space. Used for hit-testing rotated/flipped layers.
export function worldPointToLayerLocal(state: AppState, layer: Layer, world: XY): XY {
  return applyMatrix(invert(layerToWorldMatrix(state, layer)), world);
}

// Returns the four world-space corners of the layer's local rect, transformed
// by the layer's rotation + scale around its center. Order: NW, NE, SE, SW
// (top-left going clockwise). Used by selection overlays that need to render
// an oriented box and by AABB/snap consumers that need a tight world bounding
// box for a rotated/flipped layer.
export function worldOrientedCornersOfLayer(state: AppState, layer: Layer): XY[] {
  return [
    localPointToWorld(state, layer, { x: 0, y: 0 }),
    localPointToWorld(state, layer, { x: layer.w, y: 0 }),
    localPointToWorld(state, layer, { x: layer.w, y: layer.h }),
    localPointToWorld(state, layer, { x: 0, y: layer.h }),
  ];
}

// Tight axis-aligned bounding box around the four transformed corners. For an
// unrotated/unflipped layer this matches worldRectOfLayer; for rotated layers
// it expands to cover the rotated outline.
export function worldAABBOfLayer(state: AppState, layer: Layer): RectLike {
  const corners = worldOrientedCornersOfLayer(state, layer);
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const c of corners) {
    if (c.x < minX) minX = c.x;
    if (c.y < minY) minY = c.y;
    if (c.x > maxX) maxX = c.x;
    if (c.y > maxY) maxY = c.y;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function worldToParentLocal(state: AppState, parentId: string, world: XY): XY {
  return applyMatrix(invert(parentToWorldMatrix(state, parentId)), world);
}

export function worldRectToParentLocal(state: AppState, parentId: string, rect: RectLike): RectLike {
  return rectFromPoints([
    worldToParentLocal(state, parentId, { x: rect.x, y: rect.y }),
    worldToParentLocal(state, parentId, { x: rect.x + rect.w, y: rect.y }),
    worldToParentLocal(state, parentId, { x: rect.x + rect.w, y: rect.y + rect.h }),
    worldToParentLocal(state, parentId, { x: rect.x, y: rect.y + rect.h }),
  ]);
}

export function localToWorld(state: AppState, parentId: string, local: XY): XY {
  return applyMatrix(parentToWorldMatrix(state, parentId), local);
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
        if (isWorldPointInsideLayerLocalRect(state, layer, world)) return focusId;
      }
    }
  }
  // 2) Otherwise auto-parent into the deepest visible/unlocked container under
  // the cursor. Fixes #12: drawing inside an unfocused frame previously fell
  // through to the page and required a follow-up drag-into-frame.
  const page = state.document.pages.find((p) => p.id === pageId);
  if (page) {
    const deep = deepestContainerAt(state, page.children, world);
    if (deep) return deep;
  }
  return pageId;
}

// Bezier-aware bounding box for a vector network. Without this helper, pen
// creation only considers vertex coords — curves whose handles extend outside
// the anchor hull get a bbox that's too small, which is what shows up in the
// selection overlay for pen-drawn paths (#13). Conservative: uses handle
// endpoints rather than full cubic-extrema (de Casteljau), which is fine for
// the common case where curve protrusion is small relative to handle reach.
export function computeVectorNetworkBounds(network: VectorNetwork): {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
} {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const v of network.vertices) {
    if (v.x < minX) minX = v.x;
    if (v.y < minY) minY = v.y;
    if (v.x > maxX) maxX = v.x;
    if (v.y > maxY) maxY = v.y;
  }
  for (const seg of network.segments) {
    const a = network.vertices[seg.fromIndex];
    const b = network.vertices[seg.toIndex];
    if (!a || !b) continue;
    const c1 = seg.handleFrom ? { x: a.x + seg.handleFrom.dx, y: a.y + seg.handleFrom.dy } : a;
    const c2 = seg.handleTo ? { x: b.x + seg.handleTo.dx, y: b.y + seg.handleTo.dy } : b;
    for (const p of cubicBoundsPoints(a, c1, c2, b)) {
      if (p.x < minX) minX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.x > maxX) maxX = p.x;
      if (p.y > maxY) maxY = p.y;
    }
  }
  if (!Number.isFinite(minX)) return { minX: 0, minY: 0, maxX: 0, maxY: 0 };
  return { minX, minY, maxX, maxY };
}

function cubicBoundsPoints(p0: XY, p1: XY, p2: XY, p3: XY): XY[] {
  const ts = new Set<number>([0, 1]);
  for (const t of cubicExtremaTs(p0.x, p1.x, p2.x, p3.x)) ts.add(t);
  for (const t of cubicExtremaTs(p0.y, p1.y, p2.y, p3.y)) ts.add(t);
  return [...ts].map((t) => cubicPoint(p0, p1, p2, p3, t));
}

function cubicExtremaTs(p0: number, p1: number, p2: number, p3: number): number[] {
  const a = -p0 + 3 * p1 - 3 * p2 + p3;
  const b = 2 * (p0 - 2 * p1 + p2);
  const c = -p0 + p1;
  const out: number[] = [];
  const epsilon = 1e-9;
  if (Math.abs(a) < epsilon) {
    if (Math.abs(b) < epsilon) return out;
    const t = -c / b;
    if (t > 0 && t < 1) out.push(t);
    return out;
  }
  const disc = b * b - 4 * a * c;
  if (disc < -epsilon) return out;
  if (Math.abs(disc) <= epsilon) {
    const t = -b / (2 * a);
    if (t > 0 && t < 1) out.push(t);
    return out;
  }
  const root = Math.sqrt(disc);
  const t1 = (-b + root) / (2 * a);
  const t2 = (-b - root) / (2 * a);
  if (t1 > 0 && t1 < 1) out.push(t1);
  if (t2 > 0 && t2 < 1) out.push(t2);
  return out;
}

function cubicPoint(p0: XY, p1: XY, p2: XY, p3: XY, t: number): XY {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const t2 = t * t;
  return {
    x: mt2 * mt * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t2 * t * p3.x,
    y: mt2 * mt * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t2 * t * p3.y,
  };
}

function rectFromPoints(points: XY[]): RectLike {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const p of points) {
    if (p.x < minX) minX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x;
    if (p.y > maxY) maxY = p.y;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function pointInPolygon(point: XY, polygon: XY[]): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const pi = polygon[i];
    const pj = polygon[j];
    const intersects = (pi.y > point.y) !== (pj.y > point.y)
      && point.x < ((pj.x - pi.x) * (point.y - pi.y)) / (pj.y - pi.y) + pi.x;
    if (intersects) inside = !inside;
  }
  return inside;
}

export function isWorldPointInsideLayerLocalRect(state: AppState, layer: Layer, world: XY): boolean {
  const local = worldPointToLayerLocal(state, layer, world);
  const epsilon = 0.001;
  return local.x >= -epsilon
    && local.x <= layer.w + epsilon
    && local.y >= -epsilon
    && local.y <= layer.h + epsilon;
}

// Walks the layer tree top-down (z-order, last-in-array wins) and returns the
// id of the deepest visible/unlocked frame|section|group that contains the
// world point. Locked or hidden containers are skipped.
function deepestContainerAt(state: AppState, layers: Layer[], world: XY): string | null {
  for (let i = layers.length - 1; i >= 0; i--) {
    const l = layers[i];
    if (l.locked || !l.visible) continue;
    if (l.type !== "frame" && l.type !== "section" && l.type !== "group") continue;
    if (!isWorldPointInsideLayerLocalRect(state, l, world)) continue;
    const deeper = deepestContainerAt(state, l.children, world);
    if (deeper) return deeper;
    return l.id;
  }
  return null;
}
