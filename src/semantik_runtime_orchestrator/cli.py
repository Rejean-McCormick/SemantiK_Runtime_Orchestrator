from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .config import OrchestratorConfig
from .errors import OrchestratorError
from .transaction import ReleaseOrchestrator
from .wordbench import inspect_wordbench_release


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semantik-runtime-orchestrator",
        description="Independent fail-closed release orchestrator for SemantiK Architect RuntimeSets.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect-wordbench", help="Verify a finalized GF Wordbench release.")
    inspect.add_argument("run_dir")

    validate = sub.add_parser("validate-config", help="Parse and validate an orchestrator config without running external tools.")
    validate.add_argument("--config", required=True)

    plan = sub.add_parser("plan", help="Resolve inputs and show the release plan without mutations or external commands.")
    plan.add_argument("--config", required=True)

    release = sub.add_parser("release", help="Execute the complete release transaction.")
    release.add_argument("--config", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect-wordbench":
            release = inspect_wordbench_release(Path(args.run_dir))
            payload = {
                "status": "PASS",
                "run_id": release.run_id,
                "run_dir": str(release.run_dir),
                "pgf_artifacts": [
                    {"path": str(a.path), "sha256": a.sha256, "size_bytes": a.size_bytes, "required": a.required}
                    for a in release.pgf_artifacts
                ],
            }
        else:
            config = OrchestratorConfig.from_json(args.config)
            if args.command == "validate-config":
                payload = {
                    "status": "PASS",
                    "runtime_set_id": config.runtime_set_id,
                    "language": config.language,
                    "profile_id": config.profile_id,
                }
            elif args.command == "plan":
                payload = ReleaseOrchestrator(config).plan()
            else:
                payload = ReleaseOrchestrator(config).execute()
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except OrchestratorError as exc:
        print(json.dumps({"status": "FAIL", "error": exc.to_dict()}, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
