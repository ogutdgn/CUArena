// Selection overlay: bbox + 8 resize handles. Rendered inside the world-space
// group so it follows pan/zoom, but handle sizes are scaled by 1/zoom so they
// appear constant pixel size on screen.

import { useStore, selectActiveViewport } from "@/engine/store";
import { selectionBbox } from "@/engine/selectors";
import type { Rect } from "@/util/geometry";

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
  if (!bbox) return null;
  // In prototype mode, hide resize handles — connection dots take over.
  if (activeRightTab === "prototype") return null;
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
      {handlePositions(bbox).map((p) => (
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
