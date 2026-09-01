// Right-click context menu. Items vary by selection state.

import { useEffect, useRef } from "react";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  copySelection,
  cutSelection,
  pasteFromClipboard,
  duplicateSelection,
  deleteSelection,
} from "@/engine/commands";
import { groupSelection, ungroupSelection, reorderZ } from "@/engine/hierarchyCommands";
import { setVisibility, setLocked } from "@/engine/propertyCommands";
import { flipSelection } from "@/engine/transformCommands";
import { undo } from "@/engine/dispatch";
import { noopClick } from "@/ui/chrome/noopClick";

export function ContextMenu({
  x,
  y,
  onClose,
  onRequestRename,
}: {
  x: number;
  y: number;
  onClose: () => void;
  onRequestRename: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const layers = useStore((s) => getSelectedLayers(s));
  const clipboard = useStore((s) => s.clipboard);
  const canUndo = useStore((s) => s.undoStack.length > 0);
  const hasSelection = layers.length > 0;
  const allLocked = hasSelection && layers.every((l) => l.locked);
  const allHidden = hasSelection && layers.every((l) => !l.visible);
  const onlyGroup = hasSelection && layers.length === 1 && layers[0].type === "group";

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) onClose();
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("mousedown", onDoc, true);
    document.addEventListener("keydown", onKey, true);
    return () => {
      document.removeEventListener("mousedown", onDoc, true);
      document.removeEventListener("keydown", onKey, true);
    };
  }, [onClose]);

  // Clamp menu inside viewport
  const W = 220;
  const H = 480;
  const left = Math.min(x, window.innerWidth - W - 4);
  const top = Math.min(y, window.innerHeight - H);

  return (
    <div
      ref={ref}
      role="menu"
      style={{
        position: "fixed",
        left,
        top,
        minWidth: W,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 6,
        boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
        padding: 4,
        zIndex: 200,
        fontSize: "var(--fs-sm)",
      }}
    >
      <Item id="ctx.undo" label="Undo" shortcut="Ctrl+Z" disabled={!canUndo} disabledTitle="Nothing to undo" onClick={() => { undo(); onClose(); }} />
      <Sep />
      <Item id="ctx.copy" label="Copy" shortcut="⌘C" disabled={!hasSelection} onClick={() => { copySelection("context_menu"); onClose(); }} />
      <Item id="ctx.cut" label="Cut" shortcut="⌘X" disabled={!hasSelection} onClick={() => { cutSelection("context_menu"); onClose(); }} />
      <Item id="ctx.paste" label="Paste" shortcut="⌘V" disabled={!clipboard} onClick={() => { pasteFromClipboard("context_menu"); onClose(); }} />
      <Item id="ctx.duplicate" label="Duplicate" shortcut="⌘D" disabled={!hasSelection} onClick={() => { duplicateSelection(); onClose(); }} />
      <Sep />
      <Item id="ctx.rename" label="Rename" shortcut="⌘R" disabled={layers.length !== 1} onClick={() => { onRequestRename(); onClose(); }} />
      <Item id="ctx.delete" label="Delete" shortcut="⌫" disabled={!hasSelection} onClick={() => { deleteSelection("context_menu_canvas"); onClose(); }} />
      <Sep />
      <Item id="ctx.bring-front" label="Bring to front" shortcut="⌘⌥]" disabled={!hasSelection} onClick={() => { reorderZ("front"); onClose(); }} />
      <Item id="ctx.bring-forward" label="Bring forward" shortcut="⌘]" disabled={!hasSelection} onClick={() => { reorderZ("forward"); onClose(); }} />
      <Item id="ctx.send-backward" label="Send backward" shortcut="⌘[" disabled={!hasSelection} onClick={() => { reorderZ("backward"); onClose(); }} />
      <Item id="ctx.send-back" label="Send to back" shortcut="⌘⌥[" disabled={!hasSelection} onClick={() => { reorderZ("back"); onClose(); }} />
      <Sep />
      <Item id="ctx.group" label="Group selection" shortcut="⌘G" disabled={!hasSelection} onClick={() => { groupSelection("context_menu"); onClose(); }} />
      <Item id="ctx.ungroup" label="Ungroup" shortcut="⇧⌘G" disabled={!onlyGroup} onClick={() => { ungroupSelection("context_menu"); onClose(); }} />
      <Sep />
      <Item id="ctx.flip-h" label="Flip horizontal" shortcut="⇧H" disabled={!hasSelection} onClick={() => { flipSelection("horizontal", "context_menu"); onClose(); }} />
      <Item id="ctx.flip-v" label="Flip vertical" shortcut="⇧V" disabled={!hasSelection} onClick={() => { flipSelection("vertical", "context_menu"); onClose(); }} />
      <Sep />
      <Item id="ctx.toggle-lock" label={allLocked ? "Unlock" : "Lock"} shortcut="⇧⌘L" disabled={!hasSelection} onClick={() => { setLocked(!allLocked); onClose(); }} />
      <Item id="ctx.toggle-visibility" label={allHidden ? "Show" : "Hide"} shortcut="⇧⌘H" disabled={!hasSelection} onClick={() => { setVisibility(allHidden); onClose(); }} />
    </div>
  );
}

function Item({
  id,
  label,
  shortcut,
  onClick,
  disabled,
  disabledTitle,
}: {
  id: string;
  label: string;
  shortcut?: string;
  onClick?: () => void;
  disabled?: boolean;
  disabledTitle?: string;
}) {
  return (
    <button
      data-id={id}
      onClick={(e) => {
        if (disabled) {
          noopClick(id, e);
          return;
        }
        onClick?.();
      }}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        height: 26,
        padding: "0 8px",
        borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-primary)",
        background: "transparent",
        textAlign: "left",
      }}
      onMouseEnter={(e) => {
        if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      title={disabled ? disabledTitle ?? `${label} — not implemented in this mock` : label}
    >
      <span style={{ flex: 1 }}>{label}</span>
      {shortcut && (
        <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{shortcut}</span>
      )}
    </button>
  );
}

function Sep() {
  return <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />;
}
