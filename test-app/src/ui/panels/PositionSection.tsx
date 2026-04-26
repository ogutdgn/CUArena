import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTransformField } from "@/engine/propertyCommands";
import { ConstraintsControl } from "./ConstraintsControl";

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
      <Row label="∠">
        <NumericInput value={rotVal} onCommit={(v) => setTransformField("rotation", v)} suffix="°" />
      </Row>
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
