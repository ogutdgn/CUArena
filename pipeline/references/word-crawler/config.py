import os, time, pathlib

HERE = pathlib.Path(__file__).resolve().parent          # crawler/
PROJECT_ROOT = HERE.parent                               # ms-word-ui-structure/
OUTPUT_ROOT = PROJECT_ROOT / "output" / "ui-structure"   # our crawl results land here
FIXTURES = PROJECT_ROOT / "fixtures"                     # input docx the crawler opens
ORACLE = PROJECT_ROOT / "oracle"                         # verification refs (NOT our results)
SCHEMA_VERSION = 1
# PINNED PARITY BUILD (reconciled 2026-07-06, DESIGN section 3.4 "Build lock"): 16.0.20131,
# prefix-matched (patch revisions tolerated). Supersedes the original 16.0.20026.20168 pin after
# Office Current Channel auto-updated this machine past it. WordSession COM-asserts this prefix at
# every launch, so any future minor-version drift fails the run loudly instead of silently changing
# ground truth. manifest.build records the exact build per run.
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

# WINDOW-level boundaries: child windows that are WEB-HOSTED choosers whose body UIA cannot
# meaningfully enumerate (the Insert Pictures chooser exposed only its emoji-feedback chrome; its
# UIA Name can read 'Picture Bullet' while the win32 text says 'Insert Pictures'). Matched
# casefolded against the child's win32 text OR UIA name, and only for NUIDialog-class windows so a
# classic SDM dialog with a coincidental title can never be excluded.
BOUNDARY_WINDOW_TITLES = {
    "insert pictures": {"policy": "excluded", "decision": "D8", "kind": "web-hosted-chooser"},
    "picture bullet":  {"policy": "excluded", "decision": "D8", "kind": "web-hosted-chooser"},
}


def boundary_for(control_id: str):
    if control_id in BOUNDARIES:
        return BOUNDARIES[control_id]
    for pre, val in BOUNDARY_PREFIXES.items():
        if control_id.startswith(pre):
            return val
    return None
