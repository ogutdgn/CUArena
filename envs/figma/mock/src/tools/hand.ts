// Hand tool: drag-pan only.

import type { ITool } from "./types";
import type { Point } from "@/util/geometry";
import { useStore, selectActiveViewport } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { pannedViewportFromClientDelta } from "@/engine/viewportPan";

type State =
  | { kind: "idle" }
  | { kind: "panning"; startClient: Point; currentClient: Point; startViewport: { x: number; y: number; zoom: number }; rafId: number | null };

let state: State = { kind: "idle" };

export const handTool: ITool = {
  onPointerDown(_world, e) {
    const s = useStore.getState();
    state = {
      kind: "panning",
      startClient: { x: e.clientX, y: e.clientY },
      currentClient: { x: e.clientX, y: e.clientY },
      startViewport: { ...selectActiveViewport(s) },
      rafId: null,
    };
  },
  onPointerMove(_world, e) {
    if (state.kind !== "panning") return;
    state.currentClient = { x: e.clientX, y: e.clientY };
    if (state.rafId != null) return;
    state.rafId = requestAnimationFrame(() => {
      if (state.kind !== "panning") return;
      state.rafId = null;
      applyPanFrame(state);
    });
  },
  onPointerUp(_world, _e) {
    if (state.kind !== "panning") return;
    if (state.rafId != null) {
      cancelAnimationFrame(state.rafId);
      state.rafId = null;
    }
    applyPanFrame(state);
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
    if (state.kind === "panning" && state.rafId != null) cancelAnimationFrame(state.rafId);
    state = { kind: "idle" };
  },
};

function applyPanFrame(panning: Extract<State, { kind: "panning" }>): void {
  const s = useStore.getState();
  const cur = selectActiveViewport(s);
  const after = pannedViewportFromClientDelta(panning.startViewport, panning.startClient, panning.currentClient);
  if (after.x === cur.x && after.y === cur.y && after.zoom === cur.zoom) return;
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_viewport",
      pageId: s.activePageId,
      before: cur,
      after,
    },
    { skipUndo: true },
  );
}
