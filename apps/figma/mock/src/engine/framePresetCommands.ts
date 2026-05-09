import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { resolveCreationParentId, worldRectToParentLocal } from "./coordinates";
import { getSelectedLayers, getActivePage } from "./selectors";
import { setSelection } from "./commands";
import type { Frame, Layer } from "@/types/scene";
import type { TransformMap } from "@/types/ops";
import type { FramePreset } from "@/util/framePresets";
import { uid } from "@/util/id";

function frameBase(parentId: string, x: number, y: number, w: number, h: number): Omit<Frame, "id" | "type" | "name"> {
  return {
    parentId,
    x,
    y,
    w,
    h,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
    fills: [{ kind: "solid", color: { r: 0.92, g: 0.92, b: 0.92, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    cornerRadius: 0,
    clipsContent: true,
    children: [],
  };
}

function parentChildCount(parentId: string): number {
  const s = useStore.getState();
  const pageParent = s.document.pages.find((p) => p.id === parentId);
  if (pageParent) return pageParent.children.length;
  const indexedParent = s.nodesById[parentId] as (Layer & { children?: Layer[] }) | undefined;
  if (indexedParent && Array.isArray(indexedParent.children)) return indexedParent.children.length;
  return 0;
}

export function createFrameFromPreset(preset: FramePreset): void {
  const s = useStore.getState();
  const page = getActivePage(s);
  if (!page) return;

  const vp = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const anchor = s.cursorWorld ?? s.insertionCursor ?? { x: vp.x, y: vp.y };
  const parentId = resolveCreationParentId(s, anchor);

  const worldRect = {
    x: anchor.x - preset.w / 2,
    y: anchor.y - preset.h / 2,
    w: preset.w,
    h: preset.h,
  };

  const localRect = worldRectToParentLocal(s, parentId, worldRect);
  const node: Frame = {
    id: uid("frame"),
    type: "frame",
    name: preset.label,
    ...frameBase(parentId, localRect.x, localRect.y, localRect.w, localRect.h),
  };

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "create_node",
    pageId: s.activePageId,
    parentId,
    indexInParent: parentChildCount(parentId),
    node,
  });

  emitSemantic({
    name: "create_frame",
    layerId: node.id,
    x: worldRect.x,
    y: worldRect.y,
    w: worldRect.w,
    h: worldRect.h,
    parentId,
    mode: "preset",
    trigger: "preset",
  });

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
}

function transformTuple(layer: Frame) {
  return {
    x: layer.x,
    y: layer.y,
    w: layer.w,
    h: layer.h,
    rotation: layer.rotation,
    scaleX: layer.scaleX,
    scaleY: layer.scaleY,
  };
}

export function applyFramePresetToSelection(preset: FramePreset): void {
  const s = useStore.getState();
  const frames = getSelectedLayers(s).filter((layer): layer is Frame => layer.type === "frame");
  if (frames.length === 0) return;

  const before: TransformMap = {};
  const after: TransformMap = {};
  const beforeRect: Record<string, { x: number; y: number; w: number; h: number }> = {};
  const afterRect: Record<string, { x: number; y: number; w: number; h: number }> = {};

  for (const frame of frames) {
    if (frame.w === preset.w && frame.h === preset.h) continue;
    before[frame.id] = transformTuple(frame);
    after[frame.id] = {
      ...transformTuple(frame),
      w: preset.w,
      h: preset.h,
    };
    beforeRect[frame.id] = { x: frame.x, y: frame.y, w: frame.w, h: frame.h };
    afterRect[frame.id] = { x: frame.x, y: frame.y, w: preset.w, h: preset.h };
  }

  const ids = Object.keys(after);
  if (ids.length === 0) return;

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids,
    before,
    after,
  });

  emitSemantic({
    name: "resize_layer",
    layerIds: ids,
    before: beforeRect,
    after: afterRect,
    handle: "se",
    trigger: "panel_input",
    modifiers: { shift: false, alt: false },
  });
}
