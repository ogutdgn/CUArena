import re, unicodedata

# Characters that don't decompose with NFKD but should fold to ASCII
_DOTLESS_I_TRANSLATE = str.maketrans({"ı": "i", "İ": "i"})

def slug(text: str) -> str:
    t = text.translate(_DOTLESS_I_TRANSLATE)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t[:60].strip("-") or "unnamed"

def element_id(container_id: str, label: str, ordinal: int) -> str:
    base = f"el:{container_id.removeprefix('ui:')}/{slug(label)}"
    return f"{base}-{ordinal}" if ordinal else base
