// Derived selectors over store state. Pure functions over AppState.

import type { AppState } from "./store";
import type { Layer, Page } from "@/types/scene";
import type { Rect } from "@/util/geometry";

export function getActivePage(s: AppState): Page | null {
  return s.document.pages.find((p) => p.id === s.activePageId) ?? null;
}

export function getSelection(s: AppState): string[] {
  return s.selectionByPage[s.activePageId] ?? [];
}

export function getSelectedLayers(s: AppState): Layer[] {
  const ids = getSelection(s);
  const out: Layer[] = [];
  for (const id of ids) {
    const n = s.nodesById[id];
    if (n && (n as Page).type !== "page") out.push(n as Layer);
  }
  return out;
}

export function selectionBbox(s: AppState): Rect | null {
  const layers = getSelectedLayers(s);
  if (layers.length === 0) return null;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const l of layers) {
    if (l.x < minX) minX = l.x;
    if (l.y < minY) minY = l.y;
    if (l.x + l.w > maxX) maxX = l.x + l.w;
    if (l.y + l.h > maxY) maxY = l.y + l.h;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function hitTest(s: AppState, x: number, y: number): Layer | null {
  const page = getActivePage(s);
  if (!page) return null;
  return hitTestArr(page.children, x, y);
}

function hitTestArr(layers: Layer[], x: number, y: number): Layer | null {
  for (let i = layers.length - 1; i >= 0; i--) {
    const l = layers[i];
    if (l.locked || !l.visible) continue;
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      const hit = hitTestArr(l.children, x, y);
      if (hit) return hit;
      if (l.type !== "group" && contains(l, x, y)) return l;
      continue;
    }
    if (contains(l, x, y)) return l;
  }
  return null;
}

function contains(l: Layer, x: number, y: number): boolean {
  return x >= l.x && x <= l.x + l.w && y >= l.y && y <= l.y + l.h;
}
