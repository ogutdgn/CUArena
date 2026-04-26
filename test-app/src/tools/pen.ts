// Pen tool: click for corner vertex, click-drag for vertex with mirror bezier
// handles. Live preview from last anchor to cursor while in creation mode.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId, openTransaction, commitTransaction, abortTransaction } from "@/engine/dispatch";
import { setSelection } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Vector, VectorNetwork, VectorVertex, VectorSegment, Layer } from "@/types/scene";
import { worldOffsetOfLayer, worldToParentLocal } from "@/engine/coordinates";
import { getPenVectorStyleDefaults } from "@/engine/styleDefaults";

const CLOSE_HIT_PX = 8;
const DRAG_THRESHOLD = 3;
const ANGLE_STEP_DEG = 15;

interface ActiveCreation {
  layerId: string;
  txId: string;
  vertices: VectorVertex[];
  segments: VectorSegment[];
  // Stores outgoing handle vectors per vertex for segments not yet created.
  pendingOutHandles: Record<number, { dx: number; dy: number }>;
  originWorld: Point;
  originLocal: Point;
  initialNetwork: VectorNetwork;
  // Currently dragging out a handle for the vertex at this index
  dragHandleIndex: number | null;
  dragHandleStart: Point | null;
}

let creation: ActiveCreation | null = null;

function cloneNetwork(network: VectorNetwork): VectorNetwork {
  return {
    vertices: network.vertices.map((v) => ({ ...v })),
    segments: network.segments.map((seg) => ({ ...seg })),
    closed: network.closed,
  };
}

function reverseOpenNetwork(network: VectorNetwork): VectorNetwork {
  const n = network.vertices.length;
  return {
    vertices: [...network.vertices].reverse().map((v) => ({ ...v })),
    segments: [...network.segments]
      .reverse()
      .map((seg) => ({
        fromIndex: n - 1 - seg.toIndex,
        toIndex: n - 1 - seg.fromIndex,
        handleFrom: seg.handleTo ? { ...seg.handleTo } : null,
        handleTo: seg.handleFrom ? { ...seg.handleFrom } : null,
      })),
    closed: network.closed,
  };
}

function buildPendingOutHandles(network: VectorNetwork): Record<number, { dx: number; dy: number }> {
  const pending: Record<number, { dx: number; dy: number }> = {};
  for (const seg of network.segments) {
    if (seg.handleFrom && pending[seg.fromIndex] == null) {
      pending[seg.fromIndex] = { dx: seg.handleFrom.dx, dy: seg.handleFrom.dy };
    }
  }
  return pending;
}

function constrainPointAngle(from: Point, to: Point, enabled: boolean): Point {
  if (!enabled) return to;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.hypot(dx, dy);
  if (len === 0) return to;
  const step = (ANGLE_STEP_DEG * Math.PI) / 180;
  const angle = Math.atan2(dy, dx);
  const snapped = Math.round(angle / step) * step;
  return {
    x: from.x + Math.cos(snapped) * len,
    y: from.y + Math.sin(snapped) * len,
  };
}

