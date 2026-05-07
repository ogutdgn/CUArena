// Left navigation panel.

import { useState, useRef, useEffect } from "react";
import { ChevronDown, Plus } from "lucide-react";
import { noopClick } from "./noopClick";
import { LayersTree } from "@/ui/panels/LayersTree";
import { useStore } from "@/engine/store";
import { createPage, switchPage, renamePage, deletePage } from "@/engine/pageCommands";
import { renameFile } from "@/engine/documentCommands";
import type { Page } from "@/types/scene";

export function LeftPanel() {
  return (
    <aside
      className="no-select"
      data-id="left-panel"
      style={{
        width: 240,
        background: "var(--color-bg-panel)",
        borderRight: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        minWidth: 200,
        maxWidth: 480,
        minHeight: 0,
        overflow: "hidden",
      }}
    >
      <FileNameRow />
      <TabsRow />
      <PagesSection />
      <div className="scroll-y" style={{ flex: 1, minHeight: 0 }}>
        <LayersHeader />
        <LayersTree />
      </div>
    </aside>
  );
}

// User-requested mock deviation: real Figma renders only an implicit
// collapse-all icon for the Layers section. The explicit "Layers" label
// here was asked for to mirror the Pages header style.
function LayersHeader() {
  return (
    <div
      style={{
        padding: "6px 12px 4px",
        color: "var(--color-text-secondary)",
        fontSize: "var(--fs-xs)",
        fontWeight: 600,
        letterSpacing: 0.4,
        textTransform: "uppercase",
        display: "flex",
        alignItems: "center",
      }}
    >
      <span style={{ flex: 1 }}>Layers</span>
    </div>
  );
}

function FileNameRow() {
  const fileName = useStore((s) => s.document.name);
  const [editing, setEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  return (
    <div
      style={{
        height: 36,
        display: "flex",
        alignItems: "center",
        padding: "0 10px",
        gap: 6,
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      {editing ? (
        <input
          ref={inputRef}
          data-id="file-name.input"
          defaultValue={fileName}
          onBlur={(e) => {
            renameFile(e.currentTarget.value, "inline_edit");
            setEditing(false);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            else if (e.key === "Escape") setEditing(false);
          }}
          onClick={(e) => e.stopPropagation()}
          style={{
            flex: 1,
            height: 24,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-selection-blue)",
            borderRadius: "var(--radius-sm)",
            padding: "0 8px",
            fontSize: "var(--fs-sm)",
            fontWeight: 500,
            outline: 0,
          }}
        />
      ) : (
        <>
          <button
            data-id="file-name.open-edit"
            onClick={() => setEditing(true)}
            title="Rename file"
            style={{
              flex: 1,
              height: 24,
              borderRadius: "var(--radius-sm)",
              color: "var(--color-text-primary)",
              textAlign: "left",
              padding: "0 8px",
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontWeight: 500,
              minWidth: 0,
              overflow: "hidden",
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
            }}
          >
            <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{fileName}</span>
          </button>
          <button
            data-id="file-menu.open"
            onClick={(e) => noopClick("file-menu.open", e)}
            title="File menu — not implemented"
            style={{
              width: 18,
              height: 18,
              borderRadius: 4,
              display: "grid",
              placeItems: "center",
              color: "var(--color-text-secondary)",
            }}
          >
            <ChevronDown size={12} />
          </button>
        </>
      )}
    </div>
  );
}

function TabsRow() {
  return (
    <div
      style={{
        height: 32,
        display: "flex",
        alignItems: "stretch",
        borderBottom: "1px solid var(--color-border)",
        padding: "0 4px",
      }}
    >
      <Tab id="left-nav.tab.file" label="File" active />
      <Tab id="left-nav.tab.assets" label="Assets" active={false} visualOnly />
    </div>
  );
}

function Tab({ id, label, active, visualOnly }: { id: string; label: string; active: boolean; visualOnly?: boolean }) {
  return (
    <button
      data-id={id}
      onClick={(e) => visualOnly && noopClick(id, e)}
      style={{
        flex: 1,
        position: "relative",
        color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
        fontSize: "var(--fs-sm)",
        fontWeight: active ? 600 : 500,
      }}
    >
      {label}
      {active && (
        <span
          style={{
            position: "absolute",
            bottom: -1,
            left: 8,
            right: 8,
            height: 2,
            background: "var(--color-text-primary)",
            borderRadius: 2,
          }}
        />
      )}
    </button>
  );
}

function PagesSection() {
  const pages = useStore((s) => s.document.pages);
  const activePageId = useStore((s) => s.activePageId);
  const [contextMenu, setContextMenu] = useState<{ pageId: string; x: number; y: number } | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);

  return (
    <div style={{ borderBottom: "1px solid var(--color-border)" }}>
      <div
        style={{
          padding: "6px 12px 4px",
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-xs)",
          fontWeight: 600,
          letterSpacing: 0.4,
          textTransform: "uppercase",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        <span style={{ flex: 1 }}>Pages</span>
        <button
          data-id="pages.add-page"
          onClick={() => createPage()}
          title="Add page"
          style={{
            width: 18,
            height: 18,
            borderRadius: 4,
            display: "grid",
            placeItems: "center",
            color: "var(--color-text-secondary)",
          }}
        >
          <Plus size={12} />
        </button>
      </div>
      <div style={{ padding: "2px 8px 8px" }}>
        {pages.map((p) => (
          <PageRow
            key={p.id}
            page={p}
            active={p.id === activePageId}
            renaming={renamingId === p.id}
            onClick={() => switchPage(p.id, "panel_click")}
            onContextMenu={(e) => setContextMenu({ pageId: p.id, x: e.clientX, y: e.clientY })}
            onCommitRename={(name) => {
              renamePage(p.id, name);
              setRenamingId(null);
            }}
            onDoubleClick={() => setRenamingId(p.id)}
            onCancelRename={() => setRenamingId(null)}
          />
        ))}
      </div>
      {contextMenu && (
        <PageContextMenu
          pageId={contextMenu.pageId}
          x={contextMenu.x}
          y={contextMenu.y}
          canDelete={pages.length > 1}
          onClose={() => setContextMenu(null)}
          onRename={() => {
            setRenamingId(contextMenu.pageId);
            setContextMenu(null);
          }}
          onDelete={() => {
            deletePage(contextMenu.pageId, "context_menu");
            setContextMenu(null);
          }}
        />
      )}
    </div>
  );
}

function PageRow({
  page,
  active,
  renaming,
  onClick,
  onDoubleClick,
  onContextMenu,
  onCommitRename,
  onCancelRename,
}: {
  page: Page;
  active: boolean;
  renaming: boolean;
  onClick: () => void;
  onDoubleClick: () => void;
  onContextMenu: (e: React.MouseEvent) => void;
  onCommitRename: (name: string) => void;
  onCancelRename: () => void;
}) {
  const ref = useRef<HTMLInputElement | null>(null);
  useEffect(() => {
    if (renaming && ref.current) {
      ref.current.focus();
      ref.current.select();
    }
  }, [renaming]);

  if (renaming) {
    return (
      <div style={{ padding: "0 8px", marginBottom: 1 }}>
        <input
          ref={ref}
          defaultValue={page.name}
          onBlur={(e) => {
            const v = e.currentTarget.value.trim();
            if (v) onCommitRename(v);
            else onCancelRename();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            else if (e.key === "Escape") onCancelRename();
          }}
          style={{
            width: "100%",
            height: 24,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-selection-blue)",
            borderRadius: 4,
            padding: "0 8px",
            fontSize: "var(--fs-sm)",
            outline: 0,
          }}
        />
      </div>
    );
  }

  return (
    <button
      data-id={`page-row.${page.id}`}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      onContextMenu={(e) => {
        e.preventDefault();
        onContextMenu(e);
      }}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "4px 8px",
        borderRadius: 4,
        background: active ? "var(--color-bg-row-active)" : "transparent",
        color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
        fontSize: "var(--fs-sm)",
        textAlign: "left",
        marginBottom: 1,
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.background = "transparent";
      }}
    >
      {page.name}
    </button>
  );
}

