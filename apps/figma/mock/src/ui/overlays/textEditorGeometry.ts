import { layerToWorldMatrix } from "@/engine/coordinates";
import { worldToClientPoint } from "@/engine/viewportCoordinates";
import type { AppState } from "@/engine/store";
import type { Viewport } from "@/types/ops";
import type { Text as TextLayer } from "@/types/scene";

export function textEditorCssMatrix(
  state: AppState,
  layer: TextLayer,
  viewport: Viewport,
  canvasRect: { left: number; top: number; width: number; height: number },
): string {
  const m = layerToWorldMatrix(state, layer);
  const a = m.a * viewport.zoom;
  const b = m.b * viewport.zoom;
  const c = m.c * viewport.zoom;
  const d = m.d * viewport.zoom;
  const screenOrigin = worldToClientPoint(m.e, m.f, viewport, canvasRect);
  const e = screenOrigin.x;
  const f = screenOrigin.y;
  return `matrix(${a}, ${b}, ${c}, ${d}, ${e}, ${f})`;
}
