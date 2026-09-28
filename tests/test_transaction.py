from pathlib import Path
import json, sys
import pytest
from helpers import make_wordbench_run, make_inputs, dump
from semantik_runtime_orchestrator.config import ExternalCommand, GateConfig, GrammarConfig, OrchestratorConfig, SAConfig, WordbenchConfig
from semantik_runtime_orchestrator.errors import OrchestratorError
from semantik_runtime_orchestrator.transaction import ReleaseOrchestrator

def cfg(tmp_path: Path, *, level=None, obs=None):
    wb=make_wordbench_run(tmp_path/"wb"); b,l,p,s=make_inputs(tmp_path/"in")
    ev=dump(tmp_path/"evidence.json",{"passed":True,"runtime_set_id":"rt1","language":"sq","profile_id":"sa-core-1"})
    return OrchestratorConfig(
        source_path=tmp_path/"config.json",runtime_set_id="rt1",language="sq",profile_id="sa-core-1",concrete="SAGrammarSqi",sa_version_range=">=1,<2",contract_version="1.0",
        bridge=b,lexicon=l,capability_profile=p,conformance_suite=s,runtime_root=tmp_path/"runtime",state_root=tmp_path/"state",keep_staging=False,
        wordbench=WordbenchConfig(wb,None,None,None),
        sa=SAConfig(None,ev,ExternalCommand((sys.executable,"-c","import sys; sys.exit(0)"))),
        levelupdiag=level,observatory=obs,
    )

def test_full_release(tmp_path: Path):
    c=cfg(tmp_path); r=ReleaseOrchestrator(c).execute(); assert r["status"]=="RELEASED"; assert (c.runtime_root/"rt1/runtime.manifest.json").is_file(); assert json.loads((c.runtime_root/"activation.json").read_text())["bindings"]["sq|sa-core-1"]=="rt1"

def test_required_gate_failure_rolls_back(tmp_path: Path):
    gate=GateConfig(ExternalCommand((sys.executable,"-c","import sys; sys.exit(9)")),required=True); c=cfg(tmp_path,level=gate)
    with pytest.raises(OrchestratorError): ReleaseOrchestrator(c).execute()
    assert not (c.runtime_root/"rt1").exists(); assert not (c.runtime_root/"activation.json").exists()

def test_optional_observatory_failure_warns_and_releases(tmp_path: Path):
    gate=GateConfig(ExternalCommand((sys.executable,"-c","import sys; sys.exit(5)")),required=False); c=cfg(tmp_path,obs=gate); r=ReleaseOrchestrator(c).execute(); assert r["status"]=="RELEASED"; assert any(x["stage"]=="observatory" and x["status"]=="WARN" for x in r["stages"])

def test_activation_failure_rolls_back_promoted_runtime(tmp_path: Path):
    c=cfg(tmp_path); c.runtime_root.mkdir(parents=True); (c.runtime_root/"activation.json").write_text('{"schema_version":"9","bindings":{}}')
    with pytest.raises(OrchestratorError) as e: ReleaseOrchestrator(c).execute()
    assert e.value.failure.code=="SRO-ACT-002"; assert not (c.runtime_root/"rt1").exists()

def test_plan_has_no_mutation(tmp_path: Path):
    c=cfg(tmp_path); plan=ReleaseOrchestrator(c).plan(); assert plan["status"]=="PLANNED"; assert not c.runtime_root.exists(); assert not c.state_root.exists()


def test_full_release_from_prebuilt_pgf_without_wordbench(tmp_path: Path):
    c=cfg(tmp_path)
    pgf=tmp_path/"direct.pgf"; pgf.write_bytes(b"PGF-DIRECT")
    c=OrchestratorConfig(
        source_path=c.source_path,runtime_set_id=c.runtime_set_id,language=c.language,profile_id=c.profile_id,concrete=c.concrete,
        sa_version_range=c.sa_version_range,contract_version=c.contract_version,bridge=c.bridge,lexicon=c.lexicon,
        capability_profile=c.capability_profile,conformance_suite=c.conformance_suite,runtime_root=c.runtime_root,state_root=c.state_root,
        keep_staging=c.keep_staging,wordbench=None,sa=c.sa,levelupdiag=None,observatory=None,grammar=GrammarConfig(pgf,None))
    plan=ReleaseOrchestrator(c).plan(); assert plan["grammar"]["mode"]=="prebuilt_pgf" and "wordbench" not in plan
    r=ReleaseOrchestrator(c).execute(); assert r["status"]=="RELEASED"
    assert any(x["stage"]=="grammar_input" and x["status"]=="PASS" for x in r["stages"])
