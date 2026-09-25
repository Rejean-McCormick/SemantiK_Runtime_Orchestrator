import json
from pathlib import Path
import pytest
from semantik_runtime_orchestrator.config import OrchestratorConfig
from semantik_runtime_orchestrator.errors import OrchestratorError
from semantik_runtime_orchestrator.process import expand_argv

def config_data():
    return {"schema_version":"1.0","release":{"runtime_set_id":"rt1","language":"sq","profile_id":"sa-core-1","concrete":"SAGrammarSqi"},"inputs":{"bridge":"in/b.json","lexicon":"in/l.json","capability_profile":"in/p.json","conformance_suite":"in/s.json"},"runtime":{"root":"runtime"},"wordbench":{"run":"wb"},"sa":{"conformance":{"evidence":"evidence.json"},"validate_runtime":{"command":["python","validate.py","{candidate_runtime_root}","{runtime_set_id}"]}}}

def test_config_relative_paths(tmp_path: Path):
    p=tmp_path/"c.json"; p.write_text(json.dumps(config_data()))
    c=OrchestratorConfig.from_json(p); assert c.runtime_root==(tmp_path/"runtime").resolve(); assert c.wordbench.run==(tmp_path/"wb").resolve()

def test_rejects_unsafe_runtime_id(tmp_path: Path):
    d=config_data(); d["release"]["runtime_set_id"]="../bad"; p=tmp_path/"c.json"; p.write_text(json.dumps(d))
    with pytest.raises(OrchestratorError): OrchestratorConfig.from_json(p)

def test_argv_expansion_preserves_spaces():
    assert expand_argv(["python","x.py","{suite}"],{"suite":"A B.json"},stage="x")==["python","x.py","A B.json"]
