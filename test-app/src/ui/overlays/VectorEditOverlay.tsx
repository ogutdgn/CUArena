// Vector edit mode overlay: anchor points (drag to move, click to select),
// segment hit areas (click to add a vertex), Backspace deletes selected.

import { useState } from "react";
import { useStore, selectActiveViewport } from "@/engine/store";
import { dispatch, makeOpId, openTransaction, commitTransaction } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import type { Vector, VectorNetwork } from "@/types/scene";
import { worldOffsetOfLayer } from "@/engine/coordinates";

const ANCHOR_PX = 8;
const SEG_HIT_PX = 8;

export function VectorEditOverlay() {
  const editMode = useStore((s) => s.editMode);
  const viewport = useStore((s) => selectActiveViewport(s));
  const layer = useStore((s) => {
    if (s.editMode.kind !== "vector" || !s.editMode.layerId) return null;
    const n = s.nodesById[s.editMode.layerId];
    return n && (n as Vector).type === "vector" ? (n as Vector) : null;
  });
  const selected = useStore((s) => s.vectorEditSelected);
  const origin = useStore((s) => {
    if (s.editMode.kind !== "vector" || !s.editMode.layerId) return null;
    const n = s.nodesById[s.editMode.layerId];
    if (!n || (n as Vector).type !== "vector") return null;
    return worldOffsetOfLayer(s, n as Vector);
  });
  const [drag, setDrag] = useState<{ index: number; before: VectorNetwork; txId: string } | null>(null);

  if (editMode.kind !== "vector" || !layer || !origin) return null;

  const anchorSize = ANCHOR_PX / viewport.zoom;
  const segHit = SEG_HIT_PX / viewport.zoom;
  const sw = 1 / viewport.zoom;
  const ox = origin.x;
  const oy = origin.y;

  function selectAnchor(i: number) {
    useStore.setState((s) => { s.vectorEditSelected = i; });
  }

  function startDrag(idx: number, e: React.PointerEvent) {
    e.stopPropagation();
    e.currentTarget.setPointerCapture(e.pointerId);
    if (!layer) return;
    selectAnchor(idx);
    const txId = openTransaction();
    setDrag({ index: idx, before: layer.network, txId });
  }

  function moveDrag(e: React.PointerEvent) {
    if (!drag || !layer) return;
    const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
    if (!svgEl) return;
    const r = svgEl.getBoundingClientRect();
    const sx = e.clientX - r.left;
    const sy = e.clientY - r.top;
    const wx = sx / viewport.zoom + viewport.x;
    const wy = sy / viewport.zoom + viewport.y;
    const nx = wx - ox;
    const ny = wy - oy;
    const nextNetwork: VectorNetwork = {
      ...layer.network,
      vertices: layer.network.vertices.map((v, i) => (i === drag.index ? { ...v, x: nx, y: ny } : v)),
    };
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "mutate_vector_network",
        pageId: useStore.getState().activePageId,
        layerId: layer.id,
        before: drag.before,
        after: nextNetwork,
      },
      { transactionId: drag.txId },
    );
  }

  function endDrag(e: React.PointerEvent) {
    if (!drag || !layer) return;
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId);
    commitTransaction(drag.txId);
    const before = drag.before.vertices[drag.index];
    const after = layer.network.vertices[drag.index];
    if (before && after) {
      emitSemantic({
        name: "move_vector_point",
        layerId: layer.id,
        index: drag.index,
        before: { x: before.x, y: before.y },
        after: { x: after.x, y: after.y },
      });
    }
    setDrag(null);
  }

  function addPointOnSegment(segIdx: number, world: { x: number; y: number }) {
    if (!layer) return;
    const seg = layer.network.segments[segIdx];
    if (!seg) return;
    const a = layer.network.vertices[seg.fromIndex];
    const b = layer.network.vertices[seg.toIndex];
    if (!a || !b) return;

    // For a straight segment, project the click onto the segment.
    // For bezier (with handles), we'd need t-parameter solve; simplified to midpoint.
    let nx = (a.x + b.x) / 2;
    let ny = (a.y + b.y) / 2;
    if (!seg.handleFrom && !seg.handleTo) {
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len2 = dx * dx + dy * dy;
      if (len2 > 0) {
        const px = world.x - ox - a.x;
        const py = world.y - oy - a.y;
        let t = (px * dx + py * dy) / len2;
        t = Math.max(0.05, Math.min(0.95, t));
        nx = a.x + dx * t;
        ny = a.y + dy * t;
      }
    }

    const before = layer.network;
    const newIdx = layer.network.vertices.length;
    const newVertices = [...layer.network.vertices, { x: nx, y: ny, handleType: "corner" as const }];
    const newSegments: typeof layer.network.segments = [];
    for (let i = 0; i < layer.network.segments.length; i++) {
      if (i === segIdx) {
        newSegments.push({ fromIndex: layer.network.segments[i].fromIndex, toIndex: newIdx, handleFrom: null, handleTo: null });
        newSegments.push({ fromIndex: newIdx, toIndex: layer.network.segments[i].toIndex, handleFrom: null, handleTo: null });
      } else {
        newSegments.push(layer.network.segments[i]);
      }
    }
    const after: VectorNetwork = { vertices: newVertices, segments: newSegments, closed: layer.network.closed };

    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "mutate_vector_network",
      pageId: useStore.getState().activePageId,
      layerId: layer.id,
      before,
      after,
    });
    emitSemantic({
      name: "add_vector_point",
      layerId: layer.id,
      index: newIdx,
      position: { x: nx, y: ny },
    });
    selectAnchor(newIdx);
  }

  return (
    <g pointerEvents="all">
      {/* Path stroke highlight */}
      <polyline
        points={layer.network.vertices.map((v) => `${ox + v.x},${oy + v.y}`).join(" ")}
        fill="none"
        stroke="var(--color-selection-blue)"
        strokeWidth={sw}
        pointerEvents="none"
      />

      {/* Segment hit areas (click to insert vertex) */}
      {layer.network.segments.map((s, i) => {
        const a = layer.network.vertices[s.fromIndex];
        const b = layer.network.vertices[s.toIndex];
        if (!a || !b) return null;
        return (
          <line
            key={`seg-${i}`}
            x1={ox + a.x}
            y1={oy + a.y}
            x2={ox + b.x}
            y2={oy + b.y}
            stroke="transparent"
            strokeWidth={segHit}
            pointerEvents="stroke"
            style={{ cursor: "copy" }}
            onPointerDown={(e) => {
              e.stopPropagation();
              const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
              if (!svgEl) return;
              const r = svgEl.getBoundingClientRect();
              const wx = (e.clientX - r.left) / viewport.zoom + viewport.x;
              const wy = (e.clientY - r.top) / viewport.zoom + viewport.y;
              addPointOnSegment(i, { x: wx, y: wy });
            }}
          />
        );
      })}

      {/* Anchor handles */}
      {layer.network.vertices.map((v, i) => (
        <rect
          key={`a-${i}`}
          data-id={`vector.anchor.${i}`}
          x={ox + v.x - anchorSize / 2}
          y={oy + v.y - anchorSize / 2}
          width={anchorSize}
          height={anchorSize}
          fill={selected === i ? "var(--color-selection-blue)" : "white"}
          stroke="var(--color-selection-blue)"
          strokeWidth={sw}
          style={{ cursor: "move" }}
          onPointerDown={(e) => startDrag(i, e)}
          onPointerMove={moveDrag}
          onPointerUp={endDrag}
          onPointerCancel={endDrag}
        />
      ))}
    </g>
  );
}

