import type { Viewport } from "@/types/ops";

export interface CanvasRectLike {
  left: number;
  top: number;
  width: number;
  height: number;
}

export function clientToWorldPoint(
  clientX: number,
  clientY: number,
  viewport: Viewport,
  canvasRect: CanvasRectLike,
): { x: number; y: number } {
  return {
    x: (clientX - canvasRect.left - canvasRect.width / 2) / viewport.zoom + viewport.x,
    y: (clientY - canvasRect.top - canvasRect.height / 2) / viewport.zoom + viewport.y,
  };
}

export function worldToClientPoint(
  worldX: number,
  worldY: number,
  viewport: Viewport,
  canvasRect: CanvasRectLike,
): { x: number; y: number } {
  return {
    x: canvasRect.left + canvasRect.width / 2 + (worldX - viewport.x) * viewport.zoom,
    y: canvasRect.top + canvasRect.height / 2 + (worldY - viewport.y) * viewport.zoom,
  };
}

export function svgWorldTransform(viewport: Viewport, canvasSize: { width: number; height: number }): string {
  return `matrix(${viewport.zoom} 0 0 ${viewport.zoom} ${canvasSize.width / 2 - viewport.x * viewport.zoom} ${canvasSize.height / 2 - viewport.y * viewport.zoom})`;
}
