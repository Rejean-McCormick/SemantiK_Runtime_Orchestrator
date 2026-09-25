from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Mapping, Sequence

from .domain import ProcessResult
from .errors import OrchestratorError


def expand_argv(template: Sequence[str], values: Mapping[str, str], *, stage: str) -> list[str]:
    argv: list[str] = []
    for token in template:
        try:
            argv.append(token.format_map(values))
        except KeyError as exc:
            raise OrchestratorError(
                "SRO-CMD-001", stage, f"Unknown command placeholder: {exc.args[0]}"
            ) from exc
    return argv


def run_argv(
    argv: Sequence[str],
    *,
    stage: str,
    cwd: Path | None = None,
    timeout_seconds: int = 1800,
    failure_code: str = "SRO-CMD-002",
) -> ProcessResult:
    if not argv:
        raise OrchestratorError("SRO-CMD-003", stage, "Command argv is empty.")
    try:
        proc = subprocess.run(
            list(argv),
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise OrchestratorError(
            "SRO-CMD-004", stage, "External command timed out.", {"timeout_seconds": timeout_seconds, "argv": list(argv)}
        ) from exc
    result = ProcessResult(tuple(argv), proc.returncode, proc.stdout, proc.stderr)
    if proc.returncode != 0:
        raise OrchestratorError(failure_code, stage, "External command failed.", result.evidence())
    return result
