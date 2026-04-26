// High-level commands. Compose ops + emit semantic events.
// These are called from keymap, context menus, panel buttons.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { pushToast } from "@/ui/overlays/Toasts";
import type { Layer } from "@/types/scene";
import type { ClipboardPayload } from "@/types/ops";
import { uid } from "@/util/id";
import { isContainer } from "@/types/scene";
import { getActivePage, getSelectedLayers, selectionBbox } from "./selectors";

function parentChildren(state: ReturnType<typeof useStore.getState>, parentId: string): Layer[] | null {
  const page = state.document.pages.find((p) => p.id === parentId);
  if (page) return page.children;
  const node = state.nodesById[parentId];
  if (!node) return null;
  return (node as (Layer & { children?: Layer[] })).children ?? null;
}

function deepCloneLayer(layer: Layer): Layer {
  // Structured-clone for our plain-data layers (no Blobs in slice 0).
  return JSON.parse(JSON.stringify(layer)) as Layer;
}

function withFreshIds(layer: Layer, parentId: string): Layer {
  const cloned = deepCloneLayer(layer);
  cloned.id = uid(cloned.type);
  cloned.parentId = parentId;
  if (isContainer(cloned)) {
    cloned.children = cloned.children.map((c) => withFreshIds(c, cloned.id));
  }
  return cloned;
}

export function copySelection(trigger: "shortcut" | "context_menu" | "main_menu"): void {
  const state = useStore.getState();
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return;
  const bbox = selectionBbox(state);
  const payload: ClipboardPayload = {
    kind: "app_layers",
    layers: layers.map(deepCloneLayer),
    originPageId: state.activePageId,
    originBbox: bbox ?? undefined,
  };
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_clipboard",
    before: state.clipboard,
    after: payload,
  });
  emitSemantic({ name: "copy", layerIds: layers.map((l) => l.id), trigger });
  pushToast(layers.length === 1 ? "1 layer copied" : `${layers.length} layers copied`);
}

export function cutSelection(trigger: "shortcut" | "context_menu" | "main_menu"): void {
  const state = useStore.getState();
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return;

  // Snapshot for clipboard before deletion (delete_nodes mutates the tree).
  const bbox = selectionBbox(state);
  const payload: ClipboardPayload = {
    kind: "app_layers",
    layers: layers.map(deepCloneLayer),
    originPageId: state.activePageId,
    originBbox: bbox ?? undefined,
  };
  const ids = layers.map((l) => l.id);

  // Both clipboard write and delete are undoable as one entry — open a transaction.
  // (set_clipboard is non-undoable; delete_nodes is undoable. The transaction wraps
  // both so undo restores the layers AND keeps the clipboard.)
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_clipboard",
    before: state.clipboard,
    after: payload,
  });
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "delete_nodes",
    pageId: state.activePageId,
    ids,
  });
  emitSemantic({ name: "cut", layerIds: ids, trigger });
  pushToast(ids.length === 1 ? "Cut 1 layer" : `Cut ${ids.length} layers`);
}

export function pasteFromClipboard(
  trigger: "shortcut" | "context_menu" | "main_menu",
): void {
  const state = useStore.getState();
  const cb = state.clipboard;
  const page = getActivePage(state);
  if (!cb || !page) return;
  if (cb.kind !== "app_layers" || !cb.layers || cb.layers.length === 0) return;

  // Slice 0 placement: viewport center (deferred), use origin offset to keep simple.
  const targetParentId = state.focusContextByPage[state.activePageId] ?? page.id;
  const offset = { dx: 10, dy: 10 };
  const newLayers: Layer[] = cb.layers.map((source) => {
    const clone = withFreshIds(source, targetParentId);
    clone.x += offset.dx;
    clone.y += offset.dy;
    return clone;
  });

  // Insert each at end of parent's children
  const parentChildrenArr = parentChildren(state, targetParentId) ?? [];
  let insertIdx = parentChildrenArr.length;

  const newIds: string[] = [];
  for (const layer of newLayers) {
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "create_node",
      pageId: state.activePageId,
      parentId: targetParentId,
      indexInParent: insertIdx,
      node: layer,
    });
    insertIdx += 1;
    newIds.push(layer.id);
  }

  // Selection follows pasted layers.
  setSelectionImplicit(newIds);
  emitSemantic({
    name: "paste",
    newLayerIds: newIds,
    placement: "viewport_center",
    trigger,
  });
  emitSemantic({
    name: "selection_change",
    before: state.selectionByPage[state.activePageId] ?? [],
    after: newIds,
    triggerMethod: "implicit_after_paste",
    cause: null,
  });
  pushToast(newIds.length === 1 ? "Pasted 1 layer" : `Pasted ${newIds.length} layers`);
}

