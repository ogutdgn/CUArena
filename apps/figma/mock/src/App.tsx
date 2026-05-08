// Top-level layout: left rail + left panel + canvas + right panel + bottom toolbar.
// Source: .analysis/ui-report.md §1 region table.

import { useEffect } from "react";
import { useStore } from "@/engine/store";
import { Toolbar } from "@/ui/chrome/Toolbar";
import { LeftPanel } from "@/ui/chrome/LeftPanel";
import { RightPanel } from "@/ui/chrome/RightPanel";
import { LeftRail } from "@/ui/chrome/LeftRail";
import { CanvasView } from "@/ui/canvas/CanvasView";
import { TextEditor } from "@/ui/overlays/TextEditor";
import { ContextMenu } from "@/ui/overlays/ContextMenu";
import { RenameModal } from "@/ui/overlays/RenameModal";
import { Toasts } from "@/ui/overlays/Toasts";
import { PrototypePreview } from "@/ui/overlays/PrototypePreview";
import { installKeymap, uninstallKeymap } from "@/util/keymap";

export function App() {
  const uiHidden = useStore((s) => s.uiHidden);
  const contextMenu = useStore((s) => s.contextMenu);

  useEffect(() => {
    installKeymap();
    return () => uninstallKeymap();
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        display: "grid",
        gridTemplateColumns: uiHidden
          ? "1fr"
          : "var(--left-rail-width) auto 1fr auto",
        gridTemplateRows: "1fr",
        background: "var(--color-bg-canvas)",
        color: "var(--color-text-primary)",
      }}
    >
      {!uiHidden && <LeftRail />}
      {!uiHidden && <LeftPanel />}
      <div style={{ position: "relative", overflow: "hidden" }}>
        <CanvasView />
        {!uiHidden && <Toolbar />}
      </div>
      {!uiHidden && <RightPanel />}
      <TextEditor />
      <RenameModal />
      <Toasts />
      <PrototypePreview />
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onClose={() => useStore.setState((s) => { s.contextMenu = null; })}
          onRequestRename={() => {
            const sel = useStore.getState().selectionByPage[useStore.getState().activePageId] ?? [];
            if (sel.length === 1) {
              useStore.setState((s) => { s.renamingLayerId = sel[0]; });
            }
          }}
        />
      )}
    </div>
  );
}
