// Canvas overlay: connection arrows + hover dot in prototype mode.
// Rendered inside the world-space SVG group so it pans/zooms with canvas.

import { useState } from "react";
import { useStore } from "@/engine/store";
import { getActivePage } from "@/engine/selectors";
import type { Frame, Layer } from "@/types/scene";

const ARROW_COLOR = "#1ABCFE";
const DOT_R = 6; // px at zoom=1, scaled to stay constant

export function ConnectionArrows() {
  const tab = useStore((s) => s.activeRightTab);
  const page = useStore((s) => getActivePage(s));
  const zoom = useStore((s) => s.viewportByPage[s.activePageId]?.zoom ?? 1);
  const [hoverId, setHoverId] = useState<string | null>(null);

  if (tab !== "prototype" || !page) return null;

  const connections = page.prototypeConnections ?? [];
  const sc = 1 / zoom;

  // Collect all renderable layers (top-level + children of frames)
  const allLayers: Layer[] = [];
  for (const child of page.children) {
    allLayers.push(child);
    if (child.type === "frame" || child.type === "group" || child.type === "section") {
      for (const c of (child as Frame).children ?? []) {
        allLayers.push(c);
      }
    }
  }

  // Build a map from layerId to absolute world-space bounds
  const bounds = new Map<string, { x: number; y: number; w: number; h: number }>();
  for (const child of page.children) {
    bounds.set(child.id, { x: child.x, y: child.y, w: child.w, h: child.h });
    if ((child as Frame).children) {
      for (const c of (child as Frame).children) {
        bounds.set(c.id, { x: child.x + c.x, y: child.y + c.y, w: c.w, h: c.h });
      }
    }
  }

  return (
    <>
      {/* Hit-test transparent rects over all layers for hover detection */}
      {allLayers.map((layer) => {
        const b = bounds.get(layer.id);
        if (!b) return null;
        return (
          <rect
            key={`hit-${layer.id}`}
            x={b.x}
            y={b.y}
            width={b.w}
            height={b.h}
            fill="transparent"
            style={{ cursor: "crosshair" }}
            onMouseEnter={() => setHoverId(layer.id)}
            onMouseLeave={() => setHoverId(null)}
          />
        );
      })}

      {/* Hover dot on right edge */}
      {hoverId && (() => {
        const b = bounds.get(hoverId);
        if (!b) return null;
        const cx = b.x + b.w;
        const cy = b.y + b.h / 2;
        return (
          <g transform={`translate(${cx} ${cy}) scale(${sc})`} style={{ pointerEvents: "none" }}>
            <circle cx={0} cy={0} r={DOT_R} fill={ARROW_COLOR} />
            <text x={0} y={DOT_R * 0.4} textAnchor="middle" fontSize={DOT_R * 1.2} fill="white" fontFamily="Inter, sans-serif" fontWeight={700}>+</text>
          </g>
        );
      })()}

      {/* Connection arrows */}
      {connections.map((conn) => {
        if (!conn.destinationFrameId) return null;
        const src = bounds.get(conn.sourceLayerId);
        const dst = bounds.get(conn.destinationFrameId);
        if (!src || !dst) return null;

        // Source: right-center of source layer
        const x1 = src.x + src.w;
        const y1 = src.y + src.h / 2;
        // Dest: left-center of destination frame
        const x2 = dst.x;
        const y2 = dst.y + dst.h / 2;

        const cpOffset = Math.abs(x2 - x1) * 0.5 + 40;
        const path = `M ${x1} ${y1} C ${x1 + cpOffset} ${y1} ${x2 - cpOffset} ${y2} ${x2} ${y2}`;

        // Arrowhead at destination
        const arrowSc = sc * 8;
        const angle = Math.atan2(y2 - (y1), x2 - (x1 + cpOffset * 2));
        const ax = x2 - Math.cos(angle) * arrowSc;
        const ay = y2 - Math.sin(angle) * arrowSc;
        const lx1 = ax + Math.cos(angle + Math.PI * 0.75) * arrowSc;
        const ly1 = ay + Math.sin(angle + Math.PI * 0.75) * arrowSc;
        const lx2 = ax + Math.cos(angle - Math.PI * 0.75) * arrowSc;
        const ly2 = ay + Math.sin(angle - Math.PI * 0.75) * arrowSc;

        return (
          <g key={conn.id} style={{ pointerEvents: "none" }}>
            {/* Shadow for readability */}
            <path d={path} fill="none" stroke="rgba(0,0,0,0.3)" strokeWidth={3 * sc} strokeLinecap="round" />
            {/* Arrow line */}
            <path d={path} fill="none" stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            {/* Arrowhead */}
            <line x1={x2} y1={y2} x2={lx1} y2={ly1} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <line x1={x2} y1={y2} x2={lx2} y2={ly2} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            {/* Source dot */}
            <circle cx={x1} cy={y1} r={3 * sc} fill={ARROW_COLOR} />
            {/* Dest dot */}
            <circle cx={x2} cy={y2} r={3 * sc} fill={ARROW_COLOR} />
          </g>
        );
      })}
    </>
  );
}
