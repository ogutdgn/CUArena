export type FramePresetCategoryId =
  | "phone"
  | "tablet"
  | "desktop"
  | "presentation"
  | "watch"
  | "paper"
  | "social-media"
  | "figma-community"
  | "archive";

export interface FramePreset {
  id: string;
  label: string;
  w: number;
  h: number;
}

export interface FramePresetCategory {
  id: FramePresetCategoryId;
  label: string;
  presets: FramePreset[];
}

// Frozen frame-preset snapshot for this mock (May 2026 baseline).
// Sources used:
// - Figma Help: category taxonomy + desktop example rows
// - User-provided Figma screenshot: phone rows (iPhone/Android names + sizes)
// - Existing mock device rows (for overlap on tablet/desktop)
export const FRAME_PRESET_CATEGORIES: FramePresetCategory[] = [
  {
    id: "phone",
    label: "Phone",
    presets: [
      { id: "phone-iphone-17", label: "iPhone 17", w: 402, h: 874 },
      { id: "phone-iphone-16-17-pro", label: "iPhone 16 & 17 Pro", w: 402, h: 874 },
      { id: "phone-iphone-16", label: "iPhone 16", w: 393, h: 852 },
      { id: "phone-iphone-16-17-pro-max", label: "iPhone 16 & 17 Pro Max", w: 440, h: 956 },
      { id: "phone-iphone-16-plus", label: "iPhone 16 Plus", w: 430, h: 932 },
      { id: "phone-iphone-air", label: "iPhone Air", w: 420, h: 912 },
      { id: "phone-iphone-14-15-pro-max", label: "iPhone 14 & 15 Pro Max", w: 430, h: 932 },
      { id: "phone-iphone-14-15-pro", label: "iPhone 14 & 15 Pro", w: 393, h: 852 },
      { id: "phone-iphone-13-14", label: "iPhone 13 & 14", w: 390, h: 844 },
      { id: "phone-iphone-14-plus", label: "iPhone 14 Plus", w: 428, h: 926 },
      { id: "phone-android-compact", label: "Android Compact", w: 412, h: 917 },
      { id: "phone-android-medium", label: "Android Medium", w: 700, h: 840 },
    ],
  },
  {
    id: "tablet",
    label: "Tablet",
    presets: [
      { id: "tablet-ipad-mini-8-3", label: "iPad mini 8.3", w: 744, h: 1133 },
      { id: "tablet-ipad-pro-11", label: "iPad Pro 11\"", w: 834, h: 1194 },
      { id: "tablet-ipad-pro-13", label: "iPad Pro 13\"", w: 1032, h: 1376 },
      { id: "tablet-surface-pro-8", label: "Surface Pro 8", w: 1440, h: 960 },
    ],
  },
  {
    id: "desktop",
    label: "Desktop",
    presets: [
      { id: "desktop-macbook-air", label: "MacBook Air", w: 1280, h: 832 },
      { id: "desktop-macbook-pro-14", label: "MacBook Pro 14\"", w: 1512, h: 982 },
      { id: "desktop-macbook-pro-16", label: "MacBook Pro 16\"", w: 1728, h: 1117 },
      { id: "desktop-desktop", label: "Desktop", w: 1440, h: 1024 },
      { id: "desktop-wireframe", label: "Wireframe", w: 1440, h: 1024 },
      { id: "desktop-tv", label: "TV", w: 1280, h: 720 },
    ],
  },
  {
    id: "presentation",
    label: "Presentation",
    presets: [
      { id: "presentation-slide-16-9", label: "Slide 16:9", w: 1920, h: 1080 },
      { id: "presentation-slide-4-3", label: "Slide 4:3", w: 1024, h: 768 },
      { id: "presentation-slide-3-2", label: "Slide 3:2", w: 1440, h: 960 },
    ],
  },
  {
    id: "watch",
    label: "Watch",
    presets: [
      { id: "watch-apple-49", label: "Apple Watch 49mm", w: 205, h: 251 },
      { id: "watch-apple-45", label: "Apple Watch 45mm", w: 198, h: 242 },
      { id: "watch-apple-41", label: "Apple Watch 41mm", w: 176, h: 215 },
    ],
  },
  {
    id: "paper",
    label: "Paper",
    presets: [
      { id: "paper-a4", label: "A4", w: 794, h: 1123 },
      { id: "paper-a3", label: "A3", w: 1123, h: 1587 },
      { id: "paper-letter", label: "Letter", w: 816, h: 1056 },
      { id: "paper-legal", label: "Legal", w: 816, h: 1344 },
    ],
  },
  {
    id: "social-media",
    label: "Social Media",
    presets: [
      { id: "social-instagram-post", label: "Instagram Post", w: 1080, h: 1080 },
      { id: "social-instagram-story", label: "Instagram Story", w: 1080, h: 1920 },
      { id: "social-facebook-post", label: "Facebook Post", w: 1200, h: 630 },
      { id: "social-linkedin-post", label: "LinkedIn Post", w: 1200, h: 627 },
      { id: "social-x-post", label: "X Post", w: 1600, h: 900 },
      { id: "social-youtube-thumb", label: "YouTube Thumbnail", w: 1280, h: 720 },
    ],
  },
  {
    id: "figma-community",
    label: "Figma Community",
    presets: [
      { id: "community-file-cover", label: "File Cover", w: 1600, h: 960 },
      { id: "community-plugin-cover", label: "Plugin Cover", w: 1920, h: 960 },
      { id: "community-widget-cover", label: "Widget Cover", w: 1600, h: 960 },
    ],
  },
  {
    id: "archive",
    label: "Archive",
    presets: [
      { id: "archive-iphone-se", label: "iPhone SE", w: 320, h: 568 },
      { id: "archive-iphone-8", label: "iPhone 8", w: 375, h: 667 },
      { id: "archive-iphone-11", label: "iPhone 11", w: 414, h: 896 },
      { id: "archive-desktop-1366", label: "Desktop 1366", w: 1366, h: 768 },
    ],
  },
];

export function findFramePresetById(id: string): FramePreset | null {
  for (const category of FRAME_PRESET_CATEGORIES) {
    for (const preset of category.presets) {
      if (preset.id === id) return preset;
    }
  }
  return null;
}

export function findFramePresetBySize(w: number, h: number): FramePreset | null {
  for (const category of FRAME_PRESET_CATEGORIES) {
    for (const preset of category.presets) {
      if (preset.w === w && preset.h === h) return preset;
    }
  }
  return null;
}
