import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Rectangle } from "@/types/scene";

export const rectangleTool = makeCreationBboxTool({
  toolId: "rectangle",
  countOf: (page) => countByType(page, "rectangle"),
  makeNode: (bbox, parentId, ordinal): Rectangle => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("rect"),
    type: "rectangle",
    name: `Rectangle ${ordinal}`,
    cornerRadius: 0,
    fills: [{ kind: "solid", color: { r: 0.851, g: 0.851, b: 0.851, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
  }),
  emitOnCreate: (layer, bbox, parentId, modifiers, trigger) => ({
    name: "create_rectangle",
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    parentId,
    modifiers: { shift: modifiers.shift, alt: modifiers.alt },
    trigger:
      trigger === "shortcut"
        ? "shortcut_R"
        : trigger === "toolbar"
        ? "toolbar"
        : "click_default_size",
  }),
});
