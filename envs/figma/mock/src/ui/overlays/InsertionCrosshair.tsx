// Crosshair shown at cursor when a creation tool is active.

import { useStore, selectActiveViewport } from "@/engine/store";

export function InsertionCrosshair() {
  const tool = useStore((s) => s.activeTool);
  const cursor = useStore((s) => s.insertionCursor);
  const viewport = useStore((s) => selectActiveViewport(s));
  if (!cursor) return null;
  const showFor = new Set([
    "rectangle",
    "ellipse",
    "polygon",
    "star",
    "line",
    "arrow",
    "frame",
    "section",
    "slice",
  ]);
  if (!showFor.has(tool)) return null;
  const len = 12 / viewport.zoom;
  const sw = 1 / viewport.zoom;
  return (
    <g pointerEvents="none">
      <line x1={cursor.x - len} y1={cursor.y} x2={cursor.x + len} y2={cursor.y} stroke="rgba(255,255,255,0.7)" strokeWidth={sw} />
      <line x1={cursor.x} y1={cursor.y - len} x2={cursor.x} y2={cursor.y + len} stroke="rgba(255,255,255,0.7)" strokeWidth={sw} />
    </g>
  );
}
