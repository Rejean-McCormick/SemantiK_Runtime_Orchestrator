from __future__ import annotations

from pathlib import Path

from .config import GateConfig
from .domain import CandidateBundle, ProcessResult
from .process import expand_argv, run_argv
from .sa import command_values


def run_gate(
    name: str,
    config: GateConfig,
    *,
    bundle: CandidateBundle,
    runtime_root: Path,
    report_path: Path,
) -> ProcessResult:
    values = command_values(bundle, final_runtime_root=runtime_root, report_path=report_path)
    argv = expand_argv(config.command.argv, values, stage=name)
    return run_argv(
        argv,
        stage=name,
        cwd=config.command.cwd,
        timeout_seconds=config.command.timeout_seconds,
        failure_code=f"SRO-{name.upper()}-001",
    )
