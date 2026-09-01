// Constraints picker — small grid widget. Click edges/center to set
// horizontal/vertical constraints.

import { useStore } from "@/engine/store";
import { dispatch, makeOpId } from "@/engine/dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getSelectedLayers } from "@/engine/selectors";
import type { ConstraintH, ConstraintV } from "@/types/scene";

export function ConstraintsControl() {
  const layers = useStore((s) => getSelectedLayers(s));
  const ref = layers[0];
  if (!ref) return null;
  const allSameH = layers.every((l) => l.constraints.horizontal === ref.constraints.horizontal);
  const allSameV = layers.every((l) => l.constraints.vertical === ref.constraints.vertical);
  const h: ConstraintH | "Mixed" = allSameH ? ref.constraints.horizontal : "Mixed";
  const v: ConstraintV | "Mixed" = allSameV ? ref.constraints.vertical : "Mixed";

  function setConstraint(field: "horizontal" | "vertical", value: ConstraintH | ConstraintV) {
    const s = useStore.getState();
    const before: Record<string, unknown> = {};
    const after: Record<string, unknown> = {};
    for (const l of layers) {
      before[l.id] = l.constraints[field];
      after[l.id] = value;
    }
    dispatch({
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_property",
      pageId: s.activePageId,
      ids: layers.map((l) => l.id),
      path: `constraints/${field}`,
      before,
      after,
    });
    emitSemantic({
      name: "set_property",
      layerIds: layers.map((l) => l.id),
      path: `constraints/${field}`,
      before,
      after,
      trigger: "panel_input",
    });
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <ConstraintGrid h={h} v={v} setH={(c) => setConstraint("horizontal", c)} setV={(c) => setConstraint("vertical", c)} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
        <Select
          dataId="position.constraints.horizontal"
          value={h === "Mixed" ? "" : h}
          onChange={(v) => setConstraint("horizontal", v as ConstraintH)}
          options={[
            { value: "left", label: "Left" },
            { value: "right", label: "Right" },
            { value: "center", label: "Center" },
            { value: "stretch", label: "Stretch" },
            { value: "scale", label: "Scale" },
          ]}
        />
        <Select
          dataId="position.constraints.vertical"
          value={v === "Mixed" ? "" : v}
          onChange={(v) => setConstraint("vertical", v as ConstraintV)}
          options={[
            { value: "top", label: "Top" },
            { value: "bottom", label: "Bottom" },
            { value: "center", label: "Center" },
            { value: "stretch", label: "Stretch" },
            { value: "scale", label: "Scale" },
          ]}
        />
      </div>
    </div>
  );
}

function ConstraintGrid({ h, v, setH, setV }: { h: ConstraintH | "Mixed"; v: ConstraintV | "Mixed"; setH: (c: ConstraintH) => void; setV: (c: ConstraintV) => void }) {
  // Visualize: small box; bars on left/right/center for horizontal; top/bottom/center for vertical.
  const size = 36;
  const inset = 6;
  return (
    <svg width={size} height={size} style={{ background: "var(--color-bg-input)", borderRadius: 4 }}>
      <rect x={inset} y={inset} width={size - inset * 2} height={size - inset * 2} fill="none" stroke="var(--color-text-muted)" strokeWidth={1} />
      {/* Horizontal bars */}
      {(h === "left" || h === "stretch") && <line x1={inset - 2} y1={size / 2} x2={inset + 2} y2={size / 2} stroke="var(--color-selection-blue)" strokeWidth={2} />}
      {(h === "right" || h === "stretch") && <line x1={size - inset - 2} y1={size / 2} x2={size - inset + 2} y2={size / 2} stroke="var(--color-selection-blue)" strokeWidth={2} />}
      {h === "center" && <circle cx={size / 2} cy={size / 2} r={2} fill="var(--color-selection-blue)" />}
      {/* Vertical bars */}
      {(v === "top" || v === "stretch") && <line x1={size / 2} y1={inset - 2} x2={size / 2} y2={inset + 2} stroke="var(--color-selection-blue)" strokeWidth={2} />}
      {(v === "bottom" || v === "stretch") && <line x1={size / 2} y1={size - inset - 2} x2={size / 2} y2={size - inset + 2} stroke="var(--color-selection-blue)" strokeWidth={2} />}
      {/* Click hit areas — invisible squares on edges */}
      <rect x={0} y={size / 3} width={inset} height={size / 3} fill="transparent" style={{ cursor: "pointer" }} onClick={() => setH("left")} />
      <rect x={size - inset} y={size / 3} width={inset} height={size / 3} fill="transparent" style={{ cursor: "pointer" }} onClick={() => setH("right")} />
      <rect x={size / 3} y={0} width={size / 3} height={inset} fill="transparent" style={{ cursor: "pointer" }} onClick={() => setV("top")} />
      <rect x={size / 3} y={size - inset} width={size / 3} height={inset} fill="transparent" style={{ cursor: "pointer" }} onClick={() => setV("bottom")} />
    </svg>
  );
}

function Select<T extends string>({
  dataId,
  value,
  onChange,
  options,
}: {
  dataId: string;
  value: string;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
}) {
  return (
    <select
      data-id={dataId}
      value={value}
      onChange={(e) => onChange(e.target.value as T)}
      style={{
        height: 22,
        background: "var(--color-bg-input)",
        color: "var(--color-text-primary)",
        border: 0,
        borderRadius: 4,
        padding: "0 4px",
        fontSize: "var(--fs-xs)",
      }}
    >
      <option value="" disabled>
        Mixed
      </option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
