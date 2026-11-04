import json
from semantik_runtime_orchestrator.development import inspect_development_handoff

def test_practical_handoff_is_never_accepted_as_runtime_release(tmp_path):
    path=tmp_path/'handoff.json'
    path.write_text(json.dumps({'schema_id':'defluens.wordbench-sa-development-handoff',
        'schema_version':'1.0','release_ready':False,'publication_authorized':False,
        'sa_conformance_passed':False,'gf_candidates':210,'rows':[]}))
    result=inspect_development_handoff(path)
    assert result['status']=='BLOCKED'
    assert result['runtime_set_activated'] is False
