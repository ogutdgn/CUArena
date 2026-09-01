import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { applyPanelFrameContainmentForSelection, nudgeTransformField, setTransformField } from "@/engine/propertyCommands";
import { flipSelection, rotate90Selection } from "@/engine/transformCommands";
import { commitTransaction, openTransaction } from "@/engine/dispatch";
import {
  alignSelection,
  getSingleSelectionAlignmentContainer,
} from "@/engine/alignmentCommands";
import {
  AlignStartVertical, AlignCenterVertical, AlignEndVertical,
  AlignStartHorizontal, AlignCenterHorizontal, AlignEndHorizontal,
  RotateCw, FlipHorizontal2, FlipVertical2,
} from "lucide-react";
import { getLayerPositionValue } from "@/engine/positionCoordinates";

export function PositionSection() {
  const state = useStore((s) => s);
  const layers = getSelectedLayers(state);
  if (layers.length === 0) return null;

  const ref = layers[0];
  const refPos = getLayerPositionValue(useStore.getState(), ref);
  const positions = layers.map((l) => getLayerPositionValue(useStore.getState(), l));
  const xVal: number | "Mixed" = positions.every((p) => p.x === refPos.x) ? refPos.x : "Mixed";
  const yVal: number | "Mixed" = positions.every((p) => p.y === refPos.y) ? refPos.y : "Mixed";
  const rotVal: number | "Mixed" = layers.every((l) => l.rotation === ref.rotation) ? ref.rotation : "Mixed";

  const singleContainer = getSingleSelectionAlignmentContainer(state, layers);
  const canAlign = layers.length >= 2 || singleContainer !== null;
  const alignHint = canAlign ? undefined : " — select 2+ layers, or a layer inside a frame";

  function commitTransformScrub(transactionId: string) {
    applyPanelFrameContainmentForSelection(transactionId);
    commitTransaction(transactionId);
  }

  function commitPositionField(
    field: "x" | "y",
    mixed: boolean,
    v: number,
    context?: { transactionId?: string; scrubDelta?: number },
  ) {
    const opts = { ...context, deferFrameContainment: !!context?.transactionId };
    if (mixed && typeof context?.scrubDelta === "number") {
      nudgeTransformField(field, context.scrubDelta, opts);
    } else {
      setTransformField(field, v, opts);
    }
  }

  function commitRotationField(v: number, context?: { transactionId?: string; scrubDelta?: number }) {
    if (rotVal === "Mixed" && typeof context?.scrubDelta === "number") {
      nudgeTransformField("rotation", context.scrubDelta, context);
    } else {
      setTransformField("rotation", v, context);
    }
  }

  return (
    <Section title="Position">
      {/* Alignment */}
      <SubLabel>Alignment</SubLabel>
      <div style={{ display: "flex", alignItems: "center", gap: 2 }}>
        <AlignBtn id="alignment.left"     title="Align left"              disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("left")}>     <AlignStartVertical    size={14} /></AlignBtn>
        <AlignBtn id="alignment.center-x" title="Align center horizontal" disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("center-x")}> <AlignCenterVertical   size={14} /></AlignBtn>
        <AlignBtn id="alignment.right"    title="Align right"             disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("right")}>    <AlignEndVertical      size={14} /></AlignBtn>
        <div style={{ width: 8 }} />
        <AlignBtn id="alignment.top"      title="Align top"               disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("top")}>      <AlignStartHorizontal  size={14} /></AlignBtn>
        <AlignBtn id="alignment.center-y" title="Align center vertical"   disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("center-y")}> <AlignCenterHorizontal size={14} /></AlignBtn>
        <AlignBtn id="alignment.bottom"   title="Align bottom"            disabled={!canAlign} hint={alignHint} onClick={() => alignSelection("bottom")}>   <AlignEndHorizontal    size={14} /></AlignBtn>
      </div>

      {/* Position — X/Y glyphs live inside each NumericInput so they double as
          drag-scrub handles (same pattern as opacity / corner-radius). */}
      <SubLabel>Position</SubLabel>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        <NumericInput
          prefix={<AxisGlyph>X</AxisGlyph>}
          value={xVal}
          scrubBaseValue={xVal === "Mixed" ? 0 : undefined}
          onCommit={(v, context) => commitPositionField("x", xVal === "Mixed", v, context)}
          onScrubStart={openTransaction}
          onScrubEnd={commitTransformScrub}
        />
        <NumericInput
          prefix={<AxisGlyph>Y</AxisGlyph>}
          value={yVal}
          scrubBaseValue={yVal === "Mixed" ? 0 : undefined}
          onCommit={(v, context) => commitPositionField("y", yVal === "Mixed", v, context)}
          onScrubStart={openTransaction}
          onScrubEnd={commitTransformScrub}
        />
      </div>

      {/* Rotation */}
      <SubLabel>Rotation</SubLabel>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <NumericInput
            prefix={<RotationGlyph />}
            value={rotVal}
            scrubBaseValue={rotVal === "Mixed" ? 0 : undefined}
            onCommit={commitRotationField}
            onScrubStart={openTransaction}
            onScrubEnd={commitTransaction}
            suffix="°"
          />
        </div>
        <IconBtn id="position.rotate-90"       title="Rotate 90° clockwise" onClick={() => rotate90Selection("panel_button")}><RotateCw       size={14} /></IconBtn>
        <IconBtn id="position.flip-horizontal" title="Flip horizontal"      onClick={() => flipSelection("horizontal", "panel_button")}><FlipHorizontal2 size={14} /></IconBtn>
        <IconBtn id="position.flip-vertical"   title="Flip vertical"        onClick={() => flipSelection("vertical", "panel_button")}><FlipVertical2   size={14} /></IconBtn>
      </div>
    </Section>
  );
}

function AxisGlyph({ children }: { children: React.ReactNode }) {
  return <span style={{ fontWeight: 500 }}>{children}</span>;
}

function RotationGlyph() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
      <line x1="2" y1="2" x2="2" y2="11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="2" y1="11" x2="11" y2="11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M2 7 A4 4 0 0 1 6 11" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" fill="none" />
    </svg>
  );
}

function SubLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ fontSize: "var(--fs-xs)", color: "var(--color-text-secondary)", fontWeight: 500, marginTop: 2, marginBottom: 4 }}>
      {children}
    </div>
  );
}

function AlignBtn({ id, title, disabled, hint, onClick, children }: {
  id: string; title: string; disabled?: boolean; hint?: string;
  onClick: () => void; children: React.ReactNode;
}) {
  return (
    <button
      data-id={id}
      title={disabled ? title + (hint ?? "") : title}
      disabled={!!disabled}
      onClick={() => { if (!disabled) onClick(); }}
      style={{
        width: 28, height: 28, borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-secondary)",
        display: "grid", placeItems: "center",
      }}
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {children}
    </button>
  );
}

function IconBtn({ id, title, onClick, children }: {
  id: string; title: string; onClick: () => void; children: React.ReactNode;
}) {
  return (
    <button
      data-id={id} title={title} onClick={onClick}
      style={{ width: 26, height: 26, borderRadius: 4, color: "var(--color-text-secondary)", display: "grid", placeItems: "center", flexShrink: 0 }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {children}
    </button>
  );
}
