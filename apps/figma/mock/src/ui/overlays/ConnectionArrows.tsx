// Canvas overlay: connection arrows + hover dot + drag-to-create in prototype mode.
// Rendered inside the world-space SVG group so it pans/zooms with canvas.

import { useEffect, useState, useRef } from "react";
import { createPortal } from "react-dom";
import { useStore } from "@/engine/store";
import { getActivePage } from "@/engine/selectors";
import { worldAABBOfLayer, worldOrientedCornersOfLayer, type XY } from "@/engine/coordinates";
import { clientToWorldPoint } from "@/engine/viewportCoordinates";
import { uid } from "@/util/id";
import { InteractionModal } from "@/ui/overlays/InteractionModal";
import {
  createPrototypeConnection,
  deletePrototypeConnection,
} from "@/engine/prototypeCommands";
import type { Frame, Layer, PrototypeConnection } from "@/types/scene";

const ARROW_COLOR = "#1ABCFE";
const DOT_R = 6;
const HANDLE_OFFSET_PX = 10;
const HANDLE_HIT_R_PX = 18;
const DEST_HIT_MARGIN_PX = 10;

type Bounds = { x: number; y: number; w: number; h: number; corners: XY[] };
type EdgeSide = "top" | "right" | "bottom" | "left";
type DragState = { sourceId: string; sourceSide: EdgeSide; sx: number; sy: number; cx: number; cy: number } | null;

function buildBounds(state: ReturnType<typeof useStore.getState>, page: ReturnType<typeof getActivePage>): Map<string, Bounds> {
  const map = new Map<string, Bounds>();
  if (!page) return map;

  function visit(layer: Layer) {
    const aabb = worldAABBOfLayer(state, layer);
    map.set(layer.id, { ...aabb, corners: worldOrientedCornersOfLayer(state, layer) });
    if ("children" in layer) {
      for (const child of layer.children) visit(child);
    }
  }

  for (const child of page.children) visit(child);
  return map;
}

function flattenLayers(page: ReturnType<typeof getActivePage>): Layer[] {
  const layers: Layer[] = [];
  if (!page) return layers;

  function visit(layer: Layer) {
    layers.push(layer);
    if ("children" in layer) {
      for (const child of layer.children) visit(child);
    }
  }

  for (const child of page.children) visit(child);
  return layers;
}

function edgeAnchor(b: Bounds, side: EdgeSide): { x: number; y: number } {
  const [nw, ne, se, sw] = b.corners;
  const desired: Record<EdgeSide, XY> = {
    top: { x: 0, y: -1 },
    right: { x: 1, y: 0 },
    bottom: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
  };
  const center = centerOf(b);
  const edges = [
    midpoint(nw, ne),
    midpoint(ne, se),
    midpoint(se, sw),
    midpoint(sw, nw),
  ];
  let best = edges[0];
  let bestScore = -Infinity;
  for (const edge of edges) {
    const dx = edge.x - center.x;
    const dy = edge.y - center.y;
    const len = Math.hypot(dx, dy) || 1;
    const score = (dx / len) * desired[side].x + (dy / len) * desired[side].y;
    if (score > bestScore) {
      best = edge;
      bestScore = score;
    }
  }
  return best;
}

function handlePoint(b: Bounds, side: EdgeSide, sc: number): { x: number; y: number } {
  const p = edgeAnchor(b, side);
  const offset = HANDLE_OFFSET_PX * sc;
  const c = centerOf(b);
  const dx = p.x - c.x;
  const dy = p.y - c.y;
  const len = Math.hypot(dx, dy) || 1;
  return { x: p.x + (dx / len) * offset, y: p.y + (dy / len) * offset };
}

function midpoint(a: XY, b: XY): XY {
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
}

function centerOf(b: Bounds): XY {
  return {
    x: (b.corners[0].x + b.corners[2].x) / 2,
    y: (b.corners[0].y + b.corners[2].y) / 2,
  };
}

