// Move tool: click-select, shift-click toggle, drag-box-select, drag-move,
// alt-drag duplicate, click-empty-deselect, drag-resize via 8 handles.
// Source: .analysis/engine-report.md §7.3.

import type { ITool } from "./types";
import type { Point, Rect } from "@/util/geometry";
import { rectFromPoints, rectIntersects } from "@/util/geometry";
import { useStore } from "@/engine/store";
import {
  dispatch,
  makeOpId,
  openTransaction,
  commitTransaction,
  abortTransaction,
} from "@/engine/dispatch";
import { hitTest, getActivePage, selectionBbox } from "@/engine/selectors";
import { computeSnap } from "@/engine/snap";
import { setSelection, deselectAll } from "@/engine/commands";
import { enterTextEdit } from "@/engine/textCommands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { TransformMap, TransformTuple } from "@/types/ops";
import type { Layer, Page } from "@/types/scene";
import type { HandleDir, RotateCorner } from "@/ui/overlays/SelectionOverlay";
import { worldRectOfLayer } from "@/engine/coordinates";

const DRAG_THRESHOLD = 3;

type State =
  | { kind: "idle" }
  | {
      kind: "armed_layer";
      layer: Layer;
      downWorld: Point;
      modifiers: { shift: boolean; alt: boolean };
    }
  | {
      kind: "armed_box";
      downWorld: Point;
      modifiers: { shift: boolean };
      scopeContainerId: string | null;
    }
  | {
      kind: "armed_handle";
      handleDir: HandleDir;
      downWorld: Point;
      startBbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      modifiers: { shift: boolean; alt: boolean };
    }
  | {
      kind: "active_layer_drag";
      layerIds: string[];
      sourceLayerIds: string[];
      downWorld: Point;
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      txId: string;
      isDuplicate: boolean;
      duplicatedIds: string[];
    }
  | {
      kind: "active_handle_drag";
      handleDir: HandleDir;
      downWorld: Point;
      startBbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      txId: string;
      modifiers: { shift: boolean; alt: boolean };
    }
  | {
      kind: "active_box_drag";
      downWorld: Point;
      currentWorld: Point;
      modifiers: { shift: boolean };
      scopeContainerId: string | null;
    }
  | {
      kind: "armed_rotate";
      corner: RotateCorner;
      downWorld: Point;
      bbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startAngle: number;
    }
  | {
      kind: "active_rotate_drag";
      corner: RotateCorner;
      downWorld: Point;
      bbox: Rect;
      layerIds: string[];
      startTransforms: TransformMap;
      startAngle: number;
      txId: string;
    };

let state: State = { kind: "idle" };

function getHandleDirFromTarget(e: PointerEvent): HandleDir | null {
  const t = e.target as Element | null;
  if (!t) return null;
  const el = (t as Element).closest?.("[data-handle]") as HTMLElement | null;
  if (!el) return null;
  return (el.dataset.handle as HandleDir) ?? null;
}

function getRotateCornerFromTarget(e: PointerEvent): RotateCorner | null {
  const t = e.target as Element | null;
  if (!t) return null;
  const el = (t as Element).closest?.("[data-rotate]") as HTMLElement | null;
  if (!el) return null;
  return (el.dataset.rotate as RotateCorner) ?? null;
}

