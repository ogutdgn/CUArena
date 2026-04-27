// Pencil tool: pointerdown → drag captures points → pointerup commits
// a simplified open vector path.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { setSelection } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Vector, VectorNetwork } from "@/types/scene";
import { resolveCreationParentId, worldToParentLocal } from "@/engine/coordinates";
import { getPencilVectorStyleDefaults } from "@/engine/styleDefaults";

const SIMPLIFY_EPSILON = 1.5;

let raw: Point[] = [];
let drawing = false;

// Douglas-Peucker
function rdp(pts: Point[], epsilon: number): Point[] {
  if (pts.length < 3) return pts.slice();
  let maxDist = 0;
  let index = 0;
  const a = pts[0];
  const b = pts[pts.length - 1];
  for (let i = 1; i < pts.length - 1; i++) {
    const d = perpDist(pts[i], a, b);
    if (d > maxDist) {
      maxDist = d;
      index = i;
    }
  }
  if (maxDist > epsilon) {
    const left = rdp(pts.slice(0, index + 1), epsilon);
    const right = rdp(pts.slice(index), epsilon);
    return left.slice(0, -1).concat(right);
  }
  return [a, b];
}

function perpDist(p: Point, a: Point, b: Point): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (dx === 0 && dy === 0) return Math.hypot(p.x - a.x, p.y - a.y);
  const num = Math.abs(dy * p.x - dx * p.y + b.x * a.y - b.y * a.x);
  const den = Math.hypot(dx, dy);
  return num / den;
}

export const pencilTool: ITool = {
  onPointerDown(world, _e) {
    drawing = true;
    raw = [{ x: world.x, y: world.y }];
    useStore.setState((s) => {
      s.pencilPreview = { points: [{ x: world.x, y: world.y }] };
    });
  },
  onPointerMove(world, _e) {
    if (!drawing) return;
    raw.push({ x: world.x, y: world.y });
    useStore.setState((s) => {
      s.pencilPreview = { points: raw.slice() };
    });
  },
  onPointerUp(world, _e) {
    if (!drawing) return;
    drawing = false;
    if (raw.length < 2) {
      raw = [];
      useStore.setState((s) => { s.pencilPreview = null; });
      return;
    }
    const simplified = rdp(raw, SIMPLIFY_EPSILON);
    const deduped: Point[] = [];
    for (const p of simplified) {
      const last = deduped[deduped.length - 1];
      if (!last || Math.hypot(p.x - last.x, p.y - last.y) >= 0.5) deduped.push(p);
    }
    const points = deduped.length >= 2 ? deduped : raw.slice();

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const p of points) {
      if (p.x < minX) minX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.x > maxX) maxX = p.x;
      if (p.y > maxY) maxY = p.y;
    }
    const ox = minX;
    const oy = minY;
    const verts = points.map((p) => ({ x: p.x - ox, y: p.y - oy, handleType: "corner" as const }));
    const segs = [];
    for (let i = 0; i < verts.length - 1; i++) {
      segs.push({ fromIndex: i, toIndex: i + 1, handleFrom: null, handleTo: null });
    }
    const network: VectorNetwork = { vertices: verts, segments: segs, closed: false };

    const s = useStore.getState();
    const pageId = s.activePageId;
    const parentId = resolveCreationParentId(s, world);
    const styleDefaults = getPencilVectorStyleDefaults(s);
    const localOrigin = worldToParentLocal(s, parentId, { x: ox, y: oy });
    const pageParent = s.document.pages.find((p) => p.id === parentId);
    const indexedParent = s.nodesById[parentId];
    const childCount = pageParent
      ? pageParent.children.length
      : indexedParent && "children" in indexedParent && Array.isArray((indexedParent as { children?: unknown[] }).children)
      ? ((indexedParent as { children: unknown[] }).children).length
      : 0;
    const layer: Vector = {
      id: uid("vector"),
      type: "vector",
      name: "Pencil stroke",
      parentId,
      x: localOrigin.x,
      y: localOrigin.y,
      w: Math.max(1, maxX - minX),
      h: Math.max(1, maxY - minY),
      rotation: 0,
      scaleX: 1,
      scaleY: 1,
      visible: true,
      locked: false,
      opacity: 1,
      constraints: { horizontal: "left", vertical: "top" },
      network,
      fills: styleDefaults.fills,
      strokes: styleDefaults.strokes,
      effects: styleDefaults.effects,
    };

    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "create_node",
      pageId,
      parentId,
      indexInParent: childCount,
      node: layer,
    });
    setSelection([layer.id], "implicit_after_create");
    emitSemantic({
      name: "create_vector_with_pencil",
      layerId: layer.id,
      pointCount: points.length,
    });

    // Revert tool
    const beforeTool = useStore.getState().activeTool;
    if (beforeTool !== "move") {
      dispatch({
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_tool",
        before: beforeTool,
        after: "move",
      });
      emitSemantic({ name: "tool_change", before: beforeTool, after: "move", trigger: "auto_revert_after_create" });
    }

    raw = [];
    useStore.setState((sx) => { sx.pencilPreview = null; });
  },
  onAbort() {
    drawing = false;
    raw = [];
    useStore.setState((s) => { s.pencilPreview = null; });
  },
};
