import { frameLabelGeometry } from "@/engine/frameLabelsGeometry";
import { getActivePage } from "@/engine/selectors";
import { selectActiveViewport, useStore } from "@/engine/store";

export function FrameLabelsOverlay() {
  const page = useStore((s) => getActivePage(s));
  const viewport = useStore((s) => selectActiveViewport(s));
  const labels = useStore((s) => frameLabelGeometry(s, viewport.zoom));

  if (!page || labels.length === 0) return null;
  return (
    <g pointerEvents="none">
      {labels.map((label) => {
        const isSection = label.type === "section";
        return (
          <text
            key={label.id}
            x={label.x}
            y={label.y}
            fill={isSection ? "var(--color-text-secondary)" : "rgba(120,120,120,1)"}
            fontSize={(isSection ? 14 : 11) / viewport.zoom}
            opacity={label.opacity}
            textAnchor="start"
            style={{ fontFamily: "var(--font-family)", fontWeight: isSection ? 600 : 500 }}
          >
            {label.name}
          </text>
        );
      })}
    </g>
  );
}
