// Bottom-center floating toolbar. Source: ui-report.md §2.1.

import { useEffect, useRef, useState } from "react";
import {
  MousePointer2,
  Hand,
  Frame,
  Square,
  Pen,
  Type,
  MessageSquare,
  Sparkles,
  ChevronUp,
  Code2,
  Brush,
  Ruler,
  ChevronDown,
  Circle,
  Hexagon,
  Star,
  Minus,
  ArrowRight,
  Image as ImageIcon,
  Pencil,
  LayoutTemplate,
  Crop,
  Maximize2,
  MessageCircle,
} from "lucide-react";
import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { noopClick } from "./noopClick";
import { ToolbarDropdown, type DropdownItem } from "./ToolbarDropdown";
import type { ToolId } from "@/types/ops";

type DropdownKey = "move-tools" | "region-tools" | "shape-tools" | "creation-tools" | "comment-tools" | null;

export function Toolbar() {
  const activeTool = useStore((s) => s.activeTool);
  const [openDropdown, setOpenDropdown] = useState<DropdownKey>(null);
  const [lastShapeTool, setLastShapeTool] = useState<ToolId>("rectangle");
  const [lastRegionTool, setLastRegionTool] = useState<ToolId>("frame");
  const [lastCreationTool, setLastCreationTool] = useState<ToolId>("pen");
  const moveBtnRef = useRef<HTMLDivElement | null>(null);
  const regionBtnRef = useRef<HTMLDivElement | null>(null);
  const shapeBtnRef = useRef<HTMLDivElement | null>(null);
  const createBtnRef = useRef<HTMLDivElement | null>(null);
  const commentBtnRef = useRef<HTMLDivElement | null>(null);

  const setToolFromClick = (after: ToolId, trigger: "shortcut" | "toolbar_click" = "toolbar_click") => {
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
  };

  useEffect(() => {
    if (
      activeTool === "rectangle" ||
      activeTool === "line" ||
      activeTool === "arrow" ||
      activeTool === "ellipse" ||
      activeTool === "polygon" ||
      activeTool === "star"
    ) {
      setLastShapeTool(activeTool);
    }
    if (activeTool === "frame" || activeTool === "section" || activeTool === "slice") {
      setLastRegionTool(activeTool);
    }
    if (activeTool === "pen" || activeTool === "pencil") {
      setLastCreationTool(activeTool);
    }
  }, [activeTool]);

  const moveItems: DropdownItem[] = [
    { id: "toolbar.move-tools.move", label: "Move", shortcut: "V", icon: <MousePointer2 size={14} />, onClick: () => setToolFromClick("move") },
    { id: "toolbar.move-tools.hand", label: "Hand tool", shortcut: "H", icon: <Hand size={14} />, onClick: () => setToolFromClick("hand") },
    { id: "toolbar.move-tools.scale", label: "Scale", shortcut: "K", icon: <Maximize2 size={14} />, onClick: () => setToolFromClick("scale") },
  ];

  const regionItems: DropdownItem[] = [
    { id: "toolbar.region-tools.frame", label: "Frame", shortcut: "F", icon: <Frame size={14} />, onClick: () => setToolFromClick("frame") },
    { id: "toolbar.region-tools.section", label: "Section", shortcut: "Shift+S", icon: <LayoutTemplate size={14} />, onClick: () => setToolFromClick("section") },
    { id: "toolbar.region-tools.slice", label: "Slice", icon: <Crop size={14} />, onClick: () => setToolFromClick("slice") },
  ];

  const shapeItems: DropdownItem[] = [
    { id: "toolbar.shape-tools.rectangle", label: "Rectangle", shortcut: "R", icon: <Square size={14} />, onClick: () => setToolFromClick("rectangle") },
    { id: "toolbar.shape-tools.line", label: "Line", shortcut: "L", icon: <Minus size={14} />, onClick: () => setToolFromClick("line") },
    { id: "toolbar.shape-tools.arrow", label: "Arrow", shortcut: "Shift+L", icon: <ArrowRight size={14} />, onClick: () => setToolFromClick("arrow") },
    { id: "toolbar.shape-tools.ellipse", label: "Ellipse", shortcut: "O", icon: <Circle size={14} />, onClick: () => setToolFromClick("ellipse") },
    { id: "toolbar.shape-tools.polygon", label: "Polygon", icon: <Hexagon size={14} />, onClick: () => setToolFromClick("polygon") },
    { id: "toolbar.shape-tools.star", label: "Star", icon: <Star size={14} />, onClick: () => setToolFromClick("star") },
    { id: "toolbar.shape-tools.image", label: "Place image / video", shortcut: "Shift+Cmd+K", icon: <ImageIcon size={14} />, disabled: true, onClick: () => noopClick("toolbar.shape-tools.image") },
  ];

  const creationItems: DropdownItem[] = [
    { id: "toolbar.creation-tools.pen", label: "Pen", shortcut: "P", icon: <Pen size={14} />, onClick: () => setToolFromClick("pen") },
    { id: "toolbar.creation-tools.pencil", label: "Pencil", shortcut: "⇧P", icon: <Pencil size={14} />, onClick: () => setToolFromClick("pencil") },
  ];

  const commentItems: DropdownItem[] = [
    { id: "toolbar.comment-tools-dropdown.comment", label: "Comment", shortcut: "C", icon: <MessageCircle size={14} />, disabled: true, onClick: () => noopClick("toolbar.comment-tools-dropdown.comment") },
    { id: "toolbar.comment-tools-dropdown.annotation", label: "Annotation", icon: <MessageSquare size={14} />, disabled: true, onClick: () => noopClick("toolbar.comment-tools-dropdown.annotation") },
    { id: "toolbar.comment-tools-dropdown.measurement", label: "Measurement", icon: <Ruler size={14} />, disabled: true, onClick: () => noopClick("toolbar.comment-tools-dropdown.measurement") },
  ];

  const moveActive = activeTool === "move" || activeTool === "hand" || activeTool === "scale";
  const regionActive = activeTool === "frame" || activeTool === "section" || activeTool === "slice";
  const shapeActive =
    activeTool === "rectangle" ||
    activeTool === "ellipse" ||
    activeTool === "polygon" ||
    activeTool === "star" ||
    activeTool === "line" ||
    activeTool === "arrow" ||
    activeTool === "image_place";
  const creationActive = activeTool === "pen" || activeTool === "pencil";

  const moveIcon =
    activeTool === "hand" ? <Hand size={16} /> : activeTool === "scale" ? <Maximize2 size={16} /> : <MousePointer2 size={16} />;
  const regionToolForIcon = regionActive ? activeTool : lastRegionTool;
  const shapeToolForIcon = shapeActive ? activeTool : lastShapeTool;
  const creationToolForIcon = creationActive ? activeTool : lastCreationTool;
  const regionIcon =
    regionToolForIcon === "section"
      ? <LayoutTemplate size={16} />
      : regionToolForIcon === "slice"
      ? <Crop size={16} />
      : <Frame size={16} />;
  const shapeIcon =
    shapeToolForIcon === "ellipse"
      ? <Circle size={16} />
      : shapeToolForIcon === "polygon"
      ? <Hexagon size={16} />
      : shapeToolForIcon === "star"
      ? <Star size={16} />
      : shapeToolForIcon === "line"
      ? <Minus size={16} />
      : shapeToolForIcon === "arrow"
      ? <ArrowRight size={16} />
      : <Square size={16} />;
  const creationIcon = creationToolForIcon === "pencil" ? <Pencil size={16} /> : <Pen size={16} />;

  function dropdownAnchor(ref: React.RefObject<HTMLDivElement | null>) {
    if (!ref.current) return null;
    const r = ref.current.getBoundingClientRect();
    return { left: r.left, bottom: window.innerHeight - r.top + 6 };
  }

  return (
    <>
      <div
        data-id="toolbar"
        className="no-select"
        style={{
          position: "absolute",
          bottom: 16,
          left: "50%",
          transform: "translateX(-50%)",
          height: 40,
          display: "flex",
          alignItems: "center",
          gap: 2,
          padding: "0 6px",
          background: "var(--color-bg-toolbar)",
          border: "1px solid var(--color-border)",
          borderRadius: 12,
          boxShadow: "0 6px 20px rgba(0,0,0,0.36)",
          color: "var(--color-text-primary)",
          zIndex: 20,
        }}
      >
        <ToolGroup
          groupRef={moveBtnRef}
          icon={moveIcon}
          active={moveActive}
          onIconClick={() => setToolFromClick("move")}
          onChevronClick={() => setOpenDropdown(openDropdown === "move-tools" ? null : "move-tools")}
          title="Move tools"
          open={openDropdown === "move-tools"}
        />
        <Divider />
        <ToolGroup
          groupRef={regionBtnRef}
          icon={regionIcon}
          active={regionActive}
          onIconClick={() => setToolFromClick(lastRegionTool)}
          onChevronClick={() => setOpenDropdown(openDropdown === "region-tools" ? null : "region-tools")}
          title="Region tools"
          open={openDropdown === "region-tools"}
        />
        <ToolGroup
          groupRef={shapeBtnRef}
          icon={shapeIcon}
          active={shapeActive}
          onIconClick={() => setToolFromClick(lastShapeTool)}
          onChevronClick={() => setOpenDropdown(openDropdown === "shape-tools" ? null : "shape-tools")}
          title="Shape tools"
          open={openDropdown === "shape-tools"}
        />
        <ToolGroup
          groupRef={createBtnRef}
          icon={creationIcon}
          active={creationActive}
          onIconClick={() => setToolFromClick(lastCreationTool)}
          onChevronClick={() => setOpenDropdown(openDropdown === "creation-tools" ? null : "creation-tools")}
          title="Pen / Pencil"
          open={openDropdown === "creation-tools"}
        />
        <ToolButton
          id="toolbar.text"
          icon={<Type size={16} />}
          active={activeTool === "text"}
          onClick={() => setToolFromClick("text")}
          title="Text (T)"
        />
        <Divider />
        <ToolGroup
          groupRef={commentBtnRef}
          icon={<MessageSquare size={16} />}
          active={false}
          onIconClick={(e) => noopClick("toolbar.comment-tools-dropdown.open", e)}
          onChevronClick={() => setOpenDropdown(openDropdown === "comment-tools" ? null : "comment-tools")}
          title="Comments — not implemented"
          dim
          open={openDropdown === "comment-tools"}
        />
        <ToolButton
          id="toolbar.actions-menu.open"
          icon={<Sparkles size={16} />}
          active={false}
          onClick={(e) => noopClick("toolbar.actions-menu.open", e)}
          title="Actions menu — not implemented"
          dim
        />
        <ToolButton
          id="toolbar.expand"
          icon={<ChevronUp size={14} />}
          active={false}
          onClick={(e) => noopClick("toolbar.expand", e)}
          title="More — not implemented"
          dim
        />
        <Divider />
        <ModeSwitcher />
      </div>

      {openDropdown === "move-tools" &&
        renderDropdown(moveItems, () => setOpenDropdown(null), dropdownAnchor(moveBtnRef))}
      {openDropdown === "region-tools" &&
        renderDropdown(regionItems, () => setOpenDropdown(null), dropdownAnchor(regionBtnRef))}
      {openDropdown === "shape-tools" &&
        renderDropdown(shapeItems, () => setOpenDropdown(null), dropdownAnchor(shapeBtnRef))}
      {openDropdown === "creation-tools" &&
        renderDropdown(creationItems, () => setOpenDropdown(null), dropdownAnchor(createBtnRef))}
      {openDropdown === "comment-tools" &&
        renderDropdown(commentItems, () => setOpenDropdown(null), dropdownAnchor(commentBtnRef))}
    </>
  );
}

