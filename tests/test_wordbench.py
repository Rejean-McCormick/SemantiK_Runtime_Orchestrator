from pathlib import Path
import pytest
from helpers import make_wordbench_run
from semantik_runtime_orchestrator.errors import OrchestratorError
from semantik_runtime_orchestrator.wordbench import inspect_wordbench_release, select_pgf

def test_ready_release_and_selection(tmp_path: Path):
    r=inspect_wordbench_release(make_wordbench_run(tmp_path/"r")); assert select_pgf(r,None).path.name=="Grammar0.pgf"

def test_rejects_non_ready(tmp_path: Path):
    with pytest.raises(OrchestratorError) as e: inspect_wordbench_release(make_wordbench_run(tmp_path/"r",status="FAIL"))
    assert e.value.failure.code=="SRO-WB-005"

def test_rejects_tampering(tmp_path: Path):
    r=make_wordbench_run(tmp_path/"r"); (r/"artifacts/pgf/Grammar0.pgf").write_bytes(b"bad")
    with pytest.raises(OrchestratorError) as e: inspect_wordbench_release(r)
    assert e.value.failure.code=="SRO-WB-009"

def test_multiple_pgf_requires_selector(tmp_path: Path):
    r=inspect_wordbench_release(make_wordbench_run(tmp_path/"r",pgfs=2))
    with pytest.raises(OrchestratorError): select_pgf(r,None)
    assert select_pgf(r,"Grammar1.pgf").path.name=="Grammar1.pgf"
