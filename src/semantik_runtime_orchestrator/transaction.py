from __future__ import annotations

import shutil
from pathlib import Path
import time
import uuid

from .bundle import prepare_candidate, validate_inputs
from .config import OrchestratorConfig
from .errors import OrchestratorError
from .gates import run_gate
from .io import sha256_file, write_json_atomic
from .locking import ReleaseLock
from .release import activate, promote, rollback_promoted, write_release_metadata
from .sa import run_conformance, run_runtime_validation
from .wordbench import inspect_wordbench_release, resolve_wordbench_release, select_pgf


class ReleaseOrchestrator:
    def __init__(self, config: OrchestratorConfig):
        self.config = config

    def plan(self) -> dict[str, object]:
        cfg = self.config
        validate_inputs(
            cfg.bridge,
            cfg.lexicon,
            cfg.capability_profile,
            cfg.conformance_suite,
            contract_version=cfg.contract_version,
            expected_profile_id=cfg.profile_id,
        )
        payload: dict[str, object] = {
            "schema_version": "1.0",
            "status": "PLANNED",
            "release": {
                "runtime_set_id": cfg.runtime_set_id,
                "language": cfg.language,
                "profile_id": cfg.profile_id,
                "concrete": cfg.concrete,
            },
            "runtime_root": str(cfg.runtime_root),
            "state_root": str(cfg.state_root),
            "inputs": {
                "bridge": {"path": str(cfg.bridge), "sha256": sha256_file(cfg.bridge)},
                "lexicon": {"path": str(cfg.lexicon), "sha256": sha256_file(cfg.lexicon)},
                "capability_profile": {"path": str(cfg.capability_profile), "sha256": sha256_file(cfg.capability_profile)},
                "conformance_suite": {"path": str(cfg.conformance_suite), "sha256": sha256_file(cfg.conformance_suite)},
            },
            "stages": [
                "wordbench",
                "prepare",
                "sa_conformance",
                "release_metadata",
                "sa_validation",
                "promotion",
                *( ["levelupdiag"] if cfg.levelupdiag else [] ),
                *( ["observatory"] if cfg.observatory else [] ),
                "activation",
            ],
        }
        if cfg.wordbench.run is not None:
            release = inspect_wordbench_release(cfg.wordbench.run)
            pgf = select_pgf(release, cfg.wordbench.pgf_artifact)
            payload["wordbench"] = {
                "mode": "existing_release",
                "run_id": release.run_id,
                "run_dir": str(release.run_dir),
                "pgf": {"path": str(pgf.path), "sha256": pgf.sha256},
            }
        else:
            payload["wordbench"] = {
                "mode": "command",
                "out_root": str(cfg.wordbench.out_root),
                "pgf_artifact": cfg.wordbench.pgf_artifact,
            }
        return payload

    def execute(self) -> dict[str, object]:
        cfg = self.config
        transaction_id = uuid.uuid4().hex
        transaction_root = cfg.state_root.resolve() / "transactions" / transaction_id
        staging_runtime_root = transaction_root / "runtime"
        report_path = cfg.state_root.resolve() / "reports" / f"{transaction_id}.json"
        report: dict[str, object] = {
            "schema_version": "1.0",
            "transaction_id": transaction_id,
            "runtime_set_id": cfg.runtime_set_id,
            "language": cfg.language,
            "profile_id": cfg.profile_id,
            "started_unix": time.time(),
            "status": "RUNNING",
            "stages": [],
        }
        destination: Path | None = None
        critical_started = False

        def record(stage: str, status: str, **evidence: object) -> None:
            item: dict[str, object] = {"stage": stage, "status": status}
            item.update(evidence)
            stages = report["stages"]
            assert isinstance(stages, list)
            stages.append(item)
            write_json_atomic(report_path, report)

        try:
            values = {
                "runtime_set_id": cfg.runtime_set_id,
                "language": cfg.language,
                "profile": cfg.profile_id,
                "profile_id": cfg.profile_id,
                "runtime_root": str(cfg.runtime_root.resolve()),
                "state_root": str(cfg.state_root.resolve()),
            }
            release = resolve_wordbench_release(cfg.wordbench, values)
            pgf = select_pgf(release, cfg.wordbench.pgf_artifact)
            record("wordbench", "PASS", run_id=release.run_id, run_dir=str(release.run_dir), pgf_sha256=pgf.sha256)

            staging_runtime_root.mkdir(parents=True, exist_ok=False)
            bundle = prepare_candidate(
                staging_root=staging_runtime_root,
                release=release,
                runtime_set_id=cfg.runtime_set_id,
                language=cfg.language,
                profile_id=cfg.profile_id,
                concrete=cfg.concrete,
                bridge=cfg.bridge,
                lexicon=cfg.lexicon,
                capability_profile=cfg.capability_profile,
                conformance_suite=cfg.conformance_suite,
                contract_version=cfg.contract_version,
                pgf_selector=cfg.wordbench.pgf_artifact,
            )
            record("prepare", "PASS", candidate=str(bundle.root))

            evidence, conf_process = run_conformance(bundle, cfg.sa)
            record(
                "sa_conformance",
                "PASS",
                evidence=str(bundle.evidence_path),
                evidence_identity={k: evidence.get(k) for k in ("runtime_set_id", "language", "profile_id")},
                process=conf_process.evidence() if conf_process else None,
            )

            write_release_metadata(bundle, sa_version_range=cfg.sa_version_range, contract_version=cfg.contract_version)
            record("release_metadata", "PASS", manifest=str(bundle.root / "runtime.manifest.json"))

            validation = run_runtime_validation(bundle, cfg.sa.validate_runtime)
            record("sa_validation", "PASS", process=validation.evidence())

            with ReleaseLock(cfg.runtime_root, cfg.runtime_set_id):
                critical_started = True
                destination = promote(bundle, runtime_root=cfg.runtime_root)
                record("promotion", "PASS", runtime_dir=str(destination))

                if cfg.levelupdiag is not None:
                    try:
                        result = run_gate(
                            "levelupdiag",
                            cfg.levelupdiag,
                            bundle=bundle,
                            runtime_root=cfg.runtime_root,
                            report_path=report_path,
                        )
                        record("levelupdiag", "PASS", process=result.evidence())
                    except OrchestratorError as exc:
                        if cfg.levelupdiag.required:
                            raise
                        record("levelupdiag", "WARN", failure=exc.to_dict())

                if cfg.observatory is not None:
                    try:
                        result = run_gate(
                            "observatory",
                            cfg.observatory,
                            bundle=bundle,
                            runtime_root=cfg.runtime_root,
                            report_path=report_path,
                        )
                        record("observatory", "PASS", process=result.evidence())
                    except OrchestratorError as exc:
                        if cfg.observatory.required:
                            raise
                        record("observatory", "WARN", failure=exc.to_dict())

                # Persist all gate results before changing the callable binding.
                report["status"] = "READY_TO_ACTIVATE"
                write_json_atomic(report_path, report)
                activate(
                    runtime_root=cfg.runtime_root,
                    runtime_set_id=cfg.runtime_set_id,
                    language=cfg.language,
                    profile_id=cfg.profile_id,
                )
                stages = report["stages"]
                assert isinstance(stages, list)
                stages.append({"stage": "activation", "status": "PASS", "binding": f"{cfg.language}|{cfg.profile_id}"})
                report["status"] = "RELEASED"
                report["ended_unix"] = time.time()
                try:
                    write_json_atomic(report_path, report)
                except Exception as exc:  # activation is already atomic and successful; report persistence is secondary.
                    report["report_persistence_warning"] = f"{type(exc).__name__}: {exc}"

            return report
        except Exception as exc:
            if critical_started and destination is not None and destination.exists():
                rollback_promoted(destination)
            failure = exc if isinstance(exc, OrchestratorError) else OrchestratorError(
                "SRO-INT-001", "internal", f"{type(exc).__name__}: {exc}"
            )
            report["status"] = "FAIL"
            report["ended_unix"] = time.time()
            report["failure"] = failure.to_dict()
            try:
                write_json_atomic(report_path, report)
            except Exception:
                pass
            if failure is exc:
                raise
            raise failure from exc
        finally:
            if not cfg.keep_staging:
                shutil.rmtree(transaction_root, ignore_errors=True)
