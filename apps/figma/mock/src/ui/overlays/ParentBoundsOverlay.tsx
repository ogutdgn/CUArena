import { worldOrientedCornersOfLayer } from "@/engine/coordinates";
import { useStore, selectActiveViewport } from "@/engine/store";
import type { Layer, Page } from "@/types/scene";

function isContainer(node: Layer | Page | undefined): node is Layer {
  if (!node || (node as Page).type === "page") return false;
  const layer = node as Layer;
  return layer.type === "frame" || layer.type === "section" || layer.type === "group";
}

export function ParentBoundsOverlay() {
  const viewport = useStore((s) => selectActiveViewport(s));
  // Render the parent's outline as an oriented quad through its four
  // transformed corners so a rotated/flipped parent's bounds rotate with it
  // (rather than being drawn as the axis-aligned AABB).
  const corners = useStore((s) => {
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
    return worldOrientedCornersOfLayer(s, parent);
  });

  if (!corners) return null;
  const sw = 1 / viewport.zoom;
  const dash = `${4 / viewport.zoom} ${3 / viewport.zoom}`;
  const points = corners.map((c) => `${c.x},${c.y}`).join(" ");
  return (
    <polygon
      points={points}
      fill="none"
      stroke="rgba(13,153,255,0.55)"
      strokeWidth={sw}
      strokeDasharray={dash}
      pointerEvents="none"
    />
  );
}
