import { Section } from "./sectionShell";
import { NumericInput } from "./NumericInput";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { setPolygonSides, setStarPoints, setStarInnerRatio } from "@/engine/propertyCommands";

// Conditional section showing shape-specific options:
//  - Polygon: editable sides count (3..60)
//  - Star: editable point count (3..60) + inner-radius ratio (0..100%)
// Renders only when the selection is exactly one polygon or one star.
// Mixed selection (e.g. polygon + star) hides the section to avoid mixing
// "sides" with "points" in the same panel.
export function ShapeOptionsSection() {
  const layers = useStore((s) => getSelectedLayers(s));
  if (layers.length === 0) return null;
  const allPolygons = layers.every((l) => l.type === "polygon");
  const allStars = layers.every((l) => l.type === "star");
  if (!allPolygons && !allStars) return null;

  if (allPolygons) {
    const ref = layers[0] as { sides: number };
    const sidesVal: number | "Mixed" = layers.every((l) => (l as { sides: number }).sides === ref.sides)
      ? ref.sides
      : "Mixed";
    return (
      <Section title="Polygon">
        <Row label="Count">
          <NumericInput value={sidesVal} onCommit={(v) => setPolygonSides(v)} min={3} max={60} />
        </Row>
      </Section>
    );
  }

  // allStars
  const ref = layers[0] as { points: number; innerRatio: number };
  const pointsVal: number | "Mixed" = layers.every(
    (l) => (l as { points: number }).points === ref.points,
  )
    ? ref.points
    : "Mixed";
  const ratioPct: number | "Mixed" = layers.every(
    (l) => (l as { innerRatio: number }).innerRatio === ref.innerRatio,
  )
    ? Math.round(ref.innerRatio * 100)
    : "Mixed";
  return (
    <Section title="Star">
      <Row label="Count">
        <NumericInput value={pointsVal} onCommit={(v) => setStarPoints(v)} min={3} max={60} />
      </Row>
      <Row label="Ratio">
        <NumericInput value={ratioPct} onCommit={(v) => setStarInnerRatio(v)} min={0} max={100} suffix="%" />
      </Row>
    </Section>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, height: 28 }}>
      <span style={{ width: 50, color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{label}</span>
      {children}
    </div>
  );
}