function renderDropdown(items: DropdownItem[], onClose: () => void, anchor: { left: number; bottom: number } | null) {
  if (!anchor) return null;
  return <ToolbarDropdown items={items} onClose={onClose} anchor={anchor} />;
}

const ToolGroup = ({
  icon,
  active,
  onIconClick,
  onChevronClick,
  title,
  dim,
  groupRef,
  open,
}: {
  icon: React.ReactNode;
  active: boolean;
  onIconClick: (e: React.MouseEvent) => void;
  onChevronClick: () => void;
  title: string;
  dim?: boolean;
  groupRef?: React.RefObject<HTMLDivElement | null>;
  open?: boolean;
}) => (
  <div
    ref={groupRef as React.LegacyRef<HTMLDivElement>}
    style={{
      display: "flex",
      alignItems: "center",
      borderRadius: 8,
      background: active ? "var(--color-selection-blue)" : "transparent",
      color: active ? "var(--color-text-on-accent)" : dim ? "var(--color-text-muted)" : "var(--color-text-primary)",
      transition: "background 80ms ease",
    }}
  >
    <button
      title={title}
      onClick={onIconClick}
      style={{
        width: 30,
        height: 32,
        display: "grid",
        placeItems: "center",
        color: "inherit",
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.parentElement!.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.parentElement!.style.background = "transparent";
      }}
    >
      {icon}
    </button>
    <button
      title={`${title} options`}
      onClick={onChevronClick}
      style={{
        width: 14,
        height: 32,
        display: "grid",
        placeItems: "center",
        color: "inherit",
        opacity: 0.7,
        transition: "transform 100ms ease",
        transform: open ? "rotate(180deg)" : undefined,
      }}
    >
      <ChevronDown size={10} />
    </button>
  </div>
);

