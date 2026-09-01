from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentTrajectoryStep:
    turn: int
    action: dict[str, Any]
    text: str = ""


@dataclass
class AgentResult:
    provider: str
    model: str
    turns: int
    finished: bool                 # True if model emitted a final message; False if step cap hit / error
    stop_reason: str               # "done" | "step_cap" | "error"
    error: str | None = None
    trajectory: list[AgentTrajectoryStep] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
