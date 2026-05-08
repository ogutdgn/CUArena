// Hover outline — thin blue rect around the layer the cursor is currently over.
// Suppressed when the layer is already in the active selection (selection bbox
// is shown there) and during any active drag.

import { useStore, selectActiveViewport } from "@/engine/store";
import { localPointToWorld, worldOrientedCornersOfLayer } from "@/engine/coordinates";
import type { Layer, Page } from "@/types/scene";

export function HoverOutline() {
  const id = useStore((s) => s.hoveredNodeId);
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const activeTool = useStore((s) => s.activeTool);
  const dragKind = useStore((s) => s.dragPreview.kind);
  const viewport = useStore((s) => selectActiveViewport(s));
  const activeRightTab = useStore((s) => s.activeRightTab);
  const hoverGeometry = useStore((s) => {
    if (!id) return null;
    const layer = s.nodesById[id] as Layer | Page | undefined;
    if (!layer || (layer as Page).type === "page") return null;
    if ((layer as Layer).type === "line" || (layer as Layer).type === "arrow") {
      const line = layer as Extract<Layer, { type: "line" | "arrow" }>;
      return {
        kind: line.type,
        p1: localPointToWorld(s, line, line.p1),
        p2: localPointToWorld(s, line, line.p2),
        endCapStart: line.type === "arrow" ? line.endCapStart : "none",
        endCapEnd: line.type === "arrow" ? line.endCapEnd : "none",
      } as const;
    }
    // Resolve the four world-space corners of the layer's local rect after its
    // own rotation + scale (around its center). Rendering as a polygon through
    // those corners means the hover outline rotates with the layer instead of
    // wrapping the axis-aligned AABB (which would leave empty corners around a
    // rotated layer).
    return { kind: "box", corners: worldOrientedCornersOfLayer(s, layer as Layer) } as const;
  });

  if (!id || !hoverGeometry) return null;
  if (selection.includes(id)) return null;
  if (dragKind != null) return null;
  if (activeTool !== "move") return null;
  // In prototype mode, suppress hover outline — connection dot handles hover UX.
  if (activeRightTab === "prototype") return null;

  const sw = 1.5 / viewport.zoom;
  if (hoverGeometry.kind === "line" || hoverGeometry.kind === "arrow") {
    const markerSize = 6 / viewport.zoom;
    const markerId = `hover-arrow-end-${id}`;
    const startMarkerId = `hover-arrow-start-${id}`;
    return (
      <g pointerEvents="none">
        {hoverGeometry.kind === "arrow" && (
          <defs>
            {hoverGeometry.endCapEnd === "arrow" && (
              <marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth={markerSize} markerHeight={markerSize} orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-selection-blue)" />
              </marker>
            )}
            {hoverGeometry.endCapStart === "arrow" && (
              <marker id={startMarkerId} viewBox="0 0 10 10" refX="2" refY="5" markerWidth={markerSize} markerHeight={markerSize} orient="auto">
                <path d="M 10 0 L 0 5 L 10 10 z" fill="var(--color-selection-blue)" />
              </marker>
            )}
          </defs>
        )}
        <line
          x1={hoverGeometry.p1.x}
          y1={hoverGeometry.p1.y}
          x2={hoverGeometry.p2.x}
          y2={hoverGeometry.p2.y}
          stroke="var(--color-selection-blue)"
          strokeWidth={sw}
          markerEnd={hoverGeometry.kind === "arrow" && hoverGeometry.endCapEnd === "arrow" ? `url(#${markerId})` : undefined}
          markerStart={hoverGeometry.kind === "arrow" && hoverGeometry.endCapStart === "arrow" ? `url(#${startMarkerId})` : undefined}
        />
      </g>
    );
  }

  if (hoverGeometry.kind !== "box") return null;
  const points = hoverGeometry.corners.map((c) => `${c.x},${c.y}`).join(" ");
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
