// Text tool: click = auto-width text + edit, drag = bounded-width text + edit.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { createTextAt } from "@/engine/textCommands";
import { emitSemantic } from "@/logger/semantic";
import { dispatch, makeOpId } from "@/engine/dispatch";

const MIN_DRAG = 3;

type State =
  | { kind: "idle" }
  | { kind: "armed"; downWorld: Point }
  | { kind: "active"; downWorld: Point; currentWorld: Point };

let state: State = { kind: "idle" };

export const textTool: ITool = {
  onPointerDown(world, _e) {
    state = { kind: "armed", downWorld: world };
  },
  onPointerMove(world, _e) {
    if (state.kind === "armed") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < MIN_DRAG) return;
      state = { kind: "active", downWorld: state.downWorld, currentWorld: world };
    }
    if (state.kind === "active") {
      const cur = state;
      state = { ...cur, currentWorld: world };
      useStore.setState((s) => {
        s.dragPreview = {
          kind: "create_shape",
          data: {
            x: Math.min(cur.downWorld.x, world.x),
            y: Math.min(cur.downWorld.y, world.y),
            w: Math.abs(world.x - cur.downWorld.x),
            h: Math.abs(world.y - cur.downWorld.y),
          },
        };
      });
    }
  },
  onPointerUp(world, _e) {
    if (state.kind === "armed") {
      // Click = auto-width text at click point
      createTextAt(state.downWorld, "auto_width");
    } else if (state.kind === "active") {
      const minX = Math.min(state.downWorld.x, world.x);
      const minY = Math.min(state.downWorld.y, world.y);
      const w = Math.abs(world.x - state.downWorld.x);
      const h = Math.abs(world.y - state.downWorld.y);
      createTextAt({ x: minX, y: minY }, "fixed", w, h);
    }
    state = { kind: "idle" };
    useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });

    // Revert to move tool after creation
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
  },
  onAbort() {
    state = { kind: "idle" };
    useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
  },
};