export function duplicateSelection(): void {
  const state = useStore.getState();
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return;
  const offset = { dx: 10, dy: 10 };
  const newIds: string[] = [];
  for (const source of layers) {
    const clone = withFreshIds(source, source.parentId);
    clone.x += offset.dx;
    clone.y += offset.dy;
    // Insert just after the source in its parent's children
    const arr = parentChildren(state, source.parentId);
    if (!arr) continue;
    const idx = arr.findIndex((c) => c.id === source.id);
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "create_node",
      pageId: state.activePageId,
      parentId: source.parentId,
      indexInParent: idx + 1,
      node: clone,
    });
    newIds.push(clone.id);
  }
  setSelectionImplicit(newIds);
  emitSemantic({
    name: "duplicate",
    sourceLayerIds: layers.map((l) => l.id),
    newLayerIds: newIds,
    offset,
    trigger: "shortcut_cmd_d",
  });
  emitSemantic({
    name: "selection_change",
    before: state.selectionByPage[state.activePageId] ?? [],
    after: newIds,
    triggerMethod: "implicit_after_duplicate",
    cause: null,
  });
}

export function deleteSelection(
  trigger:
    | "keyboard_canvas"
    | "keyboard_panel"
    | "context_menu_canvas"
    | "context_menu_panel"
    | "main_menu",
): void {
  const state = useStore.getState();
  const ids = state.selectionByPage[state.activePageId] ?? [];
  if (ids.length === 0) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "delete_nodes",
    pageId: state.activePageId,
    ids: [...ids],
  });
  setSelectionImplicit([]);
  emitSemantic({ name: "delete", layerIds: [...ids], trigger });
  pushToast(ids.length === 1 ? "Deleted 1 layer" : `Deleted ${ids.length} layers`);
  emitSemantic({
    name: "selection_change",
    before: ids,
    after: [],
    triggerMethod: "implicit_after_delete",
    cause: null,
  });
}

export function selectAll(): void {
  const state = useStore.getState();
  const page = getActivePage(state);
  if (!page) return;
  const ids: string[] = [];
  function walk(layers: Layer[]) {
    for (const l of layers) {
      if (!l.locked) ids.push(l.id);
    }
  }
  walk(page.children);
  const before = state.selectionByPage[state.activePageId] ?? [];
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_selection",
    pageId: state.activePageId,
    before,
    after: ids,
  });
  emitSemantic({ name: "select_all", scope: "page", layerIds: ids });
  emitSemantic({
    name: "selection_change",
    before,
    after: ids,
    triggerMethod: "select_all",
    cause: null,
  });
}

export function deselectAll(trigger: "escape" | "click_empty_canvas" | "shortcut"): void {
  const state = useStore.getState();
  const before = state.selectionByPage[state.activePageId] ?? [];
  if (before.length === 0) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_selection",
    pageId: state.activePageId,
    before,
    after: [],
  });
  emitSemantic({ name: "deselect", trigger });
  emitSemantic({
    name: "selection_change",
    before,
    after: [],
    triggerMethod: "deselect",
    cause: null,
  });
}

export function setSelection(
  after: string[],
  trigger:
    | "click_select"
    | "shift_click_add"
    | "shift_click_remove"
    | "drag_box_select"
    | "panel_row_click"
    | "implicit_after_create"
    | "implicit_after_paste"
    | "implicit_after_duplicate"
    | "implicit_after_delete"
    | "implicit_after_undo"
    | "implicit_after_redo"
    | "implicit_after_group"
    | "implicit_after_ungroup",
): void {
  const state = useStore.getState();
  const before = state.selectionByPage[state.activePageId] ?? [];
  if (sameIds(before, after)) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_selection",
    pageId: state.activePageId,
    before,
    after,
  });
  emitSemantic({
    name: "selection_change",
    before,
    after,
    triggerMethod: trigger,
    cause: null,
  });
}

function setSelectionImplicit(after: string[]): void {
  const state = useStore.getState();
  const before = state.selectionByPage[state.activePageId] ?? [];
  if (sameIds(before, after)) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_selection",
    pageId: state.activePageId,
    before,
    after,
  });
}

function sameIds(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}
