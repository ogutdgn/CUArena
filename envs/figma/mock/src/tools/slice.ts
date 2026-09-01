import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Slice } from "@/types/scene";

export const sliceTool = makeCreationBboxTool({
  toolId: "slice",
  countOf: (page) => countByType(page, "slice"),
  makeNode: (bbox, parentId, ordinal): Slice => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("slice"),
    type: "slice",
    name: `Slice ${ordinal}`,
  }),
  emitOnCreate: (layer, bbox, parentId, _modifiers, trigger) => ({
    name: "create_slice" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    parentId,
    trigger:
      trigger === "shortcut"
        ? ("shortcut" as const)
        : ("toolbar" as const),
  }),
});
