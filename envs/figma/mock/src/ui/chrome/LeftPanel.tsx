// Left navigation panel.

import { useState, useRef, useEffect, useCallback } from "react";
import {
  ChevronRight, ChevronDown, Plus, Search, X, FileText,
  Square, Circle, Hexagon, Star as StarIcon, Minus, ArrowRight,
  Type, Spline, Image as ImageIcon, Frame as FrameIcon, Folder,
  Slice as SliceIcon,
} from "lucide-react";
import { noopClick } from "./noopClick";
import { LayersTree } from "@/ui/panels/LayersTree";
import { useStore } from "@/engine/store";
import { setSelection } from "@/engine/commands";
import { createPage, switchPage, renamePage, deletePage } from "@/engine/pageCommands";
import { renameFile } from "@/engine/documentCommands";
import type { Page, Layer } from "@/types/scene";

// ─── Search helpers ────────────────────────────────────────────────────────────

type SearchScope = "this_page" | "all_pages";

interface LayerItem { kind: "layer"; layer: Layer; page: Page; }
interface PageItem  { kind: "page";  page: Page; }
type SearchItem = LayerItem | PageItem;

// A "Pages" group always uses page name matches (both scopes).
// Layer groups: "this_page" → single group with no header; "all_pages" → one group per page.
interface PagesGroup  { kind: "pages_group";  items: PageItem[]; }
interface LayerGroup  { kind: "layer_group";  page: Page; items: LayerItem[]; showHeader: boolean; }
type ResultGroup = PagesGroup | LayerGroup;

function collectLayers(layers: Layer[], out: Layer[]) {
  for (const l of layers) {
    out.push(l);
    if ("children" in l && l.children) collectLayers(l.children, out);
  }
}

function buildGroups(scope: SearchScope, pages: Page[], activePageId: string, q: string): ResultGroup[] {
  if (!q.trim()) return [];
  const lower = q.toLowerCase();
  const result: ResultGroup[] = [];

  // Pages group — always search all pages by name
  const matchingPages = pages.filter((p) => p.name.toLowerCase().includes(lower));
  if (matchingPages.length > 0) {
    result.push({ kind: "pages_group", items: matchingPages.map((p) => ({ kind: "page", page: p })) });
  }

  // Layer groups
  const scopePages = scope === "this_page" ? pages.filter((p) => p.id === activePageId) : pages;
  for (const page of scopePages) {
    const flat: Layer[] = [];
    collectLayers(page.children, flat);
    const matching = flat.filter((l) => l.name.toLowerCase().includes(lower));
    if (matching.length > 0) {
      result.push({
        kind: "layer_group",
        page,
        items: matching.map((l) => ({ kind: "layer", layer: l, page })),
        showHeader: scope === "all_pages",
      });
    }
  }
  return result;
}

function flattenItems(groups: ResultGroup[]): SearchItem[] {
  return groups.flatMap((g) => g.items as SearchItem[]);
}

function SearchLayerIcon({ layer }: { layer: Layer }) {
  const props = { size: 12, color: "var(--color-text-secondary)" } as const;
  switch (layer.type) {
    case "rectangle": return <Square {...props} />;
    case "ellipse":   return <Circle {...props} />;
    case "polygon":   return <Hexagon {...props} />;
    case "star":      return <StarIcon {...props} />;
    case "line":      return <Minus {...props} />;
    case "arrow":     return <ArrowRight {...props} />;
    case "text":      return <Type {...props} />;
    case "vector":    return <Spline {...props} />;
    case "image":     return <ImageIcon {...props} />;
    case "frame":     return <FrameIcon {...props} />;
    case "section":
    case "group":     return <Folder {...props} />;
    case "slice":     return <SliceIcon {...props} />;
  }
}

function GroupHeader({ label, count }: { label: string; count: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", padding: "6px 10px 3px", gap: 4 }}>
      <ChevronDown size={11} color="var(--color-text-disabled)" />
      <span style={{ flex: 1, fontSize: "var(--fs-xs)", fontWeight: 600, color: "var(--color-text-secondary)", letterSpacing: 0.2 }}>
        {label}
      </span>
      <span style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-disabled)" }}>{count}</span>
    </div>
  );
}

