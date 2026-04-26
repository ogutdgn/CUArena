// Hover outline — thin blue rect around the layer the cursor is currently over.
// Suppressed when the layer is already in the active selection (selection bbox
// is shown there) and during any active drag.

import { useStore, selectActiveViewport } from "@/engine/store";
import type { Layer, Page } from "@/types/scene";

export function HoverOutline() {
  const id = useStore((s) => s.hoveredNodeId);
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const activeTool = useStore((s) => s.activeTool);
  const dragKind = useStore((s) => s.dragPreview.kind);
  const viewport = useStore((s) => selectActiveViewport(s));
  const layer = useStore((s) => (id ? (s.nodesById[id] as Layer | Page | undefined) : undefined));

  if (!id || !layer) return null;
  if ((layer as Page).type === "page") return null;
  if (selection.includes(id)) return null;
  if (dragKind != null) return null;
  if (activeTool !== "move") return null;

  const l = layer as Layer;
  const sw = 1.5 / viewport.zoom;
  return (
    <rect
      x={l.x}
      y={l.y}
      width={l.w}
      height={l.h}
      fill="none"
      stroke="var(--color-selection-blue)"
      strokeWidth={sw}
      pointerEvents="none"
    />
  );
}
