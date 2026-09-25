from __future__ import annotations

from pathlib import Path
import re
import shutil

from .domain import CandidateBundle, WordbenchRelease
from .errors import OrchestratorError
from .io import copy_verified, read_json, sha256_file, write_json_atomic
from .wordbench import select_pgf


def _require_keys(data: dict[str, object], keys: tuple[str, ...], *, label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise OrchestratorError("SRO-IN-001", "prepare", f"{label} is missing required fields.", missing)


def validate_inputs(
    bridge: Path,
    lexicon: Path,
    profile: Path,
    suite: Path,
    *,
    contract_version: str,
    expected_profile_id: str,
) -> None:
    b = read_json(bridge, stage="prepare")
    l = read_json(lexicon, stage="prepare")
    p = read_json(profile, stage="prepare")
    s = read_json(suite, stage="prepare")
    _require_keys(b, ("schema_version", "contract_version", "operations"), label="GF bridge spec")
    _require_keys(l, ("schema_version", "lexicon_id", "entries"), label="lexical artifact")
    _require_keys(
        p,
        ("schema_version", "profile_id", "profile_version", "required_operations", "required_features", "required_block_kinds"),
        label="capability profile",
    )
    _require_keys(s, ("schema_version",), label="conformance suite")
    if str(b.get("contract_version")) != contract_version:
        raise OrchestratorError(
            "SRO-IN-002",
            "prepare",
            "GF bridge contract version does not match requested SA↔GF contract.",
            {"bridge": b.get("contract_version"), "requested": contract_version},
        )
    if not isinstance(b.get("operations"), dict) or not b["operations"]:
        raise OrchestratorError("SRO-IN-003", "prepare", "GF bridge must declare at least one operation.")
    if not isinstance(l.get("entries"), list):
        raise OrchestratorError("SRO-IN-004", "prepare", "Lexical artifact entries must be an array.")
    profile_id = p.get("profile_id")
    base_profile_id = re.sub(r"-\d+$", "", expected_profile_id)
    if isinstance(profile_id, str) and profile_id not in {expected_profile_id, base_profile_id}:
        # A profile artifact may carry the versionless base id, but an unrelated profile is never accepted.
        raise OrchestratorError(
            "SRO-IN-005",
            "prepare",
            "Capability profile identity is unrelated to requested profile.",
            {"artifact": profile_id, "requested": expected_profile_id},
        )


def prepare_candidate(
    *,
    staging_root: Path,
    release: WordbenchRelease,
    runtime_set_id: str,
    language: str,
    profile_id: str,
    concrete: str,
    bridge: Path,
    lexicon: Path,
    capability_profile: Path,
    conformance_suite: Path,
    contract_version: str,
    pgf_selector: str | None,
) -> CandidateBundle:
    validate_inputs(
        bridge,
        lexicon,
        capability_profile,
        conformance_suite,
        contract_version=contract_version,
        expected_profile_id=profile_id,
    )
    selected_pgf = select_pgf(release, pgf_selector)
    root = (staging_root / runtime_set_id).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    pgf_path = root / "grammar.pgf"
    bridge_path = root / "bridge.json"
    lexicon_path = root / "lexicon.json"
    profile_path = root / "profile.json"
    suite_path = root / "conformance.suite.json"
    evidence_path = root / "conformance.evidence.json"

    copy_verified(selected_pgf.path, pgf_path, expected_sha256=selected_pgf.sha256, stage="prepare")
    copy_verified(bridge, bridge_path, stage="prepare")
    copy_verified(lexicon, lexicon_path, stage="prepare")
    copy_verified(capability_profile, profile_path, stage="prepare")
    copy_verified(conformance_suite, suite_path, stage="prepare")

    lock = {
        "schema_version": "1.0",
        "runtime_set_id": runtime_set_id,
        "language": language,
        "profile_id": profile_id,
        "concrete": concrete,
        "sa_gf_contract_version": contract_version,
        "wordbench": {
            "run_id": release.run_id,
            "run_dir": str(release.run_dir),
            "pgf_source": str(selected_pgf.path),
            "pgf_sha256": selected_pgf.sha256,
        },
        "inputs": {
            "grammar.pgf": sha256_file(pgf_path),
            "bridge.json": sha256_file(bridge_path),
            "lexicon.json": sha256_file(lexicon_path),
            "profile.json": sha256_file(profile_path),
            "conformance.suite.json": sha256_file(suite_path),
        },
    }
    write_json_atomic(root / "pipeline.lock.json", lock)
    return CandidateBundle(
        root,
        runtime_set_id,
        language,
        profile_id,
        concrete,
        pgf_path,
        bridge_path,
        lexicon_path,
        profile_path,
        suite_path,
        evidence_path,
    )