export const moveTool: ITool = {
  onPointerDown(world, e) {
    const s = useStore.getState();
    const mods = { shift: e.shiftKey, alt: e.altKey };

    // 1) Rotate corner (just outside the handle)?
    const rotateCorner = getRotateCornerFromTarget(e);
    if (rotateCorner) {
      const bbox = selectionBbox(s);
      const layerIds = s.selectionByPage[s.activePageId] ?? [];
      if (bbox && layerIds.length > 0) {
        const layers = layerIds
          .map((id) => s.nodesById[id])
          .filter((n): n is Layer => !!n && (n as Page).type !== "page") as Layer[];
        const startTransforms: TransformMap = {};
        for (const l of layers) startTransforms[l.id] = transformOf(l);
        const cx = bbox.x + bbox.w / 2;
        const cy = bbox.y + bbox.h / 2;
        const startAngle = Math.atan2(world.y - cy, world.x - cx);
        state = {
          kind: "armed_rotate",
          corner: rotateCorner,
          downWorld: world,
          bbox: { ...bbox },
          layerIds,
          startTransforms,
          startAngle,
        };
        return;
      }
    }

    // 2) Resize handle?
    const handleDir = getHandleDirFromTarget(e);
    if (handleDir) {
      const bbox = selectionBbox(s);
      const layerIds = s.selectionByPage[s.activePageId] ?? [];
      if (bbox && layerIds.length > 0) {
        const layers = layerIds
          .map((id) => s.nodesById[id])
          .filter((n): n is Layer => !!n && (n as Page).type !== "page") as Layer[];
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

    // 3) Layer hit?
    const hit = hitTest(s, world.x, world.y);
    if (hit) {
      const cur = s.selectionByPage[s.activePageId] ?? [];
      const alreadySelected = cur.includes(hit.id);

      // Double-click on a text layer enters text edit mode.
      if (e.detail >= 2 && hit.type === "text") {
        if (!alreadySelected) setSelection([hit.id], "click_select");
        enterTextEdit(hit.id);
        state = { kind: "idle" };
        return;
      }

      // Double-click on a vector layer enters vector edit mode.
      if (e.detail >= 2 && hit.type === "vector") {
        if (!alreadySelected) setSelection([hit.id], "click_select");
        const beforeMode = useStore.getState().editMode;
        dispatch({
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_edit_mode",
          before: beforeMode,
          after: { kind: "vector", layerId: hit.id },
        });
        emitSemantic({ name: "mode_change", before: beforeMode.kind, after: "vector" });
        state = { kind: "idle" };
        return;
      }

      // Double-click on a group enters the group focus context.
      if (e.detail >= 2 && (hit.type === "group" || hit.type === "frame" || hit.type === "section")) {
        if (!alreadySelected) setSelection([hit.id], "click_select");
        const beforeCtx = useStore.getState().focusContextByPage[useStore.getState().activePageId] ?? null;
        dispatch({
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_focus_context",
          pageId: useStore.getState().activePageId,
          before: beforeCtx,
          after: hit.id,
        });
        emitSemantic({ name: "enter_group", groupId: hit.id });
        state = { kind: "idle" };
        return;
      }

      if (mods.shift) {
        if (alreadySelected) {
          setSelection(cur.filter((id) => id !== hit.id), "shift_click_remove");
          emitSemantic({
            name: "shift_click_remove_selection",
            targetLayerId: hit.id,
            pointer: world,
            source: "canvas",
          });
        } else {
          setSelection([...cur, hit.id], "shift_click_add");
          emitSemantic({
            name: "shift_click_add_selection",
            targetLayerId: hit.id,
            pointer: world,
            source: "canvas",
          });
        }
      } else if (!alreadySelected) {
        setSelection([hit.id], "click_select");
        emitSemantic({
          name: "click_select",
          targetLayerId: hit.id,
          pointer: world,
          source: "canvas",
        });
      }
      state = { kind: "armed_layer", layer: hit, downWorld: world, modifiers: mods };
      return;
    }

    // 4) Empty canvas in vector-edit mode → exit edit mode.
    if (s.editMode.kind === "vector") {
      const beforeMode = s.editMode;
      dispatch({
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_edit_mode",
        before: beforeMode,
        after: { kind: "none" },
      });
      emitSemantic({ name: "mode_change", before: beforeMode.kind, after: "none" });
      state = { kind: "idle" };
      return;
    }

    // 4b) Empty canvas with focus context.
    // Clicking outside the active scope exits it; clicking inside keeps scope.
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

    // 5) Empty canvas → arm box-select
    state = {
      kind: "armed_box",
      downWorld: world,
      modifiers: { shift: e.shiftKey },
      scopeContainerId,
    };
  },

  onPointerMove(world, e) {
    // Hover tracking when not in any active gesture.
    if (state.kind === "idle") {
      const sLive = useStore.getState();
      const hovered = hitTest(sLive, world.x, world.y);
      const id = hovered?.id ?? null;
      if (id !== sLive.hoveredNodeId) {
        useStore.setState((s) => { s.hoveredNodeId = id; });
      }
    }

    if (state.kind === "armed_layer") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return;

      const s = useStore.getState();
      let layerIds = s.selectionByPage[s.activePageId] ?? [];
      if (!layerIds.includes(state.layer.id)) layerIds = [state.layer.id];
      const layers = layerIds
        .map((id) => s.nodesById[id])
        .filter((n): n is Layer => !!n && (n as Page).type !== "page") as Layer[];
      const startTransforms: TransformMap = {};
      const startWorldTransforms: TransformMap = {};
      for (const l of layers) startTransforms[l.id] = transformOf(l);
      for (const l of layers) startWorldTransforms[l.id] = worldTransformOf(s, l);

      const txId = openTransaction();
      let duplicatedIds: string[] = [];
      let activeIds = layerIds.slice();
      if (state.modifiers.alt) {
        duplicatedIds = duplicateForDrag(s, layers);
        activeIds = duplicatedIds;
        setSelection(duplicatedIds, "implicit_after_duplicate");
        for (let i = 0; i < layers.length; i++) {
          startTransforms[duplicatedIds[i]] = startTransforms[layers[i].id];
          startWorldTransforms[duplicatedIds[i]] = startWorldTransforms[layers[i].id];
          delete startTransforms[layers[i].id];
          delete startWorldTransforms[layers[i].id];
        }
      }

      state = {
        kind: "active_layer_drag",
        layerIds: activeIds,
        sourceLayerIds: layerIds,
        downWorld: state.downWorld,
        startTransforms,
        startWorldTransforms,
        txId,
        isDuplicate: state.modifiers.alt,
        duplicatedIds,
      };
      this.onPointerMove?.(world, e);
      return;
    }

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

    if (state.kind === "armed_rotate") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
      const txId = openTransaction();
      state = {
        kind: "active_rotate_drag",
        corner: state.corner,
        downWorld: state.downWorld,
        bbox: state.bbox,
        layerIds: state.layerIds,
        startTransforms: state.startTransforms,
        startAngle: state.startAngle,
        txId,
      };
      this.onPointerMove?.(world, e);
      return;
    }

    if (state.kind === "active_rotate_drag") {
      const cx = state.bbox.x + state.bbox.w / 2;
      const cy = state.bbox.y + state.bbox.h / 2;
      const angleNow = Math.atan2(world.y - cy, world.x - cx);
      let deltaDeg = ((angleNow - state.startAngle) * 180) / Math.PI;
      if (e.shiftKey) deltaDeg = Math.round(deltaDeg / 15) * 15;
      const after: TransformMap = {};
      let displayDeg = 0;
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        if (!t) continue;
        const newRot = t.rotation + deltaDeg;
        after[id] = { ...t, rotation: newRot };
        displayDeg = newRot;
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
      // Render rotation readout near cursor
      useStore.setState((s) => {
        s.rotateReadout = { x: world.x, y: world.y, deg: ((displayDeg % 360) + 360) % 360 };
      });
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
        modifiers: state.modifiers,
        scopeContainerId: state.scopeContainerId,
      };
      useStore.setState((s) => {
        s.dragPreview = { kind: "marquee", data: rectFromPoints((state as Extract<State, { kind: "active_box_drag" }>).downWorld, world) };
      });
      return;
    }

    if (state.kind === "active_layer_drag") {
      const rawDx = world.x - state.downWorld.x;
      const rawDy = world.y - state.downWorld.y;

      // Compute moving group bbox at start
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (const id of state.layerIds) {
        const t = state.startWorldTransforms[id];
        if (!t) continue;
        if (t.x < minX) minX = t.x;
        if (t.y < minY) minY = t.y;
        if (t.x + t.w > maxX) maxX = t.x + t.w;
        if (t.y + t.h > maxY) maxY = t.y + t.h;
      }
      const movingBbox = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };

      // Collect sibling candidates: layers in active page not being dragged.
      const sLive = useStore.getState();
      const page = getActivePage(sLive);
      const candidates: { x: number; y: number; w: number; h: number }[] = [];
      if (page) {
        const movingSet = new Set(state.layerIds);
        const collect = (arr: Layer[]) => {
          for (const l of arr) {
            if (movingSet.has(l.id)) continue;
            if (!l.visible) continue;
            const wr = worldRectOfLayer(sLive, l);
            candidates.push({ x: wr.x, y: wr.y, w: wr.w, h: wr.h });
            if (l.type === "frame" || l.type === "section" || l.type === "group") collect(l.children);
          }
        };
        collect(page.children);
      }

      const zoom = (sLive.viewportByPage[sLive.activePageId] ?? { zoom: 1 }).zoom;
      // Skip snap when shift held (shift = constrain to axis; pure raw move).
      let snapped: ReturnType<typeof computeSnap> = { dx: rawDx, dy: rawDy, lines: [], measures: [] };
      if (!e.shiftKey) {
        snapped = computeSnap(movingBbox, rawDx, rawDy, candidates, zoom);
      } else {
        if (Math.abs(rawDx) > Math.abs(rawDy)) snapped = { dx: rawDx, dy: 0, lines: [], measures: [] };
        else snapped = { dx: 0, dy: rawDy, lines: [], measures: [] };
      }

      const after: TransformMap = {};
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        if (!t) continue;
        after[id] = { ...t, x: t.x + snapped.dx, y: t.y + snapped.dy };
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

      useStore.setState((s) => {
        s.snapLines = snapped.lines;
        s.snapMeasures = snapped.measures;
      });
      return;
    }

    if (state.kind === "active_handle_drag") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      const newBbox = applyHandleResize(state.startBbox, state.handleDir, dx, dy, e.shiftKey, e.altKey);
      const after: TransformMap = {};
      // Map each layer's transform proportionally with the bbox change.
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        const tWorld = state.startWorldTransforms[id];
        if (!t) continue;
        if (!tWorld) continue;
        const nxWorld =
          state.startBbox.w === 0 ? newBbox.x : newBbox.x + ((tWorld.x - state.startBbox.x) / state.startBbox.w) * newBbox.w;
        const nyWorld =
          state.startBbox.h === 0 ? newBbox.y : newBbox.y + ((tWorld.y - state.startBbox.y) / state.startBbox.h) * newBbox.h;
        const nw = state.startBbox.w === 0 ? newBbox.w : (t.w / state.startBbox.w) * newBbox.w;
        const nh = state.startBbox.h === 0 ? newBbox.h : (t.h / state.startBbox.h) * newBbox.h;
        const layerNow = useStore.getState().nodesById[id] as Layer | undefined;
        if (!layerNow || (layerNow as Page).type === "page") continue;
        const parent = useStore.getState().nodesById[layerNow.parentId];
        const px =
          parent && (parent as Page).type !== "page"
            ? worldRectOfLayer(useStore.getState(), parent as Layer).x
            : 0;
        const py =
          parent && (parent as Page).type !== "page"
            ? worldRectOfLayer(useStore.getState(), parent as Layer).y
            : 0;
        after[id] = {
          ...t,
          x: nxWorld - px,
          y: nyWorld - py,
          w: Math.max(1, Math.abs(nw)),
          h: Math.max(1, Math.abs(nh)),
        };
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

    if (state.kind === "active_box_drag") {
      state = { ...state, currentWorld: world };
      useStore.setState((s) => {
        s.dragPreview = { kind: "marquee", data: rectFromPoints((state as Extract<State, { kind: "active_box_drag" }>).downWorld, world) };
      });
      return;
    }
  },

  onPointerUp(_world, _e) {
    if (state.kind === "armed_layer") {
      state = { kind: "idle" };
      return;
    }
    if (state.kind === "armed_handle") {
      state = { kind: "idle" };
      return;
    }
    if (state.kind === "armed_rotate") {
      state = { kind: "idle" };
      return;
    }
    if (state.kind === "active_rotate_drag") {
      commitTransaction(state.txId);
      const beforeR: Record<string, number> = {};
      const afterR: Record<string, number> = {};
      const s = useStore.getState();
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        const cur = s.nodesById[id] as Layer | undefined;
        if (!t || !cur) continue;
        beforeR[id] = t.rotation;
        afterR[id] = cur.rotation;
      }
      emitSemantic({
        name: "rotate_layer",
        layerIds: state.layerIds,
        before: beforeR,
        after: afterR,
        trigger: "drag",
      });
      useStore.setState((sx) => { sx.rotateReadout = null; });
      state = { kind: "idle" };
      return;
    }
    if (state.kind === "armed_box") {
      deselectAll("click_empty_canvas");
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "active_layer_drag") {
      commitTransaction(state.txId);
      // Read final transforms post-snap from the live state.
      const live = useStore.getState();
      const beforePos: Record<string, { x: number; y: number }> = {};
      const afterPos: Record<string, { x: number; y: number }> = {};
      let dx = 0, dy = 0;
      for (const id of state.layerIds) {
        const t = state.startTransforms[id];
        const cur = live.nodesById[id] as Layer | undefined;
        if (!t || !cur) continue;
        beforePos[id] = { x: t.x, y: t.y };
        afterPos[id] = { x: cur.x, y: cur.y };
        dx = cur.x - t.x;
        dy = cur.y - t.y;
      }
      useStore.setState((s) => {
        s.snapLines = [];
        s.snapMeasures = [];
      });
      if (state.isDuplicate) {
        emitSemantic({
          name: "duplicate",
          sourceLayerIds: state.sourceLayerIds,
          newLayerIds: state.duplicatedIds,
          offset: { dx, dy },
          trigger: "alt_drag",
        });
      } else {
        emitSemantic({
          name: "move_layer",
          layerIds: state.layerIds,
          before: beforePos,
          after: afterPos,
          trigger: "drag",
          modifiers: { shift: false, alt: false, ctrl: false },
        });
      }
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "active_handle_drag") {
      commitTransaction(state.txId);
      const before: Record<string, { x: number; y: number; w: number; h: number }> = {};
      const after: Record<string, { x: number; y: number; w: number; h: number }> = {};
      const s = useStore.getState();
      for (const id of state.layerIds) {
        const t0 = state.startTransforms[id];
        const cur = s.nodesById[id] as Layer | undefined;
        if (!t0 || !cur) continue;
        before[id] = { x: t0.x, y: t0.y, w: t0.w, h: t0.h };
        after[id] = { x: cur.x, y: cur.y, w: cur.w, h: cur.h };
      }
      emitSemantic({
        name: "resize_layer",
        layerIds: state.layerIds,
        before,
        after,
        handle: state.handleDir,
        trigger: "drag",
        modifiers: { shift: state.modifiers.shift, alt: state.modifiers.alt },
      });
      state = { kind: "idle" };
      return;
    }

    if (state.kind === "active_box_drag") {
      const page = getActivePage(useStore.getState());
      if (!page) {
        state = { kind: "idle" };
        useStore.setState((s) => {
          s.dragPreview = { kind: null, data: null };
        });
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
      const after = state.modifiers.shift ? Array.from(new Set([...before, ...hits])) : hits;
      setSelection(after, "drag_box_select");
      emitSemantic({
        name: "drag_box_select",
        start: state.downWorld,
        end: state.currentWorld,
        layerIds: hits,
        modifier: state.modifiers.shift ? "shift_additive" : "none",
      });
      useStore.setState((s) => {
        s.dragPreview = { kind: null, data: null };
      });
      state = { kind: "idle" };
      return;
    }
  },

  onAbort() {
    if (state.kind === "active_layer_drag" || state.kind === "active_handle_drag" || state.kind === "active_rotate_drag") {
      abortTransaction(state.txId);
    }
    useStore.setState((s) => {
      s.dragPreview = { kind: null, data: null };
      s.hoveredNodeId = null;
    });
    state = { kind: "idle" };
  },
};

