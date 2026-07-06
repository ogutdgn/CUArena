import re

ZONES = {"primary", "flyout", "scroll-up", "scroll-down", "more"}
_SURFACE_KINDS = {"dropdowns", "dialogs", "panes", "canvas", "ribbon"}


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:64]


def control_segment(automation_id: str, label: str) -> str:
    return slugify(automation_id) if automation_id else slugify(label)


def surface_id(kind: str, slug: str) -> str:
    assert kind in _SURFACE_KINDS, kind
    return f"{kind}/{slugify(slug)}"


def node_id(*parts: str, zone: str | None = None) -> str:
    if zone is not None and zone not in ZONES:
        raise ValueError(f"illegal zone suffix: {zone}")
    base = ".".join(slugify(p) for p in parts)
    return f"{base}.{zone}" if zone else base


def sub_addr(surface: str, local: str) -> str:
    assert is_surface_ref(surface), surface
    return f"{surface}#{local}"


def is_surface_ref(s: str) -> bool:
    return bool(re.fullmatch(r"(dropdowns|dialogs|panes|canvas|ribbon)/[a-z0-9\-]+", s))


def is_node_id(s: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9\-]+(\.[a-z0-9\-]+){2,}", s))


def is_sub_addr(s: str) -> bool:
    return "#" in s and is_surface_ref(s.split("#", 1)[0])
