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
    flyout_classes: list[str] = []
    boundaries: Boundaries = Boundaries()
    launch_args: list[str] = []          # extra argv appended after exe; "{fixture}" resolves to fixture's abs path
    fixture: str | None = None           # path (repo-root relative) to a ready-state fixture file
    destructive_label_res: list[str] = []  # per-app/locale extras; code defaults live in pipeline.teardown.DESTRUCTIVE_RES
    discard_label_res: list[str] = []      # per-app/locale extras; code defaults live in pipeline.teardown.DISCARD_RES

def load_app_config(name: str, configs_dir: Path) -> AppConfig:
    p = Path(configs_dir) / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"no app config: {p}")
    return AppConfig.model_validate_json(p.read_text(encoding="utf-8"))
