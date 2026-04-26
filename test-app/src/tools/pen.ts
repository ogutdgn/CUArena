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
import { worldToParentLocal } from "@/engine/coordinates";
import { getPenVectorStyleDefaults } from "@/engine/styleDefaults";

const CLOSE_HIT_PX = 8;
const DRAG_THRESHOLD = 3;

interface ActiveCreation {
  layerId: string;
  txId: string;
  vertices: VectorVertex[];
  segments: VectorSegment[];
  originWorld: Point;
  originLocal: Point;
  initialNetwork: VectorNetwork;
  // Currently dragging out a handle for the vertex at this index
  dragHandleIndex: number | null;
  dragHandleStart: Point | null;
}

let creation: ActiveCreation | null = null;

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
    const before = { x: node.x, y: node.y, w: node.w, h: node.h, rotation: node.rotation, scaleX: node.scaleX, scaleY: node.scaleY };
    const w = Math.max(1, maxX - minX);
    const h = Math.max(1, maxY - minY);
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_transform",
        pageId: s.activePageId,
        ids: [creation.layerId],
        before: { [creation.layerId]: before },
        after: {
          [creation.layerId]: {
            ...before,
            x: creation.originLocal.x + minX,
            y: creation.originLocal.y + minY,
            w,
            h,
          },
        },
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

function clearPreview() {
  useStore.setState((s) => { s.penPreview = null; });
}

function commitCreation(closed: boolean) {
  if (!creation) return;
  if (creation.vertices.length < 2) {
    abortTransaction(creation.txId);
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

  creation = null;
  clearPreview();
}

function distScreen(a: Point, b: Point, zoom: number): number {
  return Math.hypot(a.x - b.x, a.y - b.y) * zoom;
}

export const penTool: ITool = {
  onPointerDown(world, _e) {
    const s = useStore.getState();

    if (!creation) {
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

      const parent = s.nodesById[parentId];
      const childCount =
        parent && "children" in parent && Array.isArray((parent as { children?: unknown[] }).children)
          ? ((parent as { children: unknown[] }).children).length
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

    // Add new vertex
    const newVertex: VectorVertex = {
      x: world.x - creation.originWorld.x,
      y: world.y - creation.originWorld.y,
      handleType: "corner",
    };
    const prevIdx = creation.vertices.length - 1;
    creation.vertices.push(newVertex);
    creation.segments.push({
      fromIndex: prevIdx,
      toIndex: prevIdx + 1,
      handleFrom: null,
      handleTo: null,
    });
    creation.dragHandleIndex = creation.vertices.length - 1;
    creation.dragHandleStart = world;

    syncStore(false);
    emitSemantic({
      name: "add_vector_point",
      layerId: creation.layerId,
      index: creation.vertices.length - 1,
      position: { x: newVertex.x, y: newVertex.y },
    });
    updatePreview(world);
  },

  onPointerMove(world, _e) {
    if (!creation) return;
    if (creation.dragHandleIndex != null && creation.dragHandleStart) {
      const dx = world.x - creation.dragHandleStart.x;
      const dy = world.y - creation.dragHandleStart.y;
      if (Math.hypot(dx, dy) >= DRAG_THRESHOLD) {
        // Update handle on the active vertex (mirror).
        const idx = creation.dragHandleIndex;
        const v = creation.vertices[idx];
        const outDx = world.x - (creation.originWorld.x + v.x);
        const outDy = world.y - (creation.originWorld.y + v.y);
        creation.vertices[idx] = { ...v, handleType: "mirror" };
        // Outgoing segment: from this vertex onward — set handleFrom on segment[idx]
        const outSeg = creation.segments.find((s) => s.fromIndex === idx);
        if (outSeg) {
          outSeg.handleFrom = { dx: outDx, dy: outDy };
        }
        // Incoming segment: into this vertex — set handleTo (mirrored = -outDx,-outDy)
        const inSeg = creation.segments.find((s) => s.toIndex === idx);
        if (inSeg) {
          inSeg.handleTo = { dx: -outDx, dy: -outDy };
        }
        syncStore(false);
      }
    }
    updatePreview(world);
  },

  onPointerUp(_world, _e) {
    if (!creation) return;
    creation.dragHandleIndex = null;
    creation.dragHandleStart = null;
    updatePreview(_world);
  },

  onAbort() {
    if (creation) commitCreation(false);
  },
};

export function abortPenIfActive() {
  if (creation) commitCreation(false);
}
