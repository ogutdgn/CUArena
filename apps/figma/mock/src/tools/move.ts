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
import { computeSnap, snapBboxFromStartAABBs } from "@/engine/snap";
import { setSelection, deselectAll } from "@/engine/commands";
import { enterTextEdit } from "@/engine/textCommands";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { TransformMap, TransformTuple } from "@/types/ops";
import type { Layer, Page } from "@/types/scene";
import type { HandleDir, RotateCorner } from "@/ui/overlays/SelectionOverlay";
import {
  invertMatrix,
  layerToWorldMatrix,
  localToWorld,
  multiplyMatrices,
  parentToWorldMatrix,
  transformFromLocalMatrix,
  worldRectOfLayer,
  worldAABBOfLayer,
} from "@/engine/coordinates";
import type { Matrix } from "@/engine/coordinates";
import { resizeSingleTransformedLayer } from "@/engine/resizeGeometry";
import { resizeLineEndpointFromWorld, type LineEndpoint, type LineLikeLayer } from "@/engine/lineGeometry";

const DRAG_THRESHOLD = 3;
const FRAME_NEST_ENTER_RATIO = 0.6;
const FRAME_NEST_EXIT_RATIO = 0.4;

interface CandidateRect {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface FrameCacheEntry {
  id: string;
  rect: CandidateRect;
}

type MatrixMap = Record<string, Matrix>;
type RectMap = Record<string, Rect>;

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
      kind: "armed_line_endpoint";
      endpoint: LineEndpoint;
      layerId: string;
      downWorld: Point;
      startLayer: LineLikeLayer;
    }
  | {
      kind: "active_layer_drag";
      layerIds: string[];
      sourceLayerIds: string[];
      downWorld: Point;
      startTransforms: TransformMap;
      startWorldTransforms: TransformMap;
      startWorldMatrices: MatrixMap;
      startWorldAABBs: RectMap;
      txId: string;
      isDuplicate: boolean;
      duplicatedIds: string[];
      // Cached at drag start. Sibling rects don't change during a drag (only
      // the moving layer moves), and frames don't get added/removed mid-drag,
      // so it's safe to populate once and reuse on every pointermove. Cuts
      // the per-frame O(layers × frames) scan that previously caused the
      // visible jitter (item #11).
      candidatesCache: CandidateRect[];
      framesCache: FrameCacheEntry[];
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
      kind: "active_line_endpoint_drag";
      endpoint: LineEndpoint;
      layerId: string;
      startLayer: LineLikeLayer;
      txId: string;
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

// Throttle frame-nesting reparent checks to one per animation frame. Real
// pointer events fire 60–120Hz; without this the overlap walk thrashes the
// scene-graph and produces visible jitter.
let pendingNestingRaf = 0;

function scheduleNestingCheck(): void {
  if (pendingNestingRaf !== 0) return;
  pendingNestingRaf = requestAnimationFrame(() => {
    pendingNestingRaf = 0;
    if (state.kind === "active_layer_drag") {
      applyFrameNestingByOverlap(state, state.txId);
    }
  });
}

function flushPendingNesting(): void {
  if (pendingNestingRaf !== 0) {
    cancelAnimationFrame(pendingNestingRaf);
    pendingNestingRaf = 0;
  }
}

function getHandleDirFromTarget(e: PointerEvent): HandleDir | null {
  const t = e.target as Element | null;
  if (!t) return null;
  const el = (t as Element).closest?.("[data-handle]") as HTMLElement | null;
  if (!el) return null;
  return (el.dataset.handle as HandleDir) ?? null;
}

function getLineEndpointFromTarget(e: PointerEvent): LineEndpoint | null {
  const t = e.target as Element | null;
  if (!t) return null;
  const el = (t as Element).closest?.("[data-line-endpoint]") as HTMLElement | null;
  if (!el) return null;
  const value = el.dataset.lineEndpoint;
  return value === "p1" || value === "p2" ? value : null;
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

    // 2) Line/arrow endpoint resize?
    const endpoint = getLineEndpointFromTarget(e);
    if (endpoint) {
      const ids = s.selectionByPage[s.activePageId] ?? [];
      const node = ids.length === 1 ? (s.nodesById[ids[0]] as Layer | undefined) : undefined;
      if (node && (node.type === "line" || node.type === "arrow")) {
        state = {
          kind: "armed_line_endpoint",
          endpoint,
          layerId: node.id,
          downWorld: world,
          startLayer: cloneLineLikeLayer(node),
        };
        return;
      }
    }

    // 3) Resize handle?
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

    // 4) Layer hit?
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
          const parentId = focusNode.parentId;
          const upOne = parentId && parentId !== s.activePageId ? parentId : null;
          dispatch({
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_focus_context",
            pageId: s.activePageId,
            before: fc,
            after: upOne,
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
      const startWorldMatrices: MatrixMap = {};
      const startWorldAABBs: RectMap = {};
      for (const l of layers) startTransforms[l.id] = transformOf(l);
      for (const l of layers) startWorldTransforms[l.id] = worldTransformOf(s, l);
      for (const l of layers) startWorldMatrices[l.id] = layerToWorldMatrix(s, l);
      for (const l of layers) startWorldAABBs[l.id] = worldAABBOfLayer(s, l);

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
          startWorldMatrices[duplicatedIds[i]] = startWorldMatrices[layers[i].id];
          startWorldAABBs[duplicatedIds[i]] = startWorldAABBs[layers[i].id];
          delete startTransforms[layers[i].id];
          delete startWorldTransforms[layers[i].id];
          delete startWorldMatrices[layers[i].id];
          delete startWorldAABBs[layers[i].id];
        }
      }

      // Snapshot siblings + frames once for this drag — see State type comment.
      const liveAfterDup = useStore.getState();
      const pageAfterDup = getActivePage(liveAfterDup);
      const movingSet = new Set(activeIds);
      const candidatesCache: CandidateRect[] = [];
      const framesCache: FrameCacheEntry[] = [];
      if (pageAfterDup) {
        const collect = (arr: Layer[]) => {
          for (const l of arr) {
            if (movingSet.has(l.id)) continue;
            if (!l.visible) continue;
            // Transformed AABB so a rotated/flipped sibling exposes its visible
            // outline as a snap candidate / frame target, not its un-rotated
            // stored rect.
            const wr = worldAABBOfLayer(liveAfterDup, l);
            const rect = { x: wr.x, y: wr.y, w: wr.w, h: wr.h };
            candidatesCache.push(rect);
            if (l.type === "frame") framesCache.push({ id: l.id, rect });
            if (l.type === "frame" || l.type === "section" || l.type === "group") collect(l.children);
          }
        };
        collect(pageAfterDup.children);
      }

      state = {
        kind: "active_layer_drag",
        layerIds: activeIds,
        sourceLayerIds: layerIds,
        downWorld: state.downWorld,
        startTransforms,
        startWorldTransforms,
        startWorldMatrices,
        startWorldAABBs,
        txId,
        isDuplicate: state.modifiers.alt,
        duplicatedIds,
        candidatesCache,
        framesCache,
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

    if (state.kind === "armed_line_endpoint") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
      const txId = openTransaction();
      state = {
        kind: "active_line_endpoint_drag",
        endpoint: state.endpoint,
        layerId: state.layerId,
        startLayer: state.startLayer,
        txId,
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
        // Normalize to [0, 360) on commit so the stored rotation matches
        // what panel input + rotate-90° + the readout display. Without this
        // a long drag could leave layer.rotation negative or > 360.
        const newRot = (((t.rotation + deltaDeg) % 360) + 360) % 360;
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

      const movingBbox = snapBboxFromStartAABBs(state.startWorldAABBs, state.layerIds);

      // Sibling candidates were snapshotted at drag start (see State type).
      // Avoids the per-pointermove scene walk that produced visible jitter.
      const sLive = useStore.getState();
      const candidates = state.candidatesCache;

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
        const tLocal = state.startTransforms[id];
        const tWorld = state.startWorldTransforms[id];
        const startWorldMatrix = state.startWorldMatrices[id];
        if (!tLocal || !tWorld || !startWorldMatrix) continue;
        const liveLayer = sLive.nodesById[id] as Layer | undefined;
        if (!liveLayer || (liveLayer as unknown as Page).type === "page") continue;
        const desiredWorldMatrix = translateWorldMatrix(startWorldMatrix, snapped.dx, snapped.dy);
        const localMatrix = multiplyMatrices(invertMatrix(parentToWorldMatrix(sLive, liveLayer.parentId)), desiredWorldMatrix);
        after[id] = transformFromLocalMatrix(liveLayer, localMatrix);
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
      // Re-evaluate nesting on the next animation frame so crossing the
      // overlap threshold reparents before pointer-up. rAF coalesces high-rate
      // pointer events to one check per paint frame; pointer-up forces a flush
      // so the final classification still lands.
      scheduleNestingCheck();
      return;
    }

    if (state.kind === "active_handle_drag") {
      const dx = world.x - state.downWorld.x;
      const dy = world.y - state.downWorld.y;
      const sLive = useStore.getState();
      const transformedSingle = resizeSingleTransformedLayer(sLive, state.layerIds, state.startTransforms, state.handleDir, world);
      if (transformedSingle) {
        dispatch(
          {
            id: makeOpId(),
            timestamp: performance.now(),
            kind: "set_transform",
            pageId: sLive.activePageId,
            ids: state.layerIds,
            before: state.startTransforms,
            after: transformedSingle,
          },
          { transactionId: state.txId },
        );
        return;
      }
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

    if (state.kind === "active_line_endpoint_drag") {
      const sLive = useStore.getState();
      const layer = sLive.nodesById[state.layerId] as Layer | undefined;
      if (!layer || (layer.type !== "line" && layer.type !== "arrow")) return;
      const resized = resizeLineEndpointFromWorld(sLive, state.startLayer, state.endpoint, world);
      const startTransform = transformOf(state.startLayer);
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_transform",
          pageId: sLive.activePageId,
          ids: [layer.id],
          before: { [layer.id]: startTransform },
          after: { [layer.id]: resized.transform },
        },
        { transactionId: state.txId },
      );
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_property",
          pageId: sLive.activePageId,
          ids: [layer.id],
          path: "p1",
          before: { [layer.id]: state.startLayer.p1 },
          after: { [layer.id]: resized.p1 },
        },
        { transactionId: state.txId },
      );
      dispatch(
        {
          id: makeOpId(),
          timestamp: performance.now(),
          kind: "set_property",
          pageId: sLive.activePageId,
          ids: [layer.id],
          path: "p2",
          before: { [layer.id]: state.startLayer.p2 },
          after: { [layer.id]: resized.p2 },
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
    if (state.kind === "armed_line_endpoint") {
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
      // Cancel any pending rAF nesting check and run it synchronously so the
      // final classification fires regardless of throttle timing.
      flushPendingNesting();
      applyFrameNestingByOverlap(state, state.txId);
      commitTransaction(state.txId);
      // Read final transforms post-snap from the live state.
      const live = useStore.getState();
      const beforePos: Record<string, { x: number; y: number }> = {};
      const afterPos: Record<string, { x: number; y: number }> = {};
      let dx = 0, dy = 0;
      for (const id of state.layerIds) {
        const startMatrix = state.startWorldMatrices[id];
        const cur = live.nodesById[id] as Layer | undefined;
        if (!startMatrix || !cur) continue;
        const afterMatrix = layerToWorldMatrix(live, cur);
        beforePos[id] = { x: startMatrix.e, y: startMatrix.f };
        afterPos[id] = { x: afterMatrix.e, y: afterMatrix.f };
        dx = afterMatrix.e - startMatrix.e;
        dy = afterMatrix.f - startMatrix.f;
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

    if (state.kind === "active_line_endpoint_drag") {
      commitTransaction(state.txId);
      const live = useStore.getState();
      const cur = live.nodesById[state.layerId] as Layer | undefined;
      if (cur && (cur.type === "line" || cur.type === "arrow")) {
        emitSemantic({
          name: "resize_line_endpoint",
          layerId: state.layerId,
          endpoint: state.endpoint,
          before: {
            transform: transformOf(state.startLayer),
            p1: state.startLayer.p1,
            p2: state.startLayer.p2,
          },
          after: {
            transform: transformOf(cur),
            p1: cur.p1,
            p2: cur.p2,
          },
          trigger: "drag",
        });
      }
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
        // Marquee select against the rotated/flipped layer's visible outline.
        const wr = worldAABBOfLayer(useStore.getState(), l);
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
    if (
      state.kind === "active_layer_drag" ||
      state.kind === "active_handle_drag" ||
      state.kind === "active_rotate_drag" ||
      state.kind === "active_line_endpoint_drag"
    ) {
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

function translateWorldMatrix(matrix: Matrix, dx: number, dy: number): Matrix {
  return { ...matrix, e: matrix.e + dx, f: matrix.f + dy };
}

function cloneLineLikeLayer(layer: LineLikeLayer): LineLikeLayer {
  return {
    ...layer,
    p1: { ...layer.p1 },
    p2: { ...layer.p2 },
    strokes: layer.strokes.map((stroke) => ({ ...stroke })),
    effects: layer.effects.map((effect) => ({ ...effect })),
  } as LineLikeLayer;
}

function worldTransformOf(s: ReturnType<typeof useStore.getState>, l: Layer): TransformTuple {
  const origin = localToWorld(s, l.parentId, { x: l.x, y: l.y });
  return {
    x: origin.x,
    y: origin.y,
    w: l.w,
    h: l.h,
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

function applyFrameNestingByOverlap(
  drag: Extract<State, { kind: "active_layer_drag" }>,
  txId: string,
): void {
  const s = useStore.getState();
  const page = getActivePage(s);
  if (!page) return;

  const movedSet = new Set(drag.layerIds);
  const movedRoots = drag.layerIds.filter((id) => {
    let cur = s.nodesById[id] as Layer | undefined;
    while (cur && (cur as unknown as Page).type !== "page") {
      const parent = s.nodesById[cur.parentId] as Layer | Page | undefined;
      if (!parent || (parent as unknown as Page).type === "page") break;
      if (movedSet.has((parent as Layer).id)) return false;
      cur = parent as Layer;
    }
    return true;
  });

  // Frame rects were cached at drag start and don't move during the drag, so
  // skip the scene walk + per-frame world-rect computation.
  const frames = drag.framesCache;

  for (const id of movedRoots) {
    const now = useStore.getState();
    const layer = now.nodesById[id] as Layer | undefined;
    if (!layer || (layer as unknown as Page).type === "page") continue;

    // Use the transformed AABB so a rotated/flipped moving layer overlaps
    // its destination frame by visible outline, not by its un-rotated stored
    // rect. Frames in the cache are already AABB-based for the same reason.
    const wr = worldAABBOfLayer(now, layer);
    const area = Math.max(1, wr.w * wr.h);

    const currentParent = now.nodesById[layer.parentId] as Layer | Page | undefined;
    const currentFrameParent =
      currentParent &&
      (currentParent as Page).type !== "page" &&
      (currentParent as Layer).type === "frame"
        ? (currentParent as Layer)
        : null;
    const currentOverlap =
      currentFrameParent != null
        ? overlapRatio(wr, worldAABBOfLayer(now, currentFrameParent), area)
        : 0;

    let bestFrameId: string | null = null;
    let bestDepth = -1;
    let bestRatio = 0;

    for (const frame of frames) {
      if (frame.id === id) continue;
      if (isAncestor(now, id, frame.id)) continue; // don't move into own descendant
      if (movedSet.has(frame.id)) continue; // don't move into simultaneously moved frame

      const ratio = overlapRatio(wr, frame.rect, area);
      if (ratio < FRAME_NEST_ENTER_RATIO) continue;
      const depth = depthOf(now, frame.id);
      if (depth > bestDepth || (depth === bestDepth && ratio > bestRatio)) {
        bestDepth = depth;
        bestRatio = ratio;
        bestFrameId = frame.id;
      }
    }

    let toParentId = layer.parentId;
    if (bestFrameId) {
      toParentId = bestFrameId;
    } else if (currentFrameParent && currentOverlap < FRAME_NEST_EXIT_RATIO) {
      toParentId = currentFrameParent.parentId;
    }
    if (toParentId === layer.parentId) continue;

    const fromArr = childrenOf(now, layer.parentId);
    const toArr = childrenOf(now, toParentId);
    if (!fromArr || !toArr) continue;
    const fromIndex = fromArr.findIndex((c) => c.id === id);
    if (fromIndex < 0) continue;

    // Keep frame ejection visually near the source frame; otherwise append.
    let toIndex = toArr.length;
    if (currentFrameParent && toParentId === currentFrameParent.parentId) {
      const frameIndex = toArr.findIndex((c) => c.id === currentFrameParent.id);
      if (frameIndex >= 0) toIndex = frameIndex + 1;
    }

    // applyReparent now preserves world position by re-expressing x/y in the
    // new parent's coordinate space, so a follow-up set_transform is no longer
    // needed (and would double-correct on undo).
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "reparent",
        pageId: now.activePageId,
        moves: [{ id, fromParentId: layer.parentId, fromIndex, toParentId, toIndex }],
      },
      { transactionId: txId },
    );
    const afterState = useStore.getState();
    const afterLayer = afterState.nodesById[id] as Layer | undefined;
    const afterArr = afterLayer ? childrenOf(afterState, afterLayer.parentId) : null;
    const afterIndex = afterArr && afterLayer ? afterArr.findIndex((c) => c.id === id) : toIndex;
    emitSemantic({
      name: "reorder_layer",
      layerIds: [id],
      before: [{ parentId: layer.parentId, index: fromIndex }],
      after: [{ parentId: afterLayer?.parentId ?? toParentId, index: afterIndex >= 0 ? afterIndex : toIndex }],
      trigger: "canvas_drag",
    });
  }
}

function childrenOf(s: ReturnType<typeof useStore.getState>, parentId: string): Layer[] | null {
  const p = s.nodesById[parentId] as Layer | Page | undefined;
  if (!p) return null;
  if ((p as Page).type === "page") return (p as Page).children;
  if ("children" in (p as object)) {
    return ((p as Layer & { children?: Layer[] }).children ?? null);
  }
  return null;
}

function overlapRatio(
  a: { x: number; y: number; w: number; h: number },
  b: { x: number; y: number; w: number; h: number },
  aArea: number,
): number {
  const x1 = Math.max(a.x, b.x);
  const y1 = Math.max(a.y, b.y);
  const x2 = Math.min(a.x + a.w, b.x + b.w);
  const y2 = Math.min(a.y + a.h, b.y + b.h);
  const w = Math.max(0, x2 - x1);
  const h = Math.max(0, y2 - y1);
  return (w * h) / Math.max(1, aArea);
}

function depthOf(s: ReturnType<typeof useStore.getState>, id: string): number {
  let d = 0;
  let cur = s.nodesById[id] as Layer | Page | undefined;
  while (cur && (cur as unknown as Page).type !== "page") {
    const parent = s.nodesById[(cur as Layer).parentId] as Layer | Page | undefined;
    if (!parent || (parent as unknown as Page).type === "page") break;
    d += 1;
    cur = parent;
  }
  return d;
}

function isAncestor(
  s: ReturnType<typeof useStore.getState>,
  ancestorId: string,
  nodeId: string,
): boolean {
  let cur = s.nodesById[nodeId] as Layer | Page | undefined;
  while (cur && (cur as unknown as Page).type !== "page") {
    if ((cur as Layer).id === ancestorId) return true;
    cur = s.nodesById[(cur as Layer).parentId] as Layer | Page | undefined;
  }
  return false;
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
