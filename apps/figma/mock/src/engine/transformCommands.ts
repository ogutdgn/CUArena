// Flip horizontal/vertical, zoom-to-* commands.

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";
import { getActivePage, getSelectedLayers, selectionBbox } from "./selectors";
import type { TransformMap } from "@/types/ops";
import {
  flipSelectionAcrossVisualCenter,
  rotateSelectionAroundVisualCenter,
  selectedTransformRoots,
} from "./selectionTransforms";

export function flipSelection(
  axis: "horizontal" | "vertical",
  trigger: "shortcut" | "context_menu" | "main_menu" | "panel_button",
) {
  const s = useStore.getState();
  const selectedLayers = getSelectedLayers(s);
  const layers = selectedTransformRoots(s, selectedLayers);
  if (layers.length === 0) return;
  const before: TransformMap = {};
  const after = flipSelectionAcrossVisualCenter(s, selectedLayers, axis);
  for (const l of layers) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;
  }
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  });
  emitSemantic({
    name: "flip_layer",
    layerIds: layers.map((l) => l.id),
    axis,
    trigger,
  });
}

// Rotate each selected layer 90° clockwise around its own center.
// `set_transform`'s rendering pivot is `(w/2, h/2)` (see commonTransform in
// NodeRenderer), so we only mutate `rotation` — geometry (x/y) is untouched.
// Trigger is narrowed to `"panel_button"` because that's the only entry point
// today; widen with a corresponding `rotate_layer.trigger` union extension if
// a shortcut / context-menu surface is added later.
export function rotate90Selection(trigger: "panel_button" = "panel_button") {
  const s = useStore.getState();
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return;
  const before: TransformMap = {};
  const beforeR: Record<string, number> = {};
  const afterR: Record<string, number> = {};
  for (const l of layers) {
    const t = { x: l.x, y: l.y, w: l.w, h: l.h, rotation: l.rotation, scaleX: l.scaleX, scaleY: l.scaleY };
    before[l.id] = t;
    beforeR[l.id] = l.rotation;
  }
  const after = rotateSelectionAroundVisualCenter(s, layers, 90);
  for (const l of layers) afterR[l.id] = after[l.id]?.rotation ?? l.rotation;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_transform",
    pageId: s.activePageId,
    ids: layers.map((l) => l.id),
    before,
    after,
  });
  emitSemantic({
    name: "rotate_layer",
    layerIds: layers.map((l) => l.id),
    before: beforeR,
    after: afterR,
    trigger,
  });
}

function svgSize(): { width: number; height: number } {
  const el = document.querySelector(".canvas-svg") as SVGSVGElement | null;
  if (!el) return { width: window.innerWidth, height: window.innerHeight };
  const r = el.getBoundingClientRect();
  return { width: r.width, height: r.height };
}

export function zoomToFit(trigger: "keyboard" | "dropdown_entry" | "initial_load") {
  const s = useStore.getState();
  const page = getActivePage(s);
  if (!page) return;
  if (page.children.length === 0) {
    emitSemantic({ name: "zoom_to_fit", contentBounds: null, trigger });
    return;
  }
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const l of page.children) {
    if (l.x < minX) minX = l.x;
    if (l.y < minY) minY = l.y;
    if (l.x + l.w > maxX) maxX = l.x + l.w;
    if (l.y + l.h > maxY) maxY = l.y + l.h;
  }
  const bounds = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  applyZoomToBounds(bounds);
  emitSemantic({ name: "zoom_to_fit", contentBounds: bounds, trigger });
}

export function zoomToSelection(trigger: "keyboard" | "dropdown_entry") {
  const s = useStore.getState();
  const bounds = selectionBbox(s);
  if (!bounds) return;
  applyZoomToBounds(bounds);
  emitSemantic({
    name: "zoom_to_selection",
    selectionBounds: bounds,
    layerIds: s.selectionByPage[s.activePageId] ?? [],
    trigger,
  });
}

export function zoomBy(factor: number, trigger: "keyboard" | "scroll" | "input_field" | "dropdown_entry") {
  const s = useStore.getState();
  const cur = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const centerWorld = { x: cur.x, y: cur.y };
  const newZoom = Math.max(0.05, Math.min(32, cur.zoom * factor));
  if (newZoom === cur.zoom) return;
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_viewport",
      pageId: s.activePageId,
      before: cur,
      after: {
        x: centerWorld.x,
        y: centerWorld.y,
        zoom: newZoom,
      },
    },
    { skipUndo: true },
  );
  emitSemantic({
    name: "zoom_canvas",
    before: cur.zoom,
    after: newZoom,
    anchor: centerWorld,
    trigger,
  });
}

export function zoomToCustom(zoomPct: number, trigger: "input_field") {
  const z = Math.max(5, Math.min(3200, zoomPct)) / 100;
  const s = useStore.getState();
  const cur = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const centerWorld = { x: cur.x, y: cur.y };
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_viewport",
      pageId: s.activePageId,
      before: cur,
      after: {
        x: centerWorld.x,
        y: centerWorld.y,
        zoom: z,
      },
    },
    { skipUndo: true },
  );
  emitSemantic({ name: "zoom_canvas", before: cur.zoom, after: z, anchor: centerWorld, trigger });
}

export function zoomTo100(trigger: "keyboard" | "input_field") {
  const s = useStore.getState();
  const cur = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const newZoom = 1;
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_viewport",
      pageId: s.activePageId,
      before: cur,
      after: { x: cur.x, y: cur.y, zoom: newZoom },
    },
    { skipUndo: true },
  );
  emitSemantic({ name: "zoom_to_100", trigger });
}

function applyZoomToBounds(bounds: { x: number; y: number; w: number; h: number }) {
  const s = useStore.getState();
  const cur = s.viewportByPage[s.activePageId] ?? { x: 0, y: 0, zoom: 1 };
  const { width, height } = svgSize();
  const padding = 80;
  const zw = (width - padding * 2) / Math.max(1, bounds.w);
  const zh = (height - padding * 2) / Math.max(1, bounds.h);
  const newZoom = Math.max(0.05, Math.min(8, Math.min(zw, zh)));
  const cxW = bounds.x + bounds.w / 2;
  const cyW = bounds.y + bounds.h / 2;
  dispatch(
    {
      id: makeOpId(),
      timestamp: performance.now(),
      kind: "set_viewport",
      pageId: s.activePageId,
      before: cur,
      after: {
        x: cxW,
        y: cyW,
        zoom: newZoom,
      },
    },
    { skipUndo: true },
  );
}
