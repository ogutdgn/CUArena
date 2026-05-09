// Design tokens. Dark default. Light variant TBD via ThemeProvider switch.
// Defaults sourced from .analysis/ui-report.md §7 BLOCKER list and DEFER list.

export const tokens = {
  // Sizing
  leftPanelDefaultWidth: 240,
  leftPanelMinWidth: 200,
  leftPanelMaxWidth: 480,
  rightPanelDefaultWidth: 240,
  rightPanelMinWidth: 200,
  rightPanelMaxWidth: 400,
  toolbarHeight: 40,
  toolbarBottomGap: 12,

  // Type
  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif',
  fontSize: {
    xs: 11,
    sm: 12,
    base: 13,
    md: 14,
    lg: 16,
  },

  // Radii
  radius: {
    sm: 4,
    md: 6,
    lg: 8,
    pill: 9999,
  },

  // Z-stack
  z: {
    base: 0,
    canvasOverlay: 10,
    toolbar: 20,
    panelHeader: 30,
    dropdown: 100,
    modal: 200,
    toast: 300,
    devLogger: 400,
  },

  // Animation
  duration: {
    instant: 0,
    quick: 80,
    base: 140,
  },
};

// Dark theme color tokens
export const darkColors = {
  // Surfaces
  bgCanvas: "#1E1E1E",
  bgPanel: "#2C2C2C",
  bgPanelElevated: "#383838",
  bgToolbar: "#2C2C2C",
  bgToolbarPill: "#383838",
  bgInput: "#383838",
  bgInputHover: "#444444",
  bgRowHover: "rgba(255,255,255,0.06)",
  bgRowActive: "rgba(13,153,255,0.16)",
  bgScrim: "rgba(0,0,0,0.5)",

  // Borders / dividers
  border: "#3D3D3D",
  borderStrong: "#4A4A4A",
  divider: "#333333",

  // Text
  textPrimary: "#E5E5E5",
  textSecondary: "#A0A0A0",
  textMuted: "#777777",
  textDisabled: "#555555",
  textOnAccent: "#FFFFFF",
  textPlaceholder: "#666666",

  // Accent / selection
  selectionBlue: "#0D99FF",
  selectionBlueHover: "#3CB0FF",
  selectionBlueAlpha: "rgba(13,153,255,0.18)",

  // Status
  destructive: "#E5484D",
  warning: "#F7A23E",
  success: "#30A46C",

  // Page backgrounds (shown in canvas)
  pageBgDefault: "#FFFFFF",
};

export type ColorToken = keyof typeof darkColors;

export function cssVars(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(darkColors)) {
    out[`--color-${k.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase())}`] = v;
  }
  out["--font-family"] = tokens.fontFamily;
  out["--toolbar-height"] = `${tokens.toolbarHeight}px`;
  return out;
}
