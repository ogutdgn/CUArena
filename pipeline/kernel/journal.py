from datetime import datetime, timezone
from pathlib import Path
from kernel.models import JournalEvent

class Journal:
    def __init__(self, path: Path, run_id: str):
        self.path = Path(path)
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: JournalEvent) -> JournalEvent:
        event.ts = datetime.now(timezone.utc).isoformat()
        event.run_id = self.run_id
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
        return event

    @staticmethod
    def read_all(path: Path) -> list[JournalEvent]:
        p = Path(path)
        if not p.exists():
            return []
        return [JournalEvent.model_validate_json(line)
                for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
