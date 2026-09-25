from __future__ import annotations

from pathlib import Path
import time
from typing import Iterable

from .config import WordbenchConfig
from .domain import Artifact, WordbenchRelease
from .errors import OrchestratorError
from .io import ensure_within, read_json, sha256_file
from .process import expand_argv, run_argv


def _artifact_entries(manifest: dict[str, object]) -> Iterable[dict[str, object]]:
    entries = manifest.get("artifacts")
    if not isinstance(entries, list):
        raise OrchestratorError("SRO-WB-003", "wordbench", "Wordbench manifest has no artifacts array.")
    for entry in entries:
        if not isinstance(entry, dict):
            raise OrchestratorError("SRO-WB-003", "wordbench", "Wordbench manifest artifact is not an object.")
        yield entry


def inspect_wordbench_release(run_dir: str | Path) -> WordbenchRelease:
    stage = "wordbench"
    root = Path(run_dir).resolve()
    manifest_path = root / "manifest.json"
    summary_path = root / "summary.json"
    if not manifest_path.is_file() or not summary_path.is_file():
        raise OrchestratorError("SRO-WB-001", stage, "Wordbench run must contain manifest.json and summary.json.")

    manifest = read_json(manifest_path, stage=stage)
    summary = read_json(summary_path, stage=stage)
    if manifest.get("schema_id") != "gf-wordbench.artifact-manifest" or manifest.get("schema_version") != "1.0":
        raise OrchestratorError("SRO-WB-002", stage, "Unsupported Wordbench artifact manifest contract.")

    run = summary.get("run")
    release_state = summary.get("release")
    if not isinstance(run, dict) or not isinstance(release_state, dict):
        raise OrchestratorError("SRO-WB-004", stage, "Wordbench release summary is missing run/release state.")
    acceptable = (
        run.get("mode") == "release"
        and run.get("overall_status") == "OK"
        and run.get("execution_state") == "completed"
        and run.get("partial") is False
        and release_state.get("decision") == "READY"
        and release_state.get("release_gates_passed") is True
        and release_state.get("manifest_verified") is True
    )
    if not acceptable:
        raise OrchestratorError(
            "SRO-WB-005", stage, "Wordbench run is not a completed READY release.", {"run": run, "release": release_state}
        )

    artifacts: list[Artifact] = []
    pgfs: list[Artifact] = []
    for entry in _artifact_entries(manifest):
        rel = entry.get("path")
        role = entry.get("role")
        expected_sha = entry.get("sha256")
        expected_size = entry.get("size_bytes")
        if not isinstance(rel, str) or not isinstance(role, str) or not isinstance(expected_sha, str) or not isinstance(expected_size, int):
            raise OrchestratorError("SRO-WB-003", stage, "Malformed Wordbench artifact entry.", entry)
        path = ensure_within(root, root / rel, stage=stage)
        if not path.is_file():
            raise OrchestratorError("SRO-WB-008", stage, f"Manifest artifact is missing: {rel}")
        actual_sha = sha256_file(path)
        actual_size = path.stat().st_size
        if actual_sha != expected_sha or actual_size != expected_size:
            raise OrchestratorError(
                "SRO-WB-009",
                stage,
                f"Wordbench artifact integrity check failed: {rel}",
                {
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                    "expected_size": expected_size,
                    "actual_size": actual_size,
                },
            )
        artifact = Artifact(path, role, actual_sha, actual_size, bool(entry.get("required")))
        artifacts.append(artifact)
        if role == "pgf":
            pgfs.append(artifact)
    if not pgfs:
        raise OrchestratorError(
            "SRO-WB-010",
            stage,
            "Wordbench release contains no role=pgf artifact. The orchestrator never substitutes or compiles a PGF.",
        )
    return WordbenchRelease(
        run_dir=root,
        run_id=str(run.get("run_id") or manifest.get("run_id") or root.name),
        summary=summary,
        artifacts=tuple(artifacts),
        pgf_artifacts=tuple(pgfs),
    )


def select_pgf(release: WordbenchRelease, selector: str | None) -> Artifact:
    if selector:
        matches = [a for a in release.pgf_artifacts if a.path.name == selector or a.path.as_posix().endswith(selector)]
        if len(matches) != 1:
            raise OrchestratorError(
                "SRO-WB-007",
                "wordbench",
                "PGF selector did not resolve exactly one artifact.",
                {"selector": selector, "matches": [str(a.path) for a in matches]},
            )
        return matches[0]
    if len(release.pgf_artifacts) != 1:
        raise OrchestratorError(
            "SRO-WB-006",
            "wordbench",
            "A release must expose exactly one PGF unless wordbench.pgf_artifact selects one.",
            [str(a.path) for a in release.pgf_artifacts],
        )
    return release.pgf_artifacts[0]


def discover_latest_release(out_root: str | Path, *, not_before_ns: int | None = None) -> Path:
    root = Path(out_root).resolve()
    candidates: list[Path] = []
    for manifest in root.rglob("manifest.json"):
        run_dir = manifest.parent
        if not (run_dir / "summary.json").is_file():
            continue
        if not_before_ns is not None and manifest.stat().st_mtime_ns < not_before_ns:
            continue
        candidates.append(run_dir)
    if not candidates:
        raise OrchestratorError("SRO-WB-014", "wordbench", f"No finalized Wordbench run found under {root}")
    return max(candidates, key=lambda p: ((p / "manifest.json").stat().st_mtime_ns, str(p)))


def resolve_wordbench_release(config: WordbenchConfig, values: dict[str, str]) -> WordbenchRelease:
    if config.run is not None:
        return inspect_wordbench_release(config.run)
    if config.command is None or config.out_root is None:
        raise OrchestratorError("SRO-WB-015", "wordbench", "Incomplete Wordbench command configuration.")
    started_ns = time.time_ns() - 2_000_000_000
    argv = expand_argv(config.command.argv, values, stage="wordbench")
    run_argv(
        argv,
        stage="wordbench",
        cwd=config.command.cwd,
        timeout_seconds=config.command.timeout_seconds,
        failure_code="SRO-WB-013",
    )
    return inspect_wordbench_release(discover_latest_release(config.out_root, not_before_ns=started_ns))
