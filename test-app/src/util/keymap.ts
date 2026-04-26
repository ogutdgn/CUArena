// Keyboard shortcut router. Translates raw keydown into commands.
// Source: .analysis/engine-report.md §7 (per-tool shortcuts) + ui-report §2 toolbar.

import { useStore } from "@/engine/store";
import { dispatch, undo, redo, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { copySelection, cutSelection, pasteFromClipboard, duplicateSelection, deleteSelection, selectAll, deselectAll } from "@/engine/commands";
import { groupSelection, ungroupSelection, enterGroup, exitGroup, reorderZ } from "@/engine/hierarchyCommands";
import { flipSelection, zoomToFit, zoomTo100, zoomToSelection, zoomBy } from "@/engine/transformCommands";
import { openImageFilePicker } from "@/engine/imageCommands";
import { abortPenIfActive } from "@/tools/pen";
import { deleteSelectedVectorPoint } from "@/ui/overlays/VectorEditOverlay";
import type { ToolId } from "@/types/ops";

function setTool(after: ToolId, trigger: "shortcut" | "toolbar_click" = "shortcut") {
  const before = useStore.getState().activeTool;
  if (before === after) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_tool",
    before,
    after,
  });
  emitSemantic({ name: "tool_change", before, after, trigger });
}

function isInTextField(e: KeyboardEvent): boolean {
  const t = e.target as HTMLElement | null;
  if (!t) return false;
  const tag = t.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (t.isContentEditable) return true;
  return false;
}

function onKeyDown(e: KeyboardEvent): void {
  if (isInTextField(e)) return;

  // Space-temp-hand: while held, the active tool gives way to pan.
  if (e.key === " " || e.code === "Space") {
    if (!useStore.getState().spaceDown) {
      useStore.setState((s) => { s.spaceDown = true; });
    }
    e.preventDefault();
    return;
  }

  const meta = e.metaKey || e.ctrlKey;
  const key = e.key.toLowerCase();

  // Tool shortcuts (no modifiers)
  if (!meta && !e.altKey) {
    if (key === "v") {
      setTool("move");
      return;
    }
    if (key === "escape") {
      // Esc should finish active pen creation without switching tools.
      if (abortPenIfActive()) {
        e.preventDefault();
        return;
      }
      deselectAll("escape");
      setTool("move");
      return;
    }
    if (key === "enter" && abortPenIfActive()) {
      e.preventDefault();
      return;
    }
    if (key === "r") {
      setTool("rectangle");
      return;
    }
    if (key === "o") {
      setTool("ellipse");
      return;
    }
    if (key === "l" && !e.shiftKey) {
      setTool("line");
      return;
    }
    if (key === "l" && e.shiftKey) {
      setTool("arrow");
      return;
    }
    if (key === "h") {
      setTool("hand");
      return;
    }
    if (key === "f") {
      setTool("frame");
      return;
    }
    if (key === "t") {
      setTool("text");
      return;
    }
    if (key === "p") {
      setTool(e.shiftKey ? "pencil" : "pen");
      return;
    }
    if (key === "k") {
      setTool("scale");
      return;
    }
    if (key === "delete" || key === "backspace") {
      e.preventDefault();
      // In vector edit mode with a selected anchor, delete that point instead.
      if (deleteSelectedVectorPoint()) return;
      deleteSelection("keyboard_canvas");
      return;
    }
    if (key === "enter") {
      e.preventDefault();
      enterGroup();
      return;
    }
    if (key === "`") {
      useStore.setState({ showLogger: !useStore.getState().showLogger });
      return;
    }
    if (e.shiftKey && key === "s") {
      e.preventDefault();
      setTool("section");
      return;
    }
  }

  if (!meta && !e.altKey && key === "escape") {
    // If in a sub-mode (text/vector/pen_creation), exit it. Else exit group.
    const editMode = useStore.getState().editMode;
    if (editMode.kind === "vector" || editMode.kind === "pen_creation") {
      const before = editMode;
      dispatch({
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "set_edit_mode",
        before,
        after: { kind: "none" },
      });
      emitSemantic({ name: "mode_change", before: before.kind, after: "none" });
      return;
    }
    exitGroup();
    return;
  }

  // Cmd/Ctrl combos
  if (meta) {
    if (key === "c") {
      e.preventDefault();
      copySelection("shortcut");
      return;
    }
    if (key === "x") {
      e.preventDefault();
      cutSelection("shortcut");
      return;
    }
    if (key === "v") {
      e.preventDefault();
      pasteFromClipboard("shortcut");
      return;
    }
    if (key === "d") {
      e.preventDefault();
      duplicateSelection();
      return;
    }
    if (key === "a") {
      e.preventDefault();
      selectAll();
      return;
    }
    if (key === "z" && !e.shiftKey) {
      e.preventDefault();
      undo();
      return;
    }
    if ((key === "z" && e.shiftKey) || key === "y") {
      e.preventDefault();
      redo();
      return;
    }
    if (key === "\\") {
      e.preventDefault();
      useStore.setState({ uiHidden: !useStore.getState().uiHidden });
      return;
    }
    if (key === "k" && e.shiftKey) {
      e.preventDefault();
      openImageFilePicker();
      return;
    }
    if (key === "r" && !e.shiftKey) {
      const sel = useStore.getState().selectionByPage[useStore.getState().activePageId] ?? [];
      if (sel.length > 0) {
        e.preventDefault();
        useStore.setState((s) => { s.openModal = "rename"; });
        return;
      }
    }
    if (key === "g" && !e.shiftKey) {
      e.preventDefault();
      groupSelection("shortcut");
      return;
    }
    if (key === "g" && e.shiftKey) {
      e.preventDefault();
      ungroupSelection("shortcut");
      return;
    }
    if (key === "]" && !e.altKey) {
      e.preventDefault();
      reorderZ("forward");
      return;
    }
    if (key === "[" && !e.altKey) {
      e.preventDefault();
      reorderZ("backward");
      return;
    }
    if (key === "]" && e.altKey) {
      e.preventDefault();
      reorderZ("front");
      return;
    }
    if (key === "[" && e.altKey) {
      e.preventDefault();
      reorderZ("back");
      return;
    }
    if (key === "0") {
      e.preventDefault();
      zoomTo100("keyboard");
      return;
    }
    if (key === "1") {
      e.preventDefault();
      zoomToFit("keyboard");
      return;
    }
    if (key === "2") {
      e.preventDefault();
      zoomToSelection("keyboard");
      return;
    }
    if (key === "=" || key === "+") {
      e.preventDefault();
      zoomBy(1.2, "keyboard");
      return;
    }
    if (key === "-" || key === "_") {
      e.preventDefault();
      zoomBy(1 / 1.2, "keyboard");
      return;
    }
  }

  // Shift+H / Shift+V: flip horizontal / vertical (Figma: Shift+H, Shift+V)
  if (e.shiftKey && !meta && !e.altKey) {
    if (key === "h") {
      e.preventDefault();
      flipSelection("horizontal", "shortcut");
      return;
    }
    if (key === "v") {
      e.preventDefault();
      flipSelection("vertical", "shortcut");
      return;
    }
  }
}

function onKeyUp(e: KeyboardEvent): void {
  if (e.key === " " || e.code === "Space") {
    if (useStore.getState().spaceDown) {
      useStore.setState((s) => { s.spaceDown = false; });
    }
  }
}

export function installKeymap(): void {
  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);
}

export function uninstallKeymap(): void {
  window.removeEventListener("keydown", onKeyDown);
  window.removeEventListener("keyup", onKeyUp);
}
