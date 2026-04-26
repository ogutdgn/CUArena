import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Polygon } from "@/types/scene";

export const polygonTool = makeCreationBboxTool({
  toolId: "polygon",
  countOf: (page) => countByType(page, "polygon"),
  makeNode: (bbox, parentId, ordinal): Polygon => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("polygon"),
    type: "polygon",
    name: `Polygon ${ordinal}`,
    sides: 3,
    fills: [{ kind: "solid", color: { r: 0.851, g: 0.851, b: 0.851, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
  }),
  emitOnCreate: (layer, bbox, parentId, modifiers, trigger) => ({
    name: "create_polygon" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    sides: 3,
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