function ToolButton({
  id,
  icon,
  active,
  onClick,
  title,
  dim,
}: {
  id: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: (e: React.MouseEvent) => void;
  title: string;
  dim?: boolean;
}) {
  return (
    <button
      data-id={id}
      title={title}
      onClick={onClick}
      style={{
        width: 32,
        height: 32,
        borderRadius: 8,
        display: "grid",
        placeItems: "center",
        background: active ? "var(--color-selection-blue)" : "transparent",
        color: active ? "var(--color-text-on-accent)" : dim ? "var(--color-text-muted)" : "var(--color-text-primary)",
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.background = "transparent";
      }}
    >
      {icon}
    </button>
  );
}

function Divider() {
  return <span style={{ width: 1, height: 16, background: "var(--color-border)", margin: "0 2px" }} />;
}

function ModeSwitcher() {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        background: "var(--color-bg-toolbar-pill)",
        borderRadius: 8,
        padding: 2,
        gap: 2,
      }}
    >
      <Segment
        id="toolbar.mode-switcher.draw"
        icon={<Brush size={14} />}
        active={false}
        title="Figma Draw — not implemented in this mock"
        visualOnly
      />
      <Segment id="toolbar.mode-switcher.design" icon={<Ruler size={14} />} active title="Design" />
      <Segment
        id="toolbar.mode-switcher.dev"
        icon={<Code2 size={14} />}
        active={false}
        title="Dev Mode — not implemented in this mock"
        visualOnly
      />
    </div>
  );
}

function Segment({
  id,
  icon,
  active,
  title,
  visualOnly,
}: {
  id: string;
  icon: React.ReactNode;
  active: boolean;
  title: string;
  visualOnly?: boolean;
}) {
  return (
    <button
      data-id={id}
      title={title}
      onClick={(e) => {
        if (visualOnly) noopClick(id, e);
      }}
      style={{
        width: 28,
        height: 24,
        borderRadius: 6,
        display: "grid",
        placeItems: "center",
        background: active ? "var(--color-bg-panel-elevated)" : "transparent",
        color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
      }}
    >
      {icon}
    </button>
  );
}
