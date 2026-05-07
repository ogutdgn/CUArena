// Scene graph types. Source: .analysis/engine-report.md §1.
// Tree: Document → Page → Layer (recursive via children for containers).

export interface Color {
  r: number; // 0..1
  g: number;
  b: number;
  a: number;
}

export type ScrollBehavior = "none" | "horizontal" | "vertical" | "both";
export type ScrollPosition = "scroll_with_parent" | "fixed" | "sticky";

export interface PrototypeFlow {
  id: string;
  name: string;
  frameId: string;
}

export interface PrototypeSettings {
  device: string | null;
  backgroundColor: Color;
}

export type PrototypeTrigger =
  | "none"
  | "on_tap"
  | "on_drag"
  | "while_hovering"
  | "while_pressing"
  | "key_gamepad"
  | "mouse_enter"
  | "mouse_leave"
  | "touch_down"
  | "touch_up"
  | "after_delay";

export type PrototypeAction =
  | "none"
  | "navigate_to"
  | "change_to"
  | "back"
  | "scroll_to"
  | "open_link"
  | "set_variable"
  | "set_variable_mode"
  | "conditional"
  | "open_overlay"
  | "swap_overlay"
  | "close_overlay";

export type PrototypeAnimation =
  | "instant"
  | "dissolve"
  | "smart_animate"
  | "move_in"
  | "move_out"
  | "push"
  | "slide_in"
  | "slide_out";

export interface PrototypeConnection {
  id: string;
  sourceLayerId: string;
  trigger: PrototypeTrigger;
  action: PrototypeAction;
  destinationFrameId?: string;
  animation?: PrototypeAnimation;
  delayMs?: number;
  url?: string;
}

export type PaintKind = "solid" | "image" | "gradient" | "pattern" | "video";

export interface SolidPaint {
  kind: "solid";
  color: Color;
  opacity: number;
  visible: boolean;
}

export interface ImagePaint {
  kind: "image";
  src: string;
  fit: "fill" | "fit" | "crop" | "tile";
  rotation: number;
  opacity: number;
  visible: boolean;
}

export type Paint = SolidPaint | ImagePaint;

export interface Stroke {
  paint: Paint;
  weight: number;
  alignment: "inside" | "center" | "outside";
  dash: { dash: number; gap: number } | null;
}

export type Effect =
  | { kind: "drop_shadow"; x: number; y: number; blur: number; spread: number; color: Color; visible: boolean }
  | { kind: "layer_blur"; radius: number; visible: boolean };

export type ConstraintH = "left" | "right" | "center" | "stretch" | "scale";
export type ConstraintV = "top" | "bottom" | "center" | "stretch" | "scale";

export interface Constraints {
  horizontal: ConstraintH;
  vertical: ConstraintV;
}

export interface LayerBase {
  id: string;
  type: NodeType;
  name: string;
  parentId: string;
  // Axis-aligned bounds in parent space
  x: number;
  y: number;
  w: number;
  h: number;
  rotation: number; // degrees, CW positive
  scaleX: 1 | -1;
  scaleY: 1 | -1;
  visible: boolean;
  locked: boolean;
  opacity: number; // 0..1
  constraints: Constraints;
  scrollPosition?: ScrollPosition;
}

export type NodeType =
  | "rectangle"
  | "ellipse"
  | "polygon"
  | "star"
  | "line"
  | "arrow"
  | "text"
  | "vector"
  | "image"
  | "frame"
  | "section"
  | "group"
  | "slice";

