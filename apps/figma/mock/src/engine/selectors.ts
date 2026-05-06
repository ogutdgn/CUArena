// Derived selectors over store state. Pure functions over AppState.

import type { AppState } from "./store";
import type { Layer, Page, ContainerLayer } from "@/types/scene";
import type { Rect } from "@/util/geometry";
import { worldOffsetOfLayer, worldRectOfLayer } from "./coordinates";
import { isContainer } from "@/types/scene";

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
    const r = worldRectOfLayer(s, l);
    if (r.x < minX) minX = r.x;
    if (r.y < minY) minY = r.y;
    if (r.x + r.w > maxX) maxX = r.x + r.w;
    if (r.y + r.h > maxY) maxY = r.y + r.h;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function hitTest(s: AppState, x: number, y: number): Layer | null {
  const page = getActivePage(s);
  if (!page) return null;
  const focusId = s.focusContextByPage[s.activePageId] ?? null;
  if (focusId) {
    const node = s.nodesById[focusId];
    if (node && (node as Page).type !== "page" && isContainer(node as Layer)) {
      const scope = node as ContainerLayer;
      const origin = worldOffsetOfLayer(s, scope);
      return hitTestArr(scope.children, x, y, origin.x, origin.y);
    }
  }
  return hitTestArr(page.children, x, y, 0, 0);
}

function hitTestArr(layers: Layer[], x: number, y: number, ox: number, oy: number): Layer | null {
  for (let i = layers.length - 1; i >= 0; i--) {
    const l = layers[i];
    if (l.locked || !l.visible) continue;
    const wx = ox + l.x;
    const wy = oy + l.y;
    if (l.type === "frame" || l.type === "section" || l.type === "group") {
      const hit = hitTestArr(l.children, x, y, wx, wy);
      if (hit) return hit;
      if (l.type !== "group" && contains(wx, wy, l, x, y)) return l;
      continue;
    }
    if (contains(wx, wy, l, x, y)) return l;
  }
  return null;
}

function contains(wx: number, wy: number, l: Layer, x: number, y: number): boolean {
  return x >= wx && x <= wx + l.w && y >= wy && y <= wy + l.h;
}
