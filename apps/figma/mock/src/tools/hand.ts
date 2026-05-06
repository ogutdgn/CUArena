// Hand tool: drag-pan only.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore, selectActiveViewport } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";

type State =
  | { kind: "idle" }
  | { kind: "panning"; startWorld: Point; startViewport: { x: number; y: number; zoom: number } };

let state: State = { kind: "idle" };

export const handTool: ITool = {
  onPointerDown(world, _e) {
    const s = useStore.getState();
    state = {
      kind: "panning",
      startWorld: world,
      startViewport: { ...selectActiveViewport(s) },
    };
  },
  onPointerMove(world, _e) {
    if (state.kind !== "panning") return;
    const s = useStore.getState();
    const dx = world.x - state.startWorld.x;
    const dy = world.y - state.startWorld.y;
    const cur = selectActiveViewport(s);
    // Live viewport update — non-undoable. Skip undo on dispatch.
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_viewport",
        pageId: s.activePageId,
        before: cur,
        after: { ...cur, x: state.startViewport.x - dx, y: state.startViewport.y - dy },
      },
      { skipUndo: true },
    );
  },
  onPointerUp(_world, _e) {
    if (state.kind !== "panning") return;
    const s = useStore.getState();
    const final = selectActiveViewport(s);
    emitSemantic({
      name: "pan_canvas",
      delta: { dx: final.x - state.startViewport.x, dy: final.y - state.startViewport.y },
      before: { x: state.startViewport.x, y: state.startViewport.y },
      after: { x: final.x, y: final.y },
      trigger: "hand_tool_drag",
    });
    state = { kind: "idle" };
  },
  onAbort() {
    state = { kind: "idle" };
  },
};
