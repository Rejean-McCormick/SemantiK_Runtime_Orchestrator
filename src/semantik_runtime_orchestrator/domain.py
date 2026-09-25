from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Artifact:
    path: Path
    role: str
    sha256: str
    size_bytes: int
    required: bool


@dataclass(frozen=True, slots=True)
class WordbenchRelease:
    run_dir: Path
    run_id: str
    summary: dict[str, object]
    artifacts: tuple[Artifact, ...]
    pgf_artifacts: tuple[Artifact, ...]


@dataclass(frozen=True, slots=True)
class CandidateBundle:
    root: Path
    runtime_set_id: str
    language: str
    profile_id: str
    concrete: str
    pgf_path: Path
    bridge_path: Path
    lexicon_path: Path
    profile_path: Path
    suite_path: Path
    evidence_path: Path


@dataclass(frozen=True, slots=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def evidence(self, *, tail: int = 8000) -> dict[str, Any]:
        return {
            "argv": list(self.argv),
            "returncode": self.returncode,
            "stdout_tail": self.stdout[-tail:],
            "stderr_tail": self.stderr[-tail:],
        }
