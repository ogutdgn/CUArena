import { useState } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { addSolidStroke, setStrokeColor, setStrokeWeight } from "@/engine/propertyCommands";
import { ColorPicker, colorToHex } from "@/ui/overlays/ColorPicker";
import type { Stroke, Color } from "@/types/scene";

export function StrokeSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const layer = layers[0];
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [anchor, setAnchor] = useState<{ right: number; top: number } | null>(null);
  if (!layer) return null;
  if (!("strokes" in layer)) return null;
  const strokes: Stroke[] = (layer as { strokes: Stroke[] }).strokes;

  if (strokes.length === 0) {
    return (
      <Section title="Stroke" addId="stroke.add">
        <button
          onClick={() => addSolidStroke()}
          style={{
            height: 28,
            padding: "0 8px",
            background: "var(--color-bg-input)",
            color: "var(--color-text-muted)",
            fontSize: "var(--fs-sm)",
            borderRadius: 4,
            textAlign: "left",
          }}
        >
          + Add stroke
        </button>
      </Section>
    );
  }

  const sk = strokes[0];
  const swatchCss =
    sk.paint.kind === "solid"
      ? `rgba(${Math.round(sk.paint.color.r * 255)}, ${Math.round(sk.paint.color.g * 255)}, ${Math.round(sk.paint.color.b * 255)}, ${sk.paint.color.a})`
      : "transparent";
  const hex = sk.paint.kind === "solid" ? colorToHex(sk.paint.color) : "Image";

  return (
    <Section title="Stroke" addId="stroke.add">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          height: 28,
          padding: "0 6px",
          background: "var(--color-bg-input)",
          borderRadius: 4,
          color: "var(--color-text-primary)",
          fontSize: "var(--fs-sm)",
        }}
      >
        <button
          data-id="stroke.row.0.swatch"
          onClick={(e) => {
            const rect = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect();
            setOpenIndex(0);
            setAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          title="Open color picker"
          style={{
            width: 16,
            height: 16,
            borderRadius: 3,
            background: `${swatchCss}, repeating-conic-gradient(#666 0% 25%, #999 0% 50%) 50% / 4px 4px`,
            border: "1px solid var(--color-border)",
            padding: 0,
          }}
        />
        <span style={{ flex: 1 }}>{hex}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ flex: 1, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>Weight</span>
        <NumericInput value={sk.weight} onCommit={(v) => setStrokeWeight(v)} min={0} width={80} />
      </div>
      {openIndex != null && anchor && sk.paint.kind === "solid" && (
        <ColorPicker
          value={sk.paint.color}
          onChange={(c: Color) => setStrokeColor(openIndex, c)}
          onClose={() => setOpenIndex(null)}
          anchor={anchor}
        />
      )}
    </Section>
  );
}
