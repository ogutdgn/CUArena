import argparse, sys, uuid
from pathlib import Path
from pipeline.config import load_app_config
from pipeline import stage0, stage1_surface
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
    return p.parse_args(argv)

def main(argv=None) -> int:
    a = parse_args(argv if argv is not None else sys.argv[1:])
    cfg = load_app_config(a.app, Path(a.configs))
    journal = Journal(Path(a.kb_root) / a.app / "journal.jsonl", run_id=uuid.uuid4().hex[:8])
    writer = KBWriter(Path(a.kb_root), a.app)
    try:
        session = stage0.launch(cfg, journal)
        stage0.assert_version(Path(a.kb_root) / a.app / "app.json", session.version)
        if "1" in a.stages.split(","):
            surface_paths = stage1_surface.scan_surface(session, writer, journal,
                                                        max_containers=a.max_containers)
            if not a.no_agent:
                from pipeline.stage1_agent import SdkRunner, run_skeleton_agent
                from tools.models import UIContainer
                import json as _json
                surface = UIContainer.model_validate_json(surface_paths[0].read_text(encoding="utf-8"))
                run_skeleton_agent(SdkRunner(), cfg.name, session.version, surface, writer, journal)
        return 0
    except Exception as exc:  # journal, then loud failure
        journal.append(JournalEvent(actor="run", action="error", target=a.app, outcome=f"failed: {exc}"))
        raise

if __name__ == "__main__":
    sys.exit(main())
