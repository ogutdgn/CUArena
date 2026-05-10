// Renders one Layer as SVG.

import type { Layer, Paint, Stroke, Effect } from "@/types/scene";
import { useStore } from "@/engine/store";

export function NodeRenderer({ layer }: { layer: Layer }) {
  if (!layer.visible) return null;
  switch (layer.type) {
    case "rectangle":
    case "image":
      return <RectangleEl layer={layer} />;
    case "ellipse":
      return <EllipseEl layer={layer} />;
    case "polygon":
      return <PolygonEl layer={layer} />;
    case "star":
      return <StarEl layer={layer} />;
    case "line":
      return <LineEl layer={layer} />;
    case "arrow":
      return <ArrowEl layer={layer} />;
    case "text":
      return <TextEl layer={layer} />;
    case "vector":
      return <VectorEl layer={layer} />;
    case "frame":
    case "section":
    case "group":
      return <GroupEl layer={layer} />;
    case "slice":
      return <SliceEl layer={layer} />;
  }
}

function commonTransform(layer: Layer): string {
  const cx = layer.w / 2;
  const cy = layer.h / 2;
  let t = `translate(${layer.x} ${layer.y})`;
  if (layer.rotation !== 0) t += ` rotate(${layer.rotation} ${cx} ${cy})`;
  if (layer.scaleX !== 1 || layer.scaleY !== 1) {
    t += ` translate(${cx} ${cy}) scale(${layer.scaleX} ${layer.scaleY}) translate(${-cx} ${-cy})`;
  }
  return t;
}

function colorToCss(c: { r: number; g: number; b: number; a: number }): string {
  return `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${c.a})`;
}

// Composites all visible fills using Porter-Duff "source over". Figma stores
// fills top-down (index 0 is on top), so we walk bottom-up and composite each
// upper fill over the accumulator. Per-fill alpha controls how much each layer
// shows through, so reducing the top fill's alpha reveals lower fills.
function paintToFill(fills: Paint[] | undefined): string {
  if (!fills || fills.length === 0) return "transparent";
  let r = 0, g = 0, b = 0, a = 0;
  for (let i = fills.length - 1; i >= 0; i--) {
    const p = fills[i];
    if (!p.visible) continue;
    let sr: number, sg: number, sb: number, sa: number;
    if (p.kind === "solid") {
      sr = p.color.r; sg = p.color.g; sb = p.color.b; sa = p.color.a;
    } else if (p.kind === "image") {
      sr = 180 / 255; sg = 180 / 255; sb = 180 / 255; sa = 1;
    } else {
      continue;
    }
    const outA = sa + a * (1 - sa);
    if (outA <= 0) { r = 0; g = 0; b = 0; a = 0; continue; }
    r = (sr * sa + r * a * (1 - sa)) / outA;
    g = (sg * sa + g * a * (1 - sa)) / outA;
    b = (sb * sa + b * a * (1 - sa)) / outA;
    a = outA;
  }
  if (a <= 0) return "transparent";
  return `rgba(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)}, ${a})`;
}

function effectsToFilter(effects: Effect[] | undefined, layerId: string): { filter: string; defs: React.ReactNode } | null {
  if (!effects || effects.length === 0) return null;
  const visible = effects.filter((e) => e.visible);
  if (visible.length === 0) return null;
  const filterId = `eff-${layerId}`;
  const primitives: React.ReactNode[] = [];
  let lastResult = "SourceGraphic";
  let mergeNodes: React.ReactNode[] = [];

  visible.forEach((eff, i) => {
    if (eff.kind === "drop_shadow") {
      const offsetId = `o${i}`;
      const blurId = `b${i}`;
      const colorId = `c${i}`;
      primitives.push(
        <feOffset key={`off-${i}`} in="SourceAlpha" dx={eff.x} dy={eff.y} result={offsetId} />,
        <feGaussianBlur key={`blur-${i}`} in={offsetId} stdDeviation={eff.blur / 2} result={blurId} />,
        <feFlood key={`flood-${i}`} floodColor={`rgba(${Math.round(eff.color.r * 255)},${Math.round(eff.color.g * 255)},${Math.round(eff.color.b * 255)},${eff.color.a})`} result={`f${i}`} />,
        <feComposite key={`comp-${i}`} in={`f${i}`} in2={blurId} operator="in" result={colorId} />,
      );
      mergeNodes.push(<feMergeNode key={`mn-${i}`} in={colorId} />);
    } else if (eff.kind === "layer_blur") {
      const blurId = `lb${i}`;
      primitives.push(<feGaussianBlur key={`lblur-${i}`} in={lastResult} stdDeviation={eff.radius / 2} result={blurId} />);
      lastResult = blurId;
    }
  });

  // Final merge: shadow layers below the (possibly blurred) source.
  if (mergeNodes.length > 0) {
    primitives.push(
      <feMerge key="merge">
        {mergeNodes}
        <feMergeNode in={lastResult} />
      </feMerge>,
    );
  }

  return {
    filter: `url(#${filterId})`,
    defs: (
      <defs>
        <filter id={filterId} x="-50%" y="-50%" width="200%" height="200%">
          {primitives}
        </filter>
      </defs>
    ),
  };
}

