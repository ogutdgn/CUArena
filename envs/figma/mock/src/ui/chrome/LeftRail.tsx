// Left rolling navigation rail. Source: ui-report.md §2.2 (left-nav-rail).
// All entries are visual-only.

import { Layers, Variable, Search, Bell } from "lucide-react";
import { noopClick } from "./noopClick";

export function LeftRail() {
  return (
    <aside
      className="no-select"
      data-id="left-rail"
      style={{
        width: "var(--left-rail-width)",
        background: "var(--color-bg-panel)",
        borderRight: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
        paddingTop: 8,
        paddingBottom: 8,
      }}
    >
      <RailButton id="left-rail.layers" icon={<Layers size={16} />} label="Layers" />
      <RailButton id="left-rail.assets" icon={<Variable size={16} />} label="Assets" />
      <RailButton id="left-rail.find-replace" icon={<Search size={16} />} label="Find" />
      <div style={{ flex: 1 }} />
      <RailButton id="left-rail.notifications" icon={<Bell size={16} />} label="Notifications" />
    </aside>
  );
}

function RailButton({ id, icon, label }: { id: string; icon: React.ReactNode; label: string }) {
  return (
    <button
      data-id={id}
      title={`${label} — not implemented in this mock`}
      onClick={(e) => noopClick(id, e)}
      style={{
        width: 32,
        height: 32,
        borderRadius: "var(--radius-md)",
        display: "grid",
        placeItems: "center",
        color: "var(--color-text-secondary)",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      {icon}
    </button>
  );
}
