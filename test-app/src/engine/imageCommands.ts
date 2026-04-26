// Image placement: file picker → image_place; drag-drop; paste-image.
// Source: feature spec shape-creation/place-image.md.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { setSelection } from "./commands";
import { uid } from "@/util/id";
import type { Image as ImageLayer, Page } from "@/types/scene";
import { worldToParentLocal } from "./coordinates";

interface PlacementHint {
  worldX?: number;
  worldY?: number;
}

async function fileToDataURL(file: File): Promise<{ src: string; w: number; h: number; name: string }> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onload = () => {
      const src = String(reader.result);
      const img = new Image();
      img.onload = () => resolve({ src, w: img.naturalWidth, h: img.naturalHeight, name: file.name });
      img.onerror = (err) => reject(err);
      img.src = src;
    };
    reader.readAsDataURL(file);
  });
}

export async function placeImageFiles(
  files: File[],
  source: "file_picker" | "drag_drop" | "clipboard_paste",
  hint?: PlacementHint,
): Promise<void> {
  const sCheck = useStore.getState();
  const pageCheck = sCheck.document.pages.find((p) => p.id === sCheck.activePageId);
  if (!pageCheck) return;

  const max = 800;
  const newIds: string[] = [];
  const filenames: string[] = [];

  // Anchor at viewport center if no hint.
  const svgEl = document.querySelector(".canvas-svg") as SVGSVGElement | null;
  const r = svgEl?.getBoundingClientRect();
  const vp = sCheck.viewportByPage[sCheck.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const baseX = hint?.worldX != null ? hint.worldX : r ? vp.x + r.width / 2 / vp.zoom : 0;
  const baseY = hint?.worldY != null ? hint.worldY : r ? vp.y + r.height / 2 / vp.zoom : 0;

  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    if (!f.type.startsWith("image/")) continue;
    try {
      const { src, w, h, name } = await fileToDataURL(f);
      const scale = Math.min(1, max / Math.max(w, h));
      const W = Math.max(1, Math.round(w * scale));
      const H = Math.max(1, Math.round(h * scale));

      const sNow = useStore.getState();
      const pageId = sNow.activePageId;
      const parentId = sNow.focusContextByPage[pageId] ?? pageId;
      const parent = sNow.nodesById[parentId];
      const childCount =
        parent && "children" in parent && Array.isArray((parent as { children?: unknown[] }).children)
          ? ((parent as { children: unknown[] }).children).length
          : 0;
      const worldPos = {
        x: baseX - W / 2 + i * 12,
        y: baseY - H / 2 + i * 12,
      };
      const localPos = worldToParentLocal(sNow, parentId, worldPos);

      const layer: ImageLayer = {
        id: uid("image"),
        type: "image",
        name: name.replace(/\.[a-z0-9]+$/i, "") || `Image ${i + 1}`,
        parentId,
        x: localPos.x,
        y: localPos.y,
        w: W,
        h: H,
        rotation: 0,
        scaleX: 1,
        scaleY: 1,
        visible: true,
        locked: false,
        opacity: 1,
        constraints: { horizontal: "left", vertical: "top" },
        cornerRadius: 0,
        imageFill: {
          src,
          naturalWidth: w,
          naturalHeight: h,
          fit: "fill",
          rotation: 0,
          opacity: 1,
          visible: true,
        },
        fills: [],
        strokes: [],
        effects: [],
      };

      dispatch({
        id: makeOpId(),
        timestamp: performance.now(),
        kind: "create_node",
        pageId,
        parentId,
        indexInParent: childCount,
        node: layer,
      });
      newIds.push(layer.id);
      filenames.push(f.name);
    } catch {
      // Skip files that fail to load
    }
  }

  if (newIds.length > 0) {
    setSelection(newIds, "implicit_after_create");
  }
  emitSemantic({ name: "place_image", layerIds: newIds, source, filenames });
}

export function openImageFilePicker(): void {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.multiple = true;
  input.style.display = "none";
  document.body.appendChild(input);
  input.onchange = () => {
    const files = Array.from(input.files ?? []);
    input.remove();
    if (files.length > 0) {
      placeImageFiles(files, "file_picker");
    }
  };
  input.oncancel = () => input.remove();
  input.click();
}

// Type fallback for Page param to silence unused
export type _Page = Page;
