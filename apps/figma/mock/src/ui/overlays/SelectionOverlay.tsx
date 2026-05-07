// Selection overlay: bbox + 8 resize handles. Rendered inside the world-space
// group so it follows pan/zoom, but handle sizes are scaled by 1/zoom so they
// appear constant pixel size on screen.

import { useStore, selectActiveViewport } from "@/engine/store";
import { selectionBbox } from "@/engine/selectors";
import { worldOffsetOfLayer } from "@/engine/coordinates";
import type { Rect } from "@/util/geometry";
import type { Layer } from "@/types/scene";

const HANDLE_SIZE_PX = 8; // visual diameter on screen
const HANDLE_HIT_PADDING_PX = 4;
const ROTATE_RING_PX = 16;

export type HandleDir = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";
export type RotateCorner = "ne" | "nw" | "se" | "sw";

export function SelectionOverlay() {
  const viewport = useStore((s) => selectActiveViewport(s));
  const bbox = useStore((s) => selectionBbox(s));
  const editMode = useStore((s) => s.editMode);
  const activeTool = useStore((s) => s.activeTool);
  const activeRightTab = useStore((s) => s.activeRightTab);
  // Detect a single-line/arrow selection. Lines are 2-point geometry, not
  // bounding-box-wrapped rectangles, so the standard 8-handle bbox treats
  // them like a rect. Render a line overlay + 2 endpoint markers instead.
  // Per-line endpoint resize (drag p1/p2) is deferred (item 21f).
  const lineSelection = useStore((s) => {
    const ids = s.selectionByPage[s.activePageId] ?? [];
    if (ids.length !== 1) return null;
    const node = s.nodesById[ids[0]] as Layer | undefined;
    if (!node) return null;
    if (node.type !== "line" && node.type !== "arrow") return null;
    // World-space layer top-left = ancestor offset + layer.x/y (no transform).
    // Applies the layer's scale + rotation around its bbox center to each
    // endpoint, matching what NodeRenderer's commonTransform does in SVG.
    // Without this, flipping a line via the panel button would leave the
    // overlay drawn in the un-flipped position.
    const off = worldOffsetOfLayer(s, node);
    const wx = off.x - node.x + node.x;
    const wy = off.y - node.y + node.y;
    const cx = node.w / 2;
    const cy = node.h / 2;
    const transform = (lx: number, ly: number) => {
      let px = lx;
      let py = ly;
      if (node.scaleX !== 1 || node.scaleY !== 1) {
        px = cx + (px - cx) * node.scaleX;
        py = cy + (py - cy) * node.scaleY;
      }
      if (node.rotation !== 0) {
        const rad = (node.rotation * Math.PI) / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        const dx = px - cx;
        const dy = py - cy;
        px = cx + dx * cos - dy * sin;
        py = cy + dx * sin + dy * cos;
      }
      return { x: wx + px, y: wy + py };
    };
    return {
      p1: transform(node.p1.x, node.p1.y),
      p2: transform(node.p2.x, node.p2.y),
    };
  });
  if (!bbox) return null;
  // Pen mode should render anchor/handle previews only (no selection bbox).
  if (activeTool === "pen") return null;
  // Suppress handles/rotate hits when in a sub-mode (vector edit / text edit /
  // pen creation) — bbox stroke alone is enough.
  const minimal = editMode.kind === "vector" || editMode.kind === "text" || editMode.kind === "pen_creation";
  if (minimal) {
    const sw = 1 / viewport.zoom;
    return (
      <rect
        x={bbox.x}
        y={bbox.y}
        width={bbox.w}
        height={bbox.h}
        fill="none"
        stroke="var(--color-selection-blue)"
        strokeWidth={sw}
        pointerEvents="none"
      />
    );
  }

  const sw = 1 / viewport.zoom;
  const handle = HANDLE_SIZE_PX / viewport.zoom;
  const hitExtra = HANDLE_HIT_PADDING_PX / viewport.zoom;
  const handles = activeRightTab === "prototype" ? cornerHandlePositions(bbox) : handlePositions(bbox);

  const rotateRing = ROTATE_RING_PX / viewport.zoom;
  return (
    <g pointerEvents="all">
      {/* Rotate hit areas — transparent quarter-circles outside each corner. */}
      <RotateCorners bbox={bbox} radius={rotateRing} />

      {/* Bbox stroke */}
      <rect
        x={bbox.x}
        y={bbox.y}
        width={bbox.w}
        height={bbox.h}
        fill="none"
        stroke="var(--color-selection-blue)"
        strokeWidth={sw}
        pointerEvents="none"
      />
      <WHLabel bbox={bbox} zoom={viewport.zoom} />
      {handles.map((p) => (
        <Handle
          key={p.dir}
          dir={p.dir}
          cx={p.x}
          cy={p.y}
          size={handle}
          hit={handle + hitExtra}
          stroke={sw}
        />
      ))}
      {lineSelection && (
        <>
          {/* Visual line overlay + endpoint markers. Bbox + handles above
              still render so the user retains resize until item 21f ships
              proper endpoint-drag resize. */}
          <line
            x1={lineSelection.p1.x}
            y1={lineSelection.p1.y}
            x2={lineSelection.p2.x}
            y2={lineSelection.p2.y}
            stroke="var(--color-selection-blue)"
            strokeWidth={1.5 / viewport.zoom}
            pointerEvents="none"
          />
          <EndpointMarker x={lineSelection.p1.x} y={lineSelection.p1.y} size={HANDLE_SIZE_PX / viewport.zoom} stroke={1 / viewport.zoom} />
          <EndpointMarker x={lineSelection.p2.x} y={lineSelection.p2.y} size={HANDLE_SIZE_PX / viewport.zoom} stroke={1 / viewport.zoom} />
        </>
      )}
    </g>
  );
}

