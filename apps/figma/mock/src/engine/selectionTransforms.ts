import type { Layer } from "@/types/scene";
import type { TransformMap } from "@/types/ops";
import type { AppState } from "./store";
import {
  invertMatrix,
  layerToWorldMatrix,
  multiplyMatrices,
  parentToWorldMatrix,
  transformFromLocalMatrix,
  worldAABBOfLayer,
  type Matrix,
  type RectLike,
} from "./coordinates";

function translate(x: number, y: number): Matrix {
  return { a: 1, b: 0, c: 0, d: 1, e: x, f: y };
}

function rotate(deg: number): Matrix {
  const rad = (deg * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  return { a: cos, b: sin, c: -sin, d: cos, e: 0, f: 0 };
}

function unionRects(rects: RectLike[]): RectLike | null {
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

export function rotateSelectionAroundVisualCenter(
  state: AppState,
  layers: Layer[],
  deltaDeg: number,
): TransformMap {
  const out: TransformMap = {};
  if (layers.length === 0) return out;
  if (layers.length === 1) {
    const l = layers[0];
    out[l.id] = {
      x: l.x,
      y: l.y,
      w: l.w,
      h: l.h,
      rotation: ((l.rotation + deltaDeg) % 360 + 360) % 360,
      scaleX: l.scaleX,
      scaleY: l.scaleY,
    };
    return out;
  }

  const bbox = unionRects(layers.map((l) => worldAABBOfLayer(state, l)));
  if (!bbox) return out;
  const cx = bbox.x + bbox.w / 2;
  const cy = bbox.y + bbox.h / 2;
  const aroundSelection = multiplyMatrices(multiplyMatrices(translate(cx, cy), rotate(deltaDeg)), translate(-cx, -cy));

  for (const l of layers) {
    const nextWorld = multiplyMatrices(aroundSelection, layerToWorldMatrix(state, l));
    const parentInverse = invertMatrix(parentToWorldMatrix(state, l.parentId));
    const nextLocal = multiplyMatrices(parentInverse, nextWorld);
    out[l.id] = transformFromLocalMatrix(l, nextLocal);
  }
  return out;
}
