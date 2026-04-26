import type { AppState } from "./store";
import type { Effect, Layer, Paint, Stroke } from "@/types/scene";

export interface VectorStyleDefaults {
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

function deepClone<T>(v: T): T {
  return JSON.parse(JSON.stringify(v)) as T;
}

function layerHasStyleArrays(layer: Layer): layer is Layer & {
  fills?: Paint[];
  strokes?: Stroke[];
  effects?: Effect[];
} {
  return "strokes" in layer || "fills" in layer || "effects" in layer;
}

function fromSelection(state: AppState): VectorStyleDefaults | null {
  const ids = state.selectionByPage[state.activePageId] ?? [];
  for (const id of ids) {
    const node = state.nodesById[id];
    if (!node || (node as { type: string }).type === "page") continue;
    const layer = node as Layer;
    if (!layerHasStyleArrays(layer)) continue;
    const strokes = Array.isArray(layer.strokes) ? layer.strokes : [];
    const fills = Array.isArray(layer.fills) ? layer.fills : [];
    const effects = Array.isArray(layer.effects) ? layer.effects : [];
    if (strokes.length > 0 || fills.length > 0 || effects.length > 0) {
      return {
        fills: deepClone(fills),
        strokes: deepClone(strokes),
        effects: deepClone(effects),
      };
    }
  }
  return null;
}

function ensureVisibleStroke(strokes: Stroke[], fallbackWeight: number): Stroke[] {
  if (strokes.length > 0) return strokes;
  return [
    {
      paint: { kind: "solid", color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true },
      weight: fallbackWeight,
      alignment: "center",
      dash: null,
    },
  ];
}

export function getPenVectorStyleDefaults(state: AppState): VectorStyleDefaults {
  const sel = fromSelection(state);
  if (sel) {
    return {
      fills: sel.fills,
      strokes: ensureVisibleStroke(sel.strokes, 1),
      effects: sel.effects,
    };
  }
  return {
    fills: [],
    strokes: ensureVisibleStroke([], 1),
    effects: [],
  };
}

export function getPencilVectorStyleDefaults(state: AppState): VectorStyleDefaults {
  const sel = fromSelection(state);
  if (sel) {
    return {
      fills: sel.fills,
      strokes: ensureVisibleStroke(sel.strokes, 2),
      effects: sel.effects,
    };
  }
  return {
    fills: [],
    strokes: ensureVisibleStroke([], 2),
    effects: [],
  };
}
