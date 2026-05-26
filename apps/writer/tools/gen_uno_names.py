#!/usr/bin/env python3
"""Emit resources/uno-names.json — a compact {".uno:Cmd": "rl_name"} map for the
semantic logger (W5). Names are the catalog's curated `semanticName` (RL-friendly,
e.g. .uno:Bold -> "bold"), so semantic[].name is stable across the app.

Run from apps/writer/:  python3 tools/gen_uno_names.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cat = json.loads((ROOT / "resources" / "command-catalog.json").read_text())["commands"]
names = {cmd: meta["semanticName"] for cmd, meta in cat.items() if meta.get("semanticName")}
out = ROOT / "resources" / "uno-names.json"
out.write_text(json.dumps(names, separators=(",", ":"), sort_keys=True) + "\n")
print(f"wrote {out.relative_to(ROOT)}: {len(names)} command->name mappings "
      f"({out.stat().st_size // 1024} KB)")
