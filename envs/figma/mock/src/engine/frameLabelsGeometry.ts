import { worldAABBOfLayer } from "./coordinates";
import type { AppState } from "./store";
import type { Layer } from "@/types/scene";

export interface FrameLabelGeometry {
  id: string;
  name: string;
  x: number;
  y: number;
  type: "frame" | "section";
  opacity: number;
}

export function frameLabelGeometry(state: AppState, zoom: number): FrameLabelGeometry[] {
  const activePage = state.document.pages.find((p) => p.id === state.activePageId);
  if (!activePage) return [];
  const out: FrameLabelGeometry[] = [];
  function visit(layers: Layer[], insideFrame: boolean) {
    for (const layer of layers) {
      if (!layer.visible) continue;
      if (layer.type === "frame" || layer.type === "section") {
        if (!insideFrame) {
          const box = worldAABBOfLayer(state, layer);
          out.push({
            id: layer.id,
            name: layer.name,
            x: box.x,
            y: box.y - 6 / zoom,
            type: layer.type,
            opacity: layer.opacity,
          });
        }
        visit(layer.children, true);
      } else if (layer.type === "group") {
        visit(layer.children, insideFrame);
      }
    }
  }
  visit(activePage.children, false);
  return out;
}