function strokeAttrs(strokes: Stroke[] | undefined): { stroke: string; strokeWidth: number; strokeDasharray?: string } {
  if (!strokes || strokes.length === 0) return { stroke: "none", strokeWidth: 0 };
  // Composite stroke colors via Porter-Duff source-over (same as fills). All
  // strokes share one weight (UI invariant), so the visual stack collapses to
  // a single line whose color is the alpha-composited stack.
  let r = 0, g = 0, b = 0, a = 0;
  for (let i = strokes.length - 1; i >= 0; i--) {
    const sk = strokes[i];
    if (!sk.paint.visible) continue;
    if (sk.paint.kind !== "solid") continue;
    const sr = sk.paint.color.r, sg = sk.paint.color.g, sb = sk.paint.color.b, sa = sk.paint.color.a;
    const outA = sa + a * (1 - sa);
    if (outA <= 0) { r = 0; g = 0; b = 0; a = 0; continue; }
    r = (sr * sa + r * a * (1 - sa)) / outA;
    g = (sg * sa + g * a * (1 - sa)) / outA;
    b = (sb * sa + b * a * (1 - sa)) / outA;
    a = outA;
  }
  if (a <= 0) return { stroke: "none", strokeWidth: 0 };
  const top = strokes[0];
  return {
    stroke: `rgba(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)}, ${a})`,
    strokeWidth: top.weight,
    strokeDasharray: top.dash ? `${top.dash.dash} ${top.dash.gap}` : undefined,
  };
}

// Builds an SVG path for a rectangle whose corners may have different radii.
// Corner order: [topLeft, topRight, bottomRight, bottomLeft]. Each is clamped
// to half of the smaller dimension. Returns a closed path.
function rectCornerPath(w: number, h: number, cr: number | [number, number, number, number]): string {
  const arr: [number, number, number, number] = Array.isArray(cr) ? cr : [cr, cr, cr, cr];
  const maxR = Math.min(w, h) / 2;
  const [tl, tr, br, bl] = arr.map((v) => Math.max(0, Math.min(v, maxR))) as [number, number, number, number];
  return [
    `M${tl},0`,
    `H${w - tr}`,
    tr > 0 ? `A${tr},${tr} 0 0 1 ${w},${tr}` : `L${w},0`,
    `V${h - br}`,
    br > 0 ? `A${br},${br} 0 0 1 ${w - br},${h}` : `L${w},${h}`,
    `H${bl}`,
    bl > 0 ? `A${bl},${bl} 0 0 1 0,${h - bl}` : `L0,${h}`,
    `V${tl}`,
    tl > 0 ? `A${tl},${tl} 0 0 1 ${tl},0` : `L0,0`,
    `Z`,
  ].join(" ");
}

function RectangleEl({ layer }: { layer: Extract<Layer, { type: "rectangle" | "image" }> }) {
  const fills = "fills" in layer ? layer.fills : undefined;
  const strokes = "strokes" in layer ? layer.strokes : undefined;
  const cr = "cornerRadius" in layer ? layer.cornerRadius : 0;
  const sa = strokeAttrs(strokes);
  const eff = effectsToFilter(layer.effects, layer.id);
  const d = rectCornerPath(layer.w, layer.h, cr);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      {eff?.defs}
      <path
        d={d}
        fill={paintToFill(fills)}
        stroke={sa.stroke}
        strokeWidth={sa.strokeWidth}
        strokeDasharray={sa.strokeDasharray}
        filter={eff?.filter}
      />
      {layer.type === "image" && (
        <ImageContent layer={layer} cornerPath={d} />
      )}
    </g>
  );
}

