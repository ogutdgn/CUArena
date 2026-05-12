import type {
  Color,
  DocumentNode,
  Ellipse,
  Frame,
  Group,
  Layer,
  Line,
  Page,
  Paint,
  Polygon,
  Rectangle,
  Star,
  Stroke,
  Text,
  Vector,
  VectorNetwork,
} from "@/types/scene";
import { uid } from "@/util/id";
import { hydrateStoreFromSnapshot } from "./store";
import { logger } from "@/logger/buffer";
import { emitSemantic } from "@/logger/semantic";

interface FixtureLayerSpec {
  name?: string;
  type: string;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  fill?: string;
  stroke?: string;
  stroke_weight?: number;
  rotation?: number;
  opacity?: number;
  sides?: number;
  points?: number;
  inner_ratio?: number;
  star?: boolean;
  text?: string;
  font_size?: number;
  asset?: string;
  children?: FixtureLayerSpec[];
  // line endpoints
  x1?: number;
  y1?: number;
  x2?: number;
  y2?: number;
}

interface FixtureSpec {
  frame: { width: number; height: number; name: string };
  layers: FixtureLayerSpec[];
}

function parseHexColor(hex: string): Color {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16) / 255;
  const g = parseInt(clean.substring(2, 4), 16) / 255;
  const b = parseInt(clean.substring(4, 6), 16) / 255;
  return { r, g, b, a: 1 };
}

function makeFill(hex: string): Paint[] {
  return [{ kind: "solid", color: parseHexColor(hex), opacity: 1, visible: true }];
}

function makeStroke(hex: string, weight: number): Stroke[] {
  return [{
    paint: { kind: "solid", color: parseHexColor(hex), opacity: 1, visible: true },
    weight,
    alignment: "center",
    dash: null,
  }];
}

function baseProps(spec: FixtureLayerSpec, parentId: string): Omit<Layer, "type"> & { type: string } {
  return {
    id: uid("fix"),
    type: spec.type,
    name: spec.name ?? spec.type,
    parentId,
    x: spec.x ?? 0,
    y: spec.y ?? 0,
    w: spec.w ?? 100,
    h: spec.h ?? 100,
    rotation: spec.rotation ?? 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: spec.opacity ?? 1,
    constraints: { horizontal: "left", vertical: "top" },
  };
}

function buildLayer(spec: FixtureLayerSpec, parentId: string): Layer {
  const base = baseProps(spec, parentId);
  const fills: Paint[] = spec.fill ? makeFill(spec.fill) : [];
  const strokes: Stroke[] = spec.stroke ? makeStroke(spec.stroke, spec.stroke_weight ?? 1) : [];
  const effects: never[] = [];

  switch (spec.type) {
    case "rectangle":
      return { ...base, type: "rectangle", fills, strokes, effects, cornerRadius: 0 } as Rectangle;

    case "ellipse":
      return {
        ...base, type: "ellipse", fills, strokes, effects,
        arcStartAngle: 0, arcEndAngle: 360, innerRadius: 0,
      } as Ellipse;

    case "polygon":
      return {
        ...base, type: "polygon", fills, strokes, effects,
        sides: spec.sides ?? 3, cornerRadius: 0,
      } as Polygon;

    case "star":
      return {
        ...base, type: "star", fills, strokes, effects,
        points: spec.points ?? 5,
        innerRatio: spec.inner_ratio ?? 0.38,
        cornerRadius: 0,
      } as Star;

    case "line": {
      const lineStrokes = strokes.length > 0 ? strokes
        : [{ paint: { kind: "solid" as const, color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true }, weight: 1, alignment: "center" as const, dash: null }];
      return {
        ...base, type: "line",
        p1: { x: spec.x1 ?? 0, y: spec.y1 ?? 0 },
        p2: { x: spec.x2 ?? (spec.w ?? 100), y: spec.y2 ?? 0 },
        strokes: lineStrokes, effects,
      } as Line;
    }

    case "text": {
      const fontSize = spec.font_size ?? 16;
      const content = spec.text ?? "";
      return {
        ...base, type: "text",
        content,
        runs: [{ range: [0, content.length] }],
        fontFamily: "Inter",
        fontWeight: 400,
        fontSize,
        lineHeight: { type: "auto" },
        letterSpacing: { type: "px", value: 0 },
        hAlign: "center",
        vAlign: "middle",
        fills: fills.length > 0 ? fills : makeFill("#000000"),
        strokes: [],
        effects,
        resizingMode: "fixed",
      } as Text;
    }

    case "vector": {
      const network: VectorNetwork = {
        vertices: [
          { x: 0, y: 0, handleType: "corner" },
          { x: spec.w ?? 100, y: 0, handleType: "corner" },
          { x: spec.w ?? 100, y: spec.h ?? 100, handleType: "corner" },
          { x: 0, y: spec.h ?? 100, handleType: "corner" },
        ],
        segments: [
          { fromIndex: 0, toIndex: 1, handleFrom: null, handleTo: null },
          { fromIndex: 1, toIndex: 2, handleFrom: null, handleTo: null },
          { fromIndex: 2, toIndex: 3, handleFrom: null, handleTo: null },
          { fromIndex: 3, toIndex: 0, handleFrom: null, handleTo: null },
        ],
        closed: true,
      };
      return { ...base, type: "vector", network, fills, strokes, effects } as Vector;
    }

    case "group": {
      const groupId = base.id;
      const children = (spec.children ?? []).map((child) => buildLayer(child, groupId));
      return { ...base, type: "group", effects, children } as Group;
    }

    default:
      return { ...base, type: "rectangle", fills, strokes, effects, cornerRadius: 0 } as Rectangle;
  }
}

function buildDocumentFromFixture(fixture: FixtureSpec): DocumentNode {
  const pageId = uid("page");
  const frameId = uid("frame");

  const frameLayers: Layer[] = fixture.layers.map((spec) => buildLayer(spec, frameId));

  const frame: Frame = {
    id: frameId,
    type: "frame",
    name: fixture.frame.name,
    parentId: pageId,
    x: 0,
    y: 0,
    w: fixture.frame.width,
    h: fixture.frame.height,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    visible: true,
    locked: false,
    opacity: 1,
    constraints: { horizontal: "left", vertical: "top" },
    fills: [{ kind: "solid", color: { r: 1, g: 1, b: 1, a: 1 }, opacity: 1, visible: true }],
    strokes: [],
    effects: [],
    cornerRadius: 0,
    clipsContent: true,
    children: frameLayers,
  };

  const page: Page = {
    id: pageId,
    type: "page",
    name: "Page 1",
    backgroundColor: { r: 0.118, g: 0.118, b: 0.118, a: 1 },
    backgroundHidden: false,
    children: [frame],
  };

  return {
    id: uid("doc"),
    schemaVersion: 1,
    name: "Untitled",
    pages: [page],
  };
}

export function loadFixture(fixtureJson: FixtureSpec): boolean {
  const doc = buildDocumentFromFixture(fixtureJson);
  logger.clear();
  const ok = hydrateStoreFromSnapshot({ document: doc });
  if (ok) {
    emitSemantic({
      name: "fixture_loaded",
      frameName: fixtureJson.frame.name,
      layerCount: fixtureJson.layers.length,
    });
  }
  return ok;
}

export function installFixtureLoader(): void {
  (window as any).__loadFixture = loadFixture;
}
