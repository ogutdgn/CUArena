from pathlib import Path
from pydantic import BaseModel

class Boundaries(BaseModel):
    dismiss_title_res: list[str] = []    # nag windows to close before inspecting
    exclude_labels: list[str] = []       # areas deliberately out of scope (journaled as skips)

class AppConfig(BaseModel):
    name: str
    exe: str                             # path or bare exe resolvable on PATH
    window_title_re: str
    dialog_classes: list[str] = ["#32770"]           # classic Win32 dialog class
    flyout_classes: list[str] = ["Net UI Tool Window", "MsoCommandBarPopup"]
    boundaries: Boundaries = Boundaries()

def load_app_config(name: str, configs_dir: Path) -> AppConfig:
    p = Path(configs_dir) / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"no app config: {p}")
    return AppConfig.model_validate_json(p.read_text(encoding="utf-8"))
