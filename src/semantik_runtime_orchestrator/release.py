from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from .domain import CandidateBundle
from .errors import OrchestratorError
from .io import read_json, sha256_file, write_json_atomic
from .lexical import validate_lexical_artifact


def write_release_metadata(bundle: CandidateBundle, *, sa_version_range: str, contract_version: str) -> None:
    evidence = read_json(bundle.evidence_path, stage="release")
    if evidence.get("passed") is not True:
        raise OrchestratorError("SRO-REL-001", "release", "Cannot release a runtime with failed conformance evidence.")

    evidence_name = bundle.evidence_path.name
    lexical_policy = validate_lexical_artifact(read_json(bundle.lexicon_path, stage="release"))
    capabilities: dict[str, Any] = {
        "schema_version": "1.0",
        "manifest_id": f"cap-{bundle.runtime_set_id}",
        "runtime_set_id": bundle.runtime_set_id,
        "languages": {
            bundle.language: {
                "status": "RELEASED",
                "concrete": bundle.concrete,
                "profiles": [
                    {
                        "profile_id": bundle.profile_id,
                        "status": "RELEASED",
                        "evidence_ref": evidence_name,
                    }
                ],
            }
        },
    }
    cap_path = bundle.root / "capabilities.json"
    write_json_atomic(cap_path, capabilities)

    artifacts = [
        {"artifact_type": "grammar", "artifact_id": f"grammar-{bundle.language}", "sha256": sha256_file(bundle.pgf_path), "path": bundle.pgf_path.name},
        {"artifact_type": "lexical", "artifact_id": f"lex-{bundle.language}", "sha256": sha256_file(bundle.lexicon_path), "path": bundle.lexicon_path.name},
        {"artifact_type": "other", "artifact_id": f"sa-gf-bridge-v{contract_version.split('.')[0]}", "sha256": sha256_file(bundle.bridge_path), "path": bundle.bridge_path.name},
        {"artifact_type": "other", "artifact_id": f"capability-profile-{bundle.profile_id}", "sha256": sha256_file(bundle.profile_path), "path": bundle.profile_path.name},
        {"artifact_type": "other", "artifact_id": f"conformance-suite-{bundle.profile_id}", "sha256": sha256_file(bundle.suite_path), "path": bundle.suite_path.name},
    ]
    manifest = {
        "schema_version": "1.0",
        "runtime_set_id": bundle.runtime_set_id,
        "sa_version_range": sa_version_range,
        "sa_gf_contract_version": contract_version,
        "lexical_policy": lexical_policy,
        "artifacts": artifacts,
        "capability_manifest_ref": cap_path.name,
        "capability_manifest_sha256": sha256_file(cap_path),
        "conformance_evidence_refs": [evidence_name],
        "conformance_evidence_sha256": {evidence_name: sha256_file(bundle.evidence_path)},
        "status": "RELEASED",
    }
    write_json_atomic(bundle.root / "runtime.manifest.json", manifest)


def promote(bundle: CandidateBundle, *, runtime_root: Path) -> Path:
    root = runtime_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    destination = root / bundle.runtime_set_id
    if destination.exists():
        raise OrchestratorError("SRO-REL-002", "promotion", f"RuntimeSet already exists; refusing overwrite: {destination}")

    incoming = root / f".{bundle.runtime_set_id}.incoming"
    if incoming.exists():
        raise OrchestratorError("SRO-REL-003", "promotion", f"Incoming runtime path already exists: {incoming}")
    incoming.mkdir(parents=False)
    names = (
        "grammar.pgf",
        "bridge.json",
        "lexicon.json",
        "profile.json",
        "conformance.suite.json",
        "conformance.evidence.json",
        "capabilities.json",
        "runtime.manifest.json",
    )
    try:
        for name in names:
            source = bundle.root / name
            if not source.is_file():
                raise OrchestratorError("SRO-REL-004", "promotion", f"Required release file missing: {name}")
            shutil.copy2(source, incoming / name)
        incoming.replace(destination)
    except Exception:
        shutil.rmtree(incoming, ignore_errors=True)
        raise
    return destination


def rollback_promoted(destination: Path) -> None:
    shutil.rmtree(destination, ignore_errors=True)


def activate(*, runtime_root: Path, runtime_set_id: str, language: str, profile_id: str) -> None:
    root = runtime_root.resolve()
    destination = root / runtime_set_id
    if not destination.is_dir():
        raise OrchestratorError("SRO-ACT-001", "activation", "Cannot activate a RuntimeSet that is not promoted.")
    activation_path = root / "activation.json"
    if activation_path.exists():
        activation = read_json(activation_path, stage="activation")
    else:
        activation = {"schema_version": "1.0", "bindings": {}}
    if activation.get("schema_version") != "1.0" or not isinstance(activation.get("bindings"), dict):
        raise OrchestratorError("SRO-ACT-002", "activation", "Existing activation.json has an unsupported shape.")
    key = f"{language}|{profile_id}"
    bindings = dict(activation["bindings"])
    bindings[key] = runtime_set_id
    activation["bindings"] = bindings
    write_json_atomic(activation_path, activation)
