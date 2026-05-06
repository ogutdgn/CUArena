import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setOpacity, setVisibility, setLocked, setCornerRadius } from "@/engine/propertyCommands";
import { noopClick } from "@/ui/chrome/noopClick";
import { Eye, EyeOff, Lock, Unlock } from "lucide-react";

export function AppearanceSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;
  const ref = layers[0];
  const opacityPct: number | "Mixed" = layers.every((l) => l.opacity === ref.opacity) ? Math.round(ref.opacity * 100) : "Mixed";
  const allVisible = layers.every((l) => l.visible);
  const allLocked = layers.every((l) => l.locked);

  // Corner radius — only applicable on shapes with cornerRadius field
  const hasCorner = "cornerRadius" in ref;
  const crVal: number | "Mixed" | null = !hasCorner
    ? null
    : (() => {
        const allMatch = layers.every((l) => "cornerRadius" in l && (l as { cornerRadius: number | [number, number, number, number] }).cornerRadius === (ref as { cornerRadius: number | [number, number, number, number] }).cornerRadius);
        const cr = (ref as { cornerRadius: number | [number, number, number, number] }).cornerRadius;
        if (!allMatch) return "Mixed" as const;
        return typeof cr === "number" ? cr : "Mixed";
      })();

  return (
    <Section title="Appearance">
      <Row label="O">
        <NumericInput value={opacityPct} onCommit={(v) => setOpacity(v)} min={0} max={100} suffix="%" />
      </Row>
      {hasCorner && crVal != null && (
        <Row label="⌐">
          <NumericInput value={crVal} onCommit={(v) => setCornerRadius(v)} min={0} />
        </Row>
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <button
          data-id="appearance.blend-mode"
          onClick={(e) => noopClick("appearance.blend-mode", e)}
          title="Blend mode — not implemented"
          style={{
            flex: 1,
            height: 28,
            padding: "0 8px",
            background: "var(--color-bg-input)",
            color: "var(--color-text-secondary)",
            fontSize: "var(--fs-sm)",
            borderRadius: 4,
            textAlign: "left",
          }}
        >
          Pass through
        </button>
        <button
          data-id="appearance.visibility"
          onClick={() => setVisibility(!allVisible)}
          title={allVisible ? "Hide layer (Shift+Cmd+H)" : "Show layer"}
          style={{
            width: 24,
            height: 24,
            borderRadius: 4,
            color: allVisible ? "var(--color-text-secondary)" : "var(--color-text-muted)",
            display: "grid",
            placeItems: "center",
          }}
        >
          {allVisible ? <Eye size={14} /> : <EyeOff size={14} />}
        </button>
        <button
          data-id="appearance.locked"
          onClick={() => setLocked(!allLocked)}
          title={allLocked ? "Unlock" : "Lock"}
          style={{
            width: 24,
            height: 24,
            borderRadius: 4,
            color: allLocked ? "var(--color-selection-blue)" : "var(--color-text-secondary)",
            display: "grid",
            placeItems: "center",
          }}
        >
          {allLocked ? <Lock size={14} /> : <Unlock size={14} />}
        </button>
      </div>
    </Section>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
      <span style={{ width: 16, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", display: "flex", alignItems: "center", justifyContent: "center" }}>{label}</span>
      {children}
    </div>
  );
}
