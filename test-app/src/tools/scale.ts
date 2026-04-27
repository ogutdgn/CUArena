// Scale tool (K): handle-drag to scale layers.
// Unlike resize (move tool), scale additionally multiplies stroke weights,
// corner radii, and font sizes by the drag scale factor.
// Shift = uniform scale. Alt = scale from center.

import type { ITool } from "./types";
import type { Rect } from "@/util/geometry";
import { rectFromPoints, rectIntersects } from "@/util/geometry";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId, openTransaction, commitTransaction, abortTransaction } from "@/engine/dispatch";
import { hitTest, getActivePage, selectionBbox } from "@/engine/selectors";
import { setSelection, deselectAll } from "@/engine/commands";
import { emitSemantic } from "@/logger/semantic";
import type { TransformMap, TransformTuple } from "@/types/ops";
import type { Layer, Page, Stroke, Rectangle, Image, Frame, Text } from "@/types/scene";
import { worldRectOfLayer } from "@/engine/coordinates";
import type { HandleDir } from "@/ui/overlays/SelectionOverlay";

const DRAG_THRESHOLD = 3;

type State =
  | { kind: "idle" }
  | { kind: "armed_layer"; layerId: string; downWorld: { x: number; y: number }; shift: boolean }
  | { kind: "armed_box"; downWorld: { x: number; y: number }; shift: boolean; scopeContainerId: string | null }
  | {
      kind: "armed_handle";
      handleDir: HandleDir;
      downWorld: { x: number; y: number };
      startBbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      modifiers: { shift: boolean; alt: boolean };
    }
  | {
      kind: "active_handle_drag";
      handleDir: HandleDir;
      downWorld: { x: number; y: number };
      startBbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      txId: string;
      modifiers: { shift: boolean; alt: boolean };
    }
  | {
      kind: "active_box_drag";
      downWorld: { x: number; y: number };
      currentWorld: { x: number; y: number };
      shift: boolean;
      scopeContainerId: string | null;
    };

let state: State = { kind: "idle" };

function getHandleDirFromTarget(e: PointerEvent): HandleDir | null {
  const t = e.target as Element | null;
  if (!t) return null;
  const el = t.closest?.("[data-handle]") as HTMLElement | null;
  if (!el) return null;
  return (el.dataset.handle as HandleDir) ?? null;
}

