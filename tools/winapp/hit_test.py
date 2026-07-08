from pywinauto import Desktop
from tools.winapp.uia import ElemInfo, _info

def element_at(x: int, y: int) -> ElemInfo:
    return _info(Desktop(backend="uia").from_point(x, y))
