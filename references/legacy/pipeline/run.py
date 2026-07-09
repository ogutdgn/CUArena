import argparse, json, sys, uuid
from pathlib import Path
from pipeline.config import load_app_config
from pipeline import stage0, stage1_surface, teardown
from pipeline.explorer import replay_route, run_explorer
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent

def parse_args(argv):
    p = argparse.ArgumentParser(prog="pipeline.run")
    p.add_argument("app")
    p.add_argument("--stages", default="0,1")
    p.add_argument("--kb-root", default="kb")
    p.add_argument("--configs", default="configs/apps")
    p.add_argument("--no-agent", action="store_true")
    p.add_argument("--max-containers", type=int, default=50)
    p.add_argument("--keep-open", action="store_true")
    p.add_argument("--max-turns", type=int, default=60, help="survey-phase turn budget")
    p.add_argument("--item-max-turns", type=int, default=15, help="per-worklist-item turn budget")
    p.add_argument("--verbose", dest="verbose", action="store_true", default=True,
                   help="print explorer progress live (default on)")
    p.add_argument("--no-verbose", dest="verbose", action="store_false")
    return p.parse_args(argv)

def main(argv=None) -> int:
    a = parse_args(argv if argv is not None else sys.argv[1:])
    cfg = load_app_config(a.app, Path(a.configs))
    journal = Journal(Path(a.kb_root) / a.app / "journal.jsonl", run_id=uuid.uuid4().hex[:8])
    writer = KBWriter(Path(a.kb_root), a.app)
    session = None
    try:
        session = stage0.launch(cfg, journal)
        version_json = Path(a.kb_root) / a.app / "version.json"
        stage0.assert_version(Path(a.kb_root) / a.app / "app.json", session.version,
                               kb_version_json=version_json)
        # Persist the version pin after every successful launch+assert, independent
        # of whether the agent (stage1) runs -- a --no-agent-only KB must still be
        # able to detect drift on its next run.
        version_json.parent.mkdir(parents=True, exist_ok=True)
        version_json.write_text(json.dumps({"version": session.version}), encoding="utf-8")
        route_path = Path(a.kb_root) / a.app / "scripts" / "drive" / "ready_route.json"
        if route_path.exists():
            replay_route(session, route_path, journal)
        if "1" in a.stages.split(","):
            stage1_surface.scan_surface(session, writer, journal,
                                        max_containers=a.max_containers)
            if not a.no_agent:
                kb_app_root = Path(a.kb_root) / a.app
                run_explorer(session, writer, journal, kb_app_root, cfg,
                            survey_max_turns=a.max_turns, item_max_turns=a.item_max_turns,
                            verbose=a.verbose)
        return 0
    except Exception as exc:  # journal, then loud failure
        journal.append(JournalEvent(actor="run", action="error", target=a.app, outcome=f"failed: {exc}"))
        raise
    finally:
        if session is not None and not a.keep_open:
            teardown.close_app(session, journal)

if __name__ == "__main__":
    sys.exit(main())
