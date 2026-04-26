// Right properties panel. Source: ui-report.md §2.3 + state-matrix.md.

import { useEffect, useRef, useState } from "react";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { zoomToCustom, zoomToFit, zoomTo100, zoomToSelection } from "@/engine/transformCommands";
import { Play, Share2, ChevronDown } from "lucide-react";
import { noopClick } from "./noopClick";
import { PageSection } from "@/ui/panels/PageSection";
import { PositionSection } from "@/ui/panels/PositionSection";
import { LayoutSection } from "@/ui/panels/LayoutSection";
import { AppearanceSection } from "@/ui/panels/AppearanceSection";
import { TypographySection } from "@/ui/panels/TypographySection";
import { FillSection } from "@/ui/panels/FillSection";
import { StrokeSection } from "@/ui/panels/StrokeSection";
import { EffectsSection } from "@/ui/panels/EffectsSection";
import { ExportSection } from "@/ui/panels/ExportSection";
import { AlignmentRow } from "@/ui/panels/AlignmentRow";

export function RightPanel() {
  const selection = useStore((s) => getSelectedLayers(s));

  return (
    <aside
      data-id="right-panel"
      className="no-select"
      style={{
        width: 240,
        background: "var(--color-bg-panel)",
        borderLeft: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        minWidth: 200,
        maxWidth: 400,
      }}
    >
      <Header />
      <Tabs />
      <SubHeader hasSelection={selection.length > 0} />
      <div className="scroll-y" style={{ flex: 1 }}>
        {selection.length === 0 ? (
          <PageSection />
        ) : (
          <>
            <AlignmentRow />
            <PositionSection />
            <LayoutSection />
            <AppearanceSection />
            <TypographySection />
            <FillSection />
            <StrokeSection />
            <EffectsSection />
            <ExportSection />
          </>
        )}
      </div>
    </aside>
  );
}

