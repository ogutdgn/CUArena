import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Frame } from "@/types/scene";

export const frameTool = makeCreationBboxTool({
  toolId: "frame",
  countOf: (page) => countByType(page, "frame"),
  makeNode: (bbox, parentId, ordinal): Frame => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("frame"),
    type: "frame",
    name: `Frame ${ordinal}`,
    fills: [{ kind: "solid", color: { r: 0.92, g: 0.92, b: 0.92, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    cornerRadius: 0,
    clipsContent: true,
    children: [],
  }),
  emitOnCreate: (layer, bbox, parentId, _modifiers, trigger) => ({
    name: "create_frame" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    parentId,
    mode: "drag" as const,
    trigger:
      trigger === "shortcut"
        ? ("shortcut_F" as const)
        : trigger === "toolbar"
        ? ("toolbar" as const)
        : ("preset" as const),
  }),
});
