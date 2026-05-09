let counter = 0;

export function uid(prefix = "n"): string {
  counter += 1;
  const r = Math.random().toString(36).slice(2, 8);
  return `${prefix}_${Date.now().toString(36)}_${counter}_${r}`;
}

export function shortUid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function randomHexByte(): string {
  return Math.floor(Math.random() * 256)
    .toString(16)
    .padStart(2, "0");
}

function randomUuidV4Fallback(): string {
  // RFC4122-ish fallback when crypto APIs are unavailable.
  const bytes = Array.from({ length: 16 }, () => parseInt(randomHexByte(), 16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.map((b) => b.toString(16).padStart(2, "0"));
  return [
    hex.slice(0, 4).join(""),
    hex.slice(4, 6).join(""),
    hex.slice(6, 8).join(""),
    hex.slice(8, 10).join(""),
    hex.slice(10, 16).join(""),
  ].join("-");
}

export function randomUuidV4(): string {
  if (typeof crypto !== "undefined") {
    if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
    if (typeof crypto.getRandomValues === "function") {
      const bytes = new Uint8Array(16);
      crypto.getRandomValues(bytes);
      bytes[6] = (bytes[6] & 0x0f) | 0x40;
      bytes[8] = (bytes[8] & 0x3f) | 0x80;
      const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0"));
      return [
        hex.slice(0, 4).join(""),
        hex.slice(4, 6).join(""),
        hex.slice(6, 8).join(""),
        hex.slice(8, 10).join(""),
        hex.slice(10, 16).join(""),
      ].join("-");
    }
  }
  return randomUuidV4Fallback();
}

export function createSessionId(): string {
  return `session_${randomUuidV4()}`;
}
