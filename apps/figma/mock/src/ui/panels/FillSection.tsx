import { useState, useEffect } from "react";
import { Section } from "./sectionShell";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { addSolidFill, removeFill, setFillColor, toggleFillVisibility } from "@/engine/propertyCommands";
import { ColorPicker, colorToHex, parseHex, swatchBackground } from "@/ui/overlays/ColorPicker";
import { OpacityScrubber } from "./OpacityScrubber";
import { Eye, EyeClosed, Minus } from "lucide-react";
import type { Paint, Color } from "@/types/scene";

export function FillSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const layer = layers[0];
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [anchor, setAnchor] = useState<{ right: number; top: number } | null>(null);
  if (!layer) return null;
  const fills: Paint[] = "fills" in layer ? (layer as { fills: Paint[] }).fills : [];
  if (!("fills" in layer)) return null;

  return (
    <Section title="Fill" addId="fill.add" onAdd={() => addSolidFill()}>
      {fills.map((p, i) => (
        <FillRow
          key={i}
          paint={p}
          index={i}
          onOpen={(rect) => {
            setOpenIndex(i);
            setAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
          }}
          onRemove={() => removeFill(i)}
          onToggle={() => toggleFillVisibility(i)}
        />
      ))}

      {openIndex != null && anchor && fills[openIndex] && fills[openIndex].kind === "solid" && (
        <ColorPicker
          value={(fills[openIndex] as Extract<Paint, { kind: "solid" }>).color}
          onChange={(c: Color) => setFillColor(openIndex, c)}
          onClose={() => setOpenIndex(null)}
          anchor={anchor}
        />
      )}
    </Section>
  );
}

function FillRow({
  paint,
  index,
  onOpen,
  onRemove,
  onToggle,
}: {
  paint: Paint;
  index: number;
  onOpen: (rect: DOMRect) => void;
  onRemove: () => void;
  onToggle: () => void;
}) {
  const isSolid = paint.kind === "solid";
  const color = isSolid ? paint.color : null;
  const hex = color ? colorToHex(color) : "";
  const opacityPct = color ? Math.round(color.a * 100) : 100;

  const [hexDraft, setHexDraft] = useState(hex);
  const [editing, setEditing] = useState(false);

  useEffect(() => { if (!editing) setHexDraft(hex); }, [hex, editing]);

  const swatchBg = color ? swatchBackground(color) : "transparent";

  function commitHex() {
    setEditing(false);
    if (!isSolid || !color) return;
    const parsed = parseHex(hexDraft);
    if (parsed) setFillColor(index, { ...parsed, a: color.a });
    else setHexDraft(hex);
  }

  function commitOpacityPct(pct: number) {
    if (!isSolid || !color) return;
    setFillColor(index, { ...color, a: pct / 100 });
  }

  return (
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
        minWidth: 0,
        overflow: "hidden",
      }}
    >
      <button
        data-id={`fill.row.${index}.swatch`}
        onClick={(e) => onOpen((e.currentTarget as HTMLElement).getBoundingClientRect())}
        title="Open color picker"
        style={{
          width: 16, height: 16, borderRadius: 3, flexShrink: 0,
          background: swatchBg,
          border: "1px solid var(--color-border)", padding: 0,
        }}
      />
      <input
        data-id={`fill.row.${index}.hex`}
        value={hexDraft}
        onChange={(e) => setHexDraft(e.target.value)}
        onFocus={(e) => { setEditing(true); requestAnimationFrame(() => e.target.select()); }}
        onBlur={commitHex}
        onKeyDown={(e) => {
          if (e.key === "Enter") (e.target as HTMLInputElement).blur();
          if (e.key === "Escape") { setHexDraft(hex); setEditing(false); (e.target as HTMLInputElement).blur(); }
        }}
        style={{
          flex: 1, minWidth: 0, background: "transparent", border: 0,
          color: "var(--color-text-primary)", fontSize: "var(--fs-sm)",
          fontFamily: "monospace", outline: 0, padding: 0, cursor: "text",
        }}
      />
      <OpacityScrubber
        value={opacityPct}
        onCommit={commitOpacityPct}
        testId={`fill.row.${index}.opacity`}
      />
      <button
        data-id={`fill.row.${index}.toggle`}
        onClick={onToggle}
        title={paint.visible ? "Hide fill" : "Show fill"}
        style={{ width: 22, height: 22, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}
      >
        {paint.visible ? <Eye size={12} /> : <EyeClosed size={12} />}
      </button>
      <button
        data-id={`fill.row.${index}.remove`}
        onClick={onRemove}
        title="Remove fill"
        style={{ width: 22, height: 22, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}
      >
        <Minus size={12} />
      </button>
    </div>
  );
}
