import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { alignSelection, distributeSelection } from "@/engine/alignmentCommands";
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
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;
  const multi = layers.length >= 2;
  const distrib = layers.length >= 3;

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
      <Btn id="alignment.left" icon={<AlignStartVertical size={14} />} title="Align left" disabled={!multi} onClick={() => alignSelection("left")} />
      <Btn id="alignment.center-x" icon={<AlignCenterVertical size={14} />} title="Align center horizontal" disabled={!multi} onClick={() => alignSelection("center-x")} />
      <Btn id="alignment.right" icon={<AlignEndVertical size={14} />} title="Align right" disabled={!multi} onClick={() => alignSelection("right")} />
      <Sep />
      <Btn id="alignment.top" icon={<AlignStartHorizontal size={14} />} title="Align top" disabled={!multi} onClick={() => alignSelection("top")} />
      <Btn id="alignment.center-y" icon={<AlignCenterHorizontal size={14} />} title="Align center vertical" disabled={!multi} onClick={() => alignSelection("center-y")} />
      <Btn id="alignment.bottom" icon={<AlignEndHorizontal size={14} />} title="Align bottom" disabled={!multi} onClick={() => alignSelection("bottom")} />
      <Sep />
      <Btn id="alignment.distribute-h" icon={<StretchHorizontal size={14} />} title="Distribute horizontally" disabled={!distrib} onClick={() => distributeSelection("horizontal")} />
      <Btn id="alignment.distribute-v" icon={<StretchVertical size={14} />} title="Distribute vertically" disabled={!distrib} onClick={() => distributeSelection("vertical")} />
      <span style={{ flex: 1 }} />
      <Btn id="alignment.tidy-up" icon={<span style={{ fontSize: 11 }}>⊞</span>} title="Tidy up — not implemented" disabled visualOnly />
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
  onClick,
  visualOnly,
}: {
  id: string;
  icon: React.ReactNode;
  title: string;
  disabled?: boolean;
  onClick?: () => void;
  visualOnly?: boolean;
}) {
  return (
    <button
      data-id={id}
      title={disabled ? title + (visualOnly ? "" : " — select 2+ layers") : title}
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
