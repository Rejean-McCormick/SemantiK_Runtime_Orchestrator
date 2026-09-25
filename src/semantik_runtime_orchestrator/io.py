from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from .errors import OrchestratorError


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path, *, stage: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise OrchestratorError("SRO-JSON-001", stage, f"Invalid JSON: {path}", str(exc)) from exc
    if not isinstance(data, dict):
        raise OrchestratorError("SRO-JSON-002", stage, f"JSON root must be an object: {path}")
    return data


def write_json_atomic(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def ensure_within(root: Path, candidate: Path, *, stage: str) -> Path:
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise OrchestratorError(
            "SRO-PATH-001",
            stage,
            f"Path escapes its declared root: {resolved_candidate}",
            {"root": str(resolved_root)},
        ) from exc
    return resolved_candidate


def copy_verified(source: Path, destination: Path, *, expected_sha256: str | None = None, stage: str) -> str:
    if not source.is_file():
        raise OrchestratorError("SRO-FILE-001", stage, f"Required file does not exist: {source}")
    actual = sha256_file(source)
    if expected_sha256 is not None and actual.lower() != expected_sha256.lower():
        raise OrchestratorError(
            "SRO-HASH-001",
            stage,
            f"SHA-256 mismatch for {source}",
            {"expected": expected_sha256, "actual": actual},
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
    copied = sha256_file(destination)
    if copied != actual:
        raise OrchestratorError("SRO-HASH-002", stage, f"Copied artifact changed bytes: {destination}")
    return copied
