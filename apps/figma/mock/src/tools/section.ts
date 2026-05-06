import { makeCreationBboxTool, defaultLayerBase, countByType } from "./creationBbox";
import { uid } from "@/util/id";
import type { Section } from "@/types/scene";

export const sectionTool = makeCreationBboxTool({
  toolId: "section",
  countOf: (page) => countByType(page, "section"),
  makeNode: (bbox, parentId, ordinal): Section => ({
    ...defaultLayerBase(bbox, parentId),
    id: uid("section"),
    type: "section",
    name: `Section ${ordinal}`,
    fills: [{ kind: "solid", color: { r: 0.95, g: 0.95, b: 0.95, a: 1 }, opacity: 1, visible: true }],
    children: [],
    clipsContent: false,
    devStatus: null,
  }),
  emitOnCreate: (layer, bbox, parentId, _modifiers, trigger) => ({
    name: "create_section" as const,
    layerId: layer.id,
    x: bbox.x,
    y: bbox.y,
    w: bbox.w,
    h: bbox.h,
    parentId,
    trigger:
      trigger === "shortcut"
        ? ("shortcut_shift_S" as const)
        : ("toolbar" as const),
  }),
});
