import { useState } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  addDropShadowEffect,
  addLayerBlurEffect,
  removeEffect,
  toggleEffectVisibility,
  setEffectField,
  setEffectColor,
} from "@/engine/propertyCommands";
import { ColorPicker, colorToHex } from "@/ui/overlays/ColorPicker";
import { noopClick } from "@/ui/chrome/noopClick";
import { Eye, EyeOff, Minus, Plus, Sun, CircleDashed } from "lucide-react";
import type { Effect, Color } from "@/types/scene";

export function EffectsSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const layer = layers[0];
  const [pickerIndex, setPickerIndex] = useState<number | null>(null);
  const [pickerAnchor, setPickerAnchor] = useState<{ right: number; top: number } | null>(null);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [addMenuAnchor, setAddMenuAnchor] = useState<{ right: number; top: number } | null>(null);

  if (!layer) return null;
  if (!("effects" in layer)) return null;
  const effects = (layer as { effects: Effect[] }).effects;

  return (
    <Section title="Effects" addId="effects.add">
      {effects.length === 0 ? (
        <button
          onClick={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            setAddMenuAnchor({ right: window.innerWidth - rect.right, top: rect.bottom + 4 });
            setShowAddMenu(true);
          }}
          style={{
            height: 28,
            padding: "0 8px",
            background: "var(--color-bg-input)",
            color: "var(--color-text-muted)",
            fontSize: "var(--fs-sm)",
            borderRadius: 4,
            textAlign: "left",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <Plus size={12} /> Add effect
        </button>
      ) : (
        effects.map((eff, i) => (
          <EffectRow
            key={i}
            effect={eff}
            index={i}
            onPickerOpen={(rect) => {
              setPickerIndex(i);
              setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
            }}
            onRemove={() => removeEffect(i)}
            onToggle={() => toggleEffectVisibility(i)}
          />
        ))
      )}

      {effects.length > 0 && (
        <button
          onClick={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            setAddMenuAnchor({ right: window.innerWidth - rect.right, top: rect.bottom + 4 });
            setShowAddMenu(true);
          }}
          style={{
            height: 24,
            padding: "0 6px",
            background: "transparent",
            color: "var(--color-text-secondary)",
            fontSize: "var(--fs-xs)",
            borderRadius: 4,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <Plus size={11} /> Add another
        </button>
      )}

      {showAddMenu && addMenuAnchor && (
        <AddEffectMenu
          anchor={addMenuAnchor}
          onClose={() => setShowAddMenu(false)}
          onPickShadow={() => {
            addDropShadowEffect();
            setShowAddMenu(false);
          }}
          onPickBlur={() => {
            addLayerBlurEffect();
            setShowAddMenu(false);
          }}
        />
      )}

      {pickerIndex != null && pickerAnchor && effects[pickerIndex] && effects[pickerIndex].kind === "drop_shadow" && (
        <ColorPicker
          value={(effects[pickerIndex] as Extract<Effect, { kind: "drop_shadow" }>).color}
          onChange={(c: Color) => setEffectColor(pickerIndex, c)}
          onClose={() => setPickerIndex(null)}
          anchor={pickerAnchor}
        />
      )}
    </Section>
  );
}

function EffectRow({
  effect,
  index,
  onPickerOpen,
  onRemove,
  onToggle,
}: {
  effect: Effect;
  index: number;
  onPickerOpen: (rect: DOMRect) => void;
  onRemove: () => void;
  onToggle: () => void;
}) {
  if (effect.kind === "drop_shadow") {
    const swatch = `rgba(${Math.round(effect.color.r * 255)},${Math.round(effect.color.g * 255)},${Math.round(effect.color.b * 255)},${effect.color.a})`;
    return (
      <div style={{ display: "grid", gap: 4, padding: "6px", background: "var(--color-bg-panel-elevated)", borderRadius: 4 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Sun size={12} style={{ color: "var(--color-text-secondary)" }} />
          <span style={{ flex: 1, fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)" }}>Drop shadow</span>
          <button
            onClick={onToggle}
            title={effect.visible ? "Hide" : "Show"}
            style={{ width: 18, height: 18, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
          >
            {effect.visible ? <Eye size={11} /> : <EyeOff size={11} />}
          </button>
          <button
            onClick={onRemove}
            title="Remove"
            style={{ width: 18, height: 18, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
          >
            <Minus size={11} />
          </button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
          <Field label="X" value={effect.x} onCommit={(v) => setEffectField(index, "x", v)} />
          <Field label="Y" value={effect.y} onCommit={(v) => setEffectField(index, "y", v)} />
          <Field label="B" value={effect.blur} onCommit={(v) => setEffectField(index, "blur", v)} min={0} />
          <Field label="S" value={effect.spread} onCommit={(v) => setEffectField(index, "spread", v)} />
        </div>
        <button
          onClick={(e) => onPickerOpen((e.currentTarget as HTMLElement).getBoundingClientRect())}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            height: 24,
            padding: "0 6px",
            background: "var(--color-bg-input)",
            borderRadius: 4,
            color: "var(--color-text-primary)",
            fontSize: "var(--fs-xs)",
            textAlign: "left",
          }}
        >
          <span aria-hidden style={{ width: 12, height: 12, borderRadius: 2, background: swatch, border: "1px solid var(--color-border)" }} />
          {colorToHex(effect.color)} · {Math.round(effect.color.a * 100)}%
        </button>
      </div>
    );
  }
  if (effect.kind === "layer_blur") {
    return (
      <div style={{ display: "grid", gap: 4, padding: "6px", background: "var(--color-bg-panel-elevated)", borderRadius: 4 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <CircleDashed size={12} style={{ color: "var(--color-text-secondary)" }} />
          <span style={{ flex: 1, fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)" }}>Layer blur</span>
          <button
            onClick={onToggle}
            title={effect.visible ? "Hide" : "Show"}
            style={{ width: 18, height: 18, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
          >
            {effect.visible ? <Eye size={11} /> : <EyeOff size={11} />}
          </button>
          <button
            onClick={onRemove}
            title="Remove"
            style={{ width: 18, height: 18, color: "var(--color-text-secondary)", display: "grid", placeItems: "center" }}
          >
            <Minus size={11} />
          </button>
        </div>
        <Field label="R" value={effect.radius} onCommit={(v) => setEffectField(index, "radius", v)} min={0} />
      </div>
    );
  }
  return null;
}

function Field({ label, value, onCommit, min }: { label: string; value: number; onCommit: (v: number) => void; min?: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 4, height: 24 }}>
      <span style={{ width: 12, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{label}</span>
      <NumericInput value={value} onCommit={onCommit} min={min} />
    </div>
  );
}

function AddEffectMenu({
  anchor,
  onClose,
  onPickShadow,
  onPickBlur,
}: {
  anchor: { right: number; top: number };
  onClose: () => void;
  onPickShadow: () => void;
  onPickBlur: () => void;
}) {
  return (
    <div
      role="menu"
      onMouseLeave={onClose}
      style={{
        position: "fixed",
        right: anchor.right,
        top: anchor.top,
        minWidth: 200,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 6,
        boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
        padding: 4,
        zIndex: 100,
      }}
    >
      <Item id="effects.add.drop-shadow" label="Drop shadow" onClick={onPickShadow} />
      <Item id="effects.add.layer-blur" label="Layer blur" onClick={onPickBlur} />
      <Item id="effects.add.inner-shadow" label="Inner shadow" disabled />
      <Item id="effects.add.background-blur" label="Background blur" disabled />
      <Item id="effects.add.noise" label="Noise" disabled />
      <Item id="effects.add.texture" label="Texture" disabled />
      <Item id="effects.add.glass" label="Glass" disabled />
    </div>
  );
}

function Item({ id, label, onClick, disabled }: { id: string; label: string; onClick?: () => void; disabled?: boolean }) {
  return (
    <button
      data-id={id}
      onClick={(e) => {
        if (disabled) noopClick(id, e);
        else onClick?.();
      }}
      style={{
        width: "100%",
        textAlign: "left",
        padding: "6px 10px",
        borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-primary)",
        fontSize: "var(--fs-sm)",
        background: "transparent",
      }}
      title={disabled ? `${label} — not implemented in this mock` : label}
      onMouseEnter={(e) => {
        if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {label}
    </button>
  );
}