function ResultRow({ dataId, isActive, onClick, icon, name, query }: {
  dataId: string;
  isActive: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  name: string;
  query: string;
}) {
  return (
    <button
      data-id={dataId}
      onClick={onClick}
      style={{ width: "100%", display: "flex", alignItems: "center", gap: 8, padding: "5px 10px", background: isActive ? "var(--color-bg-row-active)" : "transparent", color: "var(--color-text-secondary)", fontSize: "var(--fs-sm)", textAlign: "left" }}
      onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = "transparent"; }}
    >
      {icon}
      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        <HighlightedName name={name} query={query} />
      </span>
    </button>
  );
}

function HighlightedName({ name, query }: { name: string; query: string }) {
  if (!query) return <span>{name}</span>;
  const idx = name.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return <span>{name}</span>;
  return (
    <span>
      {name.slice(0, idx)}
      <span style={{ color: "var(--color-text-primary)", fontWeight: 600 }}>
        {name.slice(idx, idx + query.length)}
      </span>
      {name.slice(idx + query.length)}
    </span>
  );
}

// ─── Root panel ───────────────────────────────────────────────────────────────

export function LeftPanel() {
  const [searchMode, setSearchMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const openSearch = useCallback(() => {
    setSearchQuery("");
    setSearchMode(true);
  }, []);

  const closeSearch = useCallback(() => {
    setSearchMode(false);
    setSearchQuery("");
  }, []);

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
      {searchMode ? (
        <SearchPanel query={searchQuery} setQuery={setSearchQuery} onClose={closeSearch} />
      ) : (
        <>
          <PagesSection onOpenSearch={openSearch} />
          <LayersSection />
        </>
      )}
    </aside>
  );
}

// ─── Search panel ─────────────────────────────────────────────────────────────

