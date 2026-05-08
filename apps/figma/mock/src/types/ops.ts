// Op union. Source: .analysis/engine-report.md §2.
// Every scene-graph mutation goes through one of these.

import type { Layer, Page, Color } from "./scene";

export type ToolId =
  | "move"
  | "scale"
  | "hand"
  | "frame"
  | "slice"
  | "section"
  | "rectangle"
  | "ellipse"
  | "polygon"
  | "star"
  | "line"
  | "arrow"
  | "image_place"
  | "text"
  | "pen"
  | "pencil"
  | "comment_stub"
  | "actions_menu_stub";

export interface EditMode {
  kind: "none" | "text" | "vector" | "pen_creation";
  layerId?: string;
}

// Transform tuple snapshot used by set_transform
export interface TransformTuple {
  x: number;
  y: number;
  w: number;
  h: number;
  rotation: number;
  scaleX: 1 | -1;
  scaleY: 1 | -1;
}

export type TransformMap = Record<string, TransformTuple>;

export interface Viewport {
  x: number;
  y: number;
  zoom: number;
}

// ---- Op union ----

export interface OpBase {
  id: string;
  timestamp: number;
}

export interface CreateNodeOp extends OpBase {
  kind: "create_node";
  pageId: string;
  parentId: string; // page id if top-level
  indexInParent: number;
  node: Layer;
}

export interface DeleteNodesOp extends OpBase {
  kind: "delete_nodes";
  pageId: string;
  ids: string[];
  // Snapshot for inverse — populated on apply.
  snapshot?: Array<{ node: Layer; parentId: string; indexInParent: number }>;
  // Per-page snapshot of prototype flows / connections that referenced any of
  // the deleted ids (so they can be restored on undo). Populated on apply.
  // `unknown[]` to keep this module flat; ops.ts narrows the types.
  prototypeSnapshot?: Array<{
    pageId: string;
    flowsBefore?: unknown[];
    connectionsBefore?: unknown[];
  }>;
}

export interface SetPropertyOp extends OpBase {
  kind: "set_property";
  pageId: string;
  ids: string[];
  path: string; // JSON-Pointer-ish, e.g. "name", "fills", "fills/0/color", "cornerRadius"
  before: Record<string, unknown>; // per-id snapshot
  after: Record<string, unknown>; // per-id new value
}

export interface SetTransformOp extends OpBase {
  kind: "set_transform";
  pageId: string;
  ids: string[];
  before: TransformMap;
  after: TransformMap;
}

export interface ReparentOp extends OpBase {
  kind: "reparent";
  pageId: string;
  moves: Array<{ id: string; fromParentId: string; fromIndex: number; toParentId: string; toIndex: number }>;
}

export interface ReorderZOp extends OpBase {
  kind: "reorder_z";
  pageId: string;
  parentId: string;
  ids: string[];
  toIndex: number;
  before: number[]; // original indices
}

export interface SetSelectionOp extends OpBase {
  kind: "set_selection";
  pageId: string;
  before: string[];
  after: string[];
}

export interface SetFocusContextOp extends OpBase {
  kind: "set_focus_context";
  pageId: string;
  before: string | null;
  after: string | null;
}

export interface SetViewportOp extends OpBase {
  kind: "set_viewport";
  pageId: string;
  before: Viewport;
  after: Viewport;
}

export interface SetToolOp extends OpBase {
  kind: "set_tool";
  before: ToolId;
  after: ToolId;
}

export interface SetEditModeOp extends OpBase {
  kind: "set_edit_mode";
  before: EditMode;
  after: EditMode;
}

export interface CreatePageOp extends OpBase {
  kind: "create_page";
  pageIndex: number;
  page: Page;
}

export interface DeletePageOp extends OpBase {
  kind: "delete_page";
  pageId: string;
  before: { pageIndex: number; page: Page; wasActive: boolean; fallbackPageId: string | null };
}

export interface SwitchPageOp extends OpBase {
  kind: "switch_page";
  before: { pageId: string };
  after: { pageId: string };
}

export interface MutateTextRunsOp extends OpBase {
  kind: "mutate_text_runs";
  pageId: string;
  layerId: string;
  before: { content: string; runs: unknown[]; fontFamily: string; fontWeight: number; fontSize: number };
  after: { content: string; runs: unknown[]; fontFamily: string; fontWeight: number; fontSize: number };
}

export interface MutateVectorNetworkOp extends OpBase {
  kind: "mutate_vector_network";
  pageId: string;
  layerId: string;
  before: unknown;
  after: unknown;
}

export interface ClipboardPayload {
  kind: "app_layers" | "system_image" | "system_text";
  layers?: Layer[];
  originPageId?: string;
  originBbox?: { x: number; y: number; w: number; h: number };
  text?: string;
  imageBlob?: Blob;
}

export interface SetClipboardOp extends OpBase {
  kind: "set_clipboard";
  before: ClipboardPayload | null;
  after: ClipboardPayload | null;
}

export interface SetDocumentNameOp extends OpBase {
  kind: "set_document_name";
  before: string;
  after: string;
}

// Slice 0 needs only a subset — full union below for forward-compat.
export type Op =
  | CreateNodeOp
  | DeleteNodesOp
  | SetPropertyOp
  | SetTransformOp
  | ReparentOp
  | ReorderZOp
  | SetSelectionOp
  | SetFocusContextOp
  | SetViewportOp
  | SetToolOp
  | SetEditModeOp
  | CreatePageOp
  | DeletePageOp
  | SwitchPageOp
  | SetClipboardOp
  | SetDocumentNameOp
  | MutateTextRunsOp
  | MutateVectorNetworkOp;

export const UNDOABLE_KINDS = new Set<Op["kind"]>([
  "create_node",
  "delete_nodes",
  "set_property",
  "set_transform",
  "reparent",
  "reorder_z",
  "create_page",
  "delete_page",
  "mutate_text_runs",
  "mutate_vector_network",
  "set_document_name",
]);

// Color helper used at op construction sites
export const TRANSPARENT: Color = { r: 0, g: 0, b: 0, a: 0 };
