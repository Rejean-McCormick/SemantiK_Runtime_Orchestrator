import hashlib
import json
from semantik_runtime_orchestrator.readiness import inspect_profile


def test_no_runtime_never_produces_false_ready(tmp_path):
    assert inspect_profile(tmp_path,language='fr',profile_id='agriculture-reference-1')['status']=='BLOCKED'
    (tmp_path/'activation.json').write_text(json.dumps({'schema_version':'1.0',
            'bindings':{'fr|agriculture-reference-1':'agr-fr-1'}}))
    (tmp_path/'agr-fr-1').mkdir()
    assert inspect_profile(tmp_path,language='fr',profile_id='agriculture-reference-1')['can_realize'] is False


def test_released_and_verified_artifacts_required(tmp_path):
    runtime=tmp_path/'agr-fr-1';runtime.mkdir()
    (tmp_path/'activation.json').write_text(json.dumps({'schema_version':'1.0',
        'bindings':{'fr|agriculture-reference-1':'agr-fr-1'}}))
    (runtime/'grammar.pgf').write_bytes(b'not a real GF grammar')
    (runtime/'lexicon.json').write_text('{}')
    (runtime/'bridge.json').write_text('{}')
    cap={'schema_version':'1.0','runtime_set_id':'agr-fr-1','languages':{
        'fr':{'status':'RELEASED','profiles':[{'profile_id':'agriculture-reference-1','status':'RELEASED'}]}}}
    (runtime/'capabilities.json').write_text(json.dumps(cap))
    (runtime/'conformance.evidence.json').write_text('{"passed":false}')
    hashit=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    artifacts=[{'artifact_type':kind,'path':name,'sha256':hashit(runtime/name)} for kind,name in [
        ('grammar','grammar.pgf'),('lexical','lexicon.json'),('other','bridge.json')]]
    manifest={'schema_version':'1.0','status':'RELEASED','runtime_set_id':'agr-fr-1',
        'artifacts':artifacts,'capability_manifest_sha256':hashit(runtime/'capabilities.json'),
        'conformance_evidence_refs':['conformance.evidence.json'],
        'conformance_evidence_sha256':{'conformance.evidence.json':hashit(runtime/'conformance.evidence.json')}}
    (runtime/'runtime.manifest.json').write_text(json.dumps(manifest))
    result=inspect_profile(tmp_path,language='fr',profile_id='agriculture-reference-1')
    assert result['can_realize'] is False
    assert 'conformance_evidence_unverified' in result['reasons']


def test_attestation_without_runtime_language_profile_binding_is_refused(tmp_path):
    # A signed-looking/hash-pinned "passed": true alone does not establish
    # evidence for this exact RuntimeSet/profile/language.
    import hashlib
    root=tmp_path/'rt';root.mkdir()
    (tmp_path/'activation.json').write_text(json.dumps({'schema_version':'1.0',
        'bindings':{'fr|agriculture-reference-1':'rt'}}))
    for name,data in [('grammar.pgf',b'not_a_real_pgf'),('lexicon.json',b'{}'),('bridge.json',b'{}')]:
        (root/name).write_bytes(data)
    caps={'schema_version':'1.0','runtime_set_id':'rt','languages':{'fr':{'status':'RELEASED',
        'profiles':[{'profile_id':'agriculture-reference-1','status':'RELEASED'}]}}}
    (root/'capabilities.json').write_text(json.dumps(caps))
    (root/'conformance.evidence.json').write_text(json.dumps({'passed':True}))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    artifacts=[{'artifact_type':k,'path':f,'sha256':sha(root/f)} for k,f in
        [('grammar','grammar.pgf'),('lexical','lexicon.json'),('other','bridge.json')]]
    man={'schema_version':'1.0','status':'RELEASED','runtime_set_id':'rt','artifacts':artifacts,
        'capability_manifest_sha256':sha(root/'capabilities.json'),
        'conformance_evidence_refs':['conformance.evidence.json'],
        'conformance_evidence_sha256':{'conformance.evidence.json':sha(root/'conformance.evidence.json')}}
    (root/'runtime.manifest.json').write_text(json.dumps(man))
    result=inspect_profile(tmp_path,language='fr',profile_id='agriculture-reference-1')
    assert result['status']=='BLOCKED'
    assert 'conformance_evidence_unverified' in result['reasons']
