from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Failure:
    code: str
    stage: str
    message: str
    detail: object | None = None


class OrchestratorError(RuntimeError):
    """Fail-closed orchestrator error with a stable local code."""

    def __init__(self, code: str, stage: str, message: str, detail: object | None = None):
        super().__init__(message)
        self.failure = Failure(code=code, stage=stage, message=message, detail=detail)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "code": self.failure.code,
            "stage": self.failure.stage,
            "message": self.failure.message,
        }
        if self.failure.detail is not None:
            payload["detail"] = self.failure.detail
        return payload
