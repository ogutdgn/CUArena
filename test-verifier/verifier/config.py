import os
import yaml

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
_cache: dict = {}


def _load() -> None:
    global _cache
    with open(_CONFIG_PATH) as f:
        _cache = yaml.safe_load(f) or {}


def get(dotpath: str, default=None):
    """Read a value by dot-path, e.g. get('efficiency.lambda', 0.05)."""
    if not _cache:
        _load()
    val = _cache
    for part in dotpath.split("."):
        if not isinstance(val, dict):
            return default
        val = val.get(part)
        if val is None:
            return default
    return val
