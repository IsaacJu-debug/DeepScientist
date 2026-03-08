from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunRequest:
    quest_id: str
    quest_root: Path
    run_id: str
    skill_id: str
    message: str
    model: str
    approval_policy: str
    sandbox_mode: str


@dataclass(frozen=True)
class RunResult:
    ok: bool
    run_id: str
    model: str
    output_text: str
    exit_code: int
    history_root: Path
    run_root: Path
    stderr_text: str