function syncStore(closed: boolean) {
  if (!creation) return;
  if (creation.vertices.length === 0) return;
  // Update bbox
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const v of creation.vertices) {
    if (v.x < minX) minX = v.x;
    if (v.y < minY) minY = v.y;
    if (v.x > maxX) maxX = v.x;
    if (v.y > maxY) maxY = v.y;
  }
  const shiftX = -minX;
  const shiftY = -minY;
  const after: VectorNetwork = {
    vertices: creation.vertices.map((v) => ({ ...v, x: v.x + shiftX, y: v.y + shiftY })),
    segments: creation.segments.slice(),
    closed,
  };
  const s = useStore.getState();

  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "mutate_vector_network",
      pageId: s.activePageId,
      layerId: creation.layerId,
      before: creation.initialNetwork,
      after,
    },
    { transactionId: creation.txId },
  );

  const node = s.nodesById[creation.layerId] as Layer | undefined;
  if (node) {
    const nextX = creation.originLocal.x + minX;
    const nextY = creation.originLocal.y + minY;
    const w = Math.max(1, maxX - minX);
    const h = Math.max(1, maxY - minY);

    // Keep pen-creation geometry stable: network is already normalized above,
    // so update bounds via property ops instead of set_transform (which scales
    // vector networks for resize gestures).
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: s.activePageId,
        ids: [creation.layerId],
        path: "x",
        before: { [creation.layerId]: node.x },
        after: { [creation.layerId]: nextX },
      },
      { transactionId: creation.txId },
    );
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: s.activePageId,
        ids: [creation.layerId],
        path: "y",
        before: { [creation.layerId]: node.y },
        after: { [creation.layerId]: nextY },
      },
      { transactionId: creation.txId },
    );
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: s.activePageId,
        ids: [creation.layerId],
        path: "w",
        before: { [creation.layerId]: node.w },
        after: { [creation.layerId]: w },
      },
      { transactionId: creation.txId },
    );
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_property",
        pageId: s.activePageId,
        ids: [creation.layerId],
        path: "h",
        before: { [creation.layerId]: node.h },
        after: { [creation.layerId]: h },
      },
      { transactionId: creation.txId },
    );
  }
}

function updatePreview(world: Point | null) {
  if (!creation) return;
  const handleDrag =
    creation.dragHandleIndex != null && creation.dragHandleStart && world
      ? {
          vertexIndex: creation.dragHandleIndex,
          outDx: world.x - (creation.originWorld.x + creation.vertices[creation.dragHandleIndex].x),
          outDy: world.y - (creation.originWorld.y + creation.vertices[creation.dragHandleIndex].y),
        }
      : null;
  useStore.setState((s) => {
    s.penPreview = creation
      ? { layerId: creation.layerId, cursor: world ? { x: world.x, y: world.y } : null, handleDrag }
      : null;
  });
}

function tryResumeFromSelectedEndpoint(world: Point): boolean {
  const s = useStore.getState();
  const sel = s.selectionByPage[s.activePageId] ?? [];
  if (sel.length !== 1) return false;
  const node = s.nodesById[sel[0]];
  if (!node || (node as Vector).type !== "vector") return false;
  const layer = node as Vector;
  if (layer.network.closed || layer.network.vertices.length < 2) return false;
  const vp = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const originWorld = worldOffsetOfLayer(s, layer);
  const first = layer.network.vertices[0];
  const last = layer.network.vertices[layer.network.vertices.length - 1];
  const firstWorld = { x: originWorld.x + first.x, y: originWorld.y + first.y };
  const lastWorld = { x: originWorld.x + last.x, y: originWorld.y + last.y };
  const dFirst = distScreen(firstWorld, world, vp.zoom);
  const dLast = distScreen(lastWorld, world, vp.zoom);
  const minD = Math.min(dFirst, dLast);
  if (minD > CLOSE_HIT_PX) return false;

  const originalNetwork = cloneNetwork(layer.network);
  const resumeFromStart = dFirst <= dLast;
  const workingNetwork = resumeFromStart
    ? reverseOpenNetwork(originalNetwork)
    : originalNetwork;

  const txId = openTransaction();
  const beforeMode = s.editMode;
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_edit_mode",
      before: beforeMode,
      after: { kind: "pen_creation", layerId: layer.id },
    },
    { transactionId: txId },
  );

  if (resumeFromStart) {
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "mutate_vector_network",
        pageId: s.activePageId,
        layerId: layer.id,
        before: originalNetwork,
        after: workingNetwork,
      },
      { transactionId: txId },
    );
  }

  creation = {
    layerId: layer.id,
    txId,
    vertices: workingNetwork.vertices.map((v) => ({ ...v })),
    segments: workingNetwork.segments.map((seg) => ({ ...seg })),
    pendingOutHandles: buildPendingOutHandles(workingNetwork),
    originWorld,
    originLocal: { x: layer.x, y: layer.y },
    initialNetwork: cloneNetwork(workingNetwork),
    dragHandleIndex: null,
    dragHandleStart: null,
  };
  updatePreview(world);
  return true;
}

function clearPreview() {
  useStore.setState((s) => { s.penPreview = null; });
}

