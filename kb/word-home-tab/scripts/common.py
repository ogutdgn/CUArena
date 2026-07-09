"""Shared plumbing for the Word KB scripts.

Every per-app script imports this first: it puts the repo root on sys.path (so the
kernel package imports), resolves the canonical paths, loads the app config, and hands
back a kernel Journal + KBWriter bound to kb/word/. All knowledge is written through the
kernel writers; every action is journaled. Nothing app-specific about schema lives here.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

# --- paths -------------------------------------------------------------------
# common.py -> scripts -> word -> kb -> <repo root>
REPO_ROOT = Path(__file__).resolve().parents[3]
KB_ROOT = REPO_ROOT / "kb"
APP = "word"
APP_KB = KB_ROOT / APP
CONFIG_PATH = REPO_ROOT / "configs" / "apps" / "word.json"
JOURNAL_PATH = APP_KB / "journal.jsonl"

# make `from kernel... import ...` work no matter the cwd
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def make_run_id() -> str:
    return time.strftime("run-%Y%m%d-%H%M%S")


def get_journal(run_id: str):
    """A kernel Journal appending to kb/word/journal.jsonl (append-only, cross-run)."""
    from kernel.journal import Journal
    return Journal(JOURNAL_PATH, run_id)


def journal_event(**kw):
    """Build a kernel JournalEvent (ts/run_id filled by Journal.append)."""
    from kernel.models import JournalEvent
    return JournalEvent(**kw)


def get_writer():
    from kernel.kb_writer import KBWriter
    return KBWriter(KB_ROOT, APP)


# --- scratch fixture ---------------------------------------------------------
# NEVER open the original fixture: it lives under a OneDrive-synced folder, and some
# Office builds silently enable AutoSave there and mutate the original. Always work on
# a throwaway copy in the OS temp dir (AppData\Local\Temp — not cloud-synced).
SCRATCH_DIR = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / "word-kb-scratch"


def fresh_scratch_fixture() -> Path:
    """Copy configs/fixtures/word/blank.docx to a fresh temp path and return it."""
    cfg = load_config()
    src = REPO_ROOT / cfg["fixture"]
    if not src.exists():
        raise FileNotFoundError(f"fixture missing: {src}")
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    dst = SCRATCH_DIR / f"scratch-{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}.docx"
    shutil.copy2(src, dst)
    return dst
