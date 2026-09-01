import type { AppState } from "./store";
import type { Layer, Page } from "@/types/scene";
import type { TransformTuple } from "@/types/ops";
import { localPointToWorld, worldToParentLocal } from "./coordinates";

export interface PositionValue {
  x: number;
  y: number;
}

export interface TransformOverrides {
  w?: number;
  h?: number;
  rotation?: number;
  scaleX?: 1 | -1;
  scaleY?: 1 | -1;
}

export function getLayerPositionValue(state: AppState, layer: Layer): PositionValue {
  const center = layerCenterWorld(state, layer);
  const origin = positionOriginWorld(state, layer);
  return { x: center.x - origin.x, y: center.y - origin.y };
}

export function transformForLayerPositionValue(
  state: AppState,
  layer: Layer,
  position: PositionValue,
  overrides: TransformOverrides = {},
): TransformTuple {
  const w = overrides.w ?? layer.w;
  const h = overrides.h ?? layer.h;
  const origin = positionOriginWorld(state, layer);
  const targetCenterWorld = { x: origin.x + position.x, y: origin.y + position.y };
  const targetCenterParent = worldToParentLocal(state, layer.parentId, targetCenterWorld);
  return {
    x: targetCenterParent.x - w / 2,
    y: targetCenterParent.y - h / 2,
    w,
    h,
    rotation: overrides.rotation ?? layer.rotation,
    scaleX: overrides.scaleX ?? layer.scaleX,
    scaleY: overrides.scaleY ?? layer.scaleY,
  };
}

function layerCenterWorld(state: AppState, layer: Layer): PositionValue {
  return localPointToWorld(state, layer, { x: layer.w / 2, y: layer.h / 2 });
}

function positionOriginWorld(state: AppState, layer: Layer): PositionValue {
  const parent = state.nodesById[layer.parentId];
  if (!parent || (parent as Page).type === "page") return { x: 0, y: 0 };
  const parentLayer = parent as Layer;
  return localPointToWorld(state, parentLayer, { x: parentLayer.w / 2, y: parentLayer.h / 2 });
}
