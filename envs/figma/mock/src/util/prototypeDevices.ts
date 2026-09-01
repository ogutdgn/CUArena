// Derived from framePresets.ts — single source of truth for device dimensions.
// PrototypePreview uses `kind` for frame rendering; PrototypePanel uses the
// flat list for device lookup. Do not add devices here — edit framePresets.ts.

import { getDeviceCategories, type DeviceKind } from "@/util/framePresets";

export interface ProtoDevice {
  id: string;
  label: string;
  w: number;
  h: number;
  kind: DeviceKind;
}

export const PROTOTYPE_DEVICES: ProtoDevice[] = getDeviceCategories().flatMap((cat) =>
  cat.presets.map((p) => ({
    id: p.id,
    label: p.label,
    w: p.w,
    h: p.h,
    kind: cat.deviceKind!,
  })),
);

export function findDevice(id: string | null): ProtoDevice | null {
  if (!id) return null;
  return PROTOTYPE_DEVICES.find((d) => d.id === id) ?? null;
}