function SearchPanel({ query, setQuery, onClose }: {
  query: string;
  setQuery: (q: string) => void;
  onClose: () => void;
}) {
  const pages = useStore((s) => s.document.pages);
  const activePageId = useStore((s) => s.activePageId);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const scopeRef = useRef<HTMLDivElement | null>(null);
  const [cursor, setCursor] = useState(0);
  const [scope, setScope] = useState<SearchScope>("this_page");
  const [scopeOpen, setScopeOpen] = useState(false);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const groups = buildGroups(scope, pages, activePageId, query);
  const flat = flattenItems(groups);
  const totalCount = flat.length;

  useEffect(() => { setCursor(0); }, [query, scope]);

  useEffect(() => {
    if (!scopeOpen) return;
    function onDoc(e: MouseEvent) {
      if (!scopeRef.current?.contains(e.target as Node)) setScopeOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [scopeOpen]);

  function selectFlat(idx: number) {
    const item = flat[idx];
    if (!item) return;
    setCursor(idx);
    if (item.kind === "layer") {
      if (item.page.id !== activePageId) switchPage(item.page.id, "panel_click");
      setSelection([item.layer.id], "panel_row_click");
    } else {
      switchPage(item.page.id, "panel_click");
    }
  }

  function goUp()   { selectFlat((cursor - 1 + totalCount) % Math.max(totalCount, 1)); }
  function goDown() { selectFlat((cursor + 1) % Math.max(totalCount, 1)); }

  let itemIdx = 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      {/* Input row */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 8px", borderBottom: "1px solid var(--color-border)" }}>
        <Search size={13} color="var(--color-text-secondary)" style={{ flexShrink: 0 }} />
        <input
          ref={inputRef}
          data-id="search.input"
          value={query}
          onChange={(e) => setQuery(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") onClose();
            if (e.key === "ArrowDown") { e.preventDefault(); goDown(); }
            if (e.key === "ArrowUp")   { e.preventDefault(); goUp(); }
            if (e.key === "Enter" && totalCount > 0) selectFlat(cursor);
          }}
          placeholder="Find…"
          style={{ flex: 1, height: 24, background: "transparent", color: "var(--color-text-primary)", border: "none", fontSize: "var(--fs-sm)", outline: 0 }}
        />
        <button
          data-id="search.close"
          onClick={onClose}
          title="Close search"
          style={{ width: 18, height: 18, borderRadius: 4, display: "grid", placeItems: "center", color: "var(--color-text-secondary)", flexShrink: 0 }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <X size={12} />
        </button>
      </div>

      {/* Meta row: count + scope dropdown + nav arrows */}
      {query.trim() && (
        <div style={{ display: "flex", alignItems: "center", padding: "4px 8px", fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)", borderBottom: "1px solid var(--color-border)", gap: 4 }}>
          <span>{totalCount} result{totalCount !== 1 ? "s" : ""} ·&nbsp;</span>

          {/* Scope dropdown */}
          <div ref={scopeRef} style={{ position: "relative" }}>
            <button
              data-id="search.scope"
              onClick={() => setScopeOpen((o) => !o)}
              style={{ display: "flex", alignItems: "center", gap: 2, color: "var(--color-text-secondary)", fontSize: "var(--fs-xs)", borderRadius: 3, padding: "1px 3px" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              {scope === "this_page" ? "This page" : "All pages"}
              <ChevronDown size={10} />
            </button>
            {scopeOpen && (
              <div style={{ position: "absolute", top: "100%", left: 0, marginTop: 2, minWidth: 100, background: "var(--color-bg-panel-elevated)", border: "1px solid var(--color-border-strong)", borderRadius: 6, boxShadow: "0 8px 20px rgba(0,0,0,0.4)", padding: 4, zIndex: 200 }}>
                {(["this_page", "all_pages"] as SearchScope[]).map((s) => (
                  <button
                    key={s}
                    onClick={() => { setScope(s); setScopeOpen(false); }}
                    style={{ width: "100%", textAlign: "left", padding: "5px 10px", borderRadius: 4, fontSize: "var(--fs-xs)", color: scope === s ? "var(--color-text-primary)" : "var(--color-text-secondary)", background: scope === s ? "var(--color-bg-row-active)" : "transparent", fontWeight: scope === s ? 600 : 400 }}
                    onMouseEnter={(e) => { if (scope !== s) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
                    onMouseLeave={(e) => { if (scope !== s) e.currentTarget.style.background = "transparent"; }}
                  >
                    {s === "this_page" ? "This page" : "All pages"}
                  </button>
                ))}
              </div>
            )}
          </div>

          <span style={{ flex: 1 }} />
          {/* Nav arrows */}
          {(["up", "down"] as const).map((dir) => (
            <button
              key={dir}
              onClick={dir === "up" ? goUp : goDown}
              disabled={totalCount === 0}
              title={dir === "up" ? "Previous result" : "Next result"}
              style={{ width: 18, height: 18, borderRadius: 4, display: "grid", placeItems: "center", color: totalCount > 0 ? "var(--color-text-secondary)" : "var(--color-text-disabled)" }}
              onMouseEnter={(e) => { if (totalCount > 0) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <ChevronDown size={12} style={dir === "up" ? { transform: "rotate(180deg)" } : undefined} />
            </button>
          ))}
        </div>
      )}

      {/* No results hint */}
      {query.trim() && totalCount === 0 && scope === "this_page" && (
        <div style={{ padding: "16px 12px", display: "flex", flexDirection: "column", gap: 8, alignItems: "flex-start" }}>
          <span style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-disabled)" }}>
            No results on this page.
          </span>
          <button
            onClick={() => setScope("all_pages")}
            style={{ fontSize: "var(--fs-xs)", color: "var(--color-selection-blue)", borderRadius: 4, padding: "3px 6px" }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
          >
            Search in all pages →
          </button>
        </div>
      )}

      {/* Results list */}
      <div className="scroll-y" style={{ flex: 1, minHeight: 0, padding: "4px 0" }}>
        {groups.map((group) => {
          if (group.kind === "pages_group") {
            return (
              <div key="__pages_group__">
                <GroupHeader label="Pages" count={group.items.length} />
                {group.items.map((item) => {
                  const thisIdx = itemIdx++;
                  const isActive = thisIdx === cursor;
                  return (
                    <ResultRow
                      key={`page-${item.page.id}`}
                      dataId={`search.result.page.${item.page.id}`}
                      isActive={isActive}
                      onClick={() => selectFlat(thisIdx)}
                      icon={<FileText size={12} color="var(--color-text-secondary)" />}
                      name={item.page.name}
                      query={query}
                    />
                  );
                })}
              </div>
            );
          }
          // layer_group
          return (
            <div key={group.page.id}>
              {group.showHeader && (
                <GroupHeader label={group.page.name} count={group.items.length} />
              )}
              {group.items.map((item) => {
                const thisIdx = itemIdx++;
                const isActive = thisIdx === cursor;
                return (
                  <ResultRow
                    key={item.layer.id}
                    dataId={`search.result.${item.layer.id}`}
                    isActive={isActive}
                    onClick={() => selectFlat(thisIdx)}
                    icon={<SearchLayerIcon layer={item.layer} />}
                    name={item.layer.name}
                    query={query}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── File name row ────────────────────────────────────────────────────────────

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
            fontWeight: 500,
            minWidth: 0,
            overflow: "hidden",
            whiteSpace: "nowrap",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{fileName}</span>
        </button>
      )}
    </div>
  );
}

// ─── Layers section ───────────────────────────────────────────────────────────

function LayersSection() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
      <div
        style={{
          padding: "6px 8px 4px",
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-xs)",
          fontWeight: 600,
          letterSpacing: 0.4,
          textTransform: "uppercase",
          display: "flex",
          alignItems: "center",
          gap: 4,
          flexShrink: 0,
        }}
      >
        <button
          data-id="layers.collapse"
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? "Expand layers" : "Collapse layers"}
          style={{
            width: 18,
            height: 18,
            borderRadius: 4,
            display: "grid",
            placeItems: "center",
            color: "var(--color-text-secondary)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          {collapsed ? <ChevronRight size={12} /> : <ChevronDown size={12} />}
        </button>
        <span style={{ flex: 1 }}>Layers</span>
      </div>
      {!collapsed && (
        <div className="scroll-y" style={{ flex: 1, minHeight: 0 }}>
          <LayersTree />
        </div>
      )}
    </div>
  );
}

// ─── Pages section ────────────────────────────────────────────────────────────

function PagesSection({ onOpenSearch }: { onOpenSearch: () => void }) {
  const pages = useStore((s) => s.document.pages);
  const activePageId = useStore((s) => s.activePageId);
  const [collapsed, setCollapsed] = useState(false);
  const [contextMenu, setContextMenu] = useState<{ pageId: string; x: number; y: number } | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);

  const activePage = pages.find((p) => p.id === activePageId);

  return (
    <div style={{ borderBottom: "1px solid var(--color-border)" }}>
      <div
        style={{
          padding: "6px 8px 4px",
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-xs)",
          fontWeight: 600,
          letterSpacing: 0.4,
          textTransform: "uppercase",
          display: "flex",
          alignItems: "center",
          gap: 4,
        }}
      >
        <button
          data-id="pages.collapse"
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? "Expand pages" : "Collapse pages"}
          style={{
            width: 18,
            height: 18,
            borderRadius: 4,
            display: "grid",
            placeItems: "center",
            color: "var(--color-text-secondary)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          {collapsed ? <ChevronRight size={12} /> : <ChevronDown size={12} />}
        </button>
        <span style={{ flex: 1 }}>
          {collapsed ? (activePage?.name ?? "Pages") : "Pages"}
        </span>
        <button
          data-id="pages.search"
          onClick={onOpenSearch}
          title="Find layers"
          style={{
            width: 18,
            height: 18,
            borderRadius: 4,
            display: "grid",
            placeItems: "center",
            color: "var(--color-text-secondary)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <Search size={12} />
        </button>
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
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <Plus size={12} />
        </button>
      </div>
      {!collapsed && (
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
      )}
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

// ─── Page row ─────────────────────────────────────────────────────────────────

function PageRow({
  page, active, renaming, onClick, onDoubleClick, onContextMenu, onCommitRename, onCancelRename,
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
      onContextMenu={(e) => { e.preventDefault(); onContextMenu(e); }}
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
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = "transparent"; }}
    >
      {page.name}
    </button>
  );
}

// ─── Page context menu ────────────────────────────────────────────────────────

function PageContextMenu({ pageId, x, y, canDelete, onClose, onRename, onDelete }: {
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
      <Sep />
      <MenuRow
        id={`page-context.${pageId}.delete`}
        label="Delete"
        onClick={canDelete ? onDelete : (e) => noopClick(`page-context.${pageId}.delete`, e)}
        disabled={!canDelete}
      />
    </div>
  );
}

function MenuRow({ id, label, onClick, disabled }: {
  id: string;
  label: string;
  onClick: (e: React.MouseEvent) => void;
  disabled?: boolean;
}) {
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
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {label}
    </button>
  );
}

function Sep() {
  return <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />;
}