export interface Rectangle extends LayerBase {
  type: "rectangle";
  cornerRadius: number | [number, number, number, number];
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

export interface Ellipse extends LayerBase {
  type: "ellipse";
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
  arcStartAngle: number;
  arcEndAngle: number;
  innerRadius: number;
}

export interface Polygon extends LayerBase {
  type: "polygon";
  sides: number;
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

export interface Star extends LayerBase {
  type: "star";
  points: number;
  innerRatio: number;
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

export interface Line extends LayerBase {
  type: "line";
  p1: { x: number; y: number };
  p2: { x: number; y: number };
  strokes: Stroke[];
  effects: Effect[];
}

export interface Arrow extends LayerBase {
  type: "arrow";
  p1: { x: number; y: number };
  p2: { x: number; y: number };
  strokes: Stroke[];
  endCapStart: "none" | "arrow";
  endCapEnd: "none" | "arrow";
  effects: Effect[];
}

export interface TextRun {
  range: [number, number];
  fontFamily?: string;
  fontWeight?: number;
  fontSize?: number;
  letterSpacing?: { type: "px" | "percent"; value: number };
  lineHeight?: { type: "auto" | "px" | "percent"; value?: number };
  fills?: Paint[];
}

export interface Text extends LayerBase {
  type: "text";
  content: string;
  runs: TextRun[];
  fontFamily: string;
  fontWeight: number;
  fontSize: number;
  lineHeight: { type: "auto" | "px" | "percent"; value?: number };
  letterSpacing: { type: "px" | "percent"; value: number };
  hAlign: "left" | "center" | "right" | "justify";
  vAlign: "top" | "middle" | "bottom";
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
  resizingMode: "auto_width" | "auto_height" | "fixed";
}

export interface VectorVertex {
  x: number;
  y: number;
  handleType: "corner" | "mirror" | "mirror_angle" | "independent";
}

export interface VectorSegment {
  fromIndex: number;
  toIndex: number;
  handleFrom: { dx: number; dy: number } | null;
  handleTo: { dx: number; dy: number } | null;
}

export interface VectorNetwork {
  vertices: VectorVertex[];
  segments: VectorSegment[];
  closed: boolean;
}

export interface Vector extends LayerBase {
  type: "vector";
  network: VectorNetwork;
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

export interface ImageFill {
  src: string;
  naturalWidth: number;
  naturalHeight: number;
  fit: "fill" | "fit" | "crop" | "tile";
  rotation: number;
  opacity: number;
  visible: boolean;
}

export interface Image extends LayerBase {
  type: "image";
  cornerRadius: number | [number, number, number, number];
  imageFill: ImageFill;
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
}

export interface Frame extends LayerBase {
  type: "frame";
  fills: Paint[];
  strokes: Stroke[];
  effects: Effect[];
  cornerRadius: number | [number, number, number, number];
  clipsContent: boolean;
  children: Layer[];
  overflowScrolling?: ScrollBehavior;
}

export interface Section extends LayerBase {
  type: "section";
  fills: Paint[];
  children: Layer[];
  clipsContent: false;
  devStatus: null | "ready_for_dev";
}

export interface Group extends LayerBase {
  type: "group";
  effects: Effect[];
  children: Layer[];
}

export interface Slice extends LayerBase {
  type: "slice";
}

export type Layer =
  | Rectangle
  | Ellipse
  | Polygon
  | Star
  | Line
  | Arrow
  | Text
  | Vector
  | Image
  | Frame
  | Section
  | Group
  | Slice;

export interface Page {
  id: string;
  type: "page";
  name: string;
  backgroundColor: Color;
  // When true, the canvas backdrop renders a checker pattern instead of the
  // background color. Independent of `backgroundColor.a` so toggling visibility
  // doesn't destroy the alpha value.
  backgroundHidden: boolean;
  children: Layer[];
  prototypeSettings?: PrototypeSettings;
  prototypeFlows?: PrototypeFlow[];
  prototypeConnections?: PrototypeConnection[];
}

export interface DocumentNode {
  id: string;
  schemaVersion: number;
  pages: Page[];
}

export type ContainerLayer = Frame | Section | Group;

export function isContainer(layer: Layer): layer is ContainerLayer {
  return layer.type === "frame" || layer.type === "section" || layer.type === "group";
}
