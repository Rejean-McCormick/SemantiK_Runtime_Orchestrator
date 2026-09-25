from pathlib import Path
import sys
import pytest
from helpers import make_wordbench_run, make_inputs, dump
from semantik_runtime_orchestrator.bundle import prepare_candidate
from semantik_runtime_orchestrator.config import ExternalCommand, SAConfig
from semantik_runtime_orchestrator.errors import OrchestratorError
from semantik_runtime_orchestrator.sa import run_conformance
from semantik_runtime_orchestrator.wordbench import inspect_wordbench_release

def make_bundle(tmp_path: Path):
    wb=inspect_wordbench_release(make_wordbench_run(tmp_path/"wb")); b,l,p,s=make_inputs(tmp_path/"in")
    return prepare_candidate(staging_root=tmp_path/"stage",release=wb,runtime_set_id="rt1",language="sq",profile_id="sa-core-1",concrete="SAGrammarSqi",bridge=b,lexicon=l,capability_profile=p,conformance_suite=s,contract_version="1.0",pgf_selector=None)

def test_candidate_byte_preserving(tmp_path: Path):
    b=make_bundle(tmp_path); assert b.pgf_path.read_bytes()==b"PGF-0"; assert (b.root/"pipeline.lock.json").is_file()

def test_evidence_identity_required(tmp_path: Path):
    b=make_bundle(tmp_path); ev=dump(tmp_path/"ev.json",{"passed":True})
    cfg=SAConfig(None,ev,ExternalCommand((sys.executable,"-c","pass")))
    with pytest.raises(OrchestratorError) as e: run_conformance(b,cfg)
    assert e.value.failure.code=="SRO-SA-004"

def test_evidence_identity_mismatch(tmp_path: Path):
    b=make_bundle(tmp_path); ev=dump(tmp_path/"ev.json",{"passed":True,"runtime_set_id":"x","language":"sq","profile_id":"sa-core-1"})
    cfg=SAConfig(None,ev,ExternalCommand((sys.executable,"-c","pass")))
    with pytest.raises(OrchestratorError) as e: run_conformance(b,cfg)
    assert e.value.failure.code=="SRO-SA-005"
