import { useState } from "react";
import { Section } from "./sectionShell";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { addSolidFill, removeFill, setFillColor, toggleFillVisibility } from "@/engine/propertyCommands";
import { ColorPicker, colorToHex } from "@/ui/overlays/ColorPicker";
import { Eye, EyeOff, Minus } from "lucide-react";
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
    <Section title="Fill" addId="fill.add">
      {fills.length === 0 ? (
        <button
          onClick={() => addSolidFill()}
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
          + Add solid fill
        </button>
      ) : (
        fills.map((p, i) => (
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
        ))
      )}

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
  const swatchCss =
    paint.kind === "solid"
      ? `rgba(${Math.round(paint.color.r * 255)}, ${Math.round(paint.color.g * 255)}, ${Math.round(paint.color.b * 255)}, ${paint.color.a})`
      : "transparent";
  const hex = paint.kind === "solid" ? colorToHex(paint.color) : "Image";
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
      }}
    >
      <button
        data-id={`fill.row.${index}.swatch`}
        onClick={(e) => {
          const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
          onOpen(rect);
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
      <button
        data-id={`fill.row.${index}.hex`}
        onClick={(e) => {
          const rect = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect();
          onOpen(rect);
        }}
        style={{ flex: 1, textAlign: "left", color: "inherit", padding: 0 }}
      >
        {hex}
      </button>
      <button
        data-id={`fill.row.${index}.toggle`}
        onClick={onToggle}
        title={paint.visible ? "Hide fill" : "Show fill"}
        style={{ width: 22, height: 22, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
      >
        {paint.visible ? <Eye size={12} /> : <EyeOff size={12} />}
      </button>
      <button
        data-id={`fill.row.${index}.remove`}
        onClick={onRemove}
        title="Remove fill"
        style={{ width: 22, height: 22, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
      >
        <Minus size={12} />
      </button>
    </div>
  );
}
