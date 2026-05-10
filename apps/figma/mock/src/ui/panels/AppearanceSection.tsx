import { useState } from "react";
import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import {
  setOpacity, setVisibility, setCornerRadius,
  setPolygonSides, setStarPoints, setStarInnerRatio,
} from "@/engine/propertyCommands";
import { Eye, EyeOff, Asterisk, Hexagon } from "lucide-react";

// Inline icons matching Figma's small monochrome glyphs that don't have a
// good lucide equivalent (corner brackets, opacity grid, ratio triangle).
function OpacityGridIcon({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
      <rect x="1" y="1" width="10" height="10" rx="1.5" stroke="currentColor" strokeWidth="1" />
      {[0, 1, 2].flatMap((c) => [0, 1, 2].map((r) => (
        <rect key={`${c}-${r}`} x={3 + c * 2} y={3 + r * 2} width="1.2" height="1.2" fill="currentColor" />
      )))}
    </svg>
  );
}

function CornerBracketsIcon({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
      <path d="M1 4V1H4 M8 1H11V4 M11 8V11H8 M4 11H1V8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

function CornerGlyph({ corner, size = 12 }: { corner: "tl" | "tr" | "br" | "bl"; size?: number }) {
  const path = corner === "tl" ? "M2 10 V4 A2 2 0 0 1 4 2 H10"
    : corner === "tr" ? "M2 2 H8 A2 2 0 0 1 10 4 V10"
    : corner === "br" ? "M10 2 V8 A2 2 0 0 1 8 10 H2"
    : "M10 10 H4 A2 2 0 0 1 2 8 V2";
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
      <path d={path} stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

function PerCornerToggleIcon({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
      {([
        ["tl", "M2 6 V4 A2 2 0 0 1 4 2 H6"],
        ["tr", "M8 2 H10 A2 2 0 0 1 12 4 V6"],
        ["br", "M12 8 V10 A2 2 0 0 1 10 12 H8"],
        ["bl", "M6 12 H4 A2 2 0 0 1 2 10 V8"],
      ] as const).map(([k, d]) => (
        <path key={k} d={d} stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      ))}
    </svg>
  );
}

function RatioTriangleIcon({ size = 12 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
      <path d="M3 2 L10 6 L3 10 Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
    </svg>
  );
}

export function AppearanceSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;
  const ref = layers[0];
  const opacityPct: number | "Mixed" = layers.every((l) => l.opacity === ref.opacity) ? Math.round(ref.opacity * 100) : "Mixed";
  const allVisible = layers.every((l) => l.visible);

  // Corner radius slot is always shown for layout stability — disabled for
  // shape types that don't support it (line, ellipse, frame, text, etc).
  // Per-corner toggle is enabled only on rectangle/image; polygon/star get
  // a uniform-only field.
  const CORNER_TYPES = new Set(["rectangle", "image", "polygon", "star"]);
  const PER_CORNER_TYPES = new Set(["rectangle", "image"]);
  const cornerEnabled = layers.every((l) => CORNER_TYPES.has(l.type));
  const perCornerEnabled = layers.every((l) => PER_CORNER_TYPES.has(l.type));
  const allPolygons = layers.every((l) => l.type === "polygon");
  const allStars = layers.every((l) => l.type === "star");

  return (
    <Section
      title="Appearance"
      headerActions={
        <button
          data-id="appearance.visibility"
          onClick={() => setVisibility(!allVisible)}
          title={allVisible ? "Hide layer" : "Show layer"}
          style={{
            width: 22, height: 22, borderRadius: 4,
            color: allVisible ? "var(--color-text-secondary)" : "var(--color-text-muted)",
            display: "grid", placeItems: "center",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          {allVisible ? <Eye size={13} /> : <EyeOff size={13} />}
        </button>
      }
    >
      <TopRow opacityPct={opacityPct} cornerEnabled={cornerEnabled} perCornerEnabled={perCornerEnabled} layers={layers} />
      {allPolygons && <PolygonRow layers={layers} />}
      {allStars && <StarRow layers={layers} />}
    </Section>
  );
}

// ── Top row (Opacity + Corner radius) plus expanded per-corner grid ────────

function TopRow({ opacityPct, cornerEnabled, perCornerEnabled, layers }: {
  opacityPct: number | "Mixed";
  cornerEnabled: boolean;
  perCornerEnabled: boolean;
  layers: ReturnType<typeof getSelectedLayers>;
}) {
  const [perCorner, setPerCorner] = useState(false);
  const ref = layers[0] as { cornerRadius?: number | [number, number, number, number] };
  const cr = ref.cornerRadius;
  const allMatch = !cornerEnabled ? true : layers.every(
    (l) => JSON.stringify((l as { cornerRadius: number | [number, number, number, number] }).cornerRadius)
        === JSON.stringify(cr),
  );
  const tuple: [number, number, number, number] = Array.isArray(cr)
    ? cr
    : typeof cr === "number" ? [cr, cr, cr, cr] : [0, 0, 0, 0];
  const isUniformTuple = tuple[0] === tuple[1] && tuple[1] === tuple[2] && tuple[2] === tuple[3];
  const crVal: number | "Mixed" = !cornerEnabled
    ? 0
    : !allMatch ? "Mixed" : isUniformTuple ? tuple[0] : "Mixed";

  function commitUniform(v: number) {
    setCornerRadius(v);
  }
  function commitCorner(idx: 0 | 1 | 2 | 3, v: number) {
    const next: [number, number, number, number] = [...tuple] as [number, number, number, number];
    next[idx] = Math.max(0, v);
    setCornerRadius(next);
  }

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", columnGap: 6, rowGap: 4, alignItems: "end" }}>
        <Label>Opacity</Label>
        <Label>Corner radius</Label>
        <span />
        <NumericInput
          prefix={<OpacityGridIcon />}
          value={opacityPct}
          onCommit={(v) => setOpacity(v)}
          min={0}
          max={100}
          suffix="%"
        />
        <NumericInput
          prefix={<CornerBracketsIcon />}
          value={crVal}
          onCommit={commitUniform}
          min={0}
          disabled={!cornerEnabled}
        />
        {perCornerEnabled ? (
          <button
            data-id="appearance.corner-radius.per-corner-toggle"
            onClick={() => setPerCorner((p) => !p)}
            title="Edit each corner"
            style={{
              width: 28, height: 28, borderRadius: 5,
              display: "grid", placeItems: "center",
              background: perCorner ? "var(--color-selection-blue)" : "transparent",
              color: perCorner ? "var(--color-text-on-accent)" : "var(--color-text-secondary)",
            }}
            onMouseEnter={(e) => { if (!perCorner) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
            onMouseLeave={(e) => { if (!perCorner) e.currentTarget.style.background = "transparent"; }}
          >
            <PerCornerToggleIcon />
          </button>
        ) : <span style={{ width: 28 }} />}
      </div>

      {perCornerEnabled && perCorner && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", columnGap: 6, rowGap: 6, marginTop: 6 }}>
          <NumericInput prefix={<CornerGlyph corner="tl" />} value={tuple[0]} onCommit={(v) => commitCorner(0, v)} min={0} />
          <NumericInput prefix={<CornerGlyph corner="tr" />} value={tuple[1]} onCommit={(v) => commitCorner(1, v)} min={0} />
          <span />
          <NumericInput prefix={<CornerGlyph corner="bl" />} value={tuple[3]} onCommit={(v) => commitCorner(3, v)} min={0} />
          <NumericInput prefix={<CornerGlyph corner="br" />} value={tuple[2]} onCommit={(v) => commitCorner(2, v)} min={0} />
          <span />
        </div>
      )}
    </>
  );
}

function PolygonRow({ layers }: { layers: ReturnType<typeof getSelectedLayers> }) {
  const ref = layers[0] as { sides: number };
  const sidesVal: number | "Mixed" = layers.every((l) => (l as { sides: number }).sides === ref.sides)
    ? ref.sides : "Mixed";
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", columnGap: 6, rowGap: 4, alignItems: "end", marginTop: 4 }}>
      <Label>Count</Label><span /><span />
      <NumericInput prefix={<Hexagon size={12} />} value={sidesVal} onCommit={(v) => setPolygonSides(v)} min={3} max={60} integer />
      <span /><span style={{ width: 28 }} />
    </div>
  );
}

function StarRow({ layers }: { layers: ReturnType<typeof getSelectedLayers> }) {
  const ref = layers[0] as { points: number; innerRatio: number };
  const pointsVal: number | "Mixed" = layers.every((l) => (l as { points: number }).points === ref.points)
    ? ref.points : "Mixed";
  const ratioPct: number | "Mixed" = layers.every((l) => (l as { innerRatio: number }).innerRatio === ref.innerRatio)
    ? Math.round(ref.innerRatio * 100) : "Mixed";
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", columnGap: 6, rowGap: 4, alignItems: "end", marginTop: 4 }}>
      <Label>Count</Label><Label>Ratio</Label><span />
      <NumericInput prefix={<Asterisk size={12} />} value={pointsVal} onCommit={(v) => setStarPoints(v)} min={3} max={60} integer />
      <NumericInput prefix={<RatioTriangleIcon />} value={ratioPct} onCommit={(v) => setStarInnerRatio(v)} min={10} max={100} suffix="%" />
      <span style={{ width: 28 }} />
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{children}</span>;
}
