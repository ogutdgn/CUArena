// Hover outline — thin blue rect around the layer the cursor is currently over.
// Suppressed when the layer is already in the active selection (selection bbox
// is shown there) and during any active drag.

import { useStore, selectActiveViewport } from "@/engine/store";
import { worldRectOfLayer } from "@/engine/coordinates";
import type { Layer, Page } from "@/types/scene";

export function HoverOutline() {
  const id = useStore((s) => s.hoveredNodeId);
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const activeTool = useStore((s) => s.activeTool);
  const dragKind = useStore((s) => s.dragPreview.kind);
  const viewport = useStore((s) => selectActiveViewport(s));
  const activeRightTab = useStore((s) => s.activeRightTab);
  // Resolve to a world-space rect inside the selector so ancestor offsets are
  // applied — matches selectionBbox. Using local x/y here would land the
  // outline at the canvas top-left for any frame child.
  const rect = useStore((s) => {
    if (!id) return null;
    const layer = s.nodesById[id] as Layer | Page | undefined;
    if (!layer || (layer as Page).type === "page") return null;
    return worldRectOfLayer(s, layer as Layer);
  });

  if (!id || !rect) return null;
  if (selection.includes(id)) return null;
  if (dragKind != null) return null;
  if (activeTool !== "move") return null;
  // In prototype mode, suppress hover outline — connection dot handles hover UX.
  if (activeRightTab === "prototype") return null;

  const sw = 1.5 / viewport.zoom;
  return (
    <rect
      x={rect.x}
      y={rect.y}
      width={rect.w}
      height={rect.h}
      fill="none"
      stroke="var(--color-selection-blue)"
      strokeWidth={sw}
      pointerEvents="none"
    />
  );
}
