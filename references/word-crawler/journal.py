import json, time, pathlib
import config


class Journal:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self._recs = []
        if self.path.exists():
            with open(self.path, encoding="utf-8") as fh:
                self._recs = [json.loads(l) for l in fh if l.strip()]

    def append(self, rec: dict) -> dict:
        rec = dict(rec, seq=len(self._recs), ts=time.time(),
                   schema_version=config.SCHEMA_VERSION)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._recs.append(rec)
        return rec

    def records(self):
        return list(self._recs)

    def press_attempts(self, control_id):
        return sum(1 for r in self._recs
                   if r["t"] == "press-attempted" and r["control"] == control_id)

    def press_outcome(self, control_id):
        for r in reversed(self._recs):
            if r["t"] == "press-outcome" and r["control"] == control_id:
                return r
        return None
