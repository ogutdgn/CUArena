// Hierarchical layer tree for the active page.
// Slice 3: indent-by-depth, expand/collapse for containers, click-to-select,
// double-click-to-rename, visibility & lock toggles on hover.

import { useState, useEffect, useRef } from "react";
import { useStore } from "@/engine/store";
import { setSelection } from "@/engine/commands";
import { renameLayer, reorderLayerInPanel } from "@/engine/hierarchyCommands";
import { setVisibility, setLocked } from "@/engine/propertyCommands";
import {
  Square,
  Circle,
  Star,
  Type,
  Image as ImageIcon,
  Hexagon,
  Frame as FrameIcon,
  Folder,
  Minus,
  ArrowRight,
  Slice as SliceIcon,
  Spline,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff,
  Lock,
  Unlock,
} from "lucide-react";
import type { Layer } from "@/types/scene";

export function LayersTree() {
  const page = useStore((s) => s.document.pages.find((p) => p.id === s.activePageId));
  const selection = useStore((s) => s.selectionByPage[s.activePageId] ?? []);
  const focusContextId = useStore((s) => s.focusContextByPage[s.activePageId] ?? null);
  const renamingLayerId = useStore((s) => s.renamingLayerId);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [dropHint, setDropHint] = useState<{ targetId: string; above: boolean } | null>(null);

  if (!page) return null;
  const layers = page.children;
  if (layers.length === 0) {
    return (
      <div style={{ padding: "16px 12px", color: "var(--color-text-muted)", fontSize: "var(--fs-sm)" }}>
        Nothing here yet. Press R to draw a rectangle.
      </div>
    );
  }

  const ordered = [...layers].reverse();
  function onDrop(targetId: string, above: boolean) {
    if (!draggingId) return;
    reorderLayerInPanel(draggingId, targetId, above);
    setDraggingId(null);
    setDropHint(null);
  }

  return (
    <div style={{ padding: "4px 0" }}>
      {ordered.map((l) => (
        <Subtree
          key={l.id}
          layer={l}
          depth={0}
          selection={selection}
          focusContextId={focusContextId}
          expanded={expanded}
          setExpanded={setExpanded}
          renamingLayerId={renamingLayerId}
          draggingId={draggingId}
          dropHint={dropHint}
          onDragStart={setDraggingId}
          onDragHover={(targetId, above) => setDropHint({ targetId, above })}
          onDrop={onDrop}
          onDragEnd={() => {
            setDraggingId(null);
            setDropHint(null);
          }}
        />
      ))}
    </div>
  );
}

function Subtree({
  layer,
  depth,
  selection,
  focusContextId,
  expanded,
  setExpanded,
  renamingLayerId,
  draggingId,
  dropHint,
  onDragStart,
  onDragHover,
  onDrop,
  onDragEnd,
}: {
  layer: Layer;
  depth: number;
  selection: string[];
  focusContextId: string | null;
  expanded: Set<string>;
  setExpanded: React.Dispatch<React.SetStateAction<Set<string>>>;
  renamingLayerId: string | null;
  draggingId: string | null;
  dropHint: { targetId: string; above: boolean } | null;
  onDragStart: (id: string | null) => void;
  onDragHover: (targetId: string, above: boolean) => void;
  onDrop: (targetId: string, above: boolean) => void;
  onDragEnd: () => void;
}) {
  const isContainer = layer.type === "frame" || layer.type === "section" || layer.type === "group";
  const isOpen = expanded.has(layer.id) || focusContextId === layer.id;
  return (
    <>
      <Row
        layer={layer}
        depth={depth}
        selected={selection.includes(layer.id)}
        isFocusContext={focusContextId === layer.id}
        isContainer={isContainer}
        isOpen={isOpen}
        forceRenaming={renamingLayerId === layer.id}
        draggingId={draggingId}
        dropHint={dropHint}
        onDragStart={onDragStart}
        onDragHover={onDragHover}
        onDrop={onDrop}
        onDragEnd={onDragEnd}
        onToggle={() => {
          setExpanded((prev) => {
            const next = new Set(prev);
            if (next.has(layer.id)) next.delete(layer.id);
            else next.add(layer.id);
            return next;
          });
        }}
      />
      {isContainer && isOpen && layer.children && (
        <>
          {[...layer.children].reverse().map((c) => (
            <Subtree
              key={c.id}
              layer={c}
              depth={depth + 1}
              selection={selection}
              focusContextId={focusContextId}
              expanded={expanded}
              setExpanded={setExpanded}
              renamingLayerId={renamingLayerId}
              draggingId={draggingId}
              dropHint={dropHint}
              onDragStart={onDragStart}
              onDragHover={onDragHover}
              onDrop={onDrop}
              onDragEnd={onDragEnd}
            />
          ))}
        </>
      )}
    </>
  );
}

