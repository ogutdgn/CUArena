// Selection overlay: bbox + 8 resize handles. Rendered inside the world-space
// group so it follows pan/zoom, but handle sizes are scaled by 1/zoom so they
// appear constant pixel size on screen.

import { useStore, selectActiveViewport } from "@/engine/store";
import { selectionOutlineGeometry } from "./selectionOverlayGeometry";
import { localPointToWorld } from "@/engine/coordinates";
import type { Rect } from "@/util/geometry";
import type { Layer } from "@/types/scene";

const HANDLE_SIZE_PX = 8; // visual diameter on screen
const HANDLE_HIT_PADDING_PX = 4;
const ROTATE_RING_PX = 16;

export type HandleDir = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";
export type RotateCorner = "ne" | "nw" | "se" | "sw";
type HandlePoint = { dir: HandleDir; x: number; y: number; cursor?: string };

export function SelectionOverlay() {
  const viewport = useStore((s) => selectActiveViewport(s));
  const outline = useStore((s) => selectionOutlineGeometry(s));
  const visibleOutline = outline.kind === "none" ? null : outline;
  const bbox = visibleOutline?.bbox ?? null;
  const editMode = useStore((s) => s.editMode);
  const activeTool = useStore((s) => s.activeTool);
  const activeRightTab = useStore((s) => s.activeRightTab);
  // Detect a single-line/arrow selection. Lines are 2-point geometry, not
  // bounding-box-wrapped rectangles, so the selection affordance is the
  // segment itself with two endpoint handles.
  const lineSelection = useStore((s) => {
    const ids = s.selectionByPage[s.activePageId] ?? [];
    if (ids.length !== 1) return null;
    const node = s.nodesById[ids[0]] as Layer | undefined;
    if (!node) return null;
    if (node.type !== "line" && node.type !== "arrow") return null;
    return {
      id: node.id,
      p1: localPointToWorld(s, node, node.p1),
      p2: localPointToWorld(s, node, node.p2),
    };
  });
  // Pen mode should render anchor/handle previews only (no selection bbox).
  if (activeTool === "pen") return null;
  if (lineSelection) {
    const sw = 1 / viewport.zoom;
    const handle = HANDLE_SIZE_PX / viewport.zoom;
    const hitExtra = HANDLE_HIT_PADDING_PX / viewport.zoom;
    const length = Math.hypot(lineSelection.p2.x - lineSelection.p1.x, lineSelection.p2.y - lineSelection.p1.y);
    return (
      <g pointerEvents="all">
        <line
          x1={lineSelection.p1.x}
          y1={lineSelection.p1.y}
          x2={lineSelection.p2.x}
          y2={lineSelection.p2.y}
          stroke="var(--color-selection-blue)"
          strokeWidth={1.5 / viewport.zoom}
          pointerEvents="none"
        />
        <LineEndpointHandle
          endpoint="p1"
          x={lineSelection.p1.x}
          y={lineSelection.p1.y}
          size={handle}
          hit={handle + hitExtra}
          stroke={sw}
        />
        <LineEndpointHandle
          endpoint="p2"
          x={lineSelection.p2.x}
          y={lineSelection.p2.y}
          size={handle}
          hit={handle + hitExtra}
          stroke={sw}
        />
        <LineLengthLabel
          p1={lineSelection.p1}
          p2={lineSelection.p2}
          length={length}
          zoom={viewport.zoom}
        />
      </g>
    );
  }
  if (!bbox || !visibleOutline) return null;
  // Suppress handles/rotate hits when in a sub-mode (vector edit / text edit /
  // pen creation) — bbox stroke alone is enough.
  const minimal = editMode.kind === "vector" || editMode.kind === "text" || editMode.kind === "pen_creation";
  if (minimal) {
    // TextEditor draws its own 1.5px selection-blue CSS border on the
    // contentEditable overlay; emitting a second SVG outline at the same
    // world position visibly doubles it. Suppress the SVG outline only for
    // text edit; vector / pen_creation still need the bbox stroke.
    if (editMode.kind === "text") return null;
    const sw = 1 / viewport.zoom;
    return (
      <SelectionOutline outline={visibleOutline} strokeWidth={sw} />
    );
  }

  const sw = 1 / viewport.zoom;
  const handle = HANDLE_SIZE_PX / viewport.zoom;
  const hitExtra = HANDLE_HIT_PADDING_PX / viewport.zoom;
  const visualOnlyTransformed = outlineIsTransformedSingle(visibleOutline);
  const orientedOutline = visualOnlyTransformed && visibleOutline.kind === "single_oriented" ? visibleOutline : null;
  const handles = visualOnlyTransformed
    ? (activeRightTab === "prototype" ? cornerHandlePositionsForOutline(orientedOutline!) : handlePositionsForOutline(orientedOutline!))
    : (activeRightTab === "prototype" ? cornerHandlePositions(bbox) : handlePositions(bbox));

  const rotateRing = ROTATE_RING_PX / viewport.zoom;
  return (
    <g pointerEvents="all">
      {/* Rotate hit areas — transparent quarter-circles outside each corner. */}
      {!visualOnlyTransformed && <RotateCorners bbox={bbox} radius={rotateRing} />}

      {/* Bbox stroke */}
      <SelectionOutline outline={visibleOutline} strokeWidth={sw} />
      <WHLabel bbox={bbox} visualBbox={visibleOutline.kind === "single_oriented" ? visibleOutline.visualBbox : bbox} zoom={viewport.zoom} />
      {handles.map((p) => visualOnlyTransformed ? (
        <Handle key={p.dir} dir={p.dir} cx={p.x} cy={p.y} size={handle} hit={handle + hitExtra} stroke={sw} cursor={p.cursor} />
      ) : (
        <Handle key={p.dir} dir={p.dir} cx={p.x} cy={p.y} size={handle} hit={handle + hitExtra} stroke={sw} cursor={p.cursor} />
      ))}
    </g>
  );
}

