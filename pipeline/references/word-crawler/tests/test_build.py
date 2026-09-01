import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import build

FONT_LAUNCHER = {"name": "Font Settings", "automation_id": "FontDialog",
                 "control_type": "Button", "patterns": ["invoke"],
                 "rect": (100, 60, 120, 80), "help_text": "", "access_key": "Alt, H, FN"}


def test_build_dialog_opener():
    pr = {"class": "dialog", "ref": "dialogs/font", "boundary": None, "probe_mode": "pressed-observed"}
    c = build.build_control(FONT_LAUNCHER, "home", "font", pr,
                            "icons/ribbon/home/fontdialog.png",
                            {"in": "screenshots/ribbon/home.png", "x": 0, "y": 0, "w": 20, "h": 20})
    assert c["id"] == "ribbon.home.font.fontdialog"
    assert c["action"] == {"kind": "opens-dialog", "ref": "dialogs/font"}
    assert c["idMso"] == "FontDialog" and c["type"] == "button"


def test_build_boundary_control_never_needs_ref():
    props = {"name": "Dictate", "automation_id": "Dictate", "control_type": "Button",
             "patterns": ["invoke"], "rect": (1, 2, 3, 4), "help_text": "", "access_key": ""}
    pr = {"class": "boundary", "ref": None,
          "boundary": {"policy": "excluded", "decision": "D8"}, "probe_mode": "boundary-declared"}
    c = build.build_control(props, "home", "voice", pr, None, None)
    assert c["action"]["boundary"]["decision"] == "D8" and "ref" not in c["action"]


def test_derive_split():
    assert build.derive_type({"control_type": "SplitButton", "patterns": ["invoke", "expand_collapse"]}) == "split"