function ImageContent({ layer, cornerPath }: { layer: Extract<Layer, { type: "image" }>; cornerPath: string }) {
  const clipId = `clip-img-${layer.id}`;
  const fit = layer.imageFill.fit;
  const src = layer.imageFill.src;
  return (
    <>
      <defs>
        <clipPath id={clipId}>
          <path d={cornerPath} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clipId})`}>
        <image
          href={src}
          x={0}
          y={0}
          width={layer.w}
          height={layer.h}
          preserveAspectRatio={
            fit === "fill"
              ? "none"
              : fit === "fit"
              ? "xMidYMid meet"
              : "xMidYMid slice"
          }
        />
      </g>
    </>
  );
}

function EllipseEl({ layer }: { layer: Extract<Layer, { type: "ellipse" }> }) {
  const sa = strokeAttrs(layer.strokes);
  const eff = effectsToFilter(layer.effects, layer.id);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      {eff?.defs}
      <ellipse
        cx={layer.w / 2}
        cy={layer.h / 2}
        rx={layer.w / 2}
        ry={layer.h / 2}
        fill={paintToFill(layer.fills)}
        stroke={sa.stroke}
        strokeWidth={sa.strokeWidth}
        filter={eff?.filter}
      />
    </g>
  );
}

// Rounds every vertex of a closed polygon. Each corner is replaced with a
// circular arc tangent to both adjacent edges; the input `radius` is the
// arc's circle radius (Figma semantics). The tangent length along each edge
// is t = radius / tan(angle/2). Clamping t to half the shorter edge prevents
// adjacent arcs from overlapping; when several vertices simultaneously hit
// that cap (regular polygon at apothem-equivalent input), the arcs collapse
// into a single inscribed circle — so polygons morph into circles at max
// radius. Collinear vertices (e.g. star inner points at ratio=50%) are
// passed through with no rounding.
function roundedPolygonPath(points: { x: number; y: number }[], radius: number): string {
  if (points.length < 3) return "";
  if (radius <= 0) {
    return "M" + points.map((p) => `${p.x},${p.y}`).join(" L") + " Z";
  }
  const cmds: string[] = [];
  for (let i = 0; i < points.length; i++) {
    const prev = points[(i - 1 + points.length) % points.length];
    const cur = points[i];
    const next = points[(i + 1) % points.length];
    const vp = { x: prev.x - cur.x, y: prev.y - cur.y };
    const vn = { x: next.x - cur.x, y: next.y - cur.y };
    const lenP = Math.hypot(vp.x, vp.y);
    const lenN = Math.hypot(vn.x, vn.y);
    if (lenP === 0 || lenN === 0) continue;

    // Smaller angle between the two edges meeting at cur, in [0, π].
    const cosA = Math.max(-1, Math.min(1, (vp.x * vn.x + vp.y * vn.y) / (lenP * lenN)));
    const angle = Math.acos(cosA);

    // Collinear vertex — no rounding needed; pass through exactly.
    if (angle < 1e-3 || Math.PI - angle < 1e-3) {
      cmds.push((i === 0 ? "M" : "L") + `${cur.x},${cur.y}`);
      continue;
    }

    // t is how far along each edge we move away from the vertex before the
    // arc starts. r is the actual arc radius — equals input `radius` until
    // t hits the half-edge cap, after which r is recomputed from the capped t.
    const tanHalf = Math.tan(angle / 2);
    let t = radius / tanHalf;
    t = Math.min(t, lenP / 2, lenN / 2);
    const r = t * tanHalf;

    const Pin = { x: cur.x + (vp.x / lenP) * t, y: cur.y + (vp.y / lenP) * t };
    const Pout = { x: cur.x + (vn.x / lenN) * t, y: cur.y + (vn.y / lenN) * t };

    // Cross product (SVG y-down): convex vertex of a CW polygon → cross < 0
    // → sweep=1 (clockwise arc bulges toward the original vertex). Concave
    // (e.g. star inner) flips the sweep to bulge the opposite way.
    const cross = vp.x * vn.y - vp.y * vn.x;
    const sweep = cross < 0 ? 1 : 0;

    cmds.push((i === 0 ? "M" : "L") + `${Pin.x},${Pin.y}`);
    cmds.push(`A${r},${r} 0 0 ${sweep} ${Pout.x},${Pout.y}`);
  }
  cmds.push("Z");
  return cmds.join(" ");
}

function PolygonEl({ layer }: { layer: Extract<Layer, { type: "polygon" }> }) {
  const sides = Math.max(3, layer.sides);
  const cx = layer.w / 2;
  const cy = layer.h / 2;
  const rx = layer.w / 2;
  const ry = layer.h / 2;
  const sa = strokeAttrs(layer.strokes);
  const cr = layer.cornerRadius ?? 0;

  // Inscribed ellipse axes — at this radius, every vertex's rounding has
  // collapsed and the polygon is geometrically equivalent to the inscribed
  // ellipse (a circle when rx === ry). Switching to <ellipse> gives a clean
  // single curve instead of N arcs that wouldn't align on non-regular
  // (rx ≠ ry) polygons.
  const apothemFactor = Math.cos(Math.PI / sides);
  const inscribedRx = rx * apothemFactor;
  const inscribedRy = ry * apothemFactor;
  const ellipseThreshold = Math.max(inscribedRx, inscribedRy);

  if (cr >= ellipseThreshold) {
    return (
      <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
        <ellipse cx={cx} cy={cy} rx={inscribedRx} ry={inscribedRy} fill={paintToFill(layer.fills)} stroke={sa.stroke} strokeWidth={sa.strokeWidth} />
      </g>
    );
  }

  const points: { x: number; y: number }[] = [];
  for (let i = 0; i < sides; i++) {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / sides;
    points.push({ x: cx + Math.cos(angle) * rx, y: cy + Math.sin(angle) * ry });
  }
  const d = roundedPolygonPath(points, cr);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <path d={d} fill={paintToFill(layer.fills)} stroke={sa.stroke} strokeWidth={sa.strokeWidth} />
    </g>
  );
}

function StarEl({ layer }: { layer: Extract<Layer, { type: "star" }> }) {
  const points = Math.max(3, layer.points);
  // Honor the full Figma range [0, 1]. Previously this clamped to [0.05, 0.95]
  // for "defensive" rendering, which silently diverged from the stored value
  // when the panel input set Ratio to 0% or 100%.
  const inner = Math.max(0, Math.min(1, layer.innerRatio));
  const cx = layer.w / 2;
  const cy = layer.h / 2;
  const rxOuter = layer.w / 2;
  const ryOuter = layer.h / 2;
  const pts: { x: number; y: number }[] = [];
  for (let i = 0; i < points * 2; i++) {
    const angle = -Math.PI / 2 + (i * Math.PI) / points;
    const r = i % 2 === 0 ? 1 : inner;
    pts.push({ x: cx + Math.cos(angle) * rxOuter * r, y: cy + Math.sin(angle) * ryOuter * r });
  }
  const sa = strokeAttrs(layer.strokes);
  const cr = layer.cornerRadius ?? 0;
  const d = roundedPolygonPath(pts, cr);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <path d={d} fill={paintToFill(layer.fills)} stroke={sa.stroke} strokeWidth={sa.strokeWidth} />
    </g>
  );
}

function LineEl({ layer }: { layer: Extract<Layer, { type: "line" }> }) {
  const sa = strokeAttrs(layer.strokes);
  const sw = Math.max(1, sa.strokeWidth || 1);
  return (
    <g transform={commonTransform(layer)} data-id={layer.id} opacity={layer.opacity}>
      <line x1={layer.p1.x} y1={layer.p1.y} x2={layer.p2.x} y2={layer.p2.y} stroke={sa.stroke} strokeWidth={sw} />
    </g>
  );
}

function ArrowEl({ layer }: { layer: Extract<Layer, { type: "arrow" }> }) {
  const sa = strokeAttrs(layer.strokes);
  const sw = Math.max(1, sa.strokeWidth || 1);
  const markerId = `arrow-end-${layer.id}`;
  const startMarkerId = `arrow-start-${layer.id}`;
  return (
    <g transform={commonTransform(layer)} data-id={layer.id} opacity={layer.opacity}>
      <defs>
        {layer.endCapEnd === "arrow" && (
          <marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={sa.stroke} />
          </marker>
        )}
        {layer.endCapStart === "arrow" && (
          <marker id={startMarkerId} viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 10 0 L 0 5 L 10 10 z" fill={sa.stroke} />
          </marker>
        )}
      </defs>
      <line
        x1={layer.p1.x}
        y1={layer.p1.y}
        x2={layer.p2.x}
        y2={layer.p2.y}
        stroke={sa.stroke}
        strokeWidth={sw}
        markerEnd={layer.endCapEnd === "arrow" ? `url(#${markerId})` : undefined}
        markerStart={layer.endCapStart === "arrow" ? `url(#${startMarkerId})` : undefined}
      />
    </g>
  );
}

