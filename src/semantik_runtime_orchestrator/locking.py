from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import socket
import time
import uuid

from .errors import OrchestratorError


@dataclass(slots=True)
class ReleaseLock:
    runtime_root: Path
    runtime_set_id: str
    _path: Path | None = None
    _token: str | None = None

    def __enter__(self) -> "ReleaseLock":
        root = self.runtime_root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        path = root / ".semantik-runtime-orchestrator.lock"
        token = uuid.uuid4().hex
        payload = {
            "schema_version": "1.0",
            "token": token,
            "runtime_set_id": self.runtime_set_id,
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "created_unix": time.time(),
        }
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            fd = os.open(path, flags, 0o600)
        except FileExistsError as exc:
            detail = None
            try:
                detail = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                detail = {"path": str(path)}
            raise OrchestratorError(
                "SRO-LOCK-001",
                "lock",
                "Runtime root is already locked by another release transaction.",
                detail,
            ) from exc
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        self._path = path
        self._token = token
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._path is None or self._token is None:
            return
        try:
            current = json.loads(self._path.read_text(encoding="utf-8"))
            if current.get("token") == self._token:
                self._path.unlink(missing_ok=True)
        except Exception:
            # Never turn a completed activation into an apparent release failure because
            # lock cleanup itself was externally disturbed. A leftover lock fails closed
            # on the next release and can be inspected manually.
            pass
