from dataclasses import dataclass

from verifier.types import RubricResult


@dataclass
class Rubric:
    """Generic rubric: runs a list of checks, scores 0..weight with partial credit.

    Each rubric in a task has a `weight` (default 0.5) that becomes its max_score.
    A task's base_score is the sum of all rubric scores. Tasks can size weights so
    they sum to 1.0, but that's not required by the framework.

    Empty `checks` list scores full weight (so a task can declare a rubric placeholder
    without penalty).
    """
    name: str
    checks: list
    weight: float = 0.5

    def run(self, log: dict) -> RubricResult:
        if not self.checks:
            return RubricResult(name=self.name, score=self.weight,
                                max_score=self.weight, checks=[])
        results = [c.run(log) for c in self.checks]
        passed = sum(1 for r in results if r.passed)
        score = round(self.weight * (passed / len(results)), 4)
        return RubricResult(name=self.name, score=score,
                            max_score=self.weight, checks=results)
