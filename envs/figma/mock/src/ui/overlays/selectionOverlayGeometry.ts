import { getSelectedLayers, selectionBbox } from "@/engine/selectors";
import { worldAABBOfLayer, worldOrientedCornersOfLayer, type XY } from "@/engine/coordinates";
import type { AppState } from "@/engine/store";
import type { Rect } from "@/util/geometry";

export type SelectionOutlineGeometry =
  | { kind: "none" }
  | { kind: "axis_aligned"; bbox: Rect }
  | { kind: "single_oriented"; bbox: Rect; visualBbox: Rect; points: XY[] };

export function selectionOutlineGeometry(state: AppState): SelectionOutlineGeometry {
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return { kind: "none" };
  if (layers.length === 1) {
    const layer = layers[0];
    if (layer.type === "line" || layer.type === "arrow") {
      return { kind: "axis_aligned", bbox: worldAABBOfLayer(state, layer) };
    }
    const bbox = selectionBbox(state);
    return {
      kind: "single_oriented",
      bbox: bbox ?? worldAABBOfLayer(state, layer),
      visualBbox: worldAABBOfLayer(state, layer),
      points: worldOrientedCornersOfLayer(state, layer),
    };
  }
  const bbox = visualUnionBbox(state, layers);
  return bbox ? { kind: "axis_aligned", bbox } : { kind: "none" };
}

function visualUnionBbox(state: AppState, layers: ReturnType<typeof getSelectedLayers>): Rect | null {
  if (layers.length === 0) return null;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const layer of layers) {
    const r = worldAABBOfLayer(state, layer);
    minX = Math.min(minX, r.x);
    minY = Math.min(minY, r.y);
    maxX = Math.max(maxX, r.x + r.w);
    maxY = Math.max(maxY, r.y + r.h);
  }
  if (!Number.isFinite(minX)) return null;
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}
