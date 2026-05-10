import { useState, useEffect } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  addSolidStroke, removeStroke, toggleStrokeVisibility,
  setStrokeColor, setStrokeWeight,
} from "@/engine/propertyCommands";
import { ColorPicker, colorToHex, parseHex, swatchBackground } from "@/ui/overlays/ColorPicker";
import { OpacityScrubber } from "./OpacityScrubber";
import { Eye, EyeClosed, Minus } from "lucide-react";
import type { Stroke, Color } from "@/types/scene";

export function StrokeSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const layer = layers[0];
  const [openPickerIndex, setOpenPickerIndex] = useState<number | null>(null);
  const [pickerAnchor, setPickerAnchor] = useState<{ right: number; top: number } | null>(null);

  if (!layer || !("strokes" in layer)) return null;
  const strokes: Stroke[] = (layer as { strokes: Stroke[] }).strokes;

  return (
    <Section title="Stroke" onAdd={() => addSolidStroke()}>
      {strokes.map((sk, i) => (
        <StrokeRow
          key={i}
          stroke={sk}
          index={i}
          onOpenPicker={(rect) => {
            setOpenPickerIndex(i);
            setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          onRemove={() => removeStroke(i)}
          onToggle={() => toggleStrokeVisibility(i)}
        />
      ))}
      {openPickerIndex != null && pickerAnchor && strokes[openPickerIndex]?.paint.kind === "solid" && (
        <ColorPicker
          value={(strokes[openPickerIndex].paint as Extract<Stroke["paint"], { kind: "solid" }>).color}
          onChange={(c: Color) => setStrokeColor(openPickerIndex, c)}
          onClose={() => setOpenPickerIndex(null)}
          anchor={pickerAnchor}
        />
      )}
      {strokes.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ flex: 1, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>Weight</span>
          <NumericInput
            value={strokes[0].weight}
            onCommit={(v) => setStrokeWeight(v)}
            min={0}
            width={80}
          />
        </div>
      )}
    </Section>
  );
}

function StrokeRow({
  stroke, index, onOpenPicker, onRemove, onToggle,
}: {
  stroke: Stroke;
  index: number;
  onOpenPicker: (rect: DOMRect) => void;
  onRemove: () => void;
  onToggle: () => void;
}) {
  const isSolid = stroke.paint.kind === "solid";
  const color = isSolid ? (stroke.paint as Extract<Stroke["paint"], { kind: "solid" }>).color : null;
  const hex = color ? colorToHex(color) : "";
  const opacityPct = color ? Math.round(color.a * 100) : 100;
  const swatchBg = color ? swatchBackground(color) : "transparent";

  const [hexDraft, setHexDraft] = useState(hex);
  const [editing, setEditing] = useState(false);

  useEffect(() => { if (!editing) setHexDraft(hex); }, [hex, editing]);

  function commitHex() {
    setEditing(false);
    if (!isSolid || !color) return;
    const parsed = parseHex(hexDraft);
    if (parsed) setStrokeColor(index, { ...parsed, a: color.a });
    else setHexDraft(hex);
  }

  function commitOpacityPct(pct: number) {
    if (!isSolid || !color) return;
    setStrokeColor(index, { ...color, a: pct / 100 });
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28, padding: "0 6px", background: "var(--color-bg-input)", borderRadius: 4, fontSize: "var(--fs-sm)", minWidth: 0, overflow: "hidden" }}>
      <button
        onClick={(e) => onOpenPicker((e.currentTarget as HTMLElement).getBoundingClientRect())}
        style={{ width: 16, height: 16, borderRadius: 3, flexShrink: 0, background: swatchBg, border: "1px solid var(--color-border)", padding: 0 }}
      />
      <input
        value={hexDraft}
        onChange={(e) => setHexDraft(e.target.value)}
        onFocus={(e) => { setEditing(true); requestAnimationFrame(() => e.target.select()); }}
        onBlur={commitHex}
        onKeyDown={(e) => {
          if (e.key === "Enter") (e.target as HTMLInputElement).blur();
          if (e.key === "Escape") { setHexDraft(hex); setEditing(false); (e.target as HTMLInputElement).blur(); }
        }}
        style={{ flex: 1, minWidth: 0, background: "transparent", border: 0, color: "var(--color-text-primary)", fontSize: "var(--fs-sm)", fontFamily: "monospace", outline: 0, padding: 0, cursor: "text" }}
      />
      <OpacityScrubber value={opacityPct} onCommit={commitOpacityPct} />
      <button onClick={onToggle} title={stroke.paint.visible ? "Hide" : "Show"} style={{ width: 20, height: 20, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}>
        {stroke.paint.visible ? <Eye size={12} /> : <EyeClosed size={12} />}
      </button>
      <button onClick={onRemove} title="Remove" style={{ width: 20, height: 20, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}>
        <Minus size={12} />
      </button>
    </div>
  );
}
