import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTransformField } from "@/engine/propertyCommands";
import { noopClick } from "@/ui/chrome/noopClick";
import { FramePresetBrowser } from "./FramePresetBrowser";
import { applyFramePresetToSelection } from "@/engine/framePresetCommands";
import { findFramePresetBySize } from "@/util/framePresets";

export function LayoutSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const [presetOpen, setPresetOpen] = useState(false);
  const presetRef = useRef<HTMLDivElement | null>(null);
  if (layers.length === 0) return null;

  const ref = layers[0];
  const wVal: number | "Mixed" = layers.every((l) => l.w === ref.w) ? ref.w : "Mixed";
  const hVal: number | "Mixed" = layers.every((l) => l.h === ref.h) ? ref.h : "Mixed";
  const singleFrame = layers.length === 1 && layers[0].type === "frame";
  const matchedPreset = singleFrame ? findFramePresetBySize(layers[0].w, layers[0].h) : null;

  useEffect(() => {
    if (!presetOpen) return;
    function onDoc(e: MouseEvent) {
      if (!presetRef.current?.contains(e.target as Node)) setPresetOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [presetOpen]);

  return (
    <Section title="Layout">
      {singleFrame && (
        <div ref={presetRef} style={{ position: "relative" }}>
          <button
            data-id="layout.frame-preset.open"
            onClick={() => setPresetOpen((v) => !v)}
            style={{
              width: "100%",
              height: 28,
              borderRadius: 4,
              background: "var(--color-bg-input)",
              color: "var(--color-text-primary)",
              display: "flex",
              alignItems: "center",
              padding: "0 8px",
              fontSize: "var(--fs-sm)",
              gap: 6,
            }}
          >
            <span style={{ width: 44, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>Frame</span>
            <span style={{ flex: 1, textAlign: "left", minWidth: 0 }}>
              {matchedPreset ? matchedPreset.label : "Custom"}
            </span>
            <span style={{ color: "var(--color-text-muted)", fontVariantNumeric: "tabular-nums", flexShrink: 0 }}>
              {layers[0].w}x{layers[0].h}
            </span>
            <ChevronDown size={11} style={{ color: "var(--color-text-secondary)" }} />
          </button>
          {presetOpen && (
            <div
              style={{
                position: "absolute",
                top: 32,
                left: 0,
                right: 0,
                background: "var(--color-bg-panel-elevated)",
                border: "1px solid var(--color-border-strong)",
                borderRadius: 6,
                boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
                zIndex: 240,
              }}
            >
              <FramePresetBrowser
                variant="menu"
                onPick={(preset) => {
                  applyFramePresetToSelection(preset);
                  setPresetOpen(false);
                }}
              />
            </div>
          )}
        </div>
      )}
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
