import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setTextProperty } from "@/engine/textCommands";
import { AlignLeft, AlignCenter, AlignRight, AlignJustify } from "lucide-react";
import type { Text as TextLayer } from "@/types/scene";

const FONT_FAMILIES = ["Inter", "Arial", "Helvetica", "Georgia", "Times New Roman", "Courier New", "Monaco"];
const FONT_WEIGHTS = [
  { value: 300, label: "Light" },
  { value: 400, label: "Regular" },
  { value: 500, label: "Medium" },
  { value: 600, label: "Semibold" },
  { value: 700, label: "Bold" },
];

export function TypographySection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const text = layers[0];
  if (!text || text.type !== "text") return null;
  const t = text as TextLayer;

  return (
    <Section title="Typography">
      <select
        data-id="typography.font-family"
        value={t.fontFamily}
        onChange={(e) => setTextProperty("fontFamily", e.target.value)}
        style={{
          height: 28,
          background: "var(--color-bg-input)",
          color: "var(--color-text-primary)",
          border: 0,
          borderRadius: 4,
          padding: "0 6px",
          fontSize: "var(--fs-sm)",
          width: "100%",
        }}
      >
        {FONT_FAMILIES.map((f) => (
          <option key={f} value={f} style={{ fontFamily: f }}>
            {f}
          </option>
        ))}
      </select>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 70px", gap: 6 }}>
        <select
          data-id="typography.weight"
          value={t.fontWeight}
          onChange={(e) => setTextProperty("fontWeight", parseInt(e.target.value, 10))}
          style={{
            height: 28,
            background: "var(--color-bg-input)",
            color: "var(--color-text-primary)",
            border: 0,
            borderRadius: 4,
            padding: "0 6px",
            fontSize: "var(--fs-sm)",
          }}
        >
          {FONT_WEIGHTS.map((w) => (
            <option key={w.value} value={w.value}>
              {w.label}
            </option>
          ))}
        </select>
        <NumericInput value={t.fontSize} onCommit={(v) => setTextProperty("fontSize", v)} min={1} />
      </div>
      <div style={{ display: "flex", gap: 4 }}>
        <AlignBtn id="typography.align.left" active={t.hAlign === "left"} icon={<AlignLeft size={14} />} onClick={() => setTextProperty("hAlign", "left")} title="Align left" />
        <AlignBtn id="typography.align.center" active={t.hAlign === "center"} icon={<AlignCenter size={14} />} onClick={() => setTextProperty("hAlign", "center")} title="Align center" />
        <AlignBtn id="typography.align.right" active={t.hAlign === "right"} icon={<AlignRight size={14} />} onClick={() => setTextProperty("hAlign", "right")} title="Align right" />
        <AlignBtn id="typography.align.justify" active={t.hAlign === "justify"} icon={<AlignJustify size={14} />} onClick={() => setTextProperty("hAlign", "justify")} title="Justify" />
      </div>
    </Section>
  );
}

function AlignBtn({ id, active, icon, onClick, title }: { id: string; active: boolean; icon: React.ReactNode; onClick: () => void; title: string }) {
  return (
    <button
      data-id={id}
      onClick={onClick}
      title={title}
      style={{
        width: 28,
        height: 28,
        borderRadius: 4,
        background: active ? "var(--color-bg-row-active)" : "transparent",
        color: active ? "var(--color-selection-blue)" : "var(--color-text-secondary)",
        display: "grid",
        placeItems: "center",
      }}
    >
      {icon}
    </button>
  );
}
