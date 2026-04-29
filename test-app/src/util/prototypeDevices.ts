export interface ProtoDevice {
  id: string;
  label: string;
  w: number;
  h: number;
  kind: "phone" | "tablet" | "desktop";
}

export const PROTOTYPE_DEVICES: ProtoDevice[] = [
  { id: "iphone17",        label: "iPhone 17",          w: 402, h: 874,  kind: "phone" },
  { id: "iphone17pro",     label: "iPhone 17 Pro",      w: 402, h: 874,  kind: "phone" },
  { id: "iphone17promax",  label: "iPhone 17 Pro Max",  w: 440, h: 956,  kind: "phone" },
  { id: "iphoneair",       label: "iPhone Air",         w: 420, h: 912,  kind: "phone" },
  { id: "iphone16",        label: "iPhone 16",          w: 393, h: 852,  kind: "phone" },
  { id: "iphone16pro",     label: "iPhone 16 Pro",      w: 402, h: 874,  kind: "phone" },
  { id: "iphone16promax",  label: "iPhone 16 Pro Max",  w: 440, h: 956,  kind: "phone" },
  { id: "iphone16plus",    label: "iPhone 16 Plus",     w: 430, h: 932,  kind: "phone" },
  { id: "iphone15pro",     label: "iPhone 15 Pro",      w: 393, h: 852,  kind: "phone" },
  { id: "iphone15",        label: "iPhone 15",          w: 393, h: 852,  kind: "phone" },
  { id: "iphone15promax",  label: "iPhone 15 Pro Max",  w: 430, h: 932,  kind: "phone" },
  { id: "iphone15plus",    label: "iPhone 15 Plus",     w: 430, h: 932,  kind: "phone" },
  { id: "iphone14plus",    label: "iPhone 14 Plus",     w: 428, h: 926,  kind: "phone" },
  { id: "iphone14promax",  label: "iPhone 14 Pro Max",  w: 430, h: 932,  kind: "phone" },
  { id: "iphone14pro",     label: "iPhone 14 Pro",      w: 393, h: 852,  kind: "phone" },
  { id: "iphone14",        label: "iPhone 14",          w: 390, h: 844,  kind: "phone" },
  { id: "androidcompact",  label: "Android Compact",    w: 412, h: 917,  kind: "phone" },
  { id: "androidmedium",   label: "Android Medium",     w: 700, h: 840,  kind: "phone" },
  { id: "ipadmini83",      label: "iPad mini 8.3",      w: 744, h: 1133, kind: "tablet" },
  { id: "surfacepro8",     label: "Surface Pro 8",      w: 1440, h: 960, kind: "desktop" },
];

export function findDevice(id: string | null): ProtoDevice | null {
  if (!id) return null;
  return PROTOTYPE_DEVICES.find((d) => d.id === id) ?? null;
}
