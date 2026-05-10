// Right properties panel. Source: ui-report.md §2.3 + state-matrix.md.

import { useEffect, useRef, useState } from "react";
import { useStore } from "@/engine/store";
import { getSelectedLayers } from "@/engine/selectors";
import { zoomToCustom, zoomToFit, zoomTo100 } from "@/engine/transformCommands";
import { SquarePlay, ChevronDown } from "lucide-react";
import { emitSemantic } from "@/logger/semantic";
import { PageSection } from "@/ui/panels/PageSection";
import { PositionSection } from "@/ui/panels/PositionSection";
import { LayoutSection } from "@/ui/panels/LayoutSection";
import { AppearanceSection } from "@/ui/panels/AppearanceSection";
import { TypographySection } from "@/ui/panels/TypographySection";
import { FillSection } from "@/ui/panels/FillSection";
import { StrokeSection } from "@/ui/panels/StrokeSection";
import { EffectsSection } from "@/ui/panels/EffectsSection";
import { PrototypePanel } from "@/ui/panels/PrototypePanel";
import { FramePresetsPanel } from "@/ui/panels/FramePresetsPanel";

export function RightPanel() {
  const selection = useStore((s) => getSelectedLayers(s));
  const activeTab = useStore((s) => s.activeRightTab);
  const activeTool = useStore((s) => s.activeTool);

  function openPreview() {
    const wasOpen = !!useStore.getState().prototypePreview;
    useStore.setState((st) => {
      if (st.prototypePreview) {
        st.prototypePreview = null;
      } else {
        st.prototypePreview = { pos: { x: 120, y: 80 }, flowIndex: 0 };
      }
    });
    emitSemantic(wasOpen
      ? { name: "close_prototype_preview", trigger: "play_button_toggle" }
      : { name: "open_prototype_preview", trigger: "play_button" }
    );
  }

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
        minHeight: 0,
        overflow: "hidden",
      }}
    >
      <Header onPresent={openPreview} />
      <Tabs />
      <div className="scroll-y" style={{ flex: 1, minHeight: 0 }}>
        {activeTool === "frame" ? (
          <FramePresetsPanel />
        ) : activeTab === "prototype" ? (
          <PrototypePanel />
        ) : selection.length === 0 ? (
          activeTool === "frame" ? (
            <FramePresetBrowser onPick={createFrameFromPreset} />
          ) : (
            <PageSection />
          )
        ) : (
          <>
            <PositionSection />
            <LayoutSection />
            <AppearanceSection />
            <TypographySection />
            <FillSection />
            <StrokeSection />
            <EffectsSection />
          </>
        )}
      </div>
    </aside>
  );
}