function sideToward(from: Bounds, to: Bounds): EdgeSide {
  const fromCx = from.x + from.w / 2;
  const fromCy = from.y + from.h / 2;
  const toCx = to.x + to.w / 2;
  const toCy = to.y + to.h / 2;
  const dx = toCx - fromCx;
  const dy = toCy - fromCy;
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? "right" : "left";
  return dy >= 0 ? "bottom" : "top";
}

function oppositeSide(side: EdgeSide): EdgeSide {
  switch (side) {
    case "top":
      return "bottom";
    case "right":
      return "left";
    case "bottom":
      return "top";
    case "left":
      return "right";
  }
}

function bezierPath(from: { x: number; y: number }, to: { x: number; y: number }, fromSide: EdgeSide, toSide: EdgeSide): string {
  const gap = Math.max(Math.abs(to.x - from.x), Math.abs(to.y - from.y)) * 0.45 + 40;
  const dir: Record<EdgeSide, { x: number; y: number }> = {
    top: { x: 0, y: -1 },
    right: { x: 1, y: 0 },
    bottom: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
  };
  const a = dir[fromSide];
  const b = dir[toSide];
  const c1 = { x: from.x + a.x * gap, y: from.y + a.y * gap };
  const c2 = { x: to.x + b.x * gap, y: to.y + b.y * gap };
  return `M ${from.x} ${from.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${to.x} ${to.y}`;
}

function offsetForBidirectionalPair(src: Bounds, dst: Bounds, sourceLayerId: string, destinationFrameId: string, amount: number): { x: number; y: number } {
  const srcCenter = { x: src.x + src.w / 2, y: src.y + src.h / 2 };
  const dstCenter = { x: dst.x + dst.w / 2, y: dst.y + dst.h / 2 };
  const sourceIsCanonicalStart = sourceLayerId < destinationFrameId;
  const from = sourceIsCanonicalStart ? srcCenter : dstCenter;
  const to = sourceIsCanonicalStart ? dstCenter : srcCenter;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.hypot(dx, dy) || 1;
  const sign = sourceIsCanonicalStart ? 1 : -1;
  return { x: (-dy / len) * amount * sign, y: (dx / len) * amount * sign };
}

