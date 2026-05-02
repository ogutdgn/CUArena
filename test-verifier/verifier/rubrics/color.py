from dataclasses import dataclass
from verifier.types import RubricResult

MAX_SCORE = 0.5


@dataclass
class ColorRubric:
    """Checks fill and stroke color correctness."""
    checks: list

    def run(self, log: dict) -> RubricResult:
        if not self.checks:
            return RubricResult(name="color", score=MAX_SCORE,
                                max_score=MAX_SCORE, checks=[])
        results = [c.run(log) for c in self.checks]
        passed = sum(1 for r in results if r.passed)
        score = round(MAX_SCORE * (passed / len(results)), 4)
        return RubricResult(name="color", score=score,
                            max_score=MAX_SCORE, checks=results)
