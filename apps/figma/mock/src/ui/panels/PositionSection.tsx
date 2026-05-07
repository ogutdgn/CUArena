import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTransformField } from "@/engine/propertyCommands";
import { flipSelection, rotate90Selection } from "@/engine/transformCommands";
import { ConstraintsControl } from "./ConstraintsControl";
import { RotateCw, FlipHorizontal2, FlipVertical2 } from "lucide-react";

export function PositionSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;

  const ref = layers[0];
  const xVal: number | "Mixed" = layers.every((l) => l.x === ref.x) ? ref.x : "Mixed";
  const yVal: number | "Mixed" = layers.every((l) => l.y === ref.y) ? ref.y : "Mixed";
  const rotVal: number | "Mixed" = layers.every((l) => l.rotation === ref.rotation) ? ref.rotation : "Mixed";

  return (
    <Section title="Position">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        <Row label="X">
          <NumericInput value={xVal} onCommit={(v) => setTransformField("x", v)} />
        </Row>
        <Row label="Y">
          <NumericInput value={yVal} onCommit={(v) => setTransformField("y", v)} />
        </Row>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
        <span style={{ width: 16, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>∠</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* setTransformField normalizes rotation to [0, 360) per item 20 spec
              — typing -1060° commits as 20°. */}
          <NumericInput value={rotVal} onCommit={(v) => setTransformField("rotation", v)} suffix="°" />
        </div>
        <IconButton
          id="position.rotate-90"
          title="Rotate 90° clockwise"
          onClick={() => rotate90Selection("panel_button")}
        >
          <RotateCw size={12} />
        </IconButton>
        <IconButton
          id="position.flip-horizontal"
          title="Flip horizontal"
          onClick={() => flipSelection("horizontal", "panel_button")}
        >
          <FlipHorizontal2 size={12} />
        </IconButton>
        <IconButton
          id="position.flip-vertical"
          title="Flip vertical"
          onClick={() => flipSelection("vertical", "panel_button")}
        >
          <FlipVertical2 size={12} />
        </IconButton>
      </div>
      <ConstraintsControl />
    </Section>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
      <span style={{ width: 16, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{label}</span>
      {children}
    </div>
  );
}

function IconButton({
  id,
  title,
  onClick,
  children,
}: {
  id: string;
  title: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      data-id={id}
      onClick={onClick}
      title={title}
      style={{
        width: 24,
        height: 24,
        borderRadius: 4,
        color: "var(--color-text-secondary)",
        display: "grid",
        placeItems: "center",
        flexShrink: 0,
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {children}
    </button>
  );
}
