import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from prober import classify, Snapshot, zone_point


def _s(**kw):
    d = dict(windows=[("OpusApp", "Doc1 - Word")], popups=[], panes_open=0,
             doc_hash="h0", toggle_state=None, fingerprint={"zoom": 100}, popup_els=[])
    d.update(kw)
    return Snapshot(**d)


BASE = _s()


def test_dialog():
    assert classify(BASE, _s(windows=BASE.windows + [("NUIDialog", "Font")])) == "dialog"


def test_popup():
    assert classify(BASE, _s(popups=["Net UI Tool Window"])) == "popup"


def test_pane():
    assert classify(BASE, _s(panes_open=1)) == "pane"


def test_toggle():
    assert classify(_s(toggle_state=0), _s(toggle_state=1)) == "toggles"


def test_toggle_beats_coincident_popup():
    # a toggle whose state changed must NOT be misclassified as a dropdown when a transient
    # popup-class window (tooltip / live-preview) coincidentally appears during observe (bug #2:
    # aligncenter/subscript/superscript were emitting spurious dropdowns/* refs).
    before = _s(toggle_state=0)
    after = _s(toggle_state=1, popups=["Net UI Tool Window"])
    assert classify(before, after) == "toggles"


def test_dialog_still_beats_toggle():
    # a real modal is unambiguous and outranks a coincident toggle-state read
    before = _s(toggle_state=0)
    after = _s(toggle_state=1, windows=BASE.windows + [("NUIDialog", "Font")])
    assert classify(before, after) == "dialog"


def test_feature():
    assert classify(BASE, _s(doc_hash="h1")) == "feature"


def test_unresolved():
    assert classify(BASE, _s()) == "unresolved"


def test_zone_point_vertical_split():
    # tall split (h>0.9w): primary=top center, flyout=bottom center
    x, y = zone_point((100, 60, 140, 130), "flyout", None)
    assert x == 120 and y > 95


def test_zone_point_children_preferred():
    x, y = zone_point((0, 0, 40, 20), "flyout", [(0, 0, 20, 20), (20, 0, 40, 20)])
    assert x == 30 and y == 10   # center of the second (arrow) child
