// Group/ungroup/enter-group/exit-group/reorder-z commands.

import { useStore } from "./store";
import { dispatch, makeOpId, openTransaction, commitTransaction } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "./selectors";
import { setSelection } from "./commands";
import { uid } from "@/util/id";
import type { Layer, Group, Page } from "@/types/scene";

function findParentChildren(s: ReturnType<typeof useStore.getState>, parentId: string): Layer[] | null {
  const parent = s.nodesById[parentId];
  if (!parent) return null;
  if ((parent as Page).type === "page") return (parent as Page).children;
  if ("children" in (parent as object)) {
    const arr = (parent as Layer & { children?: Layer[] }).children;
    return arr ?? null;
  }
  return null;
}

export function groupSelection(trigger: "shortcut" | "context_menu" | "main_menu"): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length < 1) return;

  // Determine parent: the common parent of selected layers (slice 3 simple: use first layer's parent).
  const parentId = layers[0].parentId;
  if (!layers.every((l) => l.parentId === parentId)) {
    // Mixed-parent grouping is intentionally blocked until a proper common-ancestor
    // reparent path exists.
    return;
  }
  const arr = findParentChildren(s, parentId);
  if (!arr) return;

  // Compute group bbox
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const l of layers) {
    if (l.x < minX) minX = l.x;
    if (l.y < minY) minY = l.y;
    if (l.x + l.w > maxX) maxX = l.x + l.w;
    if (l.y + l.h > maxY) maxY = l.y + l.h;
  }
  const group: Group = {
    id: uid("group"),
    type: "group",
    name: "Group",
    parentId,
    x: minX,
    y: minY,
    w: Math.max(1, maxX - minX),
    h: Math.max(1, maxY - minY),
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
    effects: [],
    children: [],
  };

  // Insert at the highest index among the selected layers in their parent
  const indices = layers
    .map((l) => arr.findIndex((c) => c.id === l.id))
    .filter((i) => i >= 0);
  const insertAt = Math.max(...indices) + 1;

  const txId = openTransaction();
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "create_node",
      pageId: s.activePageId,
      parentId,
      indexInParent: insertAt,
      node: group,
    },
    { transactionId: txId },
  );
  // Reparent each selected layer into the group, preserving order.
  const moves = layers.map((l, i) => ({
    id: l.id,
    fromParentId: l.parentId,
    fromIndex: arr.findIndex((c) => c.id === l.id),
    toParentId: group.id,
    toIndex: i,
  }));
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "reparent",
      pageId: s.activePageId,
      moves,
    },
    { transactionId: txId },
  );
  commitTransaction(txId);

  setSelection([group.id], "implicit_after_create");
  emitSemantic({
    name: "group_selection",
    layerIds: layers.map((l) => l.id),
    groupId: group.id,
    trigger,
  });
}

export function ungroupSelection(trigger: "shortcut" | "context_menu" | "main_menu"): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s).filter((l) => l.type === "group");
  if (layers.length === 0) return;

  const txId = openTransaction();
  const movedChildIds: string[] = [];

  for (const group of layers) {
    if (group.type !== "group") continue;
    const parentId = group.parentId;
    const parentChildren = findParentChildren(s, parentId);
    if (!parentChildren) continue;
    const groupIdx = parentChildren.findIndex((c) => c.id === group.id);

    const childIds = group.children.map((c) => c.id);
    const moves = childIds.map((id, i) => ({
      id,
      fromParentId: group.id,
      fromIndex: i,
      toParentId: parentId,
      toIndex: groupIdx + i,
    }));
    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "reparent",
        pageId: s.activePageId,
        moves,
      },
      { transactionId: txId },
    );
    movedChildIds.push(...childIds);

    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "delete_nodes",
        pageId: s.activePageId,
        ids: [group.id],
      },
      { transactionId: txId },
    );
  }
  commitTransaction(txId);

  setSelection(movedChildIds, "implicit_after_ungroup");
  emitSemantic({
    name: "ungroup",
    layerIds: layers.map((l) => l.id),
    trigger,
  });
}

export function enterGroup(): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  const target = layers.find((l) => l.type === "group" || l.type === "frame" || l.type === "section");
  if (!target) return;
  const before = s.focusContextByPage[s.activePageId] ?? null;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_focus_context",
    pageId: s.activePageId,
    before,
    after: target.id,
  });
  emitSemantic({ name: "enter_group", groupId: target.id });
}

export function exitGroup(): void {
  const s = useStore.getState();
  const cur = s.focusContextByPage[s.activePageId] ?? null;
  if (cur == null) return;
  // Walk up to parent
  const ctx = s.nodesById[cur] as Layer | undefined;
  const parentId = ctx?.parentId ?? null;
  const newCtx = parentId && parentId !== s.activePageId ? parentId : null;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_focus_context",
    pageId: s.activePageId,
    before: cur,
    after: newCtx,
  });
  emitSemantic({ name: "exit_group", groupId: cur });
}

