import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  alignSelection,
  distributeSelection,
  getSingleSelectionAlignmentContainer,
  tidySelection,
} from "@/engine/alignmentCommands";
import { noopClick } from "@/ui/chrome/noopClick";
import {
  AlignStartVertical,
  AlignCenterVertical,
  AlignEndVertical,
  AlignStartHorizontal,
  AlignCenterHorizontal,
  AlignEndHorizontal,
  StretchHorizontal,
  StretchVertical,
} from "lucide-react";

export function AlignmentRow() {
  const state = useStore((s) => s);
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return null;

  // Align is enabled when 2+ layers are selected, OR when a single layer
  // sits inside a non-page container (frame/group/section) — in which case
  // alignment targets the container's bounds.
  const singleContainer = getSingleSelectionAlignmentContainer(state, layers);
  const canAlign = layers.length >= 2 || singleContainer !== null;
  const distrib = layers.length >= 3;
  const alignDisabledHint = layers.length >= 2
    ? undefined
    : singleContainer
    ? undefined
    : " — select 2+ layers, or one layer inside a frame/group";

  return (
    <div
      style={{
        height: 32,
        display: "flex",
        alignItems: "center",
        gap: 2,
        padding: "0 8px",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      <Btn id="alignment.left" icon={<AlignStartVertical size={14} />} title="Align left" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("left")} />
      <Btn id="alignment.center-x" icon={<AlignCenterVertical size={14} />} title="Align center horizontal" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("center-x")} />
      <Btn id="alignment.right" icon={<AlignEndVertical size={14} />} title="Align right" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("right")} />
      <Sep />
      <Btn id="alignment.top" icon={<AlignStartHorizontal size={14} />} title="Align top" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("top")} />
      <Btn id="alignment.center-y" icon={<AlignCenterHorizontal size={14} />} title="Align center vertical" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("center-y")} />
      <Btn id="alignment.bottom" icon={<AlignEndHorizontal size={14} />} title="Align bottom" disabled={!canAlign} disabledHint={alignDisabledHint} onClick={() => alignSelection("bottom")} />
      <Sep />
      <Btn id="alignment.distribute-h" icon={<StretchHorizontal size={14} />} title="Distribute horizontally" disabled={!distrib} disabledHint=" — select 3+ layers" onClick={() => distributeSelection("horizontal")} />
      <Btn id="alignment.distribute-v" icon={<StretchVertical size={14} />} title="Distribute vertically" disabled={!distrib} disabledHint=" — select 3+ layers" onClick={() => distributeSelection("vertical")} />
      <span style={{ flex: 1 }} />
      <Btn id="alignment.tidy-up" icon={<span style={{ fontSize: 11 }}>⊞</span>} title="Tidy up" disabled={layers.length < 2} disabledHint=" — select 2+ layers" onClick={() => tidySelection("panel_button")} />
    </div>
  );
}

function Sep() {
  return <span style={{ width: 1, height: 14, background: "var(--color-divider)", margin: "0 4px" }} />;
}

function Btn({
  id,
  icon,
  title,
  disabled,
  disabledHint,
  onClick,
  visualOnly,
}: {
  id: string;
  icon: React.ReactNode;
  title: string;
  disabled?: boolean;
  disabledHint?: string;
  onClick?: () => void;
  visualOnly?: boolean;
}) {
  return (
    <button
      data-id={id}
      title={disabled ? title + (visualOnly ? "" : (disabledHint ?? "")) : title}
      disabled={!!disabled}
      onClick={(e) => {
        if (visualOnly || disabled) {
          if (visualOnly) noopClick(id, e);
          return;
        }
        onClick?.();
      }}
      style={{
        width: 26,
        height: 26,
        borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-secondary)",
        display: "grid",
        placeItems: "center",
        background: "transparent",
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
