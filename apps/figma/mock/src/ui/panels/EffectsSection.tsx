import { useState, useEffect, useRef } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  addDropShadowEffect, addLayerBlurEffect, removeEffect,
  toggleEffectVisibility, setEffectField, setEffectColor,
} from "@/engine/propertyCommands";
import { ColorPicker, colorToHex, parseHex, swatchBackground } from "@/ui/overlays/ColorPicker";
import { OpacityScrubber } from "./OpacityScrubber";
import { commitTransaction, openTransaction } from "@/engine/dispatch";
import { Eye, EyeClosed, Minus, X, ChevronDown, GripVertical, Sun } from "lucide-react";
import type { Effect, Color } from "@/types/scene";

// ─── Effect icons ──────────────────────────────────────────────────────────────

function LayerBlurIcon({ active }: { active: boolean }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      {[0,1,2,3,4,5,6,7,8].map((i) => {
        const col = i % 3, row = Math.floor(i / 3);
        const opacity = active ? [0.9,0.5,0.2,0.5,0.9,0.5,0.2,0.5,0.9][i] : 0.4;
        return <rect key={i} x={2 + col * 4.5} y={2 + row * 4.5} width={3} height={3} rx={0.5} fill="currentColor" opacity={opacity} />;
      })}
    </svg>
  );
}

function DropShadowIcon({ active }: { active: boolean }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="2" y="2" width="9" height="9" rx="1.5" fill={active ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5" opacity={active ? 1 : 0.6} />
      <rect x="5" y="5" width="9" height="9" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.35" />
    </svg>
  );
}

// ─── Main section ──────────────────────────────────────────────────────────────

type DetailAnchor = { right: number; top?: number; bottom?: number };

// Conservative height estimate — header + position (X/Y stacked) + blur +
// spread + color rows + paddings/gaps. Enough to detect bottom overflow
// before the popover renders, so we can flip to `bottom`-anchored layout
// pre-emptively.
const POPOVER_H = 340;

export function EffectsSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  const layer = layers[0];
  const [openDetail, setOpenDetail] = useState<{ index: number; anchor: DetailAnchor } | null>(null);

  if (!layer || !("effects" in layer)) return null;
  const effects = (layer as { effects: Effect[] }).effects;

  function anchorFor(rect: DOMRect): DetailAnchor {
    // Anchor horizontally to the right panel's LEFT edge — not the trigger
    // element's left edge — so the popover always sits just outside the
    // panel regardless of whether `+` (right side of section header) or an
    // EffectRow icon (left side of row) opened it.
    const panelEl = document.querySelector('[data-id="right-panel"]');
    const panelLeft = panelEl ? panelEl.getBoundingClientRect().left : rect.left;
    const right = window.innerWidth - panelLeft + 8;
    // Flip up if the popover would overflow the viewport bottom — pin its
    // bottom edge to the trigger's bottom so it grows upward instead.
    if (rect.top + POPOVER_H > window.innerHeight) {
      return { right, bottom: window.innerHeight - rect.bottom };
    }
    return { right, top: rect.top };
  }

  // + adds a Drop Shadow by default and opens its floating detail popover so
  // the user can tweak fields immediately. They can switch type to Layer Blur
  // from the dropdown inside the popover.
  function onAdd(e: React.MouseEvent) {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const newIndex = effects.length;
    addDropShadowEffect();
    setOpenDetail({ index: newIndex, anchor: anchorFor(rect) });
  }

  function toggleRow(i: number, rect: DOMRect) {
    if (openDetail?.index === i) setOpenDetail(null);
    else setOpenDetail({ index: i, anchor: anchorFor(rect) });
  }

  const detailEffect = openDetail != null ? effects[openDetail.index] : null;

  return (
    <Section title="Effects" addId="effects.add" onAdd={onAdd}>
      {effects.map((eff, i) => (
        <EffectRow
          key={i}
          effect={eff}
          detailOpen={openDetail?.index === i}
          onToggleDetail={(rect) => toggleRow(i, rect)}
          onRemove={() => { if (openDetail?.index === i) setOpenDetail(null); removeEffect(i); }}
          onToggle={() => toggleEffectVisibility(i)}
        />
      ))}
      {detailEffect && openDetail && (
        <EffectDetail
          effect={detailEffect}
          index={openDetail.index}
          anchor={openDetail.anchor}
          onClose={() => setOpenDetail(null)}
        />
      )}
    </Section>
  );
}

// ─── Effect row ────────────────────────────────────────────────────────────────

