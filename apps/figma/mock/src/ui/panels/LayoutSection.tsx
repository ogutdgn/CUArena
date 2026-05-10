import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTransformField } from "@/engine/propertyCommands";
import { Ratio } from "lucide-react";

export function LayoutSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const locked = useStore((s) => s.aspectRatioLocked);

  function setLocked(v: boolean) {
    useStore.setState((s) => { s.aspectRatioLocked = v; });
  }

  if (layers.length === 0) return null;

  const ref = layers[0];
  const wVal: number | "Mixed" = layers.every((l) => l.w === ref.w) ? ref.w : "Mixed";
  const hVal: number | "Mixed" = layers.every((l) => l.h === ref.h) ? ref.h : "Mixed";

  function commitW(v: number) {
    setTransformField("w", v);
    if (locked && typeof wVal === "number" && typeof hVal === "number" && wVal > 0) {
      const ratio = hVal / wVal;
      setTransformField("h", Math.max(1, Math.round(v * ratio)));
    }
  }

  function commitH(v: number) {
    setTransformField("h", v);
    if (locked && typeof wVal === "number" && typeof hVal === "number" && hVal > 0) {
      const ratio = wVal / hVal;
      setTransformField("w", Math.max(1, Math.round(v * ratio)));
    }
  }

  return (
    <Section title="Layout">
      <div style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)", fontWeight: 500, marginBottom: 4 }}>
        Dimensions
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {locked ? (
          // Connected — single unified container
          <div
            style={{
              flex: 1, display: "flex", alignItems: "center",
              height: 28, background: "var(--color-bg-input)", borderRadius: 4, overflow: "hidden",
            }}
          >
            <span style={{ padding: "0 4px 0 8px", color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", fontWeight: 500, flexShrink: 0 }}>W</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <NumericInput value={wVal} onCommit={commitW} min={1} noBg />
            </div>
            <div style={{ width: 1, height: 16, background: "var(--color-border)", flexShrink: 0 }} />
            <span style={{ padding: "0 4px 0 8px", color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", fontWeight: 500, flexShrink: 0 }}>H</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <NumericInput value={hVal} onCommit={commitH} min={1} noBg />
            </div>
          </div>
        ) : (
          // Separate — two independent inputs
          <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 4, height: 28 }}>
              <span style={{ width: 14, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", fontWeight: 500 }}>W</span>
              <NumericInput value={wVal} onCommit={commitW} min={1} />
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4, height: 28 }}>
              <span style={{ width: 14, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", fontWeight: 500 }}>H</span>
              <NumericInput value={hVal} onCommit={commitH} min={1} />
            </div>
          </div>
        )}

        {/* Lock aspect ratio */}
        <button
          data-id="layout.lock-aspect-ratio"
          onClick={() => setLocked(!locked)}
          title={locked ? "Unlock aspect ratio" : "Lock aspect ratio"}
          style={{
            width: 28, height: 28, borderRadius: 5, flexShrink: 0,
            display: "grid", placeItems: "center",
            background: locked ? "var(--color-selection-blue)" : "var(--color-bg-input)",
            color: locked ? "var(--color-text-on-accent)" : "var(--color-text-secondary)",
          }}
          onMouseEnter={(e) => { if (!locked) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
          onMouseLeave={(e) => { if (!locked) e.currentTarget.style.background = "var(--color-bg-input)"; }}
        >
          <Ratio size={14} />
        </button>
      </div>
    </Section>
  );
}