function commitCreation(closed: boolean) {
  if (!creation) return;
  if (creation.vertices.length < 2) {
    abortTransaction(creation.txId);
    creation = null;
    clearPreview();
    return;
  }

  syncStore(closed);
  commitTransaction(creation.txId);
  emitSemantic({
    name: "create_vector_with_pen",
    layerId: creation.layerId,
    closed,
    pointCount: creation.vertices.length,
  });

  const before = useStore.getState().editMode;
  if (before.kind === "pen_creation") {
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_edit_mode",
      before,
      after: { kind: "none" },
    });
  }

  creation = null;
  clearPreview();
}

function distScreen(a: Point, b: Point, zoom: number): number {
  return Math.hypot(a.x - b.x, a.y - b.y) * zoom;
}

export const penTool: ITool = {
  onPointerDown(world, e) {
    const s = useStore.getState();

    if (!creation) {
      if (tryResumeFromSelectedEndpoint(world)) return;
      // First click: create empty vector layer at click point.
      const pageId = s.activePageId;
      const parentId = pageId;
      const originLocal = worldToParentLocal(s, parentId, world);
      const styleDefaults = getPenVectorStyleDefaults(s);
      const initialNetwork: VectorNetwork = {
        vertices: [{ x: 0, y: 0, handleType: "corner" }],
        segments: [],
        closed: false,
      };
      const layer: Vector = {
        id: uid("vector"),
        type: "vector",
        name: "Vector",
        parentId,
        x: originLocal.x,
        y: originLocal.y,
        w: 1,
        h: 1,
        rotation: 0,
        scaleX: 1,
        scaleY: 1,
        visible: true,
        locked: false,
        opacity: 1,
        constraints: { horizontal: "left", vertical: "top" },
        network: initialNetwork,
        fills: styleDefaults.fills,
        strokes: styleDefaults.strokes,
        effects: styleDefaults.effects,
      };

      const pageParent = s.document.pages.find((p) => p.id === parentId);
      const indexedParent = s.nodesById[parentId];
      const childCount = pageParent
        ? pageParent.children.length
        : indexedParent && "children" in indexedParent && Array.isArray((indexedParent as { children?: unknown[] }).children)
        ? ((indexedParent as { children: unknown[] }).children).length
        : 0;
      const txId = openTransaction();
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "create_node",
          pageId,
          parentId,
          indexInParent: childCount,
          node: layer,
        },
        { transactionId: txId },
      );
      setSelection([layer.id], "implicit_after_create");

      const beforeMode = useStore.getState().editMode;
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_edit_mode",
          before: beforeMode,
          after: { kind: "pen_creation", layerId: layer.id },
        },
        { transactionId: txId },
      );
      creation = {
        layerId: layer.id,
        txId,
        vertices: [{ x: 0, y: 0, handleType: "corner" }],
        segments: [],
        pendingOutHandles: {},
        originWorld: { x: world.x, y: world.y },
        originLocal,
        initialNetwork,
        dragHandleIndex: 0, // armed for first vertex's handle
        dragHandleStart: world,
      };
      emitSemantic({
        name: "add_vector_point",
        layerId: layer.id,
        index: 0,
        position: { x: 0, y: 0 },
      });
      updatePreview(world);
      return;
    }

    // Subsequent click: close-path test on starting vertex
    const vp = useStore.getState().viewportByPage[useStore.getState().activePageId] ?? { x: 0, y: 0, zoom: 1 };
    const startWorld = {
      x: creation.originWorld.x + creation.vertices[0].x,
      y: creation.originWorld.y + creation.vertices[0].y,
    };
    if (creation.vertices.length >= 2 && distScreen(startWorld, world, vp.zoom) < CLOSE_HIT_PX) {
      commitCreation(true);
      return;
    }

    // Clicking/dragging the current endpoint should adjust that anchor's
    // handles, not create a duplicate zero-length segment.
    const lastIdx = creation.vertices.length - 1;
    const last = creation.vertices[lastIdx];
    const lastWorld = {
      x: creation.originWorld.x + last.x,
      y: creation.originWorld.y + last.y,
    };
    if (distScreen(lastWorld, world, vp.zoom) < CLOSE_HIT_PX) {
      creation.dragHandleIndex = lastIdx;
      creation.dragHandleStart = world;
      updatePreview(world);
      return;
    }

    // Add new vertex
    const prev = creation.vertices[creation.vertices.length - 1];
    const prevWorld = {
      x: creation.originWorld.x + prev.x,
      y: creation.originWorld.y + prev.y,
    };
    const constrainedWorld = constrainPointAngle(prevWorld, world, e.shiftKey);

    const newVertex: VectorVertex = {
      x: constrainedWorld.x - creation.originWorld.x,
      y: constrainedWorld.y - creation.originWorld.y,
      handleType: "corner",
    };
    const prevIdx = creation.vertices.length - 1;
    creation.vertices.push(newVertex);
    creation.segments.push({
      fromIndex: prevIdx,
      toIndex: prevIdx + 1,
      handleFrom: creation.pendingOutHandles[prevIdx]
        ? { ...creation.pendingOutHandles[prevIdx] }
        : null,
      handleTo: null,
    });
    creation.dragHandleIndex = creation.vertices.length - 1;
    creation.dragHandleStart = constrainedWorld;

    syncStore(false);
    emitSemantic({
      name: "add_vector_point",
      layerId: creation.layerId,
      index: creation.vertices.length - 1,
      position: { x: newVertex.x, y: newVertex.y },
    });
    updatePreview(constrainedWorld);
  },

  onPointerMove(world, e) {
    if (!creation) return;
    if (creation.dragHandleIndex != null && creation.dragHandleStart) {
      const dx = world.x - creation.dragHandleStart.x;
      const dy = world.y - creation.dragHandleStart.y;
      if (Math.hypot(dx, dy) >= DRAG_THRESHOLD) {
        const idx = creation.dragHandleIndex;
        const v = creation.vertices[idx];
        const anchorWorld = {
          x: creation.originWorld.x + v.x,
          y: creation.originWorld.y + v.y,
        };
        const constrainedHandleWorld = constrainPointAngle(anchorWorld, world, e.shiftKey);
        const outDx = constrainedHandleWorld.x - anchorWorld.x;
        const outDy = constrainedHandleWorld.y - anchorWorld.y;
        creation.vertices[idx] = {
          ...v,
          handleType: e.altKey ? "independent" : "mirror",
        };
        // Outgoing segment: from this vertex onward — set handleFrom on segment[idx]
        const outSeg = creation.segments.find((s) => s.fromIndex === idx);
        // Incoming segment: into this vertex — set handleTo (mirrored = -outDx,-outDy)
        const inSeg = creation.segments.find((s) => s.toIndex === idx);
        if (inSeg) {
          inSeg.handleTo = { dx: -outDx, dy: -outDy };
        }
        // Alt/Option breaks mirror coupling when both handles exist. Without
        // Alt, remember outgoing handle for future segments from this vertex.
        if (!e.altKey) {
          if (outSeg) outSeg.handleFrom = { dx: outDx, dy: outDy };
          creation.pendingOutHandles[idx] = { dx: outDx, dy: outDy };
        } else {
          if (!outSeg) delete creation.pendingOutHandles[idx];
        }
        syncStore(false);
        updatePreview(constrainedHandleWorld);
        return;
      }
    }
    let previewWorld = world;
    if (e.shiftKey && creation.vertices.length > 0) {
      const last = creation.vertices[creation.vertices.length - 1];
      const lastWorld = {
        x: creation.originWorld.x + last.x,
        y: creation.originWorld.y + last.y,
      };
      previewWorld = constrainPointAngle(lastWorld, world, true);
    }
    updatePreview(previewWorld);
  },

  onPointerUp(world, e) {
    if (!creation) return;
    void world;
    void e;
    creation.dragHandleIndex = null;
    creation.dragHandleStart = null;
    updatePreview(null);
  },

  onAbort() {
    if (creation) commitCreation(false);
  },
};

export function abortPenIfActive(): boolean {
  if (!creation) return false;
  commitCreation(false);
  return true;
}
