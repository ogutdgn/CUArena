from pathlib import Path
from PIL import Image
import re
from kernel.models import UIContainer, AppNode, FeatureNode, SubFeatureNode, ShortcutEntry

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

    def write_feature(self, f) -> Path:
        f = FeatureNode.model_validate(f)
        return self._write_json(f, self.root / "features" / (f.id.removeprefix("feature:") + ".json"))

    def write_subfeature(self, s) -> Path:
        s = SubFeatureNode.model_validate(s)
        parent = (s.parent or "feature:_unparented").removeprefix("feature:")
        return self._write_json(s, self.root / "subfeatures" / parent /
                                (s.id.removeprefix("subfeature:") + ".json"))

    def write_shortcut(self, sc) -> Path:
        sc = ShortcutEntry.model_validate(sc)
        # name punctuation keys explicitly — a bare [^a-z0-9] -> '-' collapse makes
        # Ctrl+Shift+>, Ctrl+Shift+<, Ctrl+Shift+= collide on the same filename
        named = {">": "gt", "<": "lt", "=": "eq", "*": "star", "_": "underscore",
                 "+": "plus", "-": "minus", "`": "backtick"}
        parts = [p.strip() for p in sc.keys.split("+")]
        # a trailing empty part means the key itself was '+' (e.g. "Ctrl+Shift++")
        if parts and parts[-1] == "":
            parts = [p for p in parts if p] + ["plus"]
        safe = "-".join(named.get(p, p.lower()) for p in parts if p)
        safe = re.sub(r"[^a-z0-9-]+", "-", safe).strip("-")
        return self._write_json(sc, self.root / "shortcuts" / (safe + ".json"))

    def save_screenshot(self, img: Image.Image, node_id: str, name: str) -> str:
        sanitized_id = node_id.replace(":", "-")
        rel = f"screenshots/{sanitized_id}/{name}.png"
        out = self.root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return rel
