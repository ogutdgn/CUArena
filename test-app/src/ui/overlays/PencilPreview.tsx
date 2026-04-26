// Pencil live stroke preview while drawing.

import { useStore, selectActiveViewport } from "@/engine/store";

export function PencilPreview() {
  const preview = useStore((s) => s.pencilPreview);
  const viewport = useStore((s) => selectActiveViewport(s));
  if (!preview || preview.points.length < 1) return null;
  const sw = 2 / viewport.zoom;
  const d = preview.points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");
  return <path d={d} fill="none" stroke="white" strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" pointerEvents="none" />;
}
