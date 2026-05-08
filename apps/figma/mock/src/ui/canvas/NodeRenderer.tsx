// Renders one Layer as SVG.

import type { Layer, Paint, Stroke, Effect } from "@/types/scene";

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

function paintToFill(fills: Paint[] | undefined): string {
  if (!fills) return "transparent";
  for (const p of fills) {
    if (!p.visible) continue;
    if (p.kind === "solid") return colorToCss(p.color);
    if (p.kind === "image") return "rgba(180,180,180,1)";
  }
  return "transparent";
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
  for (const s of strokes) {
    if (!s.paint.visible) continue;
    if (s.paint.kind !== "solid") continue;
    return {
      stroke: colorToCss(s.paint.color),
      strokeWidth: s.weight,
      strokeDasharray: s.dash ? `${s.dash.dash} ${s.dash.gap}` : undefined,
    };
  }
  return { stroke: "none", strokeWidth: 0 };
}

function RectangleEl({ layer }: { layer: Extract<Layer, { type: "rectangle" | "image" }> }) {
  const fills = "fills" in layer ? layer.fills : undefined;
  const strokes = "strokes" in layer ? layer.strokes : undefined;
  const cr = "cornerRadius" in layer ? layer.cornerRadius : 0;
  const rx = typeof cr === "number" ? cr : 0;
  const sa = strokeAttrs(strokes);
  const eff = effectsToFilter(layer.effects, layer.id);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      {eff?.defs}
      <rect
        x={0}
        y={0}
        width={layer.w}
        height={layer.h}
        rx={rx}
        ry={rx}
        fill={paintToFill(fills)}
        stroke={sa.stroke}
        strokeWidth={sa.strokeWidth}
        strokeDasharray={sa.strokeDasharray}
        filter={eff?.filter}
      />
      {layer.type === "image" && (
        <ImageContent layer={layer} cornerRadius={rx} />
      )}
    </g>
  );
}

function ImageContent({ layer, cornerRadius }: { layer: Extract<Layer, { type: "image" }>; cornerRadius: number }) {
  const clipId = `clip-img-${layer.id}`;
  const fit = layer.imageFill.fit;
  const src = layer.imageFill.src;
  return (
    <>
      <defs>
        <clipPath id={clipId}>
          <rect x={0} y={0} width={layer.w} height={layer.h} rx={cornerRadius} ry={cornerRadius} />
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

function PolygonEl({ layer }: { layer: Extract<Layer, { type: "polygon" }> }) {
  const sides = Math.max(3, layer.sides);
  const cx = layer.w / 2;
  const cy = layer.h / 2;
  const rx = layer.w / 2;
  const ry = layer.h / 2;
  const points: string[] = [];
  for (let i = 0; i < sides; i++) {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / sides;
    points.push(`${cx + Math.cos(angle) * rx},${cy + Math.sin(angle) * ry}`);
  }
  const sa = strokeAttrs(layer.strokes);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <polygon points={points.join(" ")} fill={paintToFill(layer.fills)} stroke={sa.stroke} strokeWidth={sa.strokeWidth} />
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
  const pts: string[] = [];
  for (let i = 0; i < points * 2; i++) {
    const angle = -Math.PI / 2 + (i * Math.PI) / points;
    const r = i % 2 === 0 ? 1 : inner;
    pts.push(`${cx + Math.cos(angle) * rxOuter * r},${cy + Math.sin(angle) * ryOuter * r}`);
  }
  const sa = strokeAttrs(layer.strokes);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <polygon points={pts.join(" ")} fill={paintToFill(layer.fills)} stroke={sa.stroke} strokeWidth={sa.strokeWidth} />
    </g>
  );
}

function LineEl({ layer }: { layer: Extract<Layer, { type: "line" }> }) {
  const sa = strokeAttrs(layer.strokes);
  const stroke = sa.stroke === "none" ? "white" : sa.stroke;
  const sw = Math.max(1, sa.strokeWidth || 1);
  return (
    <g transform={commonTransform(layer)} data-id={layer.id} opacity={layer.opacity}>
      <line x1={layer.p1.x} y1={layer.p1.y} x2={layer.p2.x} y2={layer.p2.y} stroke={stroke} strokeWidth={sw} />
    </g>
  );
}

function ArrowEl({ layer }: { layer: Extract<Layer, { type: "arrow" }> }) {
  const sa = strokeAttrs(layer.strokes);
  const stroke = sa.stroke === "none" ? "white" : sa.stroke;
  const sw = Math.max(1, sa.strokeWidth || 1);
  const markerId = `arrow-end-${layer.id}`;
  const startMarkerId = `arrow-start-${layer.id}`;
  return (
    <g transform={commonTransform(layer)} data-id={layer.id} opacity={layer.opacity}>
      <defs>
        {layer.endCapEnd === "arrow" && (
          <marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={stroke} />
          </marker>
        )}
        {layer.endCapStart === "arrow" && (
          <marker id={startMarkerId} viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 10 0 L 0 5 L 10 10 z" fill={stroke} />
          </marker>
        )}
      </defs>
      <line
        x1={layer.p1.x}
        y1={layer.p1.y}
        x2={layer.p2.x}
        y2={layer.p2.y}
        stroke={stroke}
        strokeWidth={sw}
        markerEnd={layer.endCapEnd === "arrow" ? `url(#${markerId})` : undefined}
        markerStart={layer.endCapStart === "arrow" ? `url(#${startMarkerId})` : undefined}
      />
    </g>
  );
}

function TextEl({ layer }: { layer: Extract<Layer, { type: "text" }> }) {
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
  const stroke = sa.stroke === "none" ? "white" : sa.stroke;
  const d = vectorNetworkToPath(network);
  return (
    <g transform={commonTransform(layer)} opacity={layer.opacity} data-id={layer.id}>
      <path d={d} fill={network.closed ? paintToFill(layer.fills) : "none"} stroke={stroke} strokeWidth={sa.strokeWidth || 1} />
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
  const cr = isFrame ? layer.cornerRadius : 0;
  const rx = typeof cr === "number" ? cr : 0;
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
