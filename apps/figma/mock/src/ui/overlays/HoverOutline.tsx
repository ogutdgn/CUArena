// Hover outline — thin blue rect around the layer the cursor is currently over.
// Suppressed when the layer is already in the active selection (selection bbox
// is shown there) and during any active drag.

import { useStore, selectActiveViewport } from "@/engine/store";
import { worldOrientedCornersOfLayer } from "@/engine/coordinates";
import type { Layer, Page } from "@/types/scene";

export function HoverOutline() {
  const id = useStore((s) => s.hoveredNodeId);
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const activeTool = useStore((s) => s.activeTool);
  const dragKind = useStore((s) => s.dragPreview.kind);
  const viewport = useStore((s) => selectActiveViewport(s));
  const activeRightTab = useStore((s) => s.activeRightTab);
  // Resolve the four world-space corners of the layer's local rect after its
  // own rotation + scale (around its center). Rendering as a polygon through
  // those corners means the hover outline rotates with the layer instead of
  // wrapping the axis-aligned AABB (which would leave empty corners around a
  // rotated layer).
  const corners = useStore((s) => {
    if (!id) return null;
    const layer = s.nodesById[id] as Layer | Page | undefined;
    if (!layer || (layer as Page).type === "page") return null;
    return worldOrientedCornersOfLayer(s, layer as Layer);
  });

  if (!id || !corners) return null;
  if (selection.includes(id)) return null;
  if (dragKind != null) return null;
  if (activeTool !== "move") return null;
  // In prototype mode, suppress hover outline — connection dot handles hover UX.
  if (activeRightTab === "prototype") return null;

  const sw = 1.5 / viewport.zoom;
  const points = corners.map((c) => `${c.x},${c.y}`).join(" ");
  return (
    <polygon
      points={points}
      fill="none"
      stroke="var(--color-selection-blue)"
      strokeWidth={sw}
      pointerEvents="none"
    />
  );
}
