import type { AppState } from "./store";
import type { Arrow, Line } from "@/types/scene";
import type { TransformTuple } from "@/types/ops";
import { localPointToWorld, worldToParentLocal } from "./coordinates";

export type LineLikeLayer = Line | Arrow;
export type LineEndpoint = "p1" | "p2";

interface Point {
  x: number;
  y: number;
}

export interface LineEndpointResize {
  transform: TransformTuple;
  p1: Point;
  p2: Point;
}

export function resizeLineEndpointFromWorld(
  state: AppState,
  layer: LineLikeLayer,
  endpoint: LineEndpoint,
  world: Point,
): LineEndpointResize {
  const otherEndpoint: LineEndpoint = endpoint === "p1" ? "p2" : "p1";
  const fixedWorld = localPointToWorld(state, layer, layer[otherEndpoint]);
  const p1Parent = worldToParentLocal(state, layer.parentId, endpoint === "p1" ? world : fixedWorld);
  const p2Parent = worldToParentLocal(state, layer.parentId, endpoint === "p2" ? world : fixedWorld);
  const deltaParent = { x: p2Parent.x - p1Parent.x, y: p2Parent.y - p1Parent.y };
  const deltaLocal = inverseLayerLinear(layer, deltaParent);

  const w = Math.max(1, Math.abs(deltaLocal.x));
  const h = Math.max(1, Math.abs(deltaLocal.y));
  const p1 = {
    x: deltaLocal.x < 0 ? w : 0,
    y: deltaLocal.y < 0 ? h : 0,
  };
  const p2 = {
    x: deltaLocal.x < 0 ? 0 : w,
    y: deltaLocal.y < 0 ? 0 : h,
  };

  const anchorLocal = transformedAroundCenter(layer, { w, h }, p1);
  return {
    transform: {
      x: p1Parent.x - anchorLocal.x,
      y: p1Parent.y - anchorLocal.y,
      w,
      h,
      rotation: layer.rotation,
      scaleX: layer.scaleX,
      scaleY: layer.scaleY,
    },
    p1,
    p2,
  };
}

function inverseLayerLinear(layer: LineLikeLayer, v: Point): Point {
  const rad = (layer.rotation * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const unrotated = {
    x: cos * v.x + sin * v.y,
    y: -sin * v.x + cos * v.y,
  };
  return {
    x: unrotated.x / layer.scaleX,
    y: unrotated.y / layer.scaleY,
  };
}

function transformedAroundCenter(layer: LineLikeLayer, size: { w: number; h: number }, p: Point): Point {
  const cx = size.w / 2;
  const cy = size.h / 2;
  const scaled = {
    x: cx + (p.x - cx) * layer.scaleX,
    y: cy + (p.y - cy) * layer.scaleY,
  };
  const rad = (layer.rotation * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const dx = scaled.x - cx;
  const dy = scaled.y - cy;
  return {
    x: cx + dx * cos - dy * sin,
    y: cy + dx * sin + dy * cos,
  };
}
