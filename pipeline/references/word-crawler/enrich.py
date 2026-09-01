"""Feature-leaf description enrichment (DEPTH.md §4, step 4).

Owner-drawn popup menu-items have no UIA FullDescription tooltip, so a feature/toggle LEAF's meaning
cannot be read off the live control. This stage stamps a curated 1-2 sentence `description` onto each
such leaf from fixtures/feature_descriptions.json. It runs inside the reconciling emitter every crawl,
so descriptions are regenerated with the output — never hand-edited into the JSON. Items that OPEN a
surface (submenu/pane/dialog) are not leaves and are skipped even if a stale entry names them.
"""
import json
import config

_LEAF_KINDS = {"feature", "toggles"}


def _norm(label):
    """Match key: drop trailing dots/ellipsis ('Sentence case.', 'Line Spacing Options…') and
    surrounding space, casefold. Command labels never end in a meaningful period, so stripping the
    whole trailing run of '.'/'…'/space is safe and covers both the gallery-tile and menu forms."""
    return (label or "").strip().rstrip(". …").strip().casefold()


def load_descriptions(path=None):
    """(popup-stem, normalized-label) -> description. Empty dict if the fixture is absent."""
    p = path or (config.FIXTURES / "feature_descriptions.json")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for d in raw.get("descriptions", []):
        out[(d["popup"], _norm(d["label"]))] = d["description"]
    return out


def apply_to_popup(surface_id, doc, table):
    """Stamp descriptions onto feature/toggle leaves of one popup doc. Returns the count applied."""
    if not table or not surface_id.startswith("dropdowns/"):
        return 0
    stem = surface_id.split("/", 1)[1]
    n = 0
    for sec in doc.get("sections", []):
        for it in sec.get("items", []):
            if it.get("action", {}).get("kind") not in _LEAF_KINDS:
                continue
            desc = table.get((stem, _norm(it.get("label"))))
            if desc:
                it["description"] = desc
                n += 1
    return n
