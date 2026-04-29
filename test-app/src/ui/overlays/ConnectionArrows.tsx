// Canvas overlay: connection arrows + hover dot + drag-to-create in prototype mode.
// Rendered inside the world-space SVG group so it pans/zooms with canvas.

import { useState, useRef } from "react";
import { useStore } from "@/engine/store";
import { getActivePage } from "@/engine/selectors";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Frame, Layer, PrototypeConnection } from "@/types/scene";

const ARROW_COLOR = "#1ABCFE";
const DOT_R = 6;

type Bounds = { x: number; y: number; w: number; h: number };
type DragState = { sourceId: string; sx: number; sy: number; cx: number; cy: number } | null;

function buildBounds(page: ReturnType<typeof getActivePage>): Map<string, Bounds> {
  const map = new Map<string, Bounds>();
  if (!page) return map;
  for (const child of page.children) {
    map.set(child.id, { x: child.x, y: child.y, w: child.w, h: child.h });
    if ((child as Frame).children) {
      for (const c of (child as Frame).children) {
        map.set(c.id, { x: child.x + c.x, y: child.y + c.y, w: c.w, h: c.h });
      }
    }
  }
  return map;
}

export function ConnectionArrows() {
  const tab = useStore((s) => s.activeRightTab);
  const page = useStore((s) => getActivePage(s));
  const viewport = useStore((s) => s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 });
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [drag, setDrag] = useState<DragState>(null);
  const [hoverDestId, setHoverDestId] = useState<string | null>(null);
  const svgGroupRef = useRef<SVGGElement>(null);

  if (tab !== "prototype" || !page) return null;

  const connections = page.prototypeConnections ?? [];
  const sc = 1 / viewport.zoom;
  const bounds = buildBounds(page);

  const allLayers: Layer[] = [];
  for (const child of page.children) {
    allLayers.push(child);
    if ((child as Frame).children) {
      for (const c of (child as Frame).children) allLayers.push(c);
    }
  }

  function screenToWorld(clientX: number, clientY: number): { x: number; y: number } {
    const svg = svgGroupRef.current?.ownerSVGElement;
    if (!svg) return { x: 0, y: 0 };
    const rect = svg.getBoundingClientRect();
    return {
      x: (clientX - rect.left) / viewport.zoom + viewport.x,
      y: (clientY - rect.top) / viewport.zoom + viewport.y,
    };
  }

  function hitDestFrame(wx: number, wy: number, excludeId: string): Frame | undefined {
    return page!.children.find((c): c is Frame => {
      if (c.type !== "frame" || c.id === excludeId) return false;
      return wx >= c.x && wx <= c.x + c.w && wy >= c.y && wy <= c.y + c.h;
    });
  }

  function onDotDown(e: React.PointerEvent, layerId: string, sx: number, sy: number) {
    e.stopPropagation();
    e.preventDefault();
    const w = screenToWorld(e.clientX, e.clientY);
    setDrag({ sourceId: layerId, sx, sy, cx: w.x, cy: w.y });
    setHoverId(null);
    setHoverDestId(null);
  }

  function onOverlayMove(e: React.PointerEvent) {
    if (!drag) return;
    const w = screenToWorld(e.clientX, e.clientY);
    setDrag((d) => (d ? { ...d, cx: w.x, cy: w.y } : null));
    const dest = hitDestFrame(w.x, w.y, drag.sourceId);
    setHoverDestId(dest?.id ?? null);
  }

  function onOverlayUp(e: React.PointerEvent) {
    if (!drag) return;
    const w = screenToWorld(e.clientX, e.clientY);
    const dest = hitDestFrame(w.x, w.y, drag.sourceId);
    if (dest) {
      const pageId = page!.id;
      const id = uid("conn");
      const newConn: PrototypeConnection = {
        id,
        sourceLayerId: drag.sourceId,
        trigger: "on_tap",
        action: "navigate_to",
        destinationFrameId: dest.id,
        animation: "instant",
      };
      useStore.setState((s) => {
        const pp = s.document.pages.find((q) => q.id === pageId);
        if (!pp) return;
        if (!pp.prototypeConnections) pp.prototypeConnections = [];
        pp.prototypeConnections.push(newConn);
      });
      emitSemantic({
        name: "create_prototype_connection",
        connectionId: id,
        sourceLayerId: drag.sourceId,
        trigger: "on_tap",
        action: "navigate_to",
      });
    }
    setDrag(null);
    setHoverDestId(null);
  }

  // Hover dot position
  const hoverBounds = !drag && hoverId ? bounds.get(hoverId) : null;
  const dotCx = hoverBounds ? hoverBounds.x + hoverBounds.w : 0;
  const dotCy = hoverBounds ? hoverBounds.y + hoverBounds.h / 2 : 0;

  return (
    <g ref={svgGroupRef}>
      {/* Layer hit-test rects for hover detection (only when not dragging) */}
      {!drag && allLayers.map((layer) => {
        const b = bounds.get(layer.id);
        if (!b) return null;
        return (
          <rect
            key={`hit-${layer.id}`}
            x={b.x} y={b.y} width={b.w} height={b.h}
            fill="transparent"
            onMouseEnter={() => setHoverId(layer.id)}
            onMouseLeave={() => setHoverId(null)}
          />
        );
      })}

      {/* Existing connection arrows */}
      {connections.map((conn) => {
        if (!conn.destinationFrameId) return null;
        const src = bounds.get(conn.sourceLayerId);
        const dst = bounds.get(conn.destinationFrameId);
        if (!src || !dst) return null;

        const x1 = src.x + src.w;
        const y1 = src.y + src.h / 2;
        const x2 = dst.x;
        const y2 = dst.y + dst.h / 2;
        const cp = Math.abs(x2 - x1) * 0.5 + 40;
        const path = `M ${x1} ${y1} C ${x1 + cp} ${y1} ${x2 - cp} ${y2} ${x2} ${y2}`;
        const sz = sc * 8;
        const lx1 = x2 + Math.cos(Math.PI * 0.75) * sz;
        const ly1 = y2 + Math.sin(Math.PI * 0.75) * sz;
        const lx2 = x2 + Math.cos(-Math.PI * 0.75) * sz;
        const ly2 = y2 + Math.sin(-Math.PI * 0.75) * sz;

        return (
          <g key={conn.id} style={{ pointerEvents: "none" }}>
            <path d={path} fill="none" stroke="rgba(0,0,0,0.25)" strokeWidth={3 * sc} strokeLinecap="round" />
            <path d={path} fill="none" stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <line x1={x2} y1={y2} x2={lx1} y2={ly1} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <line x1={x2} y1={y2} x2={lx2} y2={ly2} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <circle cx={x1} cy={y1} r={3 * sc} fill={ARROW_COLOR} />
            <circle cx={x2} cy={y2} r={3 * sc} fill={ARROW_COLOR} />
          </g>
        );
      })}

      {/* Hover dot — click+drag to create connection */}
      {!drag && hoverBounds && (
        <g
          transform={`translate(${dotCx} ${dotCy}) scale(${sc})`}
          style={{ cursor: "crosshair" }}
          onPointerDown={(e) => onDotDown(e, hoverId!, dotCx, dotCy)}
        >
          <circle cx={0} cy={0} r={DOT_R + 6} fill="transparent" />
          <circle cx={0} cy={0} r={DOT_R} fill={ARROW_COLOR} />
          <text
            x={0} y={DOT_R * 0.38}
            textAnchor="middle"
            fontSize={DOT_R * 1.3}
            fill="white"
            fontFamily="Inter, sans-serif"
            fontWeight={700}
            style={{ userSelect: "none", pointerEvents: "none" }}
          >
            +
          </text>
        </g>
      )}

      {/* ── Active drag ──────────────────────────────────────────────── */}
      {drag && (() => {
        const cp = Math.abs(drag.cx - drag.sx) * 0.5 + 40;
        const path = `M ${drag.sx} ${drag.sy} C ${drag.sx + cp} ${drag.sy} ${drag.cx - cp} ${drag.cy} ${drag.cx} ${drag.cy}`;

        return (
          <>
            {/* Huge transparent overlay that captures all pointer events */}
            <rect
              x={-1e7} y={-1e7} width={2e7} height={2e7}
              fill="transparent"
              style={{ cursor: "crosshair" }}
              onPointerMove={onOverlayMove}
              onPointerUp={onOverlayUp}
            />

            {/* Destination frame highlight */}
            {hoverDestId && (() => {
              const db = bounds.get(hoverDestId);
              if (!db) return null;
              return (
                <rect
                  x={db.x - 2 * sc} y={db.y - 2 * sc}
                  width={db.w + 4 * sc} height={db.h + 4 * sc}
                  fill="none"
                  stroke={ARROW_COLOR}
                  strokeWidth={2 * sc}
                  rx={3 * sc}
                  style={{ pointerEvents: "none" }}
                />
              );
            })()}

            {/* Live arrow line (dashed) */}
            <g style={{ pointerEvents: "none" }}>
              <path d={path} fill="none" stroke="rgba(0,0,0,0.2)" strokeWidth={3 * sc} strokeLinecap="round" strokeDasharray={`${6 * sc} ${4 * sc}`} />
              <path d={path} fill="none" stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" strokeDasharray={`${6 * sc} ${4 * sc}`} />
              <circle cx={drag.sx} cy={drag.sy} r={4 * sc} fill={ARROW_COLOR} />
              <circle cx={drag.cx} cy={drag.cy} r={5 * sc} fill="none" stroke={ARROW_COLOR} strokeWidth={1.5 * sc} />
              <circle cx={drag.cx} cy={drag.cy} r={2 * sc} fill={ARROW_COLOR} />
            </g>
          </>
        );
      })()}
    </g>
  );
}
