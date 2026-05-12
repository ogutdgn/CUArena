import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { applyPanelFrameContainmentForSelection, nudgeTransformField, setTransformField } from "@/engine/propertyCommands";
import { commitTransaction, openTransaction } from "@/engine/dispatch";
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

  function commitTransformScrub(transactionId: string) {
    applyPanelFrameContainmentForSelection(transactionId);
    commitTransaction(transactionId);
  }

  function commitW(v: number, context?: { transactionId?: string; scrubDelta?: number }) {
    const opts = { ...context, deferFrameContainment: !!context?.transactionId };
    if (wVal === "Mixed" && typeof context?.scrubDelta === "number") {
      nudgeTransformField("w", context.scrubDelta, opts);
    } else {
      setTransformField("w", v, opts);
    }
    if (locked && typeof wVal === "number" && typeof hVal === "number" && wVal > 0) {
      const ratio = hVal / wVal;
      setTransformField("h", Math.max(1, Math.round(v * ratio)), opts);
    }
  }

  function commitH(v: number, context?: { transactionId?: string; scrubDelta?: number }) {
    const opts = { ...context, deferFrameContainment: !!context?.transactionId };
    if (hVal === "Mixed" && typeof context?.scrubDelta === "number") {
      nudgeTransformField("h", context.scrubDelta, opts);
    } else {
      setTransformField("h", v, opts);
    }
    if (locked && typeof wVal === "number" && typeof hVal === "number" && hVal > 0) {
      const ratio = wVal / hVal;
      setTransformField("w", Math.max(1, Math.round(v * ratio)), opts);
    }
  }

  return (
    <Section title="Layout">
      <div style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)", fontWeight: 500, marginBottom: 4 }}>
        Dimensions
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {locked ? (
          // Connected — single unified container; W/H glyphs live inside each
          // NumericInput so they double as drag-scrub handles (same pattern as
          // opacity / corner-radius in AppearanceSection).
          <div
            style={{
              flex: 1, display: "flex", alignItems: "center",
              height: 28, background: "var(--color-bg-input)", borderRadius: 4, overflow: "hidden",
            }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <NumericInput prefix={<DimGlyph>W</DimGlyph>} value={wVal} scrubBaseValue={wVal === "Mixed" ? 0 : undefined} onCommit={commitW} min={1} noBg onScrubStart={openTransaction} onScrubEnd={commitTransformScrub} />
            </div>
            <div style={{ width: 1, height: 16, background: "var(--color-border)", flexShrink: 0 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <NumericInput prefix={<DimGlyph>H</DimGlyph>} value={hVal} scrubBaseValue={hVal === "Mixed" ? 0 : undefined} onCommit={commitH} min={1} noBg onScrubStart={openTransaction} onScrubEnd={commitTransformScrub} />
            </div>
          </div>
        ) : (
          // Separate — two independent inputs
          <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            <NumericInput prefix={<DimGlyph>W</DimGlyph>} value={wVal} scrubBaseValue={wVal === "Mixed" ? 0 : undefined} onCommit={commitW} min={1} onScrubStart={openTransaction} onScrubEnd={commitTransformScrub} />
            <NumericInput prefix={<DimGlyph>H</DimGlyph>} value={hVal} scrubBaseValue={hVal === "Mixed" ? 0 : undefined} onCommit={commitH} min={1} onScrubStart={openTransaction} onScrubEnd={commitTransformScrub} />
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

function DimGlyph({ children }: { children: React.ReactNode }) {
  return <span style={{ fontWeight: 500 }}>{children}</span>;
}