function transformOf(l: Layer): TransformTuple {
  return { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
}

function worldTransformOf(s: ReturnType<typeof useStore.getState>, l: Layer): TransformTuple {
  const wr = worldRectOfLayer(s, l);
  return { x: wr.x, y: wr.y, w: wr.w, h: wr.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
}

function applyHandleResize(start: Rect, dir: HandleDir, dx: number, dy: number, shift: boolean, alt: boolean): Rect {
  let { x, y, w, h } = start;
  const north = dir.includes("n");
  const south = dir.includes("s");
  const west = dir.includes("w");
  const east = dir.includes("e");

  if (alt) {
    if (north && !south) { y += dy; h -= 2 * dy; }
    if (south && !north) { h += 2 * dy; y -= dy; }
    if (west && !east) { x += dx; w -= 2 * dx; }
    if (east && !west) { w += 2 * dx; x -= dx; }
  } else {
    if (north && !south) { y += dy; h -= dy; }
    if (south && !north) { h += dy; }
    if (west && !east) { x += dx; w -= dx; }
    if (east && !west) { w += dx; }
  }

  if (shift && start.w > 0 && start.h > 0) {
    const aspect = start.w / start.h;
    if (north || south) {
      const targetW = h * aspect;
      const dw = targetW - w;
      if (east) w += dw;
      else if (west) { w += dw; x -= dw; }
      else { w = targetW; x = start.x - (targetW - start.w) / 2; }
    } else if (east || west) {
      const targetH = w / aspect;
      const dh = targetH - h;
      if (south) h += dh;
      else if (north) { h += dh; y -= dh; }
      else { h = targetH; y = start.y - (targetH - start.h) / 2; }
    }
  }

  if (w < 0) { x += w; w = -w; }
  if (h < 0) { y += h; h = -h; }
  return { x, y, w, h };
}

// Dispatch set_property ops for strokes, cornerRadius, fontSize scaled by factor.
function dispatchPropertyScale(
  layerIds: string[],
  startTransforms: TransformMap,
  txId: string,
) {
  const s = useStore.getState();
  const pageId = s.activePageId;

  for (const id of layerIds) {
    const st = startTransforms[id];
    const layer = s.nodesById[id] as Layer | undefined;
    if (!st || !layer || (layer as unknown as Page).type === "page") continue;

    const startW = Math.max(1, st.w);
    const startH = Math.max(1, st.h);
    const finalW = Math.max(1, layer.w);
    const finalH = Math.max(1, layer.h);
    const sx = finalW / startW;
    const sy = finalH / startH;
    // Geometric mean preserves scale consistently for non-uniform drags.
    const sf = Math.sqrt(Math.abs(sx) * Math.abs(sy));
    if (Math.abs(sf - 1) < 0.001) continue;

    // Scale stroke weights
    if ("strokes" in layer && Array.isArray((layer as { strokes: Stroke[] }).strokes)) {
      const src = layer as { strokes: Stroke[] };
      if (src.strokes.length > 0) {
        const before: Record<string, unknown> = {};
        const after: Record<string, unknown> = {};
        // We need the original strokes from before this drag. Re-derive from startTransforms
        // isn't possible, so snapshot the current strokes (which reflect no property change yet).
        before[id] = src.strokes;
        after[id] = src.strokes.map((stroke) => ({ ...stroke, weight: Math.max(0.01, stroke.weight * sf) }));
        dispatch(
          {
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_property",
            pageId,
            ids: [id],
            path: "strokes",
            before,
            after,
          },
          { transactionId: txId },
        );
      }
    }

    // Scale corner radius
    if ("cornerRadius" in layer) {
      const cr = (layer as Rectangle | Image | Frame).cornerRadius;
      const before: Record<string, unknown> = { [id]: cr };
      let scaled: number | [number, number, number, number];
      if (typeof cr === "number") {
        scaled = Math.max(0, cr * sf);
      } else {
        scaled = cr.map((r) => Math.max(0, r * sf)) as [number, number, number, number];
      }
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_property",
          pageId,
          ids: [id],
          path: "cornerRadius",
          before,
          after: { [id]: scaled },
        },
        { transactionId: txId },
      );
    }

    // Scale font size for text layers
    if (layer.type === "text") {
      const textLayer = layer as Text;
      const before: Record<string, unknown> = { [id]: textLayer.fontSize };
      const scaledSize = Math.max(1, textLayer.fontSize * sf);
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_property",
          pageId,
          ids: [id],
          path: "fontSize",
          before,
          after: { [id]: scaledSize },
        },
        { transactionId: txId },
      );
    }
  }
}

