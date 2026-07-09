from pipeline.prober import ProbeObservation, classify_probe
from tools.winapp.windows import WinInfo

W = lambda h, t, c: WinInfo(h, t, c)
BASE = [W(1, "Main", "AppClass")]

def obs(new=None, delta=0):
    after = BASE + ([new] if new else [])
    return ProbeObservation(new_window=new, child_delta=delta,
                            before_windows=BASE, after_windows=after)

def test_dialog_class_wins():
    assert classify_probe(obs(new=W(2, "Save As", "#32770")), ["#32770"], []) == "opens-dialog"

def test_flyout_class():
    assert classify_probe(obs(new=W(2, "", "Net UI Tool Window")), ["#32770"], ["Net UI Tool Window"]) == "opens-flyout"

def test_unknown_new_window_is_dialog_by_default():
    assert classify_probe(obs(new=W(2, "Popup", "Weird")), ["#32770"], []) == "opens-dialog"

def test_inline_expansion():
    assert classify_probe(obs(new=None, delta=12), ["#32770"], []) == "expands-inline"

def test_no_effect():
    assert classify_probe(obs(new=None, delta=0), ["#32770"], []) == "no-effect"
