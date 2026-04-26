// Shared tool interface. Each functional tool implements this; the active tool
// receives pointer events from the CanvasView.

import type { Point } from "@/util/geometry";

export interface ITool {
  onPointerDown?(world: Point, e: PointerEvent): void;
  onPointerMove?(world: Point, e: PointerEvent): void;
  onPointerUp?(world: Point, e: PointerEvent): void;
  onAbort?(): void;
}
