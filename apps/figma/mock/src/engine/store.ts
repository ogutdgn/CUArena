// Zustand + Immer store with the 6 state buckets + logger reference.
// Source: .analysis/engine-report.md §3.

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { enableMapSet } from "immer";
import type { DocumentNode, Layer, Page, Color } from "@/types/scene";
import type { ToolId, EditMode, Viewport, ClipboardPayload, Op } from "@/types/ops";
import { uid } from "@/util/id";
import { resolveSessionInfo } from "@/util/session";

enableMapSet();

interface UndoEntry {
  id: string;
  timestamp: number;
  // Page the selection / focus snapshots belong to. Pinned at capture time so
  // undo/redo restore selection on the right page even if the active page
  // changed afterward (e.g. delete_page / switch_page in the same entry).
  pageId: string;
  ops: Op[];
  selectionBefore: string[];
  selectionAfter: string[];
  focusContextBefore: string | null;
  focusContextAfter: string | null;
}

export interface DragPreview {
  kind:
    | null
    | "marquee"
    | "layer_drag"
    | "resize_drag"
    | "rotate_drag"
    | "create_shape"
    | "pan";
  data: unknown;
}

export interface ToastEntry {
  id: string;
  text: string;
  expiresAt: number;
}

export interface AppState {
  document: DocumentNode;
  // Flat lookup. Plain object so Immer handles structural sharing.
  nodesById: Record<string, Layer | Page>;
  activePageId: string;

  viewportByPage: Record<string, Viewport>;
  selectionByPage: Record<string, string[]>;

  activeTool: ToolId;
  productMode: "design";
  editMode: EditMode;
  focusContextByPage: Record<string, string | null>;

  clipboard: ClipboardPayload | null;

  hoveredNodeId: string | null;
  cursorWorld: { x: number; y: number } | null;
  dragPreview: DragPreview;
  snapLines: Array<
    | { axis: "x"; x: number; yMin: number; yMax: number }
    | { axis: "y"; y: number; xMin: number; xMax: number }
  >;
  snapMeasures: Array<{
    axis: "x" | "y";
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    value: number;
  }>;
  contextMenu: { x: number; y: number } | null;
  renamingLayerId: string | null;
  penPreview: {
    layerId: string;
    cursor: { x: number; y: number } | null;
    handleDrag: { vertexIndex: number; outDx: number; outDy: number } | null;
    appendPreviewFromTail: boolean;
  } | null;
  pencilPreview: { points: Array<{ x: number; y: number }> } | null;
  insertionCursor: { x: number; y: number } | null;
  vectorEditSelected: number | null;
  rotateReadout: { x: number; y: number; deg: number } | null;
  spaceDown: boolean;
  openDropdown: string | null;
  openModal: string | null;
  toasts: ToastEntry[];
  uiHidden: boolean;

  activeRightTab: "design" | "prototype";
  aspectRatioLocked: boolean;
  prototypePreview: { pos: { x: number; y: number }; flowIndex: number } | null;

  undoStack: UndoEntry[];
  redoStack: UndoEntry[];

  sessionId: string;
}

export interface PersistedStoreSnapshot {
  document: unknown;
  activePageId?: string;
  sessionId?: string;
}

function createDefaultPage(): Page {
  const id = uid("page");
  const bg: Color = { r: 0.118, g: 0.118, b: 0.118, a: 1 };
  return {
    id,
    type: "page",
    name: "Page 1",
    backgroundColor: bg,
    backgroundHidden: false,
    children: [],
    prototypeSettings: { device: null, backgroundColor: { r: 0.055, g: 0.051, b: 0.051, a: 1 } },
  };
}

function buildNodeIndex(doc: DocumentNode): Record<string, Layer | Page> {
  const map: Record<string, Layer | Page> = {};
  for (const page of doc.pages) {
    map[page.id] = page;
    walk(page.children, map);
  }
  return map;
}

function hasStringId(x: unknown): x is { id: string } {
  return typeof x === "object" && x !== null && typeof (x as { id?: unknown }).id === "string";
}

function isDocumentLike(x: unknown): x is DocumentNode {
  if (typeof x !== "object" || x === null) return false;
  const doc = x as { id?: unknown; pages?: unknown };
  if (typeof doc.id !== "string") return false;
  if (!Array.isArray(doc.pages) || doc.pages.length === 0) return false;
  return doc.pages.every((p) => hasStringId(p));
}

