export interface FramePreset {
  id: string;
  label: string;
  w: number;
  h: number;
}

export type DeviceKind = "phone" | "tablet" | "desktop" | "watch";

export interface FrameCategory {
  id: string;
  label: string;
  presets: FramePreset[];
  /** Present only for device-like categories (phone/tablet/desktop/watch). */
  deviceKind?: DeviceKind;
}

/** Category IDs shown in the prototype device dropdown. */
export const DEVICE_CATEGORY_IDS = ["phone", "tablet", "desktop", "watch"] as const;

/** Subset of FRAME_CATEGORIES that represent selectable prototype devices. */
export function getDeviceCategories() {
  return FRAME_CATEGORIES.filter((c) => c.deviceKind != null);
}

export const FRAME_CATEGORIES: FrameCategory[] = [
  {
    id: "phone",
    label: "Phone",
    deviceKind: "phone",
    presets: [
      { id: "iphone17",           label: "iPhone 17",               w: 402,  h: 874  },
      { id: "iphone16-17pro",     label: "iPhone 16 & 17 Pro",      w: 402,  h: 874  },
      { id: "iphone16",           label: "iPhone 16",               w: 393,  h: 852  },
      { id: "iphone16-17promax",  label: "iPhone 16 & 17 Pro Max",  w: 440,  h: 956  },
      { id: "iphone16plus",       label: "iPhone 16 Plus",          w: 430,  h: 932  },
      { id: "iphoneair",          label: "iPhone Air",              w: 420,  h: 912  },
      { id: "iphone14-15promax",  label: "iPhone 14 & 15 Pro Max",  w: 430,  h: 932  },
      { id: "iphone14-15pro",     label: "iPhone 14 & 15 Pro",      w: 393,  h: 852  },
      { id: "iphone13-14",        label: "iPhone 13 & 14",          w: 390,  h: 844  },
      { id: "iphone14plus",       label: "iPhone 14 Plus",          w: 428,  h: 926  },
      { id: "androidcompact",     label: "Android Compact",         w: 412,  h: 917  },
      { id: "androidmedium",      label: "Android Medium",          w: 700,  h: 840  },
    ],
  },
  {
    id: "tablet",
    label: "Tablet",
    deviceKind: "tablet",
    presets: [
      { id: "ipadmini83",         label: "iPad mini 8.3",           w: 744,  h: 1133 },
      { id: "surfacepro8",        label: "Surface Pro 8",           w: 1440, h: 960  },
      { id: "ipadpro11",          label: 'iPad Pro 11"',            w: 834,  h: 1194 },
      { id: "ipadpro129",         label: 'iPad Pro 12.9"',          w: 1024, h: 1366 },
      { id: "androidexpanded",    label: "Android Expanded",        w: 1280, h: 800  },
    ],
  },
  {
    id: "desktop",
    label: "Desktop",
    deviceKind: "desktop",
    presets: [
      { id: "macbookair",         label: "MacBook Air",             w: 1280, h: 832  },
      { id: "macbookpro14",       label: 'MacBook Pro 14"',         w: 1512, h: 982  },
      { id: "macbookpro16",       label: 'MacBook Pro 16"',         w: 1728, h: 1117 },
      { id: "desktop",            label: "Desktop",                 w: 1440, h: 1024 },
      { id: "wireframes",         label: "Wireframes",              w: 1440, h: 1024 },
      { id: "tv",                 label: "TV",                      w: 1280, h: 720  },
    ],
  },
  {
    id: "presentation",
    label: "Presentation",
    presets: [
      { id: "slide169",           label: "Slide 16:9",              w: 1920, h: 1080 },
      { id: "slide43",            label: "Slide 4:3",               w: 1024, h: 768  },
    ],
  },
  {
    id: "watch",
    label: "Watch",
    deviceKind: "watch",
    presets: [
      { id: "applewatch-s10-42",  label: "Apple Watch Series 10 42mm", w: 187, h: 223 },
      { id: "applewatch-s10-46",  label: "Apple Watch Series 10 46mm", w: 208, h: 248 },
      { id: "applewatch41",       label: "Apple Watch 41mm",           w: 176, h: 215 },
      { id: "applewatch45",       label: "Apple Watch 45mm",           w: 198, h: 242 },
      { id: "applewatch44",       label: "Apple Watch 44mm",           w: 184, h: 224 },
      { id: "applewatch40",       label: "Apple Watch 40mm",           w: 162, h: 197 },
    ],
  },
  {
    id: "paper",
    label: "Paper",
    presets: [
      { id: "a4",                 label: "A4",                      w: 595,  h: 842  },
      { id: "a5",                 label: "A5",                      w: 420,  h: 595  },
      { id: "a6",                 label: "A6",                      w: 297,  h: 420  },
      { id: "letter",             label: "Letter",                  w: 612,  h: 792  },
      { id: "tabloid",            label: "Tabloid",                 w: 792,  h: 1224 },
    ],
  },
  {
    id: "social",
    label: "Social media",
    presets: [
      { id: "twitter-post",       label: "Twitter post",            w: 1200, h: 675  },
      { id: "twitter-header",     label: "Twitter header",          w: 1500, h: 500  },
      { id: "facebook-post",      label: "Facebook post",           w: 1200, h: 630  },
      { id: "facebook-cover",     label: "Facebook cover",          w: 820,  h: 312  },
      { id: "instagram-post",     label: "Instagram post",          w: 1080, h: 1350 },
      { id: "instagram-story",    label: "Instagram story",         w: 1080, h: 1920 },
      { id: "dribbble",           label: "Dribbble shot",           w: 400,  h: 300  },
      { id: "dribbble-hd",        label: "Dribbble shot HD",        w: 800,  h: 600  },
      { id: "linkedin-cover",     label: "LinkedIn cover",          w: 1584, h: 396  },
    ],
  },
  {
    id: "figma-community",
    label: "Figma Community",
    presets: [
      { id: "plugin-icon",        label: "Plugin icon",             w: 128,  h: 128  },
      { id: "profile-banner",     label: "Profile banner",          w: 1680, h: 240  },
      { id: "plugin-cover",       label: "Plugin / file cover",     w: 1920, h: 1080 },
    ],
  },
  {
    id: "archive",
    label: "Archive",
    presets: [
      { id: "iphone13mini",       label: "iPhone 13 mini",          w: 375,  h: 812  },
      { id: "iphonese",           label: "iPhone SE",               w: 320,  h: 568  },
      { id: "iphone13promax",     label: "iPhone 13 Pro Max",       w: 428,  h: 926  },
      { id: "iphone13",           label: "iPhone 13 / 13 Pro",      w: 390,  h: 844  },
      { id: "iphone11promax",     label: "iPhone 11 Pro Max",       w: 414,  h: 896  },
      { id: "iphone11pro",        label: "iPhone 11 Pro / X",       w: 375,  h: 812  },
      { id: "iphone8plus",        label: "iPhone 8 Plus",           w: 414,  h: 736  },
      { id: "iphone8",            label: "iPhone 8",                w: 375,  h: 667  },
      { id: "android-small",      label: "Android Small",           w: 360,  h: 640  },
      { id: "android-large",      label: "Android Large",           w: 360,  h: 800  },
      { id: "pixel2",             label: "Google Pixel 2",          w: 411,  h: 731  },
      { id: "pixel2xl",           label: "Google Pixel 2 XL",       w: 411,  h: 823  },
      { id: "ipadmini5",          label: "iPad mini 5",             w: 768,  h: 1024 },
      { id: "surfacepro4",        label: "Surface Pro 4",           w: 1368, h: 912  },
      { id: "macbook",            label: "MacBook",                 w: 1152, h: 700  },
      { id: "macbookpro",         label: "MacBook Pro",             w: 1440, h: 900  },
      { id: "surfacebook",        label: "Surface Book",            w: 1500, h: 1000 },
      { id: "applewatch42",       label: "Apple Watch 42mm",        w: 156,  h: 195  },
      { id: "applewatch38",       label: "Apple Watch 38mm",        w: 136,  h: 170  },
      { id: "imac",               label: "iMac",                    w: 1280, h: 720  },
      { id: "macintosh128k",      label: "Macintosh 128k",          w: 512,  h: 342  },
    ],
  },
];

export function findFramePreset(id: string): FramePreset | null {
  for (const cat of FRAME_CATEGORIES) {
    const p = cat.presets.find((x) => x.id === id);
    if (p) return p;
  }
  return null;
}
