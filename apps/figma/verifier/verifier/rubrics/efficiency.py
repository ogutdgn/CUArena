from __future__ import annotations
import math
from dataclasses import dataclass
from verifier import config
from verifier.types import EfficiencyResult


@dataclass
class EfficiencyRubric:
    """
    Produces a multiplier (0.5 .. 1.0) based on semantic event count vs. target.

    Formula: 0.5 + 0.5 * exp(-lambda * max(0, actual - target))

    lambda_ defaults to config.yaml efficiency.lambda when None.
    """
    target_turns: int
    lambda_: float | None = None

    def run(self, log: dict) -> EfficiencyResult:
        lam = self.lambda_ if self.lambda_ is not None else config.get("efficiency.lambda", 0.05)
        actual = len(log["semantic"])
        target = self.target_turns
        exponent = -lam * max(0, actual - target)
        multiplier = round(0.5 + 0.5 * math.exp(exponent), 4)
        return EfficiencyResult(
            multiplier=multiplier,
            actual_turns=actual,
            target_turns=target,
            lambda_used=lam,
            message=f"{actual} turns used, target {target}, λ={lam} → multiplier {multiplier}",
        )
