from pathlib import Path
from PIL import Image
from tools.models import UIContainer, AppNode

class KBWriter:
    def __init__(self, kb_root: Path, app: str):
        self.root = Path(kb_root) / app

    def _write_json(self, model, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
        return path

    def write_container(self, c) -> Path:
        c = UIContainer.model_validate(c)                      # refuse bad input BEFORE touching disk
        return self._write_json(c, self.root / "ui" / (c.id.removeprefix("ui:") + ".json"))

    def write_app(self, a) -> Path:
        a = AppNode.model_validate(a)
        return self._write_json(a, self.root / "app.json")

    def save_screenshot(self, img: Image.Image, node_id: str, name: str) -> str:
        sanitized_id = node_id.replace(":", "-")
        rel = f"screenshots/{sanitized_id}/{name}.png"
        out = self.root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return rel
