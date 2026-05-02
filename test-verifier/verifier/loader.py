import json
from pathlib import Path


def load_log(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Log file not found: {path}")
    with open(p) as f:
        data = json.load(f)
    _validate(data)
    return data


def _validate(data: dict) -> None:
    for key in ["schemaVersion", "sessionId", "raw", "semantic", "outcome"]:
        if key not in data:
            raise ValueError(f"Log missing required field: '{key}'")
    outcome = data["outcome"]
    if "summary" not in outcome:
        raise ValueError("Log outcome missing 'summary'")
    if "document" not in outcome:
        raise ValueError("Log outcome missing 'document'")
    if "shapeCounts" not in outcome["summary"]:
        raise ValueError("Log outcome.summary missing 'shapeCounts'")
