from __future__ import annotations

from pathlib import Path

from .config import ExternalCommand, SAConfig
from .domain import CandidateBundle, ProcessResult
from .errors import OrchestratorError
from .io import copy_verified, read_json
from .process import expand_argv, run_argv


def command_values(bundle: CandidateBundle, *, final_runtime_root: Path | None = None, report_path: Path | None = None) -> dict[str, str]:
    values = {
        "candidate_root": str(bundle.root),
        "candidate_runtime_root": str(bundle.root.parent),
        "runtime_set_id": bundle.runtime_set_id,
        "language": bundle.language,
        "profile": bundle.profile_id,
        "profile_id": bundle.profile_id,
        "suite": str(bundle.suite_path),
        "evidence": str(bundle.evidence_path),
        "grammar": str(bundle.pgf_path),
        "bridge": str(bundle.bridge_path),
        "lexicon": str(bundle.lexicon_path),
        "capability_profile": str(bundle.profile_path),
    }
    if final_runtime_root is not None:
        values["runtime_root"] = str(final_runtime_root.resolve())
        values["runtime_dir"] = str(final_runtime_root.resolve() / bundle.runtime_set_id)
    if report_path is not None:
        values["transaction_report"] = str(report_path.resolve())
    return values


def validate_evidence(path: Path, *, bundle: CandidateBundle, require_identity: bool = True) -> dict[str, object]:
    evidence = read_json(path, stage="conformance")
    if evidence.get("passed") is not True:
        raise OrchestratorError("SRO-SA-003", "conformance", "SA conformance evidence did not pass.", evidence)
    expected = {
        "runtime_set_id": bundle.runtime_set_id,
        "language": bundle.language,
        "profile_id": bundle.profile_id,
    }
    for key, value in expected.items():
        if key not in evidence:
            if require_identity:
                raise OrchestratorError(
                    "SRO-SA-004",
                    "conformance",
                    f"Conformance evidence is missing required identity field: {key}",
                )
            continue
        if str(evidence[key]) != value:
            raise OrchestratorError(
                "SRO-SA-005",
                "conformance",
                f"Conformance evidence identity mismatch for {key}.",
                {"expected": value, "actual": evidence[key]},
            )
    return evidence


def run_conformance(bundle: CandidateBundle, config: SAConfig) -> tuple[dict[str, object], ProcessResult | None]:
    if config.existing_evidence is not None:
        copy_verified(config.existing_evidence, bundle.evidence_path, stage="conformance")
        return validate_evidence(bundle.evidence_path, bundle=bundle), None
    if config.conformance is None:
        raise OrchestratorError("SRO-SA-001", "conformance", "No SA conformance command or evidence configured.")
    values = command_values(bundle)
    argv = expand_argv(config.conformance.argv, values, stage="conformance")
    result = run_argv(
        argv,
        stage="conformance",
        cwd=config.conformance.cwd,
        timeout_seconds=config.conformance.timeout_seconds,
        failure_code="SRO-SA-002",
    )
    if not bundle.evidence_path.is_file():
        raise OrchestratorError(
            "SRO-SA-006",
            "conformance",
            "SA conformance command succeeded but did not create evidence.",
            result.evidence(),
        )
    return validate_evidence(bundle.evidence_path, bundle=bundle), result


def run_runtime_validation(bundle: CandidateBundle, command: ExternalCommand) -> ProcessResult:
    values = command_values(bundle)
    argv = expand_argv(command.argv, values, stage="sa_validation")
    return run_argv(
        argv,
        stage="sa_validation",
        cwd=command.cwd,
        timeout_seconds=command.timeout_seconds,
        failure_code="SRO-SA-007",
    )
