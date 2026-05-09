import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { FRAME_PRESET_CATEGORIES, type FramePreset } from "@/util/framePresets";

export function FramePresetBrowser({
  onPick,
  variant = "panel",
}: {
  onPick: (preset: FramePreset) => void;
  variant?: "panel" | "menu";
}) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ phone: true });

  function toggleCategory(id: string) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  const isMenu = variant === "menu";

  return (
    <div
      style={{
        padding: isMenu ? 4 : "8px 12px 12px",
        borderBottom: isMenu ? undefined : "1px solid var(--color-divider)",
      }}
    >
      {!isMenu && (
        <div
          style={{
            height: 24,
            color: "var(--color-text-secondary)",
            fontSize: "var(--fs-xs)",
            fontWeight: 600,
            letterSpacing: 0.4,
            textTransform: "uppercase",
            display: "flex",
            alignItems: "center",
          }}
        >
          Frame
        </div>
      )}

      <div
        style={{
          marginTop: isMenu ? 0 : 6,
          maxHeight: isMenu ? 320 : undefined,
          overflowY: isMenu ? "auto" : undefined,
          display: "grid",
          gap: 2,
        }}
      >
        {FRAME_PRESET_CATEGORIES.map((category) => {
          const open = !!expanded[category.id];
          return (
            <div key={category.id}>
              <button
                data-id={`frame-preset.category.${category.id}`}
                onClick={() => toggleCategory(category.id)}
                style={{
                  width: "100%",
                  height: 28,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "0 6px",
                  borderRadius: 4,
                  color: "var(--color-text-secondary)",
                  background: "transparent",
                  textAlign: "left",
                  fontSize: "var(--fs-sm)",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                <span>{category.label}</span>
              </button>

              {open && (
                <div style={{ display: "grid", gap: 1, marginLeft: 14 }}>
                  {category.presets.map((preset) => (
                    <button
                      key={preset.id}
                      data-id={`frame-preset.${preset.id}`}
                      onClick={() => onPick(preset)}
                      style={{
                        width: "100%",
                        minHeight: 28,
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "4px 6px",
                        borderRadius: 4,
                        color: "var(--color-text-primary)",
                        background: "transparent",
                        textAlign: "left",
                        fontSize: "var(--fs-sm)",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                    >
                      <span style={{ flex: 1, minWidth: 0 }}>{preset.label}</span>
                      <span
                        style={{
                          color: "var(--color-text-muted)",
                          fontVariantNumeric: "tabular-nums",
                          flexShrink: 0,
                        }}
                      >
                        {preset.w}x{preset.h}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