function EffectRow({
  effect, detailOpen, onToggleDetail, onRemove, onToggle,
}: {
  effect: Effect;
  detailOpen: boolean;
  onToggleDetail: (rect: DOMRect) => void;
  onRemove: () => void;
  onToggle: () => void;
}) {
  const label = effect.kind === "drop_shadow" ? "Drop shadow" : "Layer blur";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
      {/* Icon button — opens detail popover */}
      <button
        onClick={(e) => onToggleDetail((e.currentTarget as HTMLElement).getBoundingClientRect())}
        title={`Edit ${label}`}
        style={{
          width: 28, height: 28, borderRadius: 5, flexShrink: 0,
          display: "grid", placeItems: "center",
          background: detailOpen ? "var(--color-selection-blue)" : "var(--color-bg-input)",
          color: detailOpen ? "var(--color-text-on-accent)" : "var(--color-text-secondary)",
        }}
      >
        {effect.kind === "layer_blur"
          ? <LayerBlurIcon active={detailOpen} />
          : <DropShadowIcon active={detailOpen} />
        }
      </button>

      <span style={{ flex: 1, fontSize: "var(--fs-sm)", color: "var(--color-text-primary)" }}>{label}</span>

      <button onClick={onToggle} title={effect.visible ? "Hide" : "Show"} style={{ width: 20, height: 20, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}>
        {effect.visible ? <Eye size={12} /> : <EyeClosed size={12} />}
      </button>
      <button onClick={onRemove} title="Remove" style={{ width: 20, height: 20, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}>
        <Minus size={12} />
      </button>
    </div>
  );
}

// ─── Detail panel ──────────────────────────────────────────────────────────────

function EffectDetail({
  effect, index, anchor, onClose,
}: {
  effect: Effect;
  index: number;
  anchor: DetailAnchor;
  onClose: () => void;
}) {
  const [typeOpen, setTypeOpen] = useState(false);
  const typeRef = useRef<HTMLDivElement>(null);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [pickerAnchor, setPickerAnchor] = useState<{ right: number; top: number } | null>(null);
  const pickerTxRef = useRef<string | null>(null);

  useEffect(() => {
    if (!typeOpen) return;
    function onDoc(e: MouseEvent) {
      if (!typeRef.current?.contains(e.target as Node)) setTypeOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [typeOpen]);

  function switchTo(kind: "drop_shadow" | "layer_blur") {
    setTypeOpen(false);
    if (effect.kind === kind) return;
    removeEffect(index);
    if (kind === "drop_shadow") addDropShadowEffect();
    else addLayerBlurEffect();
    onClose();
  }

  const label = effect.kind === "drop_shadow" ? "Drop shadow" : "Layer blur";

  return (
    <div
      role="dialog"
      style={{
        position: "fixed",
        right: anchor.right,
        ...(anchor.bottom != null ? { bottom: anchor.bottom } : { top: anchor.top }),
        width: 280,
        background: "var(--color-bg-panel-elevated)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: 10,
        padding: "10px 14px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 10,
        boxShadow: "0 12px 32px rgba(0,0,0,0.5)",
        zIndex: 200,
      }}
    >
      {/* Header: compact type pill + droplet + close */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
        <div ref={typeRef} style={{ position: "relative" }}>
          <button
            onClick={() => setTypeOpen((o) => !o)}
            style={{
              height: 28, padding: "0 8px 0 10px", borderRadius: 999,
              background: "var(--color-bg-input)",
              color: "var(--color-text-primary)", fontSize: "var(--fs-sm)",
              display: "inline-flex", alignItems: "center", gap: 4,
            }}
          >
            <span>{label}</span>
            <ChevronDown size={12} color="var(--color-text-secondary)" />
          </button>
          {typeOpen && (
            <div style={{
              position: "absolute", top: "100%", left: 0, marginTop: 4, minWidth: 140,
              background: "var(--color-bg-panel-elevated)",
              border: "1px solid var(--color-border-strong)",
              borderRadius: 6, boxShadow: "0 8px 20px rgba(0,0,0,0.5)",
              padding: 4, zIndex: 300,
            }}>
              {(["drop_shadow", "layer_blur"] as const).map((k) => (
                <button key={k} onClick={() => switchTo(k)} style={{
                  width: "100%", textAlign: "left", padding: "5px 8px", borderRadius: 4,
                  fontSize: "var(--fs-sm)",
                  color: effect.kind === k ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                  background: effect.kind === k ? "var(--color-bg-row-active)" : "transparent",
                }}
                  onMouseEnter={(e) => { if (effect.kind !== k) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
                  onMouseLeave={(e) => { if (effect.kind !== k) e.currentTarget.style.background = "transparent"; }}
                >
                  {k === "drop_shadow" ? "Drop shadow" : "Layer blur"}
                </button>
              ))}
            </div>
          )}
        </div>
        <div style={{ flex: 1 }} />
        <button onClick={onClose} title="Close" style={{ width: 24, height: 24, borderRadius: 4, display: "grid", placeItems: "center", color: "var(--color-text-secondary)" }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <X size={14} />
        </button>
      </div>

      {/* Layer blur fields */}
      {effect.kind === "layer_blur" && (
        <DetailRow label="Blur">
          <NumericInput
            prefix={<GripVertical size={12} />}
            value={effect.radius}
            onCommit={(v, context) => setEffectField(index, "radius", v, context)}
            min={0}
            onScrubStart={openTransaction}
            onScrubEnd={commitTransaction}
          />
        </DetailRow>
      )}

      {/* Drop shadow fields */}
      {effect.kind === "drop_shadow" && (
        <>
          <DetailRow label="Position">
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <NumericInput prefix="X" value={effect.x} onCommit={(v, context) => setEffectField(index, "x", v, context)} onScrubStart={openTransaction} onScrubEnd={commitTransaction} />
              <NumericInput prefix="Y" value={effect.y} onCommit={(v, context) => setEffectField(index, "y", v, context)} onScrubStart={openTransaction} onScrubEnd={commitTransaction} />
            </div>
          </DetailRow>
          <DetailRow label="Blur">
            <NumericInput
              prefix={<GripVertical size={12} />}
              value={effect.blur}
              onCommit={(v, context) => setEffectField(index, "blur", v, context)}
              min={0}
              onScrubStart={openTransaction}
              onScrubEnd={commitTransaction}
            />
          </DetailRow>
          <DetailRow label="Spread">
            <NumericInput
              prefix={<Sun size={12} />}
              value={effect.spread}
              onCommit={(v, context) => setEffectField(index, "spread", v, context)}
              onScrubStart={openTransaction}
              onScrubEnd={commitTransaction}
            />
          </DetailRow>
          <DetailRow label="Color">
            <ShadowColorRow effect={effect} index={index} onOpenPicker={(e) => {
              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
              setPickerAnchor({ right: window.innerWidth - rect.left + 8, top: rect.top });
              setPickerOpen(true);
            }} />
          </DetailRow>
          {pickerOpen && pickerAnchor && (
            <ColorPicker
              value={effect.color}
              onChange={(c: Color) => setEffectColor(index, c, pickerTxRef.current ? { transactionId: pickerTxRef.current } : undefined)}
              onChangeStart={() => { pickerTxRef.current = openTransaction(); }}
              onChangeEnd={() => {
                if (pickerTxRef.current) commitTransaction(pickerTxRef.current);
                pickerTxRef.current = null;
              }}
              onClose={() => setPickerOpen(false)}
              anchor={pickerAnchor}
            />
          )}
        </>
      )}
    </div>
  );
}

function ShadowColorRow({ effect, index, onOpenPicker }: {
  effect: Extract<Effect, { kind: "drop_shadow" }>;
  index: number;
  onOpenPicker: (e: React.MouseEvent) => void;
}) {
  const hex = colorToHex(effect.color);
  const opacityPct = Math.round(effect.color.a * 100);
  const [hexDraft, setHexDraft] = useState(hex);
  const [editing, setEditing] = useState(false);

  useEffect(() => { if (!editing) setHexDraft(hex); }, [hex, editing]);

  function commitOpacityPct(pct: number, context?: { transactionId?: string }) {
    setEffectColor(index, { ...effect.color, a: pct / 100 }, context);
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 26, background: "var(--color-bg-input)", borderRadius: 4, padding: "0 6px", minWidth: 0, overflow: "hidden" }}>
      <button onClick={onOpenPicker} style={{ width: 14, height: 14, borderRadius: 2, flexShrink: 0, background: swatchBackground(effect.color), border: "1px solid var(--color-border)", padding: 0 }} />
      <input
        value={hexDraft}
        onChange={(e) => setHexDraft(e.target.value)}
        onFocus={(e) => { setEditing(true); requestAnimationFrame(() => e.target.select()); }}
        onBlur={() => {
          setEditing(false);
          const parsed = parseHex(hexDraft);
          if (parsed) setEffectColor(index, { ...parsed, a: effect.color.a });
          else setHexDraft(hex);
        }}
        onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); }}
        style={{ flex: 1, minWidth: 0, background: "transparent", border: 0, color: "var(--color-text-primary)", fontSize: "var(--fs-sm)", fontFamily: "monospace", outline: 0, padding: 0 }}
      />
      <OpacityScrubber value={opacityPct} onCommit={commitOpacityPct} onScrubStart={openTransaction} onScrubEnd={commitTransaction} />
    </div>
  );
}

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
      <span style={{ width: 52, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", paddingTop: 7, flexShrink: 0 }}>{label}</span>
      <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
    </div>
  );
}


