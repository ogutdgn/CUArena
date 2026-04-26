import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTransformField } from "@/engine/propertyCommands";
import { noopClick } from "@/ui/chrome/noopClick";

export function LayoutSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;

  const ref = layers[0];
  const wVal: number | "Mixed" = layers.every((l) => l.w === ref.w) ? ref.w : "Mixed";
  const hVal: number | "Mixed" = layers.every((l) => l.h === ref.h) ? ref.h : "Mixed";

  return (
    <Section title="Layout">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        <Row label="W">
          <NumericInput value={wVal} onCommit={(v) => setTransformField("w", v)} min={1} />
        </Row>
        <Row label="H">
          <NumericInput value={hVal} onCommit={(v) => setTransformField("h", v)} min={1} />
        </Row>
      </div>
      <button
        data-id="layout.use-auto-layout"
        onClick={(e) => noopClick("layout.use-auto-layout", e)}
        title="Use auto layout — not implemented in this mock"
        style={{
          height: 28,
          borderRadius: 4,
          background: "var(--color-bg-input)",
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-sm)",
        }}
      >
        Use auto layout
      </button>
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
