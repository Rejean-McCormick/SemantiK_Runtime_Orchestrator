import json
from pathlib import Path
import pytest
from helpers import make_wordbench_run, make_inputs, dump
from semantik_runtime_orchestrator.bundle import prepare_candidate
from semantik_runtime_orchestrator.errors import OrchestratorError
from semantik_runtime_orchestrator.locking import ReleaseLock
from semantik_runtime_orchestrator.release import activate, promote, write_release_metadata
from semantik_runtime_orchestrator.wordbench import inspect_wordbench_release

def bundle(tmp_path: Path):
    wb=inspect_wordbench_release(make_wordbench_run(tmp_path/"wb")); b,l,p,s=make_inputs(tmp_path/"in")
    x=prepare_candidate(staging_root=tmp_path/"stage",release=wb,runtime_set_id="rt1",language="sq",profile_id="sa-core-1",concrete="SAGrammarSqi",bridge=b,lexicon=l,capability_profile=p,conformance_suite=s,contract_version="1.0",pgf_selector=None)
    dump(x.evidence_path,{"passed":True,"runtime_set_id":"rt1","language":"sq","profile_id":"sa-core-1"}); write_release_metadata(x,sa_version_range=">=1,<2",contract_version="1.0"); return x

def test_promotion_activation(tmp_path: Path):
    b=bundle(tmp_path); root=tmp_path/"runtime"; dest=promote(b,runtime_root=root); assert dest.is_dir(); assert not (root/"activation.json").exists(); activate(runtime_root=root,runtime_set_id="rt1",language="sq",profile_id="sa-core-1"); assert json.loads((root/"activation.json").read_text())["bindings"]["sq|sa-core-1"]=="rt1"

def test_lock_excludes_second_transaction(tmp_path: Path):
    root=tmp_path/"runtime"
    with ReleaseLock(root,"a"):
        with pytest.raises(OrchestratorError) as e:
            with ReleaseLock(root,"b"): pass
        assert e.value.failure.code=="SRO-LOCK-001"


def test_release_manifest_pins_lexical_policy(tmp_path: Path):
    b = bundle(tmp_path)
    manifest = json.loads((b.root / "runtime.manifest.json").read_text())
    assert manifest["lexical_policy"]["precedence"] == [
        "request_override", "domain", "project", "wikidata", "gf_generic"
    ]
    lock = json.loads((b.root / "pipeline.lock.json").read_text())
    assert lock["lexical_policy"] == manifest["lexical_policy"]