export const scaleTool: ITool = {
  onPointerDown(world, e) {
    const s = useStore.getState();
    const mods = { shift: e.shiftKey, alt: e.altKey };

    // Handle drag?
    const handleDir = getHandleDirFromTarget(e);
    if (handleDir) {
      const bbox = selectionBbox(s);
      const layerIds = s.selectionByPage[s.activePageId] ?? [];
      if (bbox && layerIds.length > 0) {
        const layers = layerIds
          .map((id) => s.nodesById[id])
          .filter((n): n is Layer => !!n && (n as unknown as Page).type !== "page");
        const startTransforms: TransformMap = {};
        const startWorldTransforms: TransformMap = {};
        for (const l of layers) startTransforms[l.id] = transformOf(l);
        for (const l of layers) startWorldTransforms[l.id] = worldTransformOf(s, l);
        state = {
          kind: "armed_handle",
          handleDir,
          downWorld: world,
          startBbox: { ...bbox },
          layerIds,
          startTransforms,
          startWorldTransforms,
          modifiers: mods,
        };
        return;
      }
    }

    // Layer hit → select
    const hit = hitTest(s, world.x, world.y);
    if (hit) {
      const cur = s.selectionByPage[s.activePageId] ?? [];
      if (e.shiftKey) {
        if (cur.includes(hit.id)) {
          setSelection(cur.filter((id) => id !== hit.id), "shift_click_remove");
        } else {
          setSelection([...cur, hit.id], "shift_click_add");
        }
      } else if (!cur.includes(hit.id)) {
        setSelection([hit.id], "click_select");
      }
      state = { kind: "armed_layer", layerId: hit.id, downWorld: world, shift: e.shiftKey };
      return;
    }

    // Empty canvas with focus context:
    // click outside exits context; click inside keeps scoped selection.
    const fc = s.focusContextByPage[s.activePageId] ?? null;
    let scopeContainerId: string | null = fc;
    if (fc != null) {
      const focusNode = s.nodesById[fc] as Layer | undefined;
      if (focusNode && (focusNode.type === "group" || focusNode.type === "frame" || focusNode.type === "section")) {
        const wr = worldRectOfLayer(s, focusNode);
        const inside =
          world.x >= wr.x &&
          world.x <= wr.x + wr.w &&
          world.y >= wr.y &&
          world.y <= wr.y + wr.h;
        if (!inside) {
          dispatch({
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_focus_context",
            pageId: s.activePageId,
            before: fc,
            after: null,
          });
          emitSemantic({ name: "exit_group", groupId: fc });
          state = { kind: "idle" };
          return;
        }
      } else {
        scopeContainerId = null;
      }
    }

    // Empty canvas → arm box-select
    state = { kind: "armed_box", downWorld: world, shift: e.shiftKey, scopeContainerId };
  },

  onPointerMove(world, e) {
    if (state.kind === "armed_handle") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
      const txId = openTransaction();
      state = {
        kind: "active_handle_drag",
        handleDir: state.handleDir,
        downWorld: state.downWorld,
        startBbox: state.startBbox,
        layerIds: state.layerIds,
        startTransforms: state.startTransforms,
        startWorldTransforms: state.startWorldTransforms,
        txId,
        modifiers: state.modifiers,
      };
      this.onPointerMove?.(world, e);
      return;
    }

    if (state.kind === "active_handle_drag") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      const newBbox = applyHandleResize(state.startBbox, state.handleDir, dx, dy, e.shiftKey, e.altKey);
      const after: TransformMap = {};
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        const tWorld = state.startWorldTransforms[id];
        if (!t || !tWorld) continue;
        const nxWorld =
          state.startBbox.w === 0
            ? newBbox.x
            : newBbox.x + ((tWorld.x - state.startBbox.x) / state.startBbox.w) * newBbox.w;
        const nyWorld =
          state.startBbox.h === 0
            ? newBbox.y
            : newBbox.y + ((tWorld.y - state.startBbox.y) / state.startBbox.h) * newBbox.h;
        const nw = state.startBbox.w === 0 ? newBbox.w : (t.w / state.startBbox.w) * newBbox.w;
        const nh = state.startBbox.h === 0 ? newBbox.h : (t.h / state.startBbox.h) * newBbox.h;
        const layerNow = useStore.getState().nodesById[id] as Layer | undefined;
        if (!layerNow || (layerNow as unknown as Page).type === "page") continue;
        const parent = useStore.getState().nodesById[layerNow.parentId];
        const px =
          parent && (parent as unknown as Page).type !== "page"
            ? worldRectOfLayer(useStore.getState(), parent as Layer).x
            : 0;
        const py =
          parent && (parent as unknown as Page).type !== "page"
            ? worldRectOfLayer(useStore.getState(), parent as Layer).y
            : 0;
        after[id] = { ...t, x: nxWorld - px, y: nyWorld - py, w: Math.max(1, Math.abs(nw)), h: Math.max(1, Math.abs(nh)) };
      }
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_transform",
          pageId: useStore.getState().activePageId,
          ids: state.layerIds,
          before: state.startTransforms,
          after,
        },
        { transactionId: state.txId },
      );
      return;
    }

    if (state.kind === "armed_box") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
      state = {
        kind: "active_box_drag",
        downWorld: state.downWorld,
        currentWorld: world,
        shift: state.shift,
        scopeContainerId: state.scopeContainerId,
      };
      useStore.setState((s) => {
        s.dragPreview = {
          kind: "marquee",
          data: rectFromPoints((state as Extract<State, { kind: "active_box_drag" }>).downWorld, world),
        };
      });
      return;
    }

    if (state.kind === "active_box_drag") {
      state = { ...state, currentWorld: world };
      useStore.setState((s) => {
        s.dragPreview = {
          kind: "marquee",
          data: rectFromPoints((state as Extract<State, { kind: "active_box_drag" }>).downWorld, world),
        };
      });
    }
  },

  onPointerUp(_world, _e) {
    if (state.kind === "armed_layer" || state.kind === "armed_handle") {
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "active_handle_drag") {
      // Apply property scale (strokes/radii/font) within the same transaction.
      dispatchPropertyScale(state.layerIds, state.startTransforms, state.txId);
      commitTransaction(state.txId);

      const s = useStore.getState();
      const before: Record<string, { x: number; y: number; w: number; h: number }> = {};
      const after: Record<string, { x: number; y: number; w: number; h: number }> = {};
      const scaleFactor: { sx: number; sy: number } = { sx: 1, sy: 1 };
      for (const id of state.layerIds) {
        const t0 = state.startTransforms[id];
        const cur = s.nodesById[id] as Layer | undefined;
        if (!t0 || !cur) continue;
        before[id] = { x: t0.x, y: t0.y, w: t0.w, h: t0.h };
        after[id] = { x: cur.x, y: cur.y, w: cur.w, h: cur.h };
        scaleFactor.sx = Math.max(1, cur.w) / Math.max(1, t0.w);
        scaleFactor.sy = Math.max(1, cur.h) / Math.max(1, t0.h);
      }
      emitSemantic({
        name: "scale_layer",
        layerIds: state.layerIds,
        factor: scaleFactor,
        anchor: { x: state.startBbox.x, y: state.startBbox.y },
        trigger: "drag",
      });
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "armed_box") {
      deselectAll("click_empty_canvas");
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "active_box_drag") {
      const page = getActivePage(useStore.getState());
      if (!page) {
        state = { kind: "idle" };
        useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
        return;
      }
      const box: Rect = rectFromPoints(state.downWorld, state.currentWorld);
      const hits: string[] = [];
      let roots = page.children;
      if (state.scopeContainerId) {
        const scope = useStore.getState().nodesById[state.scopeContainerId] as Layer | undefined;
        if (scope && (scope.type === "frame" || scope.type === "section" || scope.type === "group")) {
          roots = scope.children;
        }
      }
      walkLayers(roots, (l) => {
        if (l.locked || !l.visible) return;
        const wr = worldRectOfLayer(useStore.getState(), l);
        if (rectIntersects(box, { x: wr.x, y: wr.y, w: wr.w, h: wr.h })) hits.push(l.id);
      });
      const s2 = useStore.getState();
      const before = s2.selectionByPage[s2.activePageId] ?? [];
      const after = state.shift ? Array.from(new Set([...before, ...hits])) : hits;
      setSelection(after, "drag_box_select");
      useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
      state = { kind: "idle" };
      return;
    }
  },

  onAbort() {
    if (state.kind === "active_handle_drag") {
      abortTransaction(state.txId);
    }
    useStore.setState((s) => { s.dragPreview = { kind: null, data: null }; });
    state = { kind: "idle" };
  },
};

function walkLayers(layers: Layer[], visit: (l: Layer) => void) {
  for (const l of layers) {
    visit(l);
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      walkLayers(l.children, visit);
    }
  }
}