function outlineIsTransformedSingle(outline: Exclude<ReturnType<typeof selectionOutlineGeometry>, { kind: "none" }>): boolean {
  if (outline.kind !== "single_oriented") return false;
  const [nw, ne, se, sw] = outline.points;
  const b = outline.bbox;
  const expected = [
    { x: b.x, y: b.y },
    { x: b.x + b.w, y: b.y },
    { x: b.x + b.w, y: b.y + b.h },
    { x: b.x, y: b.y + b.h },
  ];
  return [nw, ne, se, sw].some((p, i) => Math.abs(p.x - expected[i].x) > 0.01 || Math.abs(p.y - expected[i].y) > 0.01);
}

function SelectionOutline({ outline, strokeWidth }: { outline: Exclude<ReturnType<typeof selectionOutlineGeometry>, { kind: "none" }>; strokeWidth: number }) {
  if (outline.kind === "single_oriented") {
    return (
      <polygon
        points={outline.points.map((p) => `${p.x},${p.y}`).join(" ")}
        fill="none"
        stroke="var(--color-selection-blue)"
        strokeWidth={strokeWidth}
        pointerEvents="none"
      />
    );
  }
  return (
    <rect
      x={outline.bbox.x}
      y={outline.bbox.y}
      width={outline.bbox.w}
      height={outline.bbox.h}
      fill="none"
      stroke="var(--color-selection-blue)"
      strokeWidth={strokeWidth}
      pointerEvents="none"
    />
  );
}