function TextEl({ layer }: { layer: Extract<Layer, { type: "text" }> }) {
  // Hide the canvas text node while this layer is being edited — TextEditor
  // overlays a contentEditable at the same screen position, and rendering both
  // produces visible double-text artifacts.
  const isEditing = useStore((s) => s.editMode.kind === "text" && s.editMode.layerId === layer.id);
  if (isEditing) return null;
  const fillCol = paintToFill(layer.fills);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <foreignObject x={0} y={0} width={layer.w} height={layer.h}>
        <div
          style={{
            fontFamily: layer.fontFamily,
            fontSize: layer.fontSize,
            fontWeight: layer.fontWeight,
            color: fillCol,
            lineHeight: layer.lineHeight.type === "auto" ? "normal" : `${layer.lineHeight.value}${layer.lineHeight.type === "px" ? "px" : "%"}`,
            textAlign: layer.hAlign,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            overflow: "hidden",
            width: "100%",
            height: "100%",
          }}
        >
          {layer.content}
        </div>
      </foreignObject>
    </g>
  );
}

function VectorEl({ layer }: { layer: Extract<Layer, { type: "vector" }> }) {
  const network = layer.network;
  if (network.vertices.length === 0) return null;
  const sa = strokeAttrs(layer.strokes);
  const d = vectorNetworkToPath(network);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <path d={d} fill={network.closed ? paintToFill(layer.fills) : "none"} stroke={sa.stroke} strokeWidth={sa.strokeWidth || 1} />
    </g>
  );
}