function transformOf(l: Layer): TransformTuple {
  return {
    x: l.x,
    y: l.y,
    w: l.w,
    h: l.h,
    rotation: l.rotation,
    scaleX: l.scaleX,
    scaleY: l.scaleY,
  };
}

function worldTransformOf(s: ReturnType<typeof useStore.getState>, l: Layer): TransformTuple {
  const wr = worldRectOfLayer(s, l);
  return {
    x: wr.x,
    y: wr.y,
    w: wr.w,
    h: wr.h,
    rotation: l.rotation,
    scaleX: l.scaleX,
    scaleY: l.scaleY,
  };
}

function walkLayers(layers: Layer[], visit: (l: Layer) => void) {
  for (const l of layers) {
    visit(l);
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      walkLayers(l.children, visit);
    }
  }
}

function duplicateForDrag(s: ReturnType<typeof useStore.getState>, sources: Layer[]): string[] {
  const newIds: string[] = [];
  for (const source of sources) {
    const clone = JSON.parse(JSON.stringify(source)) as Layer;
    reseedCloneIds(clone, source.parentId);
    const pageParent = s.document.pages.find((p) => p.id === source.parentId);
    const indexedParent = s.nodesById[source.parentId];
    const arr = pageParent
      ? pageParent.children
      : (indexedParent as (Layer & { children?: Layer[] }) | undefined)?.children;
    if (!arr) continue;
    const idx = arr.findIndex((c) => c.id === source.id);
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "create_node",
      pageId: s.activePageId,
      parentId: source.parentId,
      indexInParent: idx + 1,
      node: clone,
    });
    newIds.push(clone.id);
  }
  return newIds;
}