function Header() {
  return (
    <div
      style={{
        height: 36,
        display: "flex",
        alignItems: "center",
        padding: "0 8px",
        gap: 6,
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      <ZoomControl />
      <span style={{ flex: 1 }} />
      <ChromeIconButton id="right-panel.avatar.self" label="A" tooltip="Multiplayer — not implemented" />
      <ChromeIconButton id="right-panel.present" icon={<Play size={14} />} tooltip="Present — not implemented" />
      <button
        data-id="right-panel.share"
        onClick={(e) => noopClick("right-panel.share", e)}
        title="Share — not implemented in this mock"
        style={{
          height: 24,
          padding: "0 10px",
          borderRadius: 4,
          background: "var(--color-selection-blue)",
          color: "var(--color-text-on-accent)",
          fontSize: "var(--fs-sm)",
          fontWeight: 600,
          display: "flex",
          alignItems: "center",
          gap: 4,
        }}
      >
        <Share2 size={12} />
        Share
      </button>
    </div>
  );
}

function ZoomControl() {
  const zoom = useStore((s) => s.viewportByPage[s.activePageId]?.zoom ?? 1);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [menuOpen]);

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        data-id="zoom-view-options.open"
        onClick={() => {
          setDraft(String(Math.round(zoom * 100)));
          setEditing(true);
          setMenuOpen(true);
        }}
        title="View options"
        style={{
          height: 24,
          padding: "0 6px",
          borderRadius: 4,
          color: "var(--color-text-secondary)",
          fontSize: "var(--fs-sm)",
          display: "flex",
          alignItems: "center",
          gap: 2,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      >
        {editing ? (
          <input
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={() => {
              const n = parseFloat(draft);
              if (Number.isFinite(n)) zoomToCustom(n, "input_field");
              setEditing(false);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") (e.target as HTMLInputElement).blur();
              if (e.key === "Escape") setEditing(false);
            }}
            onClick={(e) => e.stopPropagation()}
            style={{
              width: 40,
              background: "var(--color-bg-input)",
              border: 0,
              outline: 0,
              borderRadius: 3,
              color: "var(--color-text-primary)",
              padding: "0 4px",
              fontSize: "var(--fs-sm)",
            }}
          />
        ) : (
          <>
            {Math.round(zoom * 100)}%
            <ChevronDown size={11} style={{ transition: "transform 100ms ease", transform: menuOpen ? "rotate(180deg)" : undefined }} />
          </>
        )}
      </button>
      {menuOpen && (
        <div
          style={{
            position: "absolute",
            top: 30,
            left: 0,
            minWidth: 220,
            background: "var(--color-bg-panel-elevated)",
            border: "1px solid var(--color-border-strong)",
            borderRadius: 6,
            boxShadow: "0 12px 28px rgba(0,0,0,0.5)",
            padding: 4,
            zIndex: 100,
            fontSize: "var(--fs-sm)",
          }}
        >
          <ZoomMenuItem id="zoom.zoom-in" label="Zoom in" shortcut="⌘+" onClick={() => { setMenuOpen(false); zoomToCustom((zoom * 1.2) * 100, "input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-out" label="Zoom out" shortcut="⌘−" onClick={() => { setMenuOpen(false); zoomToCustom((zoom / 1.2) * 100, "input_field"); }} />
          <Sep />
          <ZoomMenuItem id="zoom.zoom-100" label="Zoom to 100%" shortcut="⌘0" onClick={() => { setMenuOpen(false); zoomTo100("input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-fit" label="Zoom to fit" shortcut="⌘1" onClick={() => { setMenuOpen(false); zoomToFit("dropdown_entry"); }} />
          <ZoomMenuItem id="zoom.zoom-selection" label="Zoom to selection" shortcut="⌘2" onClick={() => { setMenuOpen(false); zoomToSelection("dropdown_entry"); }} />
          <Sep />
          <ZoomMenuItem id="zoom-view-options.pixel-preview" label="Pixel preview" disabled />
          <ZoomMenuItem id="zoom-view-options.pixel-grid" label="Pixel grid" disabled />
          <ZoomMenuItem id="zoom-view-options.snap-to-pixel" label="Snap to pixel grid" disabled />
          <ZoomMenuItem id="zoom-view-options.layout-guides" label="Layout guides" disabled />
          <ZoomMenuItem id="zoom-view-options.multiplayer-cursors" label="Multiplayer cursors" disabled />
          <ZoomMenuItem id="zoom-view-options.outlines.show" label="Show outlines" disabled />
        </div>
      )}
    </div>
  );
}

function ZoomMenuItem({ id, label, shortcut, onClick, disabled }: { id: string; label: string; shortcut?: string; onClick?: () => void; disabled?: boolean }) {
  return (
    <button
      data-id={id}
      onClick={(e) => {
        if (disabled) {
          noopClick(id, e);
          return;
        }
        onClick?.();
      }}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        height: 26,
        padding: "0 8px",
        borderRadius: 4,
        color: disabled ? "var(--color-text-disabled)" : "var(--color-text-primary)",
        background: "transparent",
        textAlign: "left",
      }}
      onMouseEnter={(e) => {
        if (!disabled) e.currentTarget.style.background = "var(--color-bg-row-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      <span style={{ flex: 1 }}>{label}</span>
      {shortcut && <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{shortcut}</span>}
    </button>
  );
}

function Sep() {
  return <div style={{ height: 1, background: "var(--color-divider)", margin: "4px 0" }} />;
}

function ChromeIconButton({
  id,
  icon,
  label,
  tooltip,
}: {
  id: string;
  icon?: React.ReactNode;
  label?: string;
  tooltip: string;
}) {
  return (
    <button
      data-id={id}
      title={tooltip}
      onClick={(e) => noopClick(id, e)}
      style={{
        width: 24,
        height: 24,
        borderRadius: 12,
        background: label ? "var(--color-selection-blue)" : "transparent",
        color: label ? "var(--color-text-on-accent)" : "var(--color-text-secondary)",
        display: "grid",
        placeItems: "center",
        fontSize: 11,
        fontWeight: 600,
      }}
    >
      {icon ?? label}
    </button>
  );
}

function Tabs() {
  return (
    <div
      style={{
        height: 32,
        display: "flex",
        alignItems: "stretch",
        borderBottom: "1px solid var(--color-border)",
        padding: "0 4px",
      }}
    >
      <Tab id="right-panel.tab.design" label="Design" active />
      <Tab id="right-panel.tab.prototype" label="Prototype" active={false} visualOnly />
    </div>
  );
}

function Tab({
  id,
  label,
  active,
  visualOnly,
}: {
  id: string;
  label: string;
  active: boolean;
  visualOnly?: boolean;
}) {
  return (
    <button
      data-id={id}
      onClick={(e) => visualOnly && noopClick(id, e)}
      style={{
        flex: 1,
        position: "relative",
        color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
        fontSize: "var(--fs-sm)",
        fontWeight: active ? 600 : 500,
      }}
    >
      {label}
      {active && (
        <span
          style={{
            position: "absolute",
            bottom: -1,
            left: 8,
            right: 8,
            height: 2,
            background: "var(--color-text-primary)",
            borderRadius: 2,
          }}
        />
      )}
    </button>
  );
}

function SubHeader({ hasSelection }: { hasSelection: boolean }) {
  if (!hasSelection) return null;
  return (
    <div
      style={{
        height: 32,
        display: "flex",
        alignItems: "center",
        gap: 4,
        padding: "0 8px",
        borderBottom: "1px solid var(--color-border)",
        color: "var(--color-text-secondary)",
        fontSize: "var(--fs-sm)",
      }}
    >
      <SubHeaderButton id="sub-header.mask" label="Mask" />
      <SubHeaderButton id="sub-header.create-component" label="Component" />
      <SubHeaderButton id="sub-header.boolean.open" label="Boolean" />
      <span style={{ flex: 1 }} />
      <SubHeaderButton id="sub-header.more" label="•••" />
    </div>
  );
}

function SubHeaderButton({ id, label }: { id: string; label: string }) {
  return (
    <button
      data-id={id}
      title={`${label} — not implemented in this mock`}
      onClick={(e) => noopClick(id, e)}
      style={{
        height: 22,
        padding: "0 6px",
        borderRadius: 4,
        color: "var(--color-text-muted)",
        fontSize: "var(--fs-xs)",
      }}
    >
      {label}
    </button>
  );
}