function EndpointMarker({ x, y, size, stroke }: { x: number; y: number; size: number; stroke: number }) {
  const half = size / 2;
  return (
    <rect
      x={x - half}
      y={y - half}
      width={size}
      height={size}
      fill="white"
      stroke="var(--color-selection-blue)"
      strokeWidth={stroke}
    />
  );
}

function RotateCorners({ bbox, radius }: { bbox: Rect; radius: number }) {
  // Rotate hit boxes sit ENTIRELY OUTSIDE the bbox so they never steal pointer
  // events from clicks inside the layer. Each is a square at the corner's
  // outward diagonal.
  const r = radius;
  const corners: Array<{ dir: RotateCorner; x: number; y: number }> = [
    { dir: "nw", x: bbox.x - r, y: bbox.y - r },
    { dir: "ne", x: bbox.x + bbox.w, y: bbox.y - r },
    { dir: "se", x: bbox.x + bbox.w, y: bbox.y + bbox.h },
    { dir: "sw", x: bbox.x - r, y: bbox.y + bbox.h },
  ];
  return (
    <>
      {corners.map((c) => (
        <rect
          key={c.dir}
          data-id={`selection.rotate.${c.dir}`}
          data-rotate={c.dir}
          x={c.x}
          y={c.y}
          width={r}
          height={r}
          fill="transparent"
          pointerEvents="all"
          style={{ cursor: "crosshair" }}
        />
      ))}
    </>
  );
}

function Handle({ dir, cx, cy, size, hit, stroke }: { dir: HandleDir; cx: number; cy: number; size: number; hit: number; stroke: number }) {
  const half = size / 2;
  const halfHit = hit / 2;
  const cursor = cursorFor(dir);
  return (
    <g style={{ cursor }}>
      {/* Hit area, transparent */}
      <rect
        data-id={`selection.handle.${dir}`}
        data-handle={dir}
        x={cx - halfHit}
        y={cy - halfHit}
        width={hit}
        height={hit}
        fill="transparent"
        pointerEvents="all"
      />
      {/* Visible square */}
      <rect
        x={cx - half}
        y={cy - half}
        width={size}
        height={size}
        fill="white"
        stroke="var(--color-selection-blue)"
        strokeWidth={stroke}
        pointerEvents="none"
      />
    </g>
  );
}

function cursorFor(dir: HandleDir): string {
  switch (dir) {
    case "n":
    case "s":
      return "ns-resize";
    case "e":
    case "w":
      return "ew-resize";
    case "ne":
    case "sw":
      return "nesw-resize";
    case "nw":
    case "se":
      return "nwse-resize";
  }
}

export function handlePositions(b: Rect): Array<{ dir: HandleDir; x: number; y: number }> {
  const cx = b.x + b.w / 2;
  const cy = b.y + b.h / 2;
  return [
    { dir: "nw", x: b.x, y: b.y },
    { dir: "n", x: cx, y: b.y },
    { dir: "ne", x: b.x + b.w, y: b.y },
    { dir: "e", x: b.x + b.w, y: cy },
    { dir: "se", x: b.x + b.w, y: b.y + b.h },
    { dir: "s", x: cx, y: b.y + b.h },
    { dir: "sw", x: b.x, y: b.y + b.h },
    { dir: "w", x: b.x, y: cy },
  ];
}

function cornerHandlePositions(b: Rect): Array<{ dir: HandleDir; x: number; y: number }> {
  return [
    { dir: "nw", x: b.x, y: b.y },
    { dir: "ne", x: b.x + b.w, y: b.y },
    { dir: "se", x: b.x + b.w, y: b.y + b.h },
    { dir: "sw", x: b.x, y: b.y + b.h },
  ];
}

function WHLabel({ bbox, zoom }: { bbox: Rect; zoom: number }) {
  const text = `${Math.round(bbox.w)} × ${Math.round(bbox.h)}`;
  const padX = 4 / zoom;
  const padY = 2 / zoom;
  const fontSize = 11 / zoom;
  const charW = 6.5 / zoom;
  const w = text.length * charW + padX * 2;
  const h = fontSize + padY * 2;
  const x = bbox.x + (bbox.w - w) / 2;
  const y = bbox.y + bbox.h + 4 / zoom;
  return (
    <g pointerEvents="none">
      <rect x={x} y={y} width={w} height={h} fill="var(--color-selection-blue)" rx={2 / zoom} />
      <text
        x={x + w / 2}
        y={y + h / 2 + fontSize / 3}
        fill="white"
        fontSize={fontSize}
        textAnchor="middle"
        style={{ fontFamily: "var(--font-family)", fontWeight: 500 }}
      >
        {text}
      </text>
    </g>
  );
}
