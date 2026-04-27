import { worldRectOfLayer } from "@/engine/coordinates";
import { useStore, selectActiveViewport } from "@/engine/store";
import type { Layer, Page } from "@/types/scene";

function isContainer(node: Layer | Page | undefined): node is Layer {
  if (!node || (node as Page).type === "page") return false;
  const layer = node as Layer;
  return layer.type === "frame" || layer.type === "section" || layer.type === "group";
}

export function ParentBoundsOverlay() {
  const viewport = useStore((s) => selectActiveViewport(s));
  const bounds = useStore((s) => {
    const pageId = s.activePageId;
    const focusId = s.focusContextByPage[pageId] ?? null;

    let parent: Layer | null = null;
    if (focusId && isContainer(s.nodesById[focusId])) {
      parent = s.nodesById[focusId] as Layer;
    } else {
      const sel = s.selectionByPage[pageId] ?? [];
      if (sel.length === 1) {
        const selected = s.nodesById[sel[0]];
        if (selected && (selected as Page).type !== "page") {
          const selectedLayer = selected as Layer;
          const candidate = s.nodesById[selectedLayer.parentId];
          if (isContainer(candidate)) parent = candidate as Layer;
        }
      }
    }

    if (!parent) return null;
    const wr = worldRectOfLayer(s, parent);
    return { x: wr.x, y: wr.y, w: wr.w, h: wr.h };
  });

  if (!bounds) return null;
  const sw = 1 / viewport.zoom;
  const dash = `${4 / viewport.zoom} ${3 / viewport.zoom}`;
  return (
    <rect
      x={bounds.x}
      y={bounds.y}
      width={bounds.w}
      height={bounds.h}
      fill="none"
      stroke="rgba(13,153,255,0.55)"
      strokeWidth={sw}
      strokeDasharray={dash}
      pointerEvents="none"
    />
  );
}
