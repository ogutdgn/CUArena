let counter = 0;

export function uid(prefix = "n"): string {
  counter += 1;
  const r = Math.random().toString(36).slice(2, 8);
  return `${prefix}_${Date.now().toString(36)}_${counter}_${r}`;
}

export function shortUid(): string {
  return Math.random().toString(36).slice(2, 10);
}
