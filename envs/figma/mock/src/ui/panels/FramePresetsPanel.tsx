import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { FRAME_CATEGORIES } from "@/util/framePresets";
import { createFrameFromPreset } from "@/engine/framePresetCommands";

export function FramePresetsPanel() {
  const [openCat, setOpenCat] = useState<string | null>("phone");

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div
        style={{
          padding: "10px 12px 8px",
          fontSize: "var(--fs-sm)",
          fontWeight: 600,
          color: "var(--color-text-primary)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        Frame
      </div>

      {FRAME_CATEGORIES.map((cat) => {
        const isOpen = openCat === cat.id;
        return (
          <div key={cat.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
            {/* Category header */}
            <button
              onClick={() => setOpenCat(isOpen ? null : cat.id)}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "8px 12px",
                color: "var(--color-text-primary)",
                fontSize: "var(--fs-sm)",
                fontWeight: 500,
                textAlign: "left",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              {isOpen
                ? <ChevronDown size={12} color="var(--color-text-secondary)" />
                : <ChevronRight size={12} color="var(--color-text-secondary)" />
              }
              {cat.label}
            </button>

            {/* Preset rows */}
            {isOpen && (
              <div style={{ paddingBottom: 4 }}>
                {cat.presets.map((preset) => (
                  <button
                    key={preset.id}
                    data-id={`frame-preset.${preset.id}`}
                    onClick={() => createFrameFromPreset(preset.id)}
                    style={{
                      width: "100%",
                      display: "flex",
                      alignItems: "center",
                      padding: "5px 12px 5px 30px",
                      color: "var(--color-text-primary)",
                      fontSize: "var(--fs-sm)",
                      textAlign: "left",
                      gap: 8,
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-row-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                  >
                    <span style={{ flex: 1 }}>{preset.label}</span>
                    <span style={{ color: "var(--color-text-muted)", fontSize: "var(--fs-xs)", flexShrink: 0 }}>
                      {preset.w}×{preset.h}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
