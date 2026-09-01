class Frontier:
    def __init__(self, discovered, captured):
        self._pending = [s for s in discovered if s not in captured]

    @classmethod
    def from_journal(cls, j):
        disc, capt = [], set()
        for r in j.records():
            if r["t"] == "surface-discovered" and r["surface"] not in disc:
                disc.append(r["surface"])
            elif r["t"] == "surface-captured":
                capt.add(r["surface"])
        return cls(disc, capt)

    def pending(self):
        return list(self._pending)

    def is_done(self):
        return not self._pending
