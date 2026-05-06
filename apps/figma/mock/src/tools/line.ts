// Line / Arrow tools: point-defined drag from p1 (pointerdown) to p2 (pointerup).
// Click without drag = no creation.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { setSelection } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Line, Arrow, Layer, Page } from "@/types/scene";
import { resolveCreationParentId, worldToParentLocal } from "@/engine/coordinates";

const MIN_DRAG = 3;

interface LineToolConfig {
  isArrow: boolean;
}

type State =
  | { kind: "idle" }
  | { kind: "armed"; downWorld: Point; shift: boolean }
  | { kind: "active"; downWorld: Point; currentWorld: Point; shift: boolean };

function makeLineLikeTool(config: LineToolConfig): ITool {
  let state: State = { kind: "idle" };

  function makeNode(p1: Point, p2: Point, parentId: string, ordinal: number): Line | Arrow {
    const s = useStore.getState();
    const localP1 = worldToParentLocal(s, parentId, p1);
    const localP2 = worldToParentLocal(s, parentId, p2);
    const minX = Math.min(localP1.x, localP2.x);
    const minY = Math.min(localP1.y, localP2.y);
    const w = Math.abs(localP2.x - localP1.x);
    const h = Math.abs(localP2.y - localP1.y);
    const base: Pick<Layer, "id" | "parentId" | "x" | "y" | "w" | "h" | "rotation" | "scaleX" | "scaleY" | "visible" | "locked" | "opacity" | "constraints"> = {
      id: uid(config.isArrow ? "arrow" : "line"),
      parentId,
      x: minX,
      y: minY,
      w: Math.max(1, w),
      h: Math.max(1, h),
      rotation: 0,
      scaleX: 1,
      scaleY: 1,
      visible: true,
      locked: false,
      opacity: 1,
      constraints: { horizontal: "left", vertical: "top" },
    };
    const stroke = {
      paint: { kind: "solid" as const, color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true },
      weight: 1,
      alignment: "center" as const,
      dash: null,
    };
    if (config.isArrow) {
      const node: Arrow = {
        ...base,
        type: "arrow",
        name: `Arrow ${ordinal}`,
        p1: { x: localP1.x - minX, y: localP1.y - minY },
        p2: { x: localP2.x - minX, y: localP2.y - minY },
        strokes: [stroke],
        endCapStart: "none",
        endCapEnd: "arrow",
        effects: [],
      };
      return node;
    }
    const node: Line = {
      ...base,
      type: "line",
      name: `Line ${ordinal}`,
      p1: { x: localP1.x - minX, y: localP1.y - minY },
      p2: { x: localP2.x - minX, y: localP2.y - minY },
      strokes: [stroke],
      effects: [],
    };
    return node;
  }

  function countOf(page: Page, type: "line" | "arrow"): number {
    let n = 0;
    function walk(arr: Layer[]) {
      for (const l of arr) {
        if (l.type === type) n += 1;
        if (l.type === "frame" || l.type === "section" || l.type === "group") walk(l.children);
      }
    }
    walk(page.children);
    return n;
  }

  return {
    onPointerDown(world, e) {
      state = { kind: "armed", downWorld: world, shift: e.shiftKey };
    },
    onPointerMove(world, _e) {
      if (state.kind === "armed") {
        const dx = world.x - state.downWorld.x;
        const dy = world.y - state.downWorld.y;
        if (Math.hypot(dx, dy) < MIN_DRAG) return;
        state = { kind: "active", downWorld: state.downWorld, currentWorld: world, shift: state.shift };
      }
      if (state.kind === "active") {
        const downWorld = state.downWorld;
        state = { ...state, currentWorld: world };
        const p2 = constrainShift(downWorld, world, state.shift);
        const minX = Math.min(downWorld.x, p2.x);
        const minY = Math.min(downWorld.y, p2.y);
        const w = Math.abs(p2.x - downWorld.x);
        const h = Math.abs(p2.y - downWorld.y);
        useStore.setState((s) => {
          s.dragPreview = {
            kind: "create_shape",
            data: {
              shape: config.isArrow ? "arrow" : "line",
              x1: downWorld.x,
              y1: downWorld.y,
              x2: p2.x,
              y2: p2.y,
              x: minX,
              y: minY,
              w: Math.max(1, w),
              h: Math.max(1, h),
            },
          };
        });
      }
    },
    onPointerUp(world, _e) {
      if (state.kind !== "active") {
        // Click without drag → no-op
        state = { kind: "idle" };
        useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
        return;
      }

      const s = useStore.getState();
      const pageId = s.activePageId;
      const p1 = state.downWorld;
      const p2 = constrainShift(p1, world, state.shift);
      const parentId = resolveCreationParentId(s, world);

      const page = s.document.pages.find((p) => p.id === pageId);
      const ordinal = page ? countOf(page, config.isArrow ? "arrow" : "line") + 1 : 1;
      const node = makeNode(p1, p2, parentId, ordinal);

      const pageParent = s.document.pages.find((p) => p.id === parentId);
      const indexedParent = s.nodesById[parentId];
      const childCount = pageParent
        ? pageParent.children.length
        : indexedParent && "children" in indexedParent && Array.isArray((indexedParent as { children?: unknown[] }).children)
        ? ((indexedParent as { children: unknown[] }).children).length
        : 0;

      dispatch({
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "create_node",
        pageId,
        parentId,
        indexInParent: childCount,
        node,
      });

      if (config.isArrow) {
        emitSemantic({
          name: "create_arrow",
          layerId: node.id,
          p1,
          p2,
          parentId,
          modifiers: { shift: state.shift, alt: false },
          trigger: "shortcut_shift_L",
        });
      } else {
        emitSemantic({
          name: "create_line",
          layerId: node.id,
          p1,
          p2,
          parentId,
          modifiers: { shift: state.shift, alt: false },
          trigger: "shortcut_L",
        });
      }
      setSelection([node.id], "implicit_after_create");

      const beforeTool = useStore.getState().activeTool;
      if (beforeTool !== "move") {
        dispatch({
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_tool",
          before: beforeTool,
          after: "move",
        });
        emitSemantic({
          name: "tool_change",
          before: beforeTool,
          after: "move",
          trigger: "auto_revert_after_create",
        });
      }

      state = { kind: "idle" };
      useStore.setState((sx) => { sx.dragPreview = { kind: null, data: null }; });
    },
    onAbort() {
      state = { kind: "idle" };
      useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
    },
  };
}

// Snap to nearest 45° angle when shift is held.
function constrainShift(p1: Point, p2: Point, shift: boolean): Point {
  if (!shift) return p2;
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const angle = Math.atan2(dy, dx);
  const snapped = Math.round(angle / (Math.PI / 4)) * (Math.PI / 4);
  const len = Math.hypot(dx, dy);
  return { x: p1.x + Math.cos(snapped) * len, y: p1.y + Math.sin(snapped) * len };
}

export const lineTool = makeLineLikeTool({ isArrow: false });
export const arrowTool = makeLineLikeTool({ isArrow: true });
