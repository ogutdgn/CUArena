from tools.winapp.windows import classify

def test_classify():
    assert classify("#32770", ["#32770"], ["Net UI Tool Window"]) == "dialog"
    assert classify("Net UI Tool Window", ["#32770"], ["Net UI Tool Window"]) == "flyout"
    assert classify("SomethingElse", ["#32770"], []) == "unknown"
