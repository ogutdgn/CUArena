// Live preview while pen tool is creating: line from last anchor to cursor +
// dot at cursor. Also previews the handle being dragged on the current vertex.

import { useStore, selectActiveViewport } from "@/engine/store";
import type { Vector } from "@/types/scene";
import { worldOffsetOfLayer } from "@/engine/coordinates";

export function PenPreview() {
  const preview = useStore((s) => s.penPreview);
  const viewport = useStore((s) => selectActiveViewport(s));
  const origin = useStore((s) => {
    if (!s.penPreview) return null;
    const n = s.nodesById[s.penPreview.layerId];
    if (!n || (n as Vector).type !== "vector") return null;
    return worldOffsetOfLayer(s, n as Vector);
  });
  const layer = useStore((s) => {
    if (!s.penPreview) return null;
    const n = s.nodesById[s.penPreview.layerId];
    return n && (n as Vector).type === "vector" ? (n as Vector) : null;
  });
  if (!preview || !layer || !origin) return null;

  const sw = 1 / viewport.zoom;
  const ox = origin.x;
  const oy = origin.y;

  const lastVertex = layer.network.vertices[layer.network.vertices.length - 1];
  const lastWorld = lastVertex ? { x: ox + lastVertex.x, y: oy + lastVertex.y } : null;

  // First-vertex hit indicator (close-path target)
  const first = layer.network.vertices[0];
  const firstWorld = first ? { x: ox + first.x, y: oy + first.y } : null;
  const closeHitR = 6 / viewport.zoom;

  return (
    <g pointerEvents="none">
      {/* Preview segment from last anchor to cursor */}
      {lastWorld && preview.cursor && (
        <line
          x1={lastWorld.x}
          y1={lastWorld.y}
          x2={preview.cursor.x}
          y2={preview.cursor.y}
          stroke="var(--color-selection-blue)"
          strokeWidth={sw}
          strokeDasharray={`${4 / viewport.zoom} ${3 / viewport.zoom}`}
        />
      )}
      {/* Existing anchors as small squares */}
      {layer.network.vertices.map((v, i) => (
        <rect
          key={i}
          x={ox + v.x - 3 / viewport.zoom}
          y={oy + v.y - 3 / viewport.zoom}
          width={6 / viewport.zoom}
          height={6 / viewport.zoom}
          fill="white"
          stroke="var(--color-selection-blue)"
          strokeWidth={sw}
        />
      ))}
      {/* Close-path indicator on first vertex when 2+ vertices */}
      {firstWorld && layer.network.vertices.length >= 2 && (
        <circle
          cx={firstWorld.x}
          cy={firstWorld.y}
          r={closeHitR}
          fill="none"
          stroke="var(--color-selection-blue)"
          strokeWidth={sw}
        />
      )}
      {/* Handle drag preview */}
      {preview.handleDrag && layer.network.vertices[preview.handleDrag.vertexIndex] && (() => {
        const v = layer.network.vertices[preview.handleDrag.vertexIndex];
        const cx = ox + v.x;
        const cy = oy + v.y;
        const hx = cx + preview.handleDrag.outDx;
        const hy = cy + preview.handleDrag.outDy;
        const mx = cx - preview.handleDrag.outDx;
        const my = cy - preview.handleDrag.outDy;
        return (
          <g>
            <line x1={mx} y1={my} x2={hx} y2={hy} stroke="var(--color-selection-blue)" strokeWidth={sw} opacity={0.7} />
            <circle cx={hx} cy={hy} r={3 / viewport.zoom} fill="var(--color-selection-blue)" />
            <circle cx={mx} cy={my} r={3 / viewport.zoom} fill="var(--color-selection-blue)" />
          </g>
        );
      })()}
    </g>
  );
}