function reseedCloneIds(layer: Layer, parentId: string): void {
  layer.id = uid(layer.type);
  layer.parentId = parentId;
  if (layer.type === "frame" || layer.type === "section" || layer.type === "group") {
    for (const c of layer.children) {
      reseedCloneIds(c, layer.id);
    }
  }
}

// Compute new bbox given a handle drag.
function applyHandleResize(
  start: Rect,
  dir: HandleDir,
  dx: number,
  dy: number,
  shift: boolean,
  alt: boolean,
): Rect {
  let { x, y, w, h } = start;

  // Edge moves
  let north = dir.includes("n");
  let south = dir.includes("s");
  let west = dir.includes("w");
  let east = dir.includes("e");

  if (alt) {
    // Scale from center: mirror the drag on opposite edges
    if (north) { y += dy; h -= dy * 2; }
    if (south) { h += dy * 2; if (!north) y -= 0; }
    if (south && !north) { /* already applied symmetric via *2 */ }
    // The above isn't symmetric; redo properly:
  }

  // Reset and redo without the experimental block
  x = start.x; y = start.y; w = start.w; h = start.h;

  if (alt) {
    // Symmetric resize about the center
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

  // Shift = preserve aspect ratio of the original bbox
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

  // Handle inversion (drag past opposite edge): normalize so w/h stay positive.
  if (w < 0) { x += w; w = -w; }
  if (h < 0) { y += h; h = -h; }

  return { x, y, w, h };
}
