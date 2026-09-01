// Page lifecycle commands.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { uid } from "@/util/id";
import type { Page } from "@/types/scene";

export function createPage(name?: string, trigger: "panel_button" | "context_menu" = "panel_button"): void {
  const s = useStore.getState();
  const ordinal = s.document.pages.length + 1;
  const page: Page = {
    id: uid("page"),
    type: "page",
    name: name ?? `Page ${ordinal}`,
    backgroundColor: { r: 0.118, g: 0.118, b: 0.118, a: 1 },
    backgroundHidden: false,
    children: [],
  };
  const pageIndex = s.document.pages.length;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "create_page",
    pageIndex,
    page,
  });
  emitSemantic({ name: "create_page", newPageId: page.id, pageIndex, trigger });
  // Switch to the new page (non-undoable)
  switchPage(page.id, "implicit_after_create");
}

export function switchPage(pageId: string, trigger: "panel_click" | "shortcut" | "implicit_after_create"): void {
  const s = useStore.getState();
  if (s.activePageId === pageId) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "switch_page",
    before: { pageId: s.activePageId },
    after: { pageId },
  });
  emitSemantic({ name: "switch_page", beforePageId: s.activePageId, afterPageId: pageId, trigger });
}

export function renamePage(pageId: string, after: string): void {
  const s = useStore.getState();
  const page = s.document.pages.find((p) => p.id === pageId);
  if (!page) return;
  const before = page.name;
  if (before === after) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_property",
    pageId: s.activePageId,
    ids: [pageId],
    path: "name",
    before: { [pageId]: before },
    after: { [pageId]: after },
  });
  emitSemantic({ name: "rename_page", targetPageId: pageId, before, after });
}

export function deletePage(pageId: string, trigger: "context_menu" | "shortcut" = "context_menu"): void {
  const s = useStore.getState();
  if (s.document.pages.length <= 1) return; // last page protected
  const idx = s.document.pages.findIndex((p) => p.id === pageId);
  if (idx === -1) return;
  const page = s.document.pages[idx];
  const wasActive = s.activePageId === pageId;
  const fallback = s.document.pages[Math.max(0, idx - 1)] ?? s.document.pages[1];
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "delete_page",
    pageId,
    before: { pageIndex: idx, page, wasActive, fallbackPageId: fallback?.id ?? null },
  });
  emitSemantic({ name: "delete_page", targetPageId: pageId, pageIndex: idx, trigger });
}