export function vectorNetworkToPath(network: { vertices: { x: number; y: number }[]; segments: { fromIndex: number; toIndex: number; handleFrom: { dx: number; dy: number } | null; handleTo: { dx: number; dy: number } | null }[]; closed: boolean }): string {
  const v = network.vertices;
  if (v.length === 0) return "";
  const parts: string[] = [`M ${v[0].x} ${v[0].y}`];
  for (const s of network.segments) {
    const a = v[s.fromIndex];
    const b = v[s.toIndex];
    if (!a || !b) continue;
    if (s.handleFrom || s.handleTo) {
      const cp1x = a.x + (s.handleFrom?.dx ?? 0);
      const cp1y = a.y + (s.handleFrom?.dy ?? 0);
      const cp2x = b.x + (s.handleTo?.dx ?? 0);
      const cp2y = b.y + (s.handleTo?.dy ?? 0);
      parts.push(`C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${b.x} ${b.y}`);
    } else {
      parts.push(`L ${b.x} ${b.y}`);
    }
  }
  if (network.closed) parts.push("Z");
  return parts.join(" ");
}

function SliceEl({ layer }: { layer: Extract<Layer, { type: "slice" }> }) {
  return (
    <g transform={commonTransform(layer)} data-id={layer.id} opacity={0.6}>
      <rect x={0} y={0} width={layer.w} height={layer.h} fill="transparent" stroke="orange" strokeDasharray="4 3" />
    </g>
  );
}

function GroupEl({ layer }: { layer: Extract<Layer, { type: "frame" | "section" | "group" }> }) {
  const isFrame = layer.type === "frame";
  const isSection = layer.type === "section";
  const fills = isFrame ? layer.fills : isSection ? layer.fills : [];
  const strokes = isFrame ? layer.strokes : [];
  // Frames are always rectangles — corner radius is intentionally ignored
  // even if the model carries a non-zero value.
  const rx = 0;
  const clip = isFrame && layer.clipsContent;
  const clipId = `clip-${layer.id}`;
  const sa = strokeAttrs(strokes);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      {clip && (
        <defs>
          <clipPath id={clipId}>
            <rect x={0} y={0} width={layer.w} height={layer.h} rx={rx} ry={rx} />
          </clipPath>
        </defs>
      )}
      {(isFrame || isSection) && (
        <rect
          x={0}
          y={0}
          width={layer.w}
          height={layer.h}
          rx={rx}
          ry={rx}
          fill={paintToFill(fills)}
          stroke={isFrame ? sa.stroke : "none"}
          strokeWidth={isFrame ? sa.strokeWidth : 0}
        />
      )}
      <g clipPath={clip ? `url(#${clipId})` : undefined}>
        {layer.children.map((c) => (
          <NodeRenderer key={c.id} layer={c} />
        ))}
      </g>
    </g>
  );
}
