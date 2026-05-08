import { layerToWorldMatrix } from "@/engine/coordinates";
import type { AppState } from "@/engine/store";
import type { Viewport } from "@/types/ops";
import type { Text as TextLayer } from "@/types/scene";

export function textEditorCssMatrix(
  state: AppState,
  layer: TextLayer,
  viewport: Viewport,
  canvasRect: { left: number; top: number },
): string {
  const m = layerToWorldMatrix(state, layer);
  const a = m.a * viewport.zoom;
  const b = m.b * viewport.zoom;
  const c = m.c * viewport.zoom;
  const d = m.d * viewport.zoom;
  const e = canvasRect.left + (m.e - viewport.x) * viewport.zoom;
  const f = canvasRect.top + (m.f - viewport.y) * viewport.zoom;
  return `matrix(${a}, ${b}, ${c}, ${d}, ${e}, ${f})`;
}
