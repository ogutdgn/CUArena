import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Star } from "@/types/scene";

export const starTool = makeCreationBboxTool({
  toolId: "star",
  countOf: (page) => countByType(page, "star"),
  makeNode: (bbox, parentId, ordinal): Star => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("star"),
    type: "star",
    name: `Star ${ordinal}`,
    points: 5,
    innerRatio: 0.5,
    fills: [{ kind: "solid", color: { r: 0.851, g: 0.851, b: 0.851, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
  }),
  emitOnCreate: (layer, bbox, parentId, modifiers, trigger) => ({
    name: "create_star" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    points: 5,
    innerRatio: 0.5,
    parentId,
    modifiers,
    trigger:
      trigger === "shortcut"
        ? ("shortcut" as const)
        : trigger === "toolbar"
        ? ("toolbar" as const)
        : ("click_default_size" as const),
  }),
});