function LineEndpointHandle({
  endpoint,
  x,
  y,
  size,
  hit,
  stroke,
}: {
  endpoint: "p1" | "p2";
  x: number;
  y: number;
  size: number;
  hit: number;
  stroke: number;
}) {
  const half = size / 2;
  const halfHit = hit / 2;
  return (
    <g style={{ cursor: "move" }}>
      <rect
        data-id={`selection.line.${endpoint}`}
        data-line-endpoint={endpoint}
        x={x - halfHit}
        y={y - halfHit}
        width={hit}
        height={hit}
        fill="transparent"
        pointerEvents="all"
      />
      <rect
        x={x - half}
        y={y - half}
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

function LineLengthLabel({
  p1,
  p2,
  length,
  zoom,
}: {
  p1: { x: number; y: number };
  p2: { x: number; y: number };
  length: number;
  zoom: number;
}) {
  const text = `${length.toFixed(2)} × 0`;
  const mid = midpoint(p1, p2);
  const angle = (Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180) / Math.PI;
  const padX = 4 / zoom;
  const padY = 2 / zoom;
  const fontSize = 11 / zoom;
  const charW = 6.5 / zoom;
  const w = text.length * charW + padX * 2;
  const h = fontSize + padY * 2;
  return (
    <g transform={`translate(${mid.x} ${mid.y}) rotate(${angle})`} pointerEvents="none">
      <rect x={-w / 2} y={-h / 2} width={w} height={h} fill="var(--color-selection-blue)" rx={2 / zoom} />
      <text
        x={0}
        y={fontSize / 3}
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
  return <RotateCornerRects corners={corners} radius={r} />;
}

function RotateCornerRects({ corners, radius }: { corners: Array<{ dir: RotateCorner; x: number; y: number }>; radius: number }) {
  return (
    <>
      {corners.map((c) => (
        <rect
          key={c.dir}
          data-id={`selection.rotate.${c.dir}`}
          data-rotate={c.dir}
          x={c.x}
          y={c.y}
          width={radius}
          height={radius}
          fill="transparent"
          pointerEvents="all"
          style={{ cursor: "crosshair" }}
        />
      ))}
    </>
  );
}

function Handle({ dir, cx, cy, size, hit, stroke, cursor: cursorOverride }: { dir: HandleDir; cx: number; cy: number; size: number; hit: number; stroke: number; cursor?: string }) {
  const half = size / 2;
  const halfHit = hit / 2;
  const cursor = cursorOverride ?? cursorFor(dir);
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

export function handlePositions(b: Rect): HandlePoint[] {
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

function cornerHandlePositions(b: Rect): HandlePoint[] {
  return [
    { dir: "nw", x: b.x, y: b.y },
    { dir: "ne", x: b.x + b.w, y: b.y },
    { dir: "se", x: b.x + b.w, y: b.y + b.h },
    { dir: "sw", x: b.x, y: b.y + b.h },
  ];
}

function handlePositionsForOutline(outline: Extract<ReturnType<typeof selectionOutlineGeometry>, { kind: "single_oriented" }>): HandlePoint[] {
  const [nw, ne, se, sw] = outline.points;
  const center = midpoint(nw, se);
  return withVisualCursors(center, [
    { dir: "nw", ...nw },
    { dir: "n", ...midpoint(nw, ne) },
    { dir: "ne", ...ne },
    { dir: "e", ...midpoint(ne, se) },
    { dir: "se", ...se },
    { dir: "s", ...midpoint(se, sw) },
    { dir: "sw", ...sw },
    { dir: "w", ...midpoint(sw, nw) },
  ]);
}

function cornerHandlePositionsForOutline(outline: Extract<ReturnType<typeof selectionOutlineGeometry>, { kind: "single_oriented" }>): HandlePoint[] {
  const [nw, ne, se, sw] = outline.points;
  const center = midpoint(nw, se);
  return withVisualCursors(center, [
    { dir: "nw", ...nw },
    { dir: "ne", ...ne },
    { dir: "se", ...se },
    { dir: "sw", ...sw },
  ]);
}

function midpoint(a: { x: number; y: number }, b: { x: number; y: number }): { x: number; y: number } {
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
}

function withVisualCursors(center: { x: number; y: number }, points: HandlePoint[]): HandlePoint[] {
  return points.map((p) => ({ ...p, cursor: cursorFromVector(p.x - center.x, p.y - center.y) }));
}

function cursorFromVector(dx: number, dy: number): string {
  const ax = Math.abs(dx);
  const ay = Math.abs(dy);
  if (ax > ay * 2) return "ew-resize";
  if (ay > ax * 2) return "ns-resize";
  return dx * dy < 0 ? "nesw-resize" : "nwse-resize";
}

function WHLabel({ bbox, visualBbox, zoom }: { bbox: Rect; visualBbox: Rect; zoom: number }) {
  const text = `${Math.round(bbox.w)} × ${Math.round(bbox.h)}`;
  const padX = 4 / zoom;
  const padY = 2 / zoom;
  const fontSize = 11 / zoom;
  const charW = 6.5 / zoom;
  const w = text.length * charW + padX * 2;
  const h = fontSize + padY * 2;
  const x = visualBbox.x + (visualBbox.w - w) / 2;
  const y = visualBbox.y + visualBbox.h + 4 / zoom;
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
