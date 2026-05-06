from dataclasses import dataclass
from verifier.types import RubricResult

MAX_SCORE = 0.5


@dataclass
class FundamentalsRubric:
    """Checks that the agent used the correct shape primitives."""
    checks: list

    def run(self, log: dict) -> RubricResult:
        if not self.checks:
            return RubricResult(name="fundamentals", score=MAX_SCORE,
                                max_score=MAX_SCORE, checks=[])
        results = [c.run(log) for c in self.checks]
        passed = sum(1 for r in results if r.passed)
        score = round(MAX_SCORE * (passed / len(results)), 4)
        return RubricResult(name="fundamentals", score=score,
                            max_score=MAX_SCORE, checks=results)