function PageContextMenu({
  pageId,
  x,
  y,
  canDelete,
  onClose,
  onRename,
  onDelete,
}: {
  pageId: string;
  x: number;
  y: number;
  canDelete: boolean;
  onClose: () => void;
  onRename: () => void;
  onDelete: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
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

  return (
    <div
      ref={ref}
      role="menu"
      style={{
        position: "fixed",
        left: x,
        top: y,
        minWidth: 180,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 6,
        boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
        padding: 4,
        zIndex: 100,
      }}
    >
      <MenuRow id={`page-context.${pageId}.rename`} label="Rename" onClick={onRename} />
      <MenuRow id={`page-context.${pageId}.duplicate`} label="Duplicate" onClick={(e) => noopClick(`page-context.${pageId}.duplicate`, e)} disabled />
      <MenuRow id={`page-context.${pageId}.copy-link`} label="Copy link to page" onClick={(e) => noopClick(`page-context.${pageId}.copy-link`, e)} disabled />
      <Sep />
      <MenuRow id={`page-context.${pageId}.delete`} label="Delete" onClick={canDelete ? onDelete : (e) => noopClick(`page-context.${pageId}.delete`, e)} disabled={!canDelete} />
    </div>
  );
}

function MenuRow({ id, label, onClick, disabled }: { id: string; label: string; onClick: (e: React.MouseEvent) => void; disabled?: boolean }) {
  return (
    <button
      data-id={id}
      disabled={disabled}
      onClick={onClick}
      style={{
        width: "100%",
        textAlign: "left",
        padding: "6px 10px",
        borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-primary)",
        fontSize: "var(--fs-sm)",
        background: "transparent",
      }}
      onMouseEnter={(e) => {
        if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {label}
    </button>
  );
}

function Sep() {
  return <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />;
}
