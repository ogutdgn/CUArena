from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    passed:    bool
    score:     float    # 1.0 if passed, 0.0 if not
    max_score: float    # always 1.0
    message:   str


@dataclass
class RubricResult:
    name:      str
    score:     float    # 0 .. 0.5
    max_score: float    # 0.5
    checks:    list[CheckResult]


@dataclass
class EfficiencyResult:
    multiplier:   float   # 0.5 .. 1.0
    actual_turns: int
    target_turns: int
    lambda_used:  float
    message:      str


@dataclass
class TaskResult:
    task_id:     str
    log_path:    str
    rubrics:     list[RubricResult]
    base_score:  float            # sum of rubric scores
    efficiency:  EfficiencyResult
    final_score: float            # base_score × multiplier


@dataclass
class Task:
    id:          str
    description: str
    rubrics:     list   # list of rubric objects
    efficiency:  Any    # EfficiencyRubric instance
