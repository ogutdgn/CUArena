from dataclasses import dataclass, field

from verifier.types import RubricResult


@dataclass
class Rubric:
    """Generic rubric: runs a list of checks, scores 0..weight with partial credit.

    Each rubric in a task has a `weight` (default 0.5) that becomes its max_score.
    A task's base_score is the sum of all rubric scores. Tasks can size weights so
    they sum to 1.0, but that's not required by the framework.

    Empty `checks` list scores full weight (so a task can declare a rubric placeholder
    without penalty).

    `critical` — list of 0-based check indices that are prompt-critical.
    If ANY critical check fails, the rubric's score is HALVED. This anchors
    hard requirements (frame must be 1280×832, distinct colors, roof on body)
    so a single critical failure isn't diluted across a many-check rubric,
    but other passing checks still earn partial credit.
    """
    name: str
    checks: list
    weight: float = 0.5
    critical: list = field(default_factory=list)

    def run(self, log: dict) -> RubricResult:
        if not self.checks:
            return RubricResult(name=self.name, score=self.weight,
                                max_score=self.weight, checks=[])
        results = [c.run(log) for c in self.checks]
        passed = sum(1 for r in results if r.passed)
        score = self.weight * (passed / len(results))
        # Halve the rubric score if any critical check failed
        if any(i < len(results) and not results[i].passed for i in self.critical):
            score *= 0.5
        return RubricResult(name=self.name, score=round(score, 4),
                            max_score=self.weight, checks=results)
