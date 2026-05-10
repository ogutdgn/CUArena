import type { AppState } from "./store";
import type { Layer, Page } from "@/types/scene";
import { isContainer } from "@/types/scene";
import { localToWorld, worldToParentLocal } from "./coordinates";

export type PastePlacementKind = "viewport_center" | "into_frame" | "at_cursor" | "from_origin";

export interface PastePlacement {
  parentId: string;
  x: number;
  y: number;
  placement: PastePlacementKind;
}

function layerTreeContainsParent(layers: Layer[], parentId: string): boolean {
  for (const layer of layers) {
    if (layer.id === parentId) return isContainer(layer);
    if (isContainer(layer) && layerTreeContainsParent(layer.children, parentId)) return true;
  }
  return false;
}

function parentExistsOnActivePage(state: AppState, parentId: string): boolean {
  const page = state.document.pages.find((p) => p.id === state.activePageId);
  if (!page) return false;
  if (page.id === parentId) return true;
  return layerTreeContainsParent(page.children, parentId);
}

function parentExistsInDocument(state: AppState, parentId: string): boolean {
  const page = state.document.pages.find((p) => p.id === parentId);
  if (page) return true;
  const node = state.nodesById[parentId];
  return !!node && (node as Page).type !== "page" && isContainer(node as Layer);
}

function isContainerParent(state: AppState, parentId: string): boolean {
  const node = state.nodesById[parentId];
  return !!node && (node as Page).type !== "page" && isContainer(node as Layer);
}

export function placementForPastedLayer(
  state: AppState,
  source: Layer,
  offset: { dx: number; dy: number },
): PastePlacement {
  const pageId = state.activePageId;
  const page = state.document.pages.find((p) => p.id === pageId);
  const focusId = state.focusContextByPage[pageId] ?? null;
  const targetParentId =
    parentExistsOnActivePage(state, source.parentId)
      ? source.parentId
      : focusId && parentExistsOnActivePage(state, focusId)
      ? focusId
      : page?.id ?? pageId;

  const desiredLocal = { x: source.x + offset.dx, y: source.y + offset.dy };
  const nextLocal =
    source.parentId === targetParentId || !parentExistsInDocument(state, source.parentId)
      ? desiredLocal
      : worldToParentLocal(state, targetParentId, localToWorld(state, source.parentId, desiredLocal));

  return {
    parentId: targetParentId,
    x: nextLocal.x,
    y: nextLocal.y,
    placement: isContainerParent(state, targetParentId) ? "into_frame" : "from_origin",
  };
}
