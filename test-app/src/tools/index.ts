// Tool registry — looked up by activeTool from the store.

import type { ITool } from "./types";
import type { ToolId } from "@/types/ops";
import { moveTool } from "./move";
import { rectangleTool } from "./rectangle";
import { ellipseTool } from "./ellipse";
import { polygonTool } from "./polygon";
import { starTool } from "./star";
import { lineTool, arrowTool } from "./line";
import { handTool } from "./hand";
import { frameTool } from "./frame";
import { sectionTool } from "./section";
import { sliceTool } from "./slice";
import { textTool } from "./text";
import { penTool } from "./pen";
import { pencilTool } from "./pencil";
import { scaleTool } from "./scale";

const noopTool: ITool = {};

export const TOOLS: Record<ToolId, ITool> = {
  move: moveTool,
  rectangle: rectangleTool,
  ellipse: ellipseTool,
  polygon: polygonTool,
  star: starTool,
  line: lineTool,
  arrow: arrowTool,
  hand: handTool,
  frame: frameTool,
  section: sectionTool,
  slice: sliceTool,
  text: textTool,
  pen: penTool,
  pencil: pencilTool,
  scale: scaleTool,
  image_place: noopTool,
  comment_stub: noopTool,
  actions_menu_stub: noopTool,
};

export function getActiveTool(toolId: ToolId): ITool {
  return TOOLS[toolId] ?? noopTool;
}
