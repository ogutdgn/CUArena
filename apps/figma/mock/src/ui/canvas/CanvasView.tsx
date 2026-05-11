// SVG canvas root. Owns viewport (pan/zoom) and routes pointer events to the
// active tool. Renders the active page's layer tree + selection overlay + marquee.

import { useEffect, useRef, useState } from "react";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { getActivePage, hitTest, selectionBbox } from "@/engine/selectors";
import { setSelection } from "@/engine/commands";
import { getActiveTool } from "@/tools";
import { NodeRenderer } from "./NodeRenderer";
import { emitSemantic } from "@/logger/semantic";
import { SelectionOverlay } from "@/ui/overlays/SelectionOverlay";
import { VectorEditOverlay } from "@/ui/overlays/VectorEditOverlay";
import { HoverOutline } from "@/ui/overlays/HoverOutline";
import { ParentBoundsOverlay } from "@/ui/overlays/ParentBoundsOverlay";
import { PenPreview } from "@/ui/overlays/PenPreview";
import { PencilPreview } from "@/ui/overlays/PencilPreview";
import { InsertionCrosshair } from "@/ui/overlays/InsertionCrosshair";
import { RotateReadout } from "@/ui/overlays/RotateReadout";
import { ConnectionArrows } from "@/ui/overlays/ConnectionArrows";
import { FrameLabelsOverlay } from "@/ui/overlays/FrameLabelsOverlay";
import { placeImageFiles } from "@/engine/imageCommands";
import { clientToWorldPoint, svgWorldTransform } from "@/engine/viewportCoordinates";

const MIN_ZOOM = 0.05;
const MAX_ZOOM = 32;

