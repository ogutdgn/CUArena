import type { Point } from "@/util/geometry";

export interface ViewportLike {
  x: number;
  y: number;
  zoom: number;
}

export function pannedViewportFromClientDelta(
  startViewport: ViewportLike,
  startClient: Point,
  currentClient: Point,
): ViewportLike {
  return {
    ...startViewport,
    x: startViewport.x - (currentClient.x - startClient.x) / startViewport.zoom,
    y: startViewport.y - (currentClient.y - startClient.y) / startViewport.zoom,
  };
}
