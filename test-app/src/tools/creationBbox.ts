// Shared drag-create state machine for bbox-defined shapes (rectangle, ellipse,
// polygon, star, frame, section, slice). The caller provides a node factory.

import type { ITool } from "./types";
import type { Point, Rect } from "@/util/geometry";
import { rectFromPoints } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { setSelection } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Layer, Page } from "@/types/scene";
import type { ToolId } from "@/types/ops";
import type { SemanticEventInput } from "@/types/events";
import { resolveCreationParentId, worldRectToParentLocal } from "@/engine/coordinates";

const DEFAULT_SIZE = 100;
const MIN_DRAG = 3;

export interface BboxToolConfig {
  toolId: ToolId;
  // Build a layer node from the bbox + name suffix index. Implementer fills
  // type-specific fields. Returned layer must include id, parentId, type, etc.
  makeNode: (bbox: Rect, parentId: string, ordinal: number) => Layer;
  countOf: (page: Page) => number;
  emitOnCreate: (
    layer: Layer,
    bbox: Rect,
    parentId: string,
    modifiers: { shift: boolean; alt: boolean },
    trigger: "shortcut" | "toolbar" | "click_default_size",
  ) => SemanticEventInput;
  // If false, click without drag creates nothing (e.g. line/arrow handle points-only)
  allowDefaultSize?: boolean;
  // After commit, revert to "move"? (Default true.)
  revertToMove?: boolean;
}

type State =
  | { kind: "idle" }
  | { kind: "armed"; downWorld: Point; modifiers: { shift: boolean; alt: boolean } }
  | { kind: "active"; downWorld: Point; currentWorld: Point; modifiers: { shift: boolean; alt: boolean } };

export function makeCreationBboxTool(config: BboxToolConfig): ITool {
  let state: State = { kind: "idle" };

  return {
    onPointerDown(world, e) {
      state = { kind: "armed", downWorld: world, modifiers: { shift: e.shiftKey, alt: e.altKey } };
    },
    onPointerMove(world, _e) {
      if (state.kind === "armed") {
        const dx = world.x - state.downWorld.x;
        const dy = world.y - state.downWorld.y;
        if (Math.hypot(dx, dy) < MIN_DRAG) return;
        state = { kind: "active", downWorld: state.downWorld, currentWorld: world, modifiers: state.modifiers };
      }
      if (state.kind === "active") {
        state = { ...state, currentWorld: world };
        useStore.setState((s) => {
          s.dragPreview = {
            kind: "create_shape",
            data: {
              ...rectFromPoints((state as Extract<State, { kind: "active" }>).downWorld, world),
              shape: config.toolId,
            },
          };
        });
      }
    },
    onPointerUp(world, _e) {
      if (state.kind === "idle") return;

      const s = useStore.getState();
      const pageId = s.activePageId;
      const creationPoint = state.kind === "armed" ? state.downWorld : world;
      const parentId = resolveCreationParentId(s, creationPoint);

      let bbox: Rect;
      let trigger: "shortcut" | "toolbar" | "click_default_size";

      if (state.kind === "armed") {
        if (config.allowDefaultSize === false) {
          state = { kind: "idle" };
          useStore.setState((sx) => { sx.dragPreview = { kind: null, data: null }; });
          return;
        }
        bbox = {
          x: state.downWorld.x - DEFAULT_SIZE / 2,
          y: state.downWorld.y - DEFAULT_SIZE / 2,
          w: DEFAULT_SIZE,
          h: DEFAULT_SIZE,
        };
        trigger = "click_default_size";
      } else {
        bbox = rectFromPoints(state.downWorld, world);
        if (state.modifiers.shift) {
          const side = Math.max(bbox.w, bbox.h);
          bbox = { x: bbox.x, y: bbox.y, w: side, h: side };
        }
        trigger = "shortcut";
      }

      if (bbox.w === 0 || bbox.h === 0) {
        state = { kind: "idle" };
        useStore.setState((sx) => { sx.dragPreview = { kind: null, data: null }; });
        return;
      }

      const page = s.document.pages.find((p) => p.id === pageId);
      const ordinal = page ? config.countOf(page) + 1 : 1;
      const localBbox = worldRectToParentLocal(s, parentId, bbox);
      const node = config.makeNode(localBbox, parentId, ordinal);

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

      setSelection([node.id], "implicit_after_create");
      emitSemantic(config.emitOnCreate(node, bbox, parentId, state.modifiers, trigger));

      const revert = config.revertToMove !== false;
      if (revert) {
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

export function defaultLayerBase(bbox: Rect, parentId: string): Pick<Layer, "id" | "parentId" | "x" | "y" | "w" | "h" | "rotation" | "scaleX" | "scaleY" | "visible" | "locked" | "opacity" | "constraints"> {
  return {
    id: uid("layer"),
    parentId,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
  };
}

export function countByType(page: Page, type: Layer["type"]): number {
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
