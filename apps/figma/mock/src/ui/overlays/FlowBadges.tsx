// Flow starting-point badges shown in prototype mode.
// Rendered inside the world-space SVG group so they pan/zoom with the canvas.

import { useStore } from "@/engine/store";
import { getActivePage } from "@/engine/selectors";

const BADGE_H = 20; // world units at zoom=1 (scaled by 1/zoom to stay constant px)
const BADGE_FONT = 11;
const BADGE_PAD_X = 8;
const BADGE_GAP = 6;
const ICON_SIZE = 12;

export function FlowBadges() {
  const tab = useStore((s) => s.activeRightTab);
  const page = useStore((s) => getActivePage(s));
  const zoom = useStore((s) => s.viewportByPage[s.activePageId]?.zoom ?? 1);

  if (tab !== "prototype" || !page) return null;

  const flows = page.prototypeFlows ?? [];
  if (flows.length === 0) return null;

  // scale factor so badge stays visually constant regardless of zoom
  const sc = 1 / zoom;

  return (
    <>
      {flows.map((flow) => {
        const frame = page.children.find((c) => c.id === flow.frameId);
        if (!frame) return null;

        const bx = frame.x;
        const by = frame.y - BADGE_H * sc - 4 * sc;

        const textW = flow.name.length * (BADGE_FONT * 0.6);
        const badgeW = BADGE_PAD_X * 2 + textW + BADGE_GAP + ICON_SIZE;

        return (
          <g key={flow.id} transform={`translate(${bx} ${by}) scale(${sc})`} pointerEvents="none">
            {/* Badge pill */}
            <rect
              x={0}
              y={0}
              width={badgeW}
              height={BADGE_H}
              rx={4}
              ry={4}
              fill="var(--color-selection-blue)"
            />
            {/* Flow name */}
            <text
              x={BADGE_PAD_X}
              y={BADGE_H / 2 + BADGE_FONT * 0.35}
              fontSize={BADGE_FONT}
              fill="white"
              fontFamily="Inter, sans-serif"
              fontWeight={500}
            >
              {flow.name}
            </text>
            {/* Small icon placeholder (rounded square) */}
            <rect
              x={BADGE_PAD_X + textW + BADGE_GAP}
              y={(BADGE_H - ICON_SIZE) / 2}
              width={ICON_SIZE}
              height={ICON_SIZE}
              rx={2}
              ry={2}
              fill="rgba(255,255,255,0.25)"
            />
            <text
              x={BADGE_PAD_X + textW + BADGE_GAP + ICON_SIZE / 2}
              y={(BADGE_H - ICON_SIZE) / 2 + ICON_SIZE * 0.72}
              fontSize={8}
              fill="white"
              fontFamily="Inter, sans-serif"
              textAnchor="middle"
            >
              ▶
            </text>
          </g>
        );
      })}
    </>
  );
}
