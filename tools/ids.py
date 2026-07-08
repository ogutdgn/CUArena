import re, unicodedata

def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t[:60].strip("-") or "unnamed"

def element_id(container_id: str, label: str, ordinal: int) -> str:
    base = f"el:{container_id.removeprefix('ui:')}/{slug(label)}"
    return f"{base}-{ordinal}" if ordinal else base