export function CanvasView() {
  const ref = useRef<SVGSVGElement | null>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const activeTool = useStore((s) => s.activeTool);
  const viewport = useStore((s) => s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 });
  const page = useStore((s) => getActivePage(s));
  const dragPreview = useStore((s) => s.dragPreview);
  const snapLines = useStore((s) => s.snapLines);
  const snapMeasures = useStore((s) => s.snapMeasures);
  // selectionBbox subscription is consumed by SelectionOverlay, not here.
  void selectionBbox;
  const pageBg = page
    ? `rgba(${Math.round(page.backgroundColor.r * 255)}, ${Math.round(page.backgroundColor.g * 255)}, ${Math.round(page.backgroundColor.b * 255)}, ${page.backgroundColor.a})`
    : "white";
  const bgHidden = page?.backgroundHidden === true;
  const checkerPatternId = "canvas-bg-checker";

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => {
      const r = el.getBoundingClientRect();
      setCanvasSize({ width: r.width, height: r.height });
    };
    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  function clientToWorld(clientX: number, clientY: number): { x: number; y: number } {
    const el = ref.current;
    if (!el) return { x: 0, y: 0 };
    const rect = el.getBoundingClientRect();
    return clientToWorldPoint(clientX, clientY, viewport, rect);
  }

  function effectiveTool(): typeof activeTool {
    return useStore.getState().spaceDown ? "hand" : activeTool;
  }

  function onPointerDown(e: React.PointerEvent<SVGSVGElement>) {
    if (e.button !== 0) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    const world = clientToWorld(e.clientX, e.clientY);
    getActiveTool(effectiveTool()).onPointerDown?.(world, e.nativeEvent);
  }
  function onPointerMove(e: React.PointerEvent<SVGSVGElement>) {
    const world = clientToWorld(e.clientX, e.clientY);
    const tool = effectiveTool();
    getActiveTool(tool).onPointerMove?.(world, e.nativeEvent);
    if (tool !== "hand") {
      useStore.setState((s) => {
        s.cursorWorld = world;
        s.insertionCursor = world;
      });
    }
  }
  function onPointerUp(e: React.PointerEvent<SVGSVGElement>) {
    const world = clientToWorld(e.clientX, e.clientY);
    getActiveTool(effectiveTool()).onPointerUp?.(world, e.nativeEvent);
    if (e.currentTarget.hasPointerCapture(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  }

  // Native non-passive wheel listener so we can preventDefault and stop the
  // browser from page-zooming on trackpad pinch (ctrl+wheel). React's onWheel
  // is attached passively on the root and would no-op preventDefault.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      const s = useStore.getState();
      const cur = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
      const isZoom = e.ctrlKey || e.metaKey;
      if (isZoom) {
        const rect = el.getBoundingClientRect();
        const cursorWorld = clientToWorldPoint(e.clientX, e.clientY, cur, rect);
        const factor = Math.exp(-e.deltaY * 0.005);
        const newZoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, cur.zoom * factor));
        const newViewport = {
          x: cursorWorld.x - (e.clientX - rect.left - rect.width / 2) / newZoom,
          y: cursorWorld.y - (e.clientY - rect.top - rect.height / 2) / newZoom,
          zoom: newZoom,
        };
        dispatch(
          {
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_viewport",
            pageId: s.activePageId,
            before: cur,
            after: newViewport,
          },
          { skipUndo: true },
        );
        emitSemantic({
          name: "zoom_canvas",
          before: cur.zoom,
          after: newZoom,
          anchor: cursorWorld,
          trigger: "scroll",
        });
      } else {
        const factor = 1 / cur.zoom;
        dispatch(
          {
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_viewport",
            pageId: s.activePageId,
            before: cur,
            after: { ...cur, x: cur.x + e.deltaX * factor, y: cur.y + e.deltaY * factor },
          },
          { skipUndo: true },
        );
      }
    };
    el.addEventListener("wheel", handler, { passive: false });
    return () => el.removeEventListener("wheel", handler);
  }, []);

  function onContextMenu(e: React.MouseEvent<SVGSVGElement>) {
    e.preventDefault();
    // If right-clicking on a layer that isn't selected, select it first.
    const world = clientToWorld(e.clientX, e.clientY);
    const sNow = useStore.getState();
    const hit = hitTest(sNow, world.x, world.y);
    if (hit) {
      const cur = sNow.selectionByPage[sNow.activePageId] ?? [];
      if (!cur.includes(hit.id)) {
        setSelection([hit.id], "click_select");
      }
    }
    useStore.setState((s) => {
      s.contextMenu = { x: e.clientX, y: e.clientY };
    });
  }

  function onDragOver(e: React.DragEvent<SVGSVGElement>) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  }
  function onDrop(e: React.DragEvent<SVGSVGElement>) {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith("image/"));
    if (files.length === 0) return;
    const world = clientToWorld(e.clientX, e.clientY);
    placeImageFiles(files, "drag_drop", { worldX: world.x, worldY: world.y });
  }

  const hoveredId = useStore((s) => s.hoveredNodeId);
  const spaceDown = useStore((s) => s.spaceDown);
  const cursor = spaceDown
    ? "grab"
    : activeTool === "hand"
      ? "grab"
      : activeTool === "rectangle" ||
        activeTool === "ellipse" ||
        activeTool === "polygon" ||
        activeTool === "star" ||
        activeTool === "line" ||
        activeTool === "arrow" ||
        activeTool === "frame" ||
        activeTool === "section" ||
        activeTool === "slice"
      ? "crosshair"
      : activeTool === "text"
      ? "text"
      : activeTool === "pen" || activeTool === "pencil"
      ? "crosshair"
      : activeTool === "move" && hoveredId
      ? "move"
      : "default";

  return (
    <svg
      ref={ref}
      className="canvas-svg"
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        cursor,
        touchAction: "none",
        userSelect: "none",
      }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onContextMenu={onContextMenu}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      {/* Backdrop — checker always present underneath so partial alpha shows through.
          Color rect sits on top; when background is hidden the color is invisible. */}
      <defs>
        <pattern id={checkerPatternId} width={16} height={16} patternUnits="userSpaceOnUse">
          <rect x={0} y={0} width={16} height={16} fill="#2a2a2a" />
          <rect x={0} y={0} width={8} height={8} fill="#1e1e1e" />
          <rect x={8} y={8} width={8} height={8} fill="#1e1e1e" />
        </pattern>
      </defs>
      <rect x="0" y="0" width="100%" height="100%" fill={`url(#${checkerPatternId})`} />
      <rect
        data-id="canvas-backdrop"
        x="0"
        y="0"
        width="100%"
        height="100%"
        fill={pageBg}
        opacity={bgHidden ? 0 : 1}
      />

      {/* World-space group. With zoom=1 and viewport=(0,0), world origin is the visible canvas center. */}
      <g transform={svgWorldTransform(viewport, canvasSize)}>
        {page && page.children.map((l) => <NodeRenderer key={l.id} layer={l} />)}

        <FrameLabelsOverlay />
        <HoverOutline />
        <ParentBoundsOverlay />
        <SelectionOverlay />
        <VectorEditOverlay />
        <PenPreview />
        <PencilPreview />
        <InsertionCrosshair />
        <RotateReadout />
        <ConnectionArrows />

        {snapLines.map((l, i) =>
          l.axis === "x" ? (
            <line
              key={i}
              x1={l.x}
              y1={l.yMin}
              x2={l.x}
              y2={l.yMax}
              stroke="#FF3B82"
              strokeWidth={1 / viewport.zoom}
              pointerEvents="none"
            />
          ) : (
            <line
              key={i}
              x1={l.xMin}
              y1={l.y}
              x2={l.xMax}
              y2={l.y}
              stroke="#FF3B82"
              strokeWidth={1 / viewport.zoom}
              pointerEvents="none"
            />
          ),
        )}
        {snapMeasures.map((m, i) => {
          const fontSize = 11 / viewport.zoom;
          const padX = 4 / viewport.zoom;
          const padY = 2 / viewport.zoom;
          const text = String(Math.round(m.value));
          const charW = 6.5 / viewport.zoom;
          const w = text.length * charW + padX * 2;
          const h = fontSize + padY * 2;
          const cx = (m.x1 + m.x2) / 2;
          const cy = (m.y1 + m.y2) / 2;
          const offset = m.axis === "y" ? 8 / viewport.zoom : 0;
          const tickLen = 4 / viewport.zoom;
          return (
            <g key={`m${i}`} pointerEvents="none">
              <line x1={m.x1} y1={m.y1} x2={m.x2} y2={m.y2} stroke="#FF3B82" strokeWidth={1 / viewport.zoom} />
              {m.axis === "y" && (
                <>
                  <line x1={m.x1 - tickLen} y1={m.y1} x2={m.x1 + tickLen} y2={m.y1} stroke="#FF3B82" strokeWidth={1 / viewport.zoom} />
                  <line x1={m.x2 - tickLen} y1={m.y2} x2={m.x2 + tickLen} y2={m.y2} stroke="#FF3B82" strokeWidth={1 / viewport.zoom} />
                </>
              )}
              {m.axis === "x" && (
                <>
                  <line x1={m.x1} y1={m.y1 - tickLen} x2={m.x1} y2={m.y1 + tickLen} stroke="#FF3B82" strokeWidth={1 / viewport.zoom} />
                  <line x1={m.x2} y1={m.y2 - tickLen} x2={m.x2} y2={m.y2 + tickLen} stroke="#FF3B82" strokeWidth={1 / viewport.zoom} />
                </>
              )}
              <rect
                x={cx + offset - w / 2}
                y={cy - h / 2}
                width={w}
                height={h}
                fill="#FF3B82"
                rx={2 / viewport.zoom}
              />
              <text
                x={cx + offset}
                y={cy + fontSize / 3}
                fill="white"
                fontSize={fontSize}
                textAnchor="middle"
                style={{ fontFamily: "var(--font-family)", fontWeight: 500 }}
              >
                {text}
              </text>
            </g>
          );
        })}

        {dragPreview.kind === "marquee" && (
          <rect
            x={(dragPreview.data as { x: number; y: number; w: number; h: number }).x}
            y={(dragPreview.data as { x: number; y: number; w: number; h: number }).y}
            width={(dragPreview.data as { x: number; y: number; w: number; h: number }).w}
            height={(dragPreview.data as { x: number; y: number; w: number; h: number }).h}
            fill="rgba(13,153,255,0.08)"
            stroke="var(--color-selection-blue)"
            strokeWidth={1 / viewport.zoom}
            pointerEvents="none"
          />
        )}
        {dragPreview.kind === "create_shape" && (
          (() => {
            const d = dragPreview.data as {
              x: number;
              y: number;
              w: number;
              h: number;
              shape?: string;
              x1?: number;
              y1?: number;
              x2?: number;
              y2?: number;
            };
            const shape = d.shape ?? "rectangle";
            const fill =
              shape === "frame"
                ? "rgba(235,235,235,1)"
                : shape === "section"
                ? "rgba(242,242,242,1)"
                : shape === "slice" || shape === "line" || shape === "arrow"
                ? "transparent"
                : "rgba(217,217,217,1)";
            const stroke =
              shape === "line" || shape === "arrow"
                ? "rgba(255,255,255,1)"
                : shape === "slice"
                ? "orange"
                : "var(--color-selection-blue)";
            const sw = 1 / viewport.zoom;
            if ((d.shape === "line" || d.shape === "arrow") && d.x1 != null && d.y1 != null && d.x2 != null && d.y2 != null) {
              if (d.shape === "arrow") {
                const markerId = `preview-arrow-${Math.round(d.x1)}-${Math.round(d.y1)}-${Math.round(d.x2)}-${Math.round(d.y2)}`;
                return (
                  <g pointerEvents="none">
                    <defs>
                      <marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill={stroke} />
                      </marker>
                    </defs>
                    <line x1={d.x1} y1={d.y1} x2={d.x2} y2={d.y2} stroke={stroke} strokeWidth={sw} markerEnd={`url(#${markerId})`} />
                  </g>
                );
              }
              return <line x1={d.x1} y1={d.y1} x2={d.x2} y2={d.y2} stroke={stroke} strokeWidth={sw} pointerEvents="none" />;
            }
            if (d.shape === "ellipse") {
              return (
                <ellipse
                  cx={d.x + d.w / 2}
                  cy={d.y + d.h / 2}
                  rx={d.w / 2}
                  ry={d.h / 2}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={sw}
                  pointerEvents="none"
                />
              );
            }
            if (d.shape === "polygon") {
              const sides = 3;
              const cx = d.x + d.w / 2;
              const cy = d.y + d.h / 2;
              const rx = d.w / 2;
              const ry = d.h / 2;
              const pts: string[] = [];
              for (let i = 0; i < sides; i++) {
                const angle = -Math.PI / 2 + (i * 2 * Math.PI) / sides;
                pts.push(`${cx + Math.cos(angle) * rx},${cy + Math.sin(angle) * ry}`);
              }
              return <polygon points={pts.join(" ")} fill={fill} stroke={stroke} strokeWidth={sw} pointerEvents="none" />;
            }
            if (d.shape === "star") {
              const points = 5;
              const inner = 0.5;
              const cx = d.x + d.w / 2;
              const cy = d.y + d.h / 2;
              const rx = d.w / 2;
              const ry = d.h / 2;
              const pts: string[] = [];
              for (let i = 0; i < points * 2; i++) {
                const angle = -Math.PI / 2 + (i * Math.PI) / points;
                const r = i % 2 === 0 ? 1 : inner;
                pts.push(`${cx + Math.cos(angle) * rx * r},${cy + Math.sin(angle) * ry * r}`);
              }
              return <polygon points={pts.join(" ")} fill={fill} stroke={stroke} strokeWidth={sw} pointerEvents="none" />;
            }
            return (
              <rect
                x={d.x}
                y={d.y}
                width={d.w}
                height={d.h}
                fill={fill}
                stroke={stroke}
                strokeWidth={sw}
                strokeDasharray={shape === "slice" ? `${4 / viewport.zoom} ${3 / viewport.zoom}` : undefined}
                pointerEvents="none"
              />
            );
          })()
        )}
      </g>
    </svg>
  );
}
