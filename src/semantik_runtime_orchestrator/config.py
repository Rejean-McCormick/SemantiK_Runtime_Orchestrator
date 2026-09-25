from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from .errors import OrchestratorError
from .io import read_json

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _safe_id(value: object, name: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise OrchestratorError(
            "SRO-CFG-001", "config", f"{name} must match {_SAFE_ID.pattern}", {"value": value}
        )
    return value


def _string(value: object, name: str, *, default: str | None = None) -> str:
    if value is None:
        value = default
    if not isinstance(value, str) or not value:
        raise OrchestratorError("SRO-CFG-002", "config", f"{name} must be a non-empty string.")
    return value


def _path(base: Path, value: object, name: str, *, optional: bool = False) -> Path | None:
    if value in (None, "") and optional:
        return None
    raw = Path(_string(value, name))
    return raw.resolve() if raw.is_absolute() else (base / raw).resolve()


def _argv(value: object, name: str, *, optional: bool = False) -> tuple[str, ...] | None:
    if value is None and optional:
        return None
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise OrchestratorError("SRO-CFG-003", "config", f"{name} must be a non-empty array of strings.")
    return tuple(value)


def _section(data: dict[str, Any], name: str, *, optional: bool = False) -> dict[str, Any]:
    value = data.get(name)
    if value is None and optional:
        return {}
    if not isinstance(value, dict):
        raise OrchestratorError("SRO-CFG-004", "config", f"{name} must be an object.")
    return value


@dataclass(frozen=True, slots=True)
class ExternalCommand:
    argv: tuple[str, ...]
    cwd: Path | None = None
    timeout_seconds: int = 1800


@dataclass(frozen=True, slots=True)
class WordbenchConfig:
    run: Path | None
    command: ExternalCommand | None
    out_root: Path | None
    pgf_artifact: str | None


@dataclass(frozen=True, slots=True)
class SAConfig:
    conformance: ExternalCommand | None
    existing_evidence: Path | None
    validate_runtime: ExternalCommand


@dataclass(frozen=True, slots=True)
class GateConfig:
    command: ExternalCommand
    required: bool = True


@dataclass(frozen=True, slots=True)
class OrchestratorConfig:
    source_path: Path
    runtime_set_id: str
    language: str
    profile_id: str
    concrete: str
    sa_version_range: str
    contract_version: str
    bridge: Path
    lexicon: Path
    capability_profile: Path
    conformance_suite: Path
    runtime_root: Path
    state_root: Path
    keep_staging: bool
    wordbench: WordbenchConfig
    sa: SAConfig
    levelupdiag: GateConfig | None
    observatory: GateConfig | None

    @classmethod
    def from_json(cls, path: str | Path) -> "OrchestratorConfig":
        source = Path(path).resolve()
        data = read_json(source, stage="config")
        if data.get("schema_version") != "1.0":
            raise OrchestratorError("SRO-CFG-005", "config", "Unsupported config schema_version.")
        base = source.parent
        release = _section(data, "release")
        inputs = _section(data, "inputs")
        runtime = _section(data, "runtime")
        wb = _section(data, "wordbench")
        sa = _section(data, "sa")

        runtime_set_id = _safe_id(release.get("runtime_set_id"), "release.runtime_set_id")
        language = _safe_id(release.get("language"), "release.language")
        profile_id = _safe_id(release.get("profile_id"), "release.profile_id")
        concrete = _string(release.get("concrete"), "release.concrete")
        sa_version_range = _string(release.get("sa_version_range"), "release.sa_version_range", default=">=1.0,<2.0")
        contract_version = _string(release.get("contract_version"), "release.contract_version", default="1.0")

        bridge = _path(base, inputs.get("bridge"), "inputs.bridge")
        lexicon = _path(base, inputs.get("lexicon"), "inputs.lexicon")
        profile = _path(base, inputs.get("capability_profile"), "inputs.capability_profile")
        suite = _path(base, inputs.get("conformance_suite"), "inputs.conformance_suite")
        runtime_root = _path(base, runtime.get("root"), "runtime.root")
        state_root = _path(base, runtime.get("state_root", ".semantik-runtime-orchestrator"), "runtime.state_root")
        assert bridge and lexicon and profile and suite and runtime_root and state_root

        wb_run = _path(base, wb.get("run"), "wordbench.run", optional=True)
        wb_command = _external_command(base, wb.get("command"), wb.get("cwd"), wb.get("timeout_seconds"), "wordbench", optional=True)
        wb_out_root = _path(base, wb.get("out_root"), "wordbench.out_root", optional=True)
        if wb_run is None and (wb_command is None or wb_out_root is None):
            raise OrchestratorError(
                "SRO-CFG-006", "config", "Configure wordbench.run or both wordbench.command and wordbench.out_root."
            )

        conf = _section(sa, "conformance", optional=True)
        existing_evidence = _path(base, conf.get("evidence"), "sa.conformance.evidence", optional=True)
        conformance_command = _external_command(base, conf.get("command"), conf.get("cwd"), conf.get("timeout_seconds"), "sa.conformance", optional=True)
        if existing_evidence is None and conformance_command is None:
            raise OrchestratorError(
                "SRO-CFG-007", "config", "Configure sa.conformance.command or sa.conformance.evidence."
            )
        validate = _section(sa, "validate_runtime")
        validate_command = _external_command(base, validate.get("command"), validate.get("cwd"), validate.get("timeout_seconds"), "sa.validate_runtime")
        assert validate_command is not None

        levelupdiag = _gate(base, data.get("levelupdiag"), "levelupdiag")
        observatory = _gate(base, data.get("observatory"), "observatory")

        return cls(
            source_path=source,
            runtime_set_id=runtime_set_id,
            language=language,
            profile_id=profile_id,
            concrete=concrete,
            sa_version_range=sa_version_range,
            contract_version=contract_version,
            bridge=bridge,
            lexicon=lexicon,
            capability_profile=profile,
            conformance_suite=suite,
            runtime_root=runtime_root,
            state_root=state_root,
            keep_staging=bool(runtime.get("keep_staging", False)),
            wordbench=WordbenchConfig(wb_run, wb_command, wb_out_root, wb.get("pgf_artifact") if isinstance(wb.get("pgf_artifact"), str) else None),
            sa=SAConfig(conformance_command, existing_evidence, validate_command),
            levelupdiag=levelupdiag,
            observatory=observatory,
        )


def _external_command(
    base: Path,
    command: object,
    cwd: object,
    timeout: object,
    label: str,
    *,
    optional: bool = False,
) -> ExternalCommand | None:
    argv = _argv(command, f"{label}.command", optional=optional)
    if argv is None:
        return None
    resolved_cwd = _path(base, cwd, f"{label}.cwd", optional=True)
    seconds = 1800 if timeout is None else timeout
    if not isinstance(seconds, int) or seconds <= 0:
        raise OrchestratorError("SRO-CFG-008", "config", f"{label}.timeout_seconds must be a positive integer.")
    return ExternalCommand(argv=argv, cwd=resolved_cwd, timeout_seconds=seconds)


def _gate(base: Path, value: object, label: str) -> GateConfig | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise OrchestratorError("SRO-CFG-004", "config", f"{label} must be an object.")
    command = _external_command(base, value.get("command"), value.get("cwd"), value.get("timeout_seconds"), label)
    assert command is not None
    return GateConfig(command=command, required=bool(value.get("required", True)))