function resolveActivePageId(doc: DocumentNode, requested?: string): string {
  if (requested && doc.pages.some((p) => p.id === requested)) return requested;
  return doc.pages[0].id;
}

function buildPageBuckets(doc: DocumentNode): {
  viewportByPage: Record<string, Viewport>;
  selectionByPage: Record<string, string[]>;
  focusContextByPage: Record<string, string | null>;
} {
  const viewportByPage: Record<string, Viewport> = {};
  const selectionByPage: Record<string, string[]> = {};
  const focusContextByPage: Record<string, string | null> = {};
  for (const page of doc.pages) {
    viewportByPage[page.id] = { x: 0, y: 0, zoom: 1 };
    selectionByPage[page.id] = [];
    focusContextByPage[page.id] = null;
  }
  return { viewportByPage, selectionByPage, focusContextByPage };
}

function walk(layers: Layer[], map: Record<string, Layer | Page>) {
  for (const l of layers) {
    map[l.id] = l;
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      walk(l.children, map);
    }
  }
}

const initialPage = createDefaultPage();
const initialDoc: DocumentNode = {
  id: uid("doc"),
  schemaVersion: 1,
  name: "Untitled",
  pages: [initialPage],
};
const initialSessionInfo = resolveSessionInfo();

const initialState: AppState = {
  document: initialDoc,
  nodesById: buildNodeIndex(initialDoc),
  activePageId: initialPage.id,

  viewportByPage: { [initialPage.id]: { x: 0, y: 0, zoom: 1 } },
  selectionByPage: { [initialPage.id]: [] as string[] },

  activeTool: "move",
  productMode: "design",
  editMode: { kind: "none" },
  focusContextByPage: { [initialPage.id]: null },

  clipboard: null,

  hoveredNodeId: null,
  cursorWorld: null,
  dragPreview: { kind: null, data: null },
  snapLines: [],
  snapMeasures: [],
  contextMenu: null,
  renamingLayerId: null,
  penPreview: null,
  pencilPreview: null,
  insertionCursor: null,
  vectorEditSelected: null,
  rotateReadout: null,
  spaceDown: false,
  openDropdown: null,
  openModal: null,
  toasts: [],
  uiHidden: false,

  activeRightTab: "design",
  aspectRatioLocked: false,
  prototypePreview: null,

  undoStack: [],
  redoStack: [],

  sessionId: initialSessionInfo.sessionId,
};

export const useStore = create<AppState>()(immer(() => initialState));

export function hydrateStoreFromSnapshot(snapshot: PersistedStoreSnapshot): boolean {
  if (!isDocumentLike(snapshot.document)) return false;
  const doc = snapshot.document;
  const activePageId = resolveActivePageId(doc, snapshot.activePageId);
  const pageBuckets = buildPageBuckets(doc);
  useStore.setState((s) => {
    s.document = doc;
    s.nodesById = buildNodeIndex(doc);
    s.activePageId = activePageId;
    s.viewportByPage = pageBuckets.viewportByPage;
    s.selectionByPage = pageBuckets.selectionByPage;
    s.focusContextByPage = pageBuckets.focusContextByPage;
    s.hoveredNodeId = null;
    s.cursorWorld = null;
    s.dragPreview = { kind: null, data: null };
    s.snapLines = [];
    s.snapMeasures = [];
    s.contextMenu = null;
    s.renamingLayerId = null;
    s.penPreview = null;
    s.pencilPreview = null;
    s.insertionCursor = null;
    s.vectorEditSelected = null;
    s.rotateReadout = null;
    s.undoStack = [];
    s.redoStack = [];
    if (typeof snapshot.sessionId === "string" && snapshot.sessionId.length > 0) {
      s.sessionId = snapshot.sessionId;
    }
  });
  return true;
}

// ---- Selectors / derived ----

export const selectActivePage = (s: AppState): Page | undefined =>
  s.document.pages.find((p) => p.id === s.activePageId);

export const selectActiveSelection = (s: AppState): string[] =>
  s.selectionByPage[s.activePageId] ?? [];

export const selectActiveViewport = (s: AppState): Viewport =>
  s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };

export const selectActiveFocusContext = (s: AppState): string | null =>
  s.focusContextByPage[s.activePageId] ?? null;

export function getLayerById(state: AppState, id: string): Layer | undefined {
  const n = state.nodesById[id];
  if (!n) return undefined;
  if ((n as Page).type === "page") return undefined;
  return n as Layer;
}

export type { UndoEntry };
