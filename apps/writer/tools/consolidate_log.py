#!/usr/bin/env python3
"""Merge a live session dir (raw/semantic/outcome .jsonl) into the single
figma-shaped `session.json` (W5 consolidator). Matches the cross-app contract's
top-level export shape so one verifier reads figma and Writer logs alike:

  { schemaVersion, sessionId, exportedAt, raw[], semantic[], outcome{} }

`outcome` is the latest snapshot (last line of outcome.jsonl) — history is not
preserved, mirroring figma's `exportLog()`.

Usage:  python3 tools/consolidate_log.py <session-dir> [-o session.json]
        python3 tools/consolidate_log.py --latest        # newest under ~/.writer-rl-logs
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def consolidate(session_dir: Path) -> dict:
    raw = read_jsonl(session_dir / "raw.jsonl")
    semantic = read_jsonl(session_dir / "semantic.jsonl")
    outcomes = read_jsonl(session_dir / "outcome.jsonl")
    outcome = outcomes[-1] if outcomes else {}
    session_id = (outcome.get("sessionId")
                  or (semantic[0].get("sessionId") if semantic else None)
                  or session_dir.name)
    return {
        "schemaVersion": 1,
        "sessionId": session_id,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "raw": raw,
        "semantic": semantic,
        "outcome": outcome,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_dir", nargs="?", help="session directory")
    ap.add_argument("--latest", action="store_true",
                    help="use the newest session under ~/.writer-rl-logs")
    ap.add_argument("-o", "--out", help="output file (default: <dir>/session.json)")
    args = ap.parse_args()

    if args.latest:
        base = Path(os.environ.get("WRITER_LOG_DIR", Path.home() / ".writer-rl-logs"))
        dirs = sorted((d for d in base.iterdir() if d.is_dir()),
                      key=lambda d: d.stat().st_mtime, reverse=True)
        if not dirs:
            print(f"no sessions under {base}", file=sys.stderr)
            return 1
        session_dir = dirs[0]
    elif args.session_dir:
        session_dir = Path(args.session_dir)
    else:
        ap.error("give a session dir or --latest")

    data = consolidate(session_dir)
    out = Path(args.out) if args.out else session_dir / "session.json"
    out.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {out}  (raw={len(data['raw'])} semantic={len(data['semantic'])} "
          f"outcome={'yes' if data['outcome'] else 'no'}, "
          f"semanticEventCount={data['outcome'].get('summary', {}).get('semanticEventCount')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
