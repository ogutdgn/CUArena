// Floating angle label rendered near the cursor during rotate drag.

import { useStore, selectActiveViewport } from "@/engine/store";

export function RotateReadout() {
  const ro = useStore((s) => s.rotateReadout);
  const viewport = useStore((s) => selectActiveViewport(s));
  if (!ro) return null;
  const fontSize = 11 / viewport.zoom;
  const padX = 5 / viewport.zoom;
  const padY = 3 / viewport.zoom;
  const text = `${Math.round(ro.deg)}°`;
  const charW = 6.5 / viewport.zoom;
  const w = text.length * charW + padX * 2;
  const h = fontSize + padY * 2;
  const offset = 14 / viewport.zoom;
  return (
    <g pointerEvents="none">
      <rect
        x={ro.x + offset}
        y={ro.y - h / 2}
        width={w}
        height={h}
        fill="black"
        opacity={0.85}
        rx={3 / viewport.zoom}
      />
      <text
        x={ro.x + offset + w / 2}
        y={ro.y + fontSize / 3}
        fill="white"
        fontSize={fontSize}
        textAnchor="middle"
        style={{ fontFamily: "var(--font-family)", fontWeight: 500 }}
      >
        {text}
      </text>
    </g>
  );
}