export function deleteSelectedVectorPoint(): boolean {
  const s = useStore.getState();
  if (s.editMode.kind !== "vector" || !s.editMode.layerId) return false;
  const idx = s.vectorEditSelected;
  if (idx == null) return false;
  const layer = s.nodesById[s.editMode.layerId] as Vector | undefined;
  if (!layer || layer.type !== "vector") return false;
  const before = layer.network;
  if (before.vertices.length <= 1) {
    // Last point — delete the whole layer.
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "delete_nodes",
      pageId: s.activePageId,
      ids: [layer.id],
    });
    const beforeMode = s.editMode;
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_edit_mode",
      before: beforeMode,
      after: { kind: "none" },
    });
    useStore.setState((st) => { st.vectorEditSelected = null; });
    return true;
  }
  // Remove vertex idx; remap segments.
  const verts = before.vertices.filter((_, i) => i !== idx);
  const remap = (i: number) => (i > idx ? i - 1 : i);
  const segs: typeof before.segments = [];
  for (const seg of before.segments) {
    if (seg.fromIndex === idx || seg.toIndex === idx) continue;
    segs.push({ ...seg, fromIndex: remap(seg.fromIndex), toIndex: remap(seg.toIndex) });
  }
  const after = { vertices: verts, segments: segs, closed: before.closed && verts.length >= 3 };
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "mutate_vector_network",
    pageId: s.activePageId,
    layerId: layer.id,
    before,
    after,
  });
  emitSemantic({ name: "delete_vector_point", layerId: layer.id, index: idx });
  useStore.setState((st) => { st.vectorEditSelected = null; });
  return true;
}