export function reorderZ(direction: "front" | "back" | "forward" | "backward"): void {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const layerIds = layers.map((l) => l.id);
  const beforeById = new Map<string, { parentId: string; index: number }>();
  for (const l of layers) {
    const arr = findParentChildren(s, l.parentId);
    beforeById.set(l.id, { parentId: l.parentId, index: arr ? arr.findIndex((c) => c.id === l.id) : -1 });
  }

  // Group by parent.
  const byParent = new Map<string, Layer[]>();
  for (const l of layers) {
    if (!byParent.has(l.parentId)) byParent.set(l.parentId, []);
    byParent.get(l.parentId)!.push(l);
  }

  const txId = openTransaction();
  for (const [parentId, items] of byParent) {
    const arr = findParentChildren(s, parentId);
    if (!arr) continue;
    const sortedItems = [...items].sort((a, b) => arr.indexOf(a) - arr.indexOf(b));
    const before = sortedItems.map((it) => arr.indexOf(it));
    let toIndex = 0;
    if (direction === "front") toIndex = arr.length;
    else if (direction === "back") toIndex = 0;
    else if (direction === "forward") toIndex = Math.min(arr.length, before[before.length - 1] + 2);
    else if (direction === "backward") toIndex = Math.max(0, before[0] - 1);

    dispatch(
      {
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "reorder_z",
        pageId: s.activePageId,
        parentId,
        ids: sortedItems.map((it) => it.id),
        toIndex,
        before,
      },
      { transactionId: txId },
    );
  }
  commitTransaction(txId);
  const sAfter = useStore.getState();
  const afterById = new Map<string, { parentId: string; index: number }>();
  for (const id of layerIds) {
    const node = sAfter.nodesById[id] as Layer | undefined;
    if (!node || (node as unknown as Page).type === "page") continue;
    const arr = findParentChildren(sAfter, node.parentId);
    afterById.set(id, { parentId: node.parentId, index: arr ? arr.findIndex((c) => c.id === id) : -1 });
  }

  emitSemantic({
    name: "reorder_layer",
    layerIds,
    before: layerIds.map((id) => beforeById.get(id) ?? { parentId: "", index: -1 }),
    after: layerIds.map((id) => afterById.get(id) ?? { parentId: "", index: -1 }),
    trigger:
      direction === "front"
        ? "shortcut_cmd_alt_close_bracket"
        : direction === "back"
        ? "shortcut_cmd_alt_open_bracket"
        : direction === "forward"
        ? "shortcut_cmd_close_bracket"
        : "shortcut_cmd_open_bracket",
  });
}

export function reorderLayerInPanel(
  draggedId: string,
  targetId: string,
  dropAboveTarget: boolean,
): void {
  if (draggedId === targetId) return;
  const s = useStore.getState();
  const dragged = s.nodesById[draggedId] as Layer | undefined;
  const target = s.nodesById[targetId] as Layer | undefined;
  if (!dragged || !target) return;
  if ((dragged as unknown as Page).type === "page" || (target as unknown as Page).type === "page") return;
  if (dragged.parentId !== target.parentId) return;

  const parentId = dragged.parentId;
  const parent = s.nodesById[parentId];
  const arr =
    (parent as Page | undefined)?.type === "page"
      ? (parent as Page).children
      : (parent as (Layer & { children?: Layer[] }) | undefined)?.children;
  if (!arr) return;

  const beforeIndex = arr.findIndex((c) => c.id === draggedId);
  const targetIndex = arr.findIndex((c) => c.id === targetId);
  if (beforeIndex < 0 || targetIndex < 0) return;

  const without = arr.filter((c) => c.id !== draggedId);
  const targetPos = without.findIndex((c) => c.id === targetId);
  if (targetPos < 0) return;
  const toIndex = dropAboveTarget ? targetPos + 1 : targetPos;

  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "reorder_z",
    pageId: s.activePageId,
    parentId,
    ids: [draggedId],
    toIndex,
    before: [beforeIndex],
  });

  const afterState = useStore.getState();
  const p2 = afterState.nodesById[parentId];
  const arr2 =
    (p2 as Page | undefined)?.type === "page"
      ? (p2 as Page).children
      : (p2 as (Layer & { children?: Layer[] }) | undefined)?.children;
  const afterIndex = arr2 ? arr2.findIndex((c) => c.id === draggedId) : toIndex;

  emitSemantic({
    name: "reorder_layer",
    layerIds: [draggedId],
    before: [{ parentId, index: beforeIndex }],
    after: [{ parentId, index: afterIndex }],
    trigger: "panel_drag",
  });
}

export function renameLayer(layerId: string, after: string, trigger: "inline_panel" | "rename_modal" | "context_menu"): void {
  const s = useStore.getState();
  const node = s.nodesById[layerId] as Layer | undefined;
  if (!node) return;
  const before = node.name;
  if (before === after) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: [layerId],
    path: "name",
    before: { [layerId]: before },
    after: { [layerId]: after },
  });
  emitSemantic({ name: "rename_layer", layerId, before, after, trigger });
}