export function ConnectionArrows() {
  const tab = useStore((s) => s.activeRightTab);
  const page = useStore((s) => getActivePage(s));
  const appState = useStore((s) => s);
  const viewport = useStore((s) => s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 });
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const [drag, setDrag] = useState<DragState>(null);
  const [hoverDestId, setHoverDestId] = useState<string | null>(null);
  const [modalConnectionId, setModalConnectionId] = useState<string | null>(null);
  const svgGroupRef = useRef<SVGGElement>(null);

  const connections = page?.prototypeConnections ?? [];
  const sc = 1 / viewport.zoom;
  const bounds = buildBounds(appState, page);
  const allLayers = flattenLayers(page);
  const selectedIds = new Set(selection);
  const frameLayers = allLayers.filter((layer): layer is Frame => layer.type === "frame");
  const selectedFrameLayers = frameLayers.filter((frame) => selectedIds.has(frame.id));

  function screenToWorld(clientX: number, clientY: number): { x: number; y: number } {
    const svg = svgGroupRef.current?.ownerSVGElement;
    if (!svg) return { x: 0, y: 0 };
    const rect = svg.getBoundingClientRect();
    return clientToWorldPoint(clientX, clientY, viewport, rect);
  }

  function hitDestFrame(wx: number, wy: number, excludeId: string): Frame | undefined {
    let hit: Frame | undefined;
    const margin = DEST_HIT_MARGIN_PX * sc;
    for (const layer of frameLayers) {
      if (layer.id === excludeId) continue;
      const b = bounds.get(layer.id);
      if (!b) continue;
      if (pointInPolygonWithMargin({ x: wx, y: wy }, b.corners, margin)) {
        hit = layer;
      }
    }
    return hit;
  }

  function onDotDown(e: React.PointerEvent, layerId: string, side: EdgeSide, sx: number, sy: number) {
    e.stopPropagation();
    e.preventDefault();
    const w = screenToWorld(e.clientX, e.clientY);
    setDrag({ sourceId: layerId, sourceSide: side, sx, sy, cx: w.x, cy: w.y });
    setHoverDestId(null);
  }

  function updateDragFromPointer(clientX: number, clientY: number) {
    if (!drag) return;
    const w = screenToWorld(clientX, clientY);
    setDrag((d) => (d ? { ...d, cx: w.x, cy: w.y } : null));
    const dest = hitDestFrame(w.x, w.y, drag.sourceId);
    setHoverDestId(dest?.id ?? null);
  }

  function finishDrag(clientX: number, clientY: number) {
    if (!drag) return;
    if (!page) {
      setDrag(null);
      setHoverDestId(null);
      return;
    }
    const w = screenToWorld(clientX, clientY);
    const dest = hitDestFrame(w.x, w.y, drag.sourceId);
    if (dest) {
      const pageId = page.id;
      const id = uid("conn");
      const newConn: PrototypeConnection = {
        id,
        sourceLayerId: drag.sourceId,
        trigger: "on_tap",
        action: "navigate_to",
        destinationFrameId: dest.id,
        animation: "instant",
        delayMs: 800,
      };
      createPrototypeConnection(pageId, newConn);
      setModalConnectionId(id);
    }
    setDrag(null);
    setHoverDestId(null);
  }

  useEffect(() => {
    if (!drag) return;

    function onWindowMove(e: PointerEvent) {
      e.stopPropagation();
      e.preventDefault();
      updateDragFromPointer(e.clientX, e.clientY);
    }

    function onWindowUp(e: PointerEvent) {
      e.stopPropagation();
      e.preventDefault();
      finishDrag(e.clientX, e.clientY);
    }

    window.addEventListener("pointermove", onWindowMove, { capture: true });
    window.addEventListener("pointerup", onWindowUp, { capture: true, once: true });
    window.addEventListener("pointercancel", onWindowUp, { capture: true, once: true });
    return () => {
      window.removeEventListener("pointermove", onWindowMove, { capture: true });
      window.removeEventListener("pointerup", onWindowUp, { capture: true });
      window.removeEventListener("pointercancel", onWindowUp, { capture: true });
    };
  }, [drag?.sourceId, viewport.zoom, viewport.x, viewport.y, page?.id]);

  if (tab !== "prototype" || !page) return null;

  const modalConnection = modalConnectionId ? connections.find((conn) => conn.id === modalConnectionId) ?? null : null;

  function deleteConnection(id: string) {
    if (!page) return;
    deletePrototypeConnection(page.id, id);
    setModalConnectionId(null);
  }

  return (
    <>
    <g ref={svgGroupRef}>
      {/* Existing connection arrows */}
      {connections.map((conn) => {
        if (!conn.destinationFrameId) return null;
        const src = bounds.get(conn.sourceLayerId);
        const dst = bounds.get(conn.destinationFrameId);
        if (!src || !dst) return null;

        const srcSide = sideToward(src, dst);
        const dstSide = oppositeSide(srcSide);
        const reverseExists = connections.some(
          (other) =>
            other.id !== conn.id &&
            other.sourceLayerId === conn.destinationFrameId &&
            other.destinationFrameId === conn.sourceLayerId,
        );
        const offset = reverseExists && conn.destinationFrameId
          ? offsetForBidirectionalPair(src, dst, conn.sourceLayerId, conn.destinationFrameId, 12 * sc)
          : { x: 0, y: 0 };
        const rawStart = edgeAnchor(src, srcSide);
        const rawEnd = edgeAnchor(dst, dstSide);
        const start = { x: rawStart.x + offset.x, y: rawStart.y + offset.y };
        const end = { x: rawEnd.x + offset.x, y: rawEnd.y + offset.y };
        const path = bezierPath(start, end, srcSide, dstSide);
        const sz = sc * 8;
        const headAngle = Math.atan2(end.y - start.y, end.x - start.x);
        const lx1 = end.x + Math.cos(headAngle + Math.PI * 0.75) * sz;
        const ly1 = end.y + Math.sin(headAngle + Math.PI * 0.75) * sz;
        const lx2 = end.x + Math.cos(headAngle - Math.PI * 0.75) * sz;
        const ly2 = end.y + Math.sin(headAngle - Math.PI * 0.75) * sz;

        return (
          <g key={conn.id} style={{ pointerEvents: "none" }}>
            <path d={path} fill="none" stroke="rgba(0,0,0,0.25)" strokeWidth={3 * sc} strokeLinecap="round" />
            <path d={path} fill="none" stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <line x1={end.x} y1={end.y} x2={lx1} y2={ly1} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <line x1={end.x} y1={end.y} x2={lx2} y2={ly2} stroke={ARROW_COLOR} strokeWidth={1.5 * sc} strokeLinecap="round" />
            <circle cx={start.x} cy={start.y} r={3 * sc} fill={ARROW_COLOR} />
            <circle cx={end.x} cy={end.y} r={3 * sc} fill={ARROW_COLOR} />
          </g>
        );
      })}

      {/* Frame connector handles: drag from any side + to another frame. */}
      {!drag && selectedFrameLayers.flatMap((frame) => {
        const b = bounds.get(frame.id);
        if (!b) return [];
        const sides: EdgeSide[] = ["top", "right", "bottom", "left"];
        return sides.map((side) => {
          const anchor = edgeAnchor(b, side);
          const handle = handlePoint(b, side, sc);
          return (
          <g
            key={`connector-${frame.id}-${side}`}
            transform={`translate(${handle.x} ${handle.y}) scale(${sc})`}
            style={{ cursor: "crosshair" }}
            onPointerDown={(e) => onDotDown(e, frame.id, side, anchor.x, anchor.y)}
          >
            <circle cx={0} cy={0} r={HANDLE_HIT_R_PX} fill="transparent" />
            <circle cx={0} cy={0} r={DOT_R + 2} fill="rgba(20, 20, 20, 0.65)" stroke={ARROW_COLOR} strokeWidth={1.5} />
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
          );
        });
      })}

      {/* ── Active drag ──────────────────────────────────────────────── */}
      {drag && (() => {
        const start = { x: drag.sx, y: drag.sy };
        const end = { x: drag.cx, y: drag.cy };
        const path = bezierPath(start, end, drag.sourceSide, oppositeSide(drag.sourceSide));

        return (
          <>
            {/* Huge transparent overlay that captures all pointer events */}
            <rect
              x={-1e7} y={-1e7} width={2e7} height={2e7}
              fill="transparent"
              style={{ cursor: "crosshair" }}
              onPointerMove={(e) => {
                e.stopPropagation();
                e.preventDefault();
                updateDragFromPointer(e.clientX, e.clientY);
              }}
              onPointerUp={(e) => {
                e.stopPropagation();
                e.preventDefault();
                finishDrag(e.clientX, e.clientY);
              }}
            />

            {/* Destination frame highlight */}
            {hoverDestId && (() => {
              const db = bounds.get(hoverDestId);
              if (!db) return null;
              return (
                <polygon
                  points={db.corners.map((p) => `${p.x},${p.y}`).join(" ")}
                  fill="none"
                  stroke={ARROW_COLOR}
                  strokeWidth={2 * sc}
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
    {modalConnection && createPortal(
      <InteractionModal
        connection={modalConnection}
        sourceLayerId={modalConnection.sourceLayerId}
        pageId={page.id}
        frames={frameLayers}
        onClose={() => setModalConnectionId(null)}
        onDelete={deleteConnection}
      />,
      document.body,
    )}
    </>
  );
}

function pointInPolygonWithMargin(point: XY, polygon: XY[], margin: number): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[i];
    const b = polygon[j];
    if (pointToSegmentDistance(point, a, b) <= margin) return true;
    const crosses = a.y > point.y !== b.y > point.y;
    if (crosses) {
      const xAtY = ((b.x - a.x) * (point.y - a.y)) / (b.y - a.y) + a.x;
      if (point.x < xAtY) inside = !inside;
    }
  }
  return inside;
}

function pointToSegmentDistance(point: XY, a: XY, b: XY): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len2 = dx * dx + dy * dy;
  if (len2 === 0) return Math.hypot(point.x - a.x, point.y - a.y);
  let t = ((point.x - a.x) * dx + (point.y - a.y) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(point.x - (a.x + dx * t), point.y - (a.y + dy * t));
}
