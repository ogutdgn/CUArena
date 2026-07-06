import os, time, pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "oracle" / "ui-structure"
FIXTURES = REPO_ROOT / "oracle" / "ui-structure-fixtures"
SCHEMA_VERSION = 1
# Re-pinned 2026-07-06 from 16.0.20026 to the live installed build after Office
# auto-updated past the intended freeze (user-approved). ADR-0006 + DESIGN section 3.4
# still cite 16.0.20026.20168 and must be reconciled to this build separately.
BUILD_PREFIX = "16.0.20131"


def new_run_dir() -> pathlib.Path:
    base = pathlib.Path(os.environ.get("UI_CRAWL_RUNS",
        pathlib.Path(os.environ["LOCALAPPDATA"]) / "ui-crawl-runs"))
    rd = base / time.strftime("run-%Y%m%d-%H%M%S")
    rd.mkdir(parents=True, exist_ok=True)
    return rd


BOUNDARIES = {
    "ribbon.file":                  {"policy": "excluded", "decision": "D4", "kind": "opens-backstage"},
    "ribbon.home.voice.dictate":    {"policy": "excluded", "decision": "D8", "kind": "feature"},
    "ribbon.home.voice.read-aloud": {"policy": "excluded", "decision": "D8", "kind": "feature"},
}
# Prefix boundaries. Editor/Adobe-Acrobat pinned from the live Home UIA dump (T6): the Editor
# button's real idMso is 'WritingAssistanceCheckDocument' (not label 'editor'), and the Acrobat
# COM add-in injects an 'Adobe Acrobat' group (Create a PDF) that survived the launch-time
# disconnect -> both boundary-declared (D8) so the crawler never presses them. copilot.* /
# add-ins.* kept from the plan (add-ins.* matches OfficeExtensionsShowAddinFlyout; copilot.* is
# unused on Home in this build -> reported as unused_boundary_config).
BOUNDARY_PREFIXES = {
    "ribbon.home.editor.":        {"policy": "excluded", "decision": "D8", "kind": "opens-pane"},
    "ribbon.home.adobe-acrobat.": {"policy": "excluded", "decision": "D8", "kind": "feature"},
    "ribbon.home.copilot.":       {"policy": "excluded", "decision": "D8", "kind": "opens-pane"},
    "ribbon.home.add-ins.":       {"policy": "excluded", "decision": "D8", "kind": "opens-dialog"},
}
# Seeded after the T6 --dump-tree; teaching-callout / nag window title or class regexes.
NAG_SIGNATURES = [r"(?i)try\s+", r"(?i)what's new", r"(?i)coming soon", r"(?i)get add-ins"]


def boundary_for(control_id: str):
    if control_id in BOUNDARIES:
        return BOUNDARIES[control_id]
    for pre, val in BOUNDARY_PREFIXES.items():
        if control_id.startswith(pre):
            return val
    return None
