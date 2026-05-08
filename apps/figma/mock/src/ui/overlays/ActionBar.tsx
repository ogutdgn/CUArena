// Floating action bar above the selection bbox. Shows quick actions: most are
// visual-only (mask / boolean / component / use auto layout) per spec, but a
// few are wired (mark-as-component is visual-only since real component system
// is out of scope).

import { useStore, selectActiveViewport } from "@/engine/store";
import { selectionBbox, getSelectedLayers } from "@/engine/selectors";
import { groupSelection } from "@/engine/hierarchyCommands";
import { noopClick } from "@/ui/chrome/noopClick";
import { Group, Component, Box, Combine } from "lucide-react";
import { worldToClientPoint } from "@/engine/viewportCoordinates";

const HEIGHT = 32;
const GAP = 12;

export function ActionBar() {
  const viewport = useStore((s) => selectActiveViewport(s));
  const bbox = useStore((s) => selectionBbox(s));
  const layers = useStore((s) => getSelectedLayers(s));
  const dragKind = useStore((s) => s.dragPreview.kind);

  const editMode = useStore((s) => s.editMode);
  if (!bbox || layers.length === 0) return null;
  if (dragKind != null) return null;
  if (editMode.kind !== "none") return null;

  // Position above the bbox in screen coords.
  const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
  if (!svgEl) return null;
  const r = svgEl.getBoundingClientRect();
  const screenTopLeft = worldToClientPoint(bbox.x, bbox.y, viewport, r);
  const screenX = screenTopLeft.x;
  const screenY = screenTopLeft.y;
  const screenW = bbox.w * viewport.zoom;

  // If selection is too high on screen, render BELOW the bbox.
  let top = screenY - HEIGHT - GAP;
  if (top < r.top + 16) top = screenY + bbox.h * viewport.zoom + GAP;

  const left = Math.max(r.left + 16, screenX + screenW / 2 - 110);

  const multi = layers.length >= 2;

  return (
    <div
      className="no-select"
      style={{
        position: "fixed",
        left,
        top,
        height: HEIGHT,
        display: "flex",
        alignItems: "center",
        background: "var(--color-bg-toolbar)",
        border: "1px solid var(--color-border)",
        borderRadius: 8,
        boxShadow: "0 4px 14px rgba(0,0,0,0.35)",
        padding: "0 4px",
        zIndex: 60,
      }}
    >
      <ActionBtn id="action-bar.create-component" icon={<Component size={14} />} title="Create component — not implemented" disabled />
      {multi && (
        <ActionBtn
          id="action-bar.group"
          icon={<Group size={14} />}
          title="Group selection (⌘G)"
          onClick={() => groupSelection("main_menu")}
        />
      )}
      <ActionBtn id="action-bar.use-as-mask" icon={<Box size={14} />} title="Use as mask — not implemented" disabled />
      {multi && (
        <ActionBtn id="action-bar.boolean" icon={<Combine size={14} />} title="Boolean — not implemented" disabled />
      )}
      <ActionBtn id="action-bar.suggest-auto-layout" icon={<span style={{ fontSize: 11, fontWeight: 600 }}>AL</span>} title="Suggest auto layout — not implemented" disabled />
    </div>
  );
}

function ActionBtn({
  id,
  icon,
  title,
  onClick,
  disabled,
}: {
  id: string;
  icon: React.ReactNode;
  title: string;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      data-id={id}
      title={title}
      onClick={(e) => {
        if (disabled) {
          noopClick(id, e);
          return;
        }
        onClick?.();
      }}
      style={{
        width: 28,
        height: 24,
        margin: "0 2px",
        borderRadius: 4,
        color: disabled ? "var(--color-text-muted)" : "var(--color-text-secondary)",
        display: "grid",
        placeItems: "center",
      }}
      onMouseEnter={(e) => {
        if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {icon}
    </button>
  );
}
