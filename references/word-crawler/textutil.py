"""UIA text sanitization (KNOWN_GAPS C1/C2/C3).

Raw UIA Name/HelpText strings carry control characters, collapsed-whitespace noise, and
disabled/gallery-state suffixes that must not reach the emitted JSON.
"""
import re
import unicodedata

# Trailing UIA state suffixes appended to a disabled/stateful control's Name.
_STATE_SUFFIXES = ("(No Data)", "(Disabled)", "(disabled)")
# Chrome/scrollbar names that are not real UI content. Owner-drawn popups sometimes expose their
# vertical scrollbar's part buttons in the UIA tree; those leak in as fake menu-items.
_CHROME_NAMES = {"gallery filters", "gallery filter",
                 "line up", "line down", "page up", "page down",
                 "column left", "column right", "row up", "row down"}
_CTRL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_WS = re.compile(r"\s+")


def sanitize_label(s):
    """Strip control chars, collapse whitespace, drop trailing UIA state suffixes."""
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = _CTRL_CHARS.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    for suf in _STATE_SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)].strip()
    return s


def is_chrome(name):
    """True for UIA gallery-chrome pseudo-items ('Gallery Filters', empty/space-only titles)."""
    n = sanitize_label(name).lower()
    return (not n) or n in _CHROME_NAMES