function Header({ onPresent }: { onPresent: () => void }) {
  return (
    <div
      style={{
        height: 32,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 8px",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      <button
        data-id="right-panel.present"
        onClick={onPresent}
        title="Preview prototype"
        style={{
          height: 24,
          padding: "0 10px",
          borderRadius: 6,
          background: "transparent",
          color: "var(--color-text-secondary)",
          display: "flex",
          alignItems: "center",
          gap: 5,
          fontSize: "var(--fs-sm)",
          fontWeight: 500,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      >
        <SquarePlay size={14} />
        Preview
      </button>
    </div>
  );
}

function ZoomControl() {
  const zoom = useStore((s) => s.viewportByPage[s.activePageId]?.zoom ?? 1);
  const [draft, setDraft] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function onDoc(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", onDoc, true);
    return () => document.removeEventListener("mousedown", onDoc, true);
  }, [menuOpen]);

  useEffect(() => {
    if (menuOpen) {
      setDraft(String(Math.round(zoom * 100)));
      requestAnimationFrame(() => { inputRef.current?.focus(); inputRef.current?.select(); });
    }
  }, [menuOpen]);

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        data-id="zoom-view-options.open"
        onClick={() => setMenuOpen((o) => !o)}
        title="View options"
        style={{
          height: 24, padding: "0 6px", borderRadius: 4,
          color: "var(--color-text-secondary)", fontSize: "var(--fs-sm)",
          display: "flex", alignItems: "center", gap: 2,
          background: menuOpen ? "var(--color-bg-row-active)" : "transparent",
        }}
        onMouseEnter={(e) => { if (!menuOpen) e.currentTarget.style.background = "var(--color-bg-row-hover)"; }}
        onMouseLeave={(e) => { if (!menuOpen) e.currentTarget.style.background = "transparent"; }}
      >
        {Math.round(zoom * 100)}%
        <ChevronDown size={11} style={{ transition: "transform 100ms ease", transform: menuOpen ? "rotate(180deg)" : undefined }} />
      </button>

      {menuOpen && (
        <div
          style={{
            position: "absolute",
            top: 28,
            right: 0,
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
          {/* Inline zoom input at the top */}
          <div style={{ padding: "4px 4px 6px" }}>
            <input
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={() => {
                const n = parseFloat(draft);
                if (Number.isFinite(n)) zoomToCustom(n, "input_field");
                setMenuOpen(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                if (e.key === "Escape") setMenuOpen(false);
              }}
              style={{
                width: "100%", height: 28, boxSizing: "border-box",
                background: "var(--color-bg-input)",
                border: "1.5px solid var(--color-selection-blue)",
                borderRadius: 4, outline: 0,
                color: "var(--color-text-primary)",
                padding: "0 8px", fontSize: "var(--fs-sm)",
              }}
            />
          </div>
          <ZoomMenuItem id="zoom.zoom-in"  label="Zoom in"       shortcut="⌘+" onClick={() => { setMenuOpen(false); zoomToCustom((zoom * 1.2) * 100, "input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-out" label="Zoom out"      shortcut="⌘−" onClick={() => { setMenuOpen(false); zoomToCustom((zoom / 1.2) * 100, "input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-fit" label="Zoom to fit"   shortcut="⇧1" onClick={() => { setMenuOpen(false); zoomToFit("dropdown_entry"); }} />
          <ZoomMenuItem id="zoom.zoom-50"  label="Zoom to 50%"                 onClick={() => { setMenuOpen(false); zoomToCustom(50, "input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-100" label="Zoom to 100%"  shortcut="⌘0" onClick={() => { setMenuOpen(false); zoomTo100("input_field"); }} />
          <ZoomMenuItem id="zoom.zoom-200" label="Zoom to 200%"                onClick={() => { setMenuOpen(false); zoomToCustom(200, "input_field"); }} />
        </div>
      )}
    </div>
  );
}

function ZoomMenuItem({ id, label, shortcut, onClick }: { id: string; label: string; shortcut?: string; onClick?: () => void }) {
  return (
    <button
      data-id={id}
      // Prevent focus shift on mousedown — without this, the zoom input above
      // blurs, its onBlur runs setMenuOpen(false) and the menu unmounts before
      // this button's click fires, swallowing the action.
      onMouseDown={(e) => e.preventDefault()}
      onClick={() => onClick?.()}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        height: 26,
        padding: "0 8px",
        borderRadius: 4,
        color: "var(--color-text-primary)",
        background: "transparent",
        textAlign: "left",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      <span style={{ flex: 1 }}>{label}</span>
      {shortcut && <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)" }}>{shortcut}</span>}
    </button>
  );
}



function Tabs() {
  const activeTab = useStore((s) => s.activeRightTab);

  function switchTab(tab: "design" | "prototype") {
    const before = useStore.getState().activeRightTab;
    if (before === tab) return;
    useStore.setState((s) => { s.activeRightTab = tab; });
    emitSemantic({ name: "prototype_tab_switch", before, after: tab, trigger: "tab_click" });
  }

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
      <Tab id="right-panel.tab.design" label="Design" active={activeTab === "design"} onClick={() => switchTab("design")} />
      <Tab id="right-panel.tab.prototype" label="Prototype" active={activeTab === "prototype"} onClick={() => switchTab("prototype")} />
      <div style={{ flex: 1 }} />
      <div style={{ display: "flex", alignItems: "center", paddingRight: 4 }}>
        <ZoomControl />
      </div>
    </div>
  );
}

function Tab({ id, label, active, onClick }: { id: string; label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      data-id={id}
      onClick={onClick}
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

