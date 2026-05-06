import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Ellipse } from "@/types/scene";

export const ellipseTool = makeCreationBboxTool({
  toolId: "ellipse",
  countOf: (page) => countByType(page, "ellipse"),
  makeNode: (bbox, parentId, ordinal): Ellipse => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("ellipse"),
    type: "ellipse",
    name: `Ellipse ${ordinal}`,
    fills: [{ kind: "solid", color: { r: 0.851, g: 0.851, b: 0.851, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    arcStartAngle: 0,
    arcEndAngle: 360,
    innerRadius: 0,
  }),
  emitOnCreate: (layer, bbox, parentId, modifiers, trigger) => ({
    name: "create_ellipse" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    parentId,
    modifiers,
    trigger:
      trigger === "shortcut"
        ? ("shortcut_O" as const)
        : trigger === "toolbar"
        ? ("toolbar" as const)
        : ("click_default_size" as const),
  }),
});