function Row({
  layer,
  depth,
  selected,
  isFocusContext,
  isContainer,
  isOpen,
  onToggle,
  forceRenaming,
  draggingId,
  dropHint,
  onDragStart,
  onDragHover,
  onDrop,
  onDragEnd,
}: {
  layer: Layer;
  depth: number;
  selected: boolean;
  isFocusContext: boolean;
  isContainer: boolean;
  isOpen: boolean;
  onToggle: () => void;
  forceRenaming?: boolean;
  draggingId: string | null;
  dropHint: { targetId: string; above: boolean } | null;
  onDragStart: (id: string | null) => void;
  onDragHover: (targetId: string, above: boolean) => void;
  onDrop: (targetId: string, above: boolean) => void;
  onDragEnd: () => void;
}) {
  const [hover, setHover] = useState(false);
  const [renamingLocal, setRenamingLocal] = useState(false);
  const renaming = renamingLocal || !!forceRenaming;
  const inputRef = useRef<HTMLInputElement | null>(null);
  const isDropTarget = dropHint?.targetId === layer.id;

  useEffect(() => {
    if (renaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [renaming]);

  function endRename() {
    setRenamingLocal(false);
    if (forceRenaming) {
      useStore.setState((s) => { s.renamingLayerId = null; });
    }
  }

  if (renaming) {
    return (
      <div style={{ padding: `0 12px 0 ${12 + depth * 12}px`, height: 26 }}>
        <input
          ref={inputRef}
          defaultValue={layer.name}
          onBlur={(e) => {
            const v = e.currentTarget.value.trim();
            if (v) renameLayer(layer.id, v, "inline_panel");
            endRename();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            if (e.key === "Escape") endRename();
          }}
          style={{
            width: "100%",
            height: 24,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-selection-blue)",
            borderRadius: 4,
            padding: "0 6px",
            fontSize: "var(--fs-sm)",
            outline: 0,
          }}
        />
      </div>
    );
  }

  return (
    <button
      data-id={`layer-row.${layer.id}`}
      draggable
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onDragStart={(e) => {
        e.stopPropagation();
        onDragStart(layer.id);
        try {
          e.dataTransfer.effectAllowed = "move";
          e.dataTransfer.setData("text/plain", layer.id);
        } catch {
          // noop
        }
      }}
      onDragOver={(e) => {
        if (!draggingId || draggingId === layer.id) return;
        e.preventDefault();
        const rect = e.currentTarget.getBoundingClientRect();
        onDragHover(layer.id, e.clientY < rect.top + rect.height / 2);
      }}
      onDrop={(e) => {
        if (!draggingId || draggingId === layer.id) return;
        e.preventDefault();
        const rect = e.currentTarget.getBoundingClientRect();
        onDrop(layer.id, e.clientY < rect.top + rect.height / 2);
      }}
      onDragEnd={() => onDragEnd()}
      onClick={(e) => {
        if (e.shiftKey) {
          const cur = useStore.getState().selectionByPage[useStore.getState().activePageId] ?? [];
          const next = cur.includes(layer.id) ? cur.filter((id) => id !== layer.id) : [...cur, layer.id];
          setSelection(next, "panel_row_click");
        } else {
          setSelection([layer.id], "panel_row_click");
        }
      }}
      onDoubleClick={() => setRenamingLocal(true)}
      onContextMenu={(e) => {
        e.preventDefault();
        e.stopPropagation();
        const cur = useStore.getState().selectionByPage[useStore.getState().activePageId] ?? [];
        if (!cur.includes(layer.id)) {
          setSelection([layer.id], "panel_row_click");
        }
        useStore.setState((s) => {
          s.contextMenu = { x: e.clientX, y: e.clientY };
        });
      }}
      style={{
        position: "relative",
        width: "100%",
        height: 26,
        display: "flex",
        alignItems: "center",
        gap: 4,
        padding: `0 8px 0 ${4 + depth * 12}px`,
        textAlign: "left",
        color: "var(--color-text-primary)",
        background: selected ? "var(--color-bg-row-active)" : isFocusContext ? "rgba(13,153,255,0.06)" : "transparent",
        fontSize: "var(--fs-sm)",
        borderTop: isDropTarget && dropHint?.above ? "1px solid var(--color-selection-blue)" : "1px solid transparent",
        borderBottom: isDropTarget && !dropHint?.above ? "1px solid var(--color-selection-blue)" : "1px solid transparent",
      }}
    >
      {/* Indent guide lines for depth > 0 */}
      {Array.from({ length: depth }).map((_, i) => (
        <span
          key={i}
          style={{
            position: "absolute",
            left: 10 + i * 12,
            top: 0,
            bottom: 0,
            width: 1,
            background: "var(--color-divider)",
            pointerEvents: "none",
          }}
        />
      ))}
      <span
        onClick={(e) => {
          if (isContainer) {
            e.stopPropagation();
            onToggle();
          }
        }}
        style={{ width: 14, display: "grid", placeItems: "center", color: "var(--color-text-secondary)" }}
      >
        {isContainer ? isOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} /> : null}
      </span>
      <LayerIcon layer={layer} />
      <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", opacity: layer.visible ? 1 : 0.5 }}>
        {layer.name}
      </span>
      {(hover || !layer.visible) && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            const wasSelected = selected;
            if (!wasSelected) setSelection([layer.id], "panel_row_click");
            setVisibility(!layer.visible);
            if (!wasSelected) setSelection([], "panel_row_click");
          }}
          title={layer.visible ? "Hide" : "Show"}
          style={{ width: 18, height: 18, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
        >
          {layer.visible ? <Eye size={12} /> : <EyeOff size={12} />}
        </button>
      )}
      {(hover || layer.locked) && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            const wasSelected = selected;
            if (!wasSelected) setSelection([layer.id], "panel_row_click");
            setLocked(!layer.locked);
            if (!wasSelected) setSelection([], "panel_row_click");
          }}
          title={layer.locked ? "Unlock" : "Lock"}
          style={{ width: 18, height: 18, color: layer.locked ? "var(--color-selection-blue)" : "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
        >
          {layer.locked ? <Lock size={12} /> : <Unlock size={12} />}
        </button>
      )}
    </button>
  );
}

function LayerIcon({ layer }: { layer: Layer }) {
  const props = { size: 12, color: "var(--color-text-secondary)" } as const;
  switch (layer.type) {
    case "rectangle":
      return <Square {...props} />;
    case "ellipse":
      return <Circle {...props} />;
    case "polygon":
      return <Hexagon {...props} />;
    case "star":
      return <Star {...props} />;
    case "line":
      return <Minus {...props} />;
    case "arrow":
      return <ArrowRight {...props} />;
    case "text":
      return <Type {...props} />;
    case "vector":
      return <Spline {...props} />;
    case "image":
      return <ImageIcon {...props} />;
    case "frame":
      return <FrameIcon {...props} />;
    case "section":
    case "group":
      return <Folder {...props} />;
    case "slice":
      return <SliceIcon {...props} />;
  }
}
