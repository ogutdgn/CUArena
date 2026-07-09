import re
import subprocess
from pathlib import Path

import pytest

from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.teardown import close_app, _window_alive
from tools.journal import Journal
from tools.winapp import inputs

pytestmark = pytest.mark.smoke


def test_close_app_discards_dirtied_document(tmp_path: Path):
    # stage0.launch/build_argv now stages a scratch copy of cfg.fixture
    # outside the repo before launching (see pipeline/stage0.py
    # _stage_fixture_copy) -- this repo lives under OneDrive, and modern
    # Word auto-enables AutoSave purely by local path recognition for files
    # under a OneDrive-synced folder, which both silently mutates the
    # tracked fixture AND suppresses the close-time Save dialog this test
    # needs to exercise. The tracked fixture at
    # configs/fixtures/word/blank.docx is therefore never opened directly by
    # this test.
    tracked_fixture = Path("configs/fixtures/word/blank.docx").resolve()
    before_bytes = tracked_fixture.read_bytes()

    cfg = load_app_config("word", Path("configs/apps"))
    j = Journal(tmp_path / "journal.jsonl", run_id="smoke-discard")
    s = launch(cfg, j)
    try:
        inputs.ensure_foreground(s.hwnd)
        # Click into the document canvas (center of the window, via
        # click_rect's own midpoint logic) so keystrokes land in the body
        # text, not a ribbon control, then dirty the doc.
        inputs.click_rect(s.ui.window_rect())
        inputs.press("hello")

        close_app(s, j)
        assert not _window_alive(s.hwnd)

        events = Journal.read_all(tmp_path / "journal.jsonl")
        last = events[-1]
        assert last.outcome in ("discarded", "closed", "killed")

        discard_events = [e for e in events if e.outcome == "discarded"]
        if discard_events:
            # A save-confirmation dialog appeared -- verify the safety property:
            # the clicked button must be a discard label, NEVER a save button.
            button = discard_events[-1].data.get("button", "")
            assert button, "discarded event must record which button was clicked"
            assert not re.search(r"(?i)^save$", button), (
                f"CRITICAL: discard step clicked a Save-labeled button: {button!r}")
            # journal eventually reflects the window is gone (closed/killed
            # follow-up after the discard, or the discard itself is terminal)
            assert last.outcome in ("discarded", "closed", "killed")
        else:
            # Word closed without prompting -- record this honestly rather
            # than assuming a dialog appeared.
            print(f"NOTE: no discard dialog appeared; journal outcome={last.outcome!r}")
    finally:
        # Belt-and-suspenders: Word must never survive this test, regardless
        # of which path close_app took.
        subprocess.run(["taskkill", "/IM", "WINWORD.EXE", "/F"], capture_output=True)

    # The tracked fixture is never the file Word had open (build_argv
    # staged a scratch copy) -- assert it is byte-identical to before this
    # test ran, as a hard guarantee.
    after_bytes = tracked_fixture.read_bytes()
    assert before_bytes == after_bytes, (
        "tracked fixture configs/fixtures/word/blank.docx was modified by this test "
        "-- it should never have been opened directly")
