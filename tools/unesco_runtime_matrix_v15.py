#!/usr/bin/env python3
"""Check activated GF RuntimeSet *for each target language* with the real readiness checker.

A passed artifact-integrity check is not proof of successful realization or
permission to publish, even if the runtime is installed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantik_runtime_orchestrator.readiness import inspect_profile

LOCALES=('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')
class RuntimeMatrixError(ValueError):pass

def matrix(root:Path,profiles=('defluens-core-1',)):
    root=Path(root)
    if root.is_symlink():raise RuntimeMatrixError('Runtime root symbolique refuse')
    activation=root/'activation.json'
    bindings={}
    if activation.is_file() and not activation.is_symlink() and activation.stat().st_size<300_000:
        obj=json.loads(activation.read_text('utf-8-sig'))
        if obj.get('schema_version')=='1.0' and isinstance(obj.get('bindings'),dict):
            bindings=obj['bindings']
    probes={};checked=0;integrity_ok=0
    for lang in LOCALES:
        active=sorted(k.split('|',1)[1] for k in bindings if isinstance(k,str) and k.startswith(lang+'|') and len(k.split('|',1))==2 and re.fullmatch(r'[a-z][a-z0-9-]*-[0-9]+',k.split('|',1)[1]))
        wanted=sorted(set(profiles)|set(active))
        cases=[]
        for profile in wanted:
            result=inspect_profile(root,language=lang,profile_id=profile)
            checked+=1;integrity_ok+=result.get('can_attempt_realization') is True
            cases.append({'profile_id':profile,'status':result['status'],'reason_codes':result.get('reasons',[]),
                          'runtime_set_id':result.get('runtime_set_id'),
                          'grammar_pgf_verified':result['grammar_pgf_verified'],
                          'conformance_evidence_verified':result['conformance_evidence_verified'],
                          'may_attempt_realization':result['can_attempt_realization'],
                          'realization_success_tested':False,'public_release_qualified':False})
        probes[lang]=cases
    return {'format':'semantik.unesco-mt1-10-runtime-matrix/1.0','branch':'unesco-mt1-10',
            'root_checked':str(root),'runtime_root_present':root.is_dir(),
            'languages':probes,'languages_targeted':len(LOCALES), 'profiles_checked':checked,
            'artifact_integrity_ready_profiles':integrity_ok,
            'generated_articles':0,'realizations_attempted':0,'languages_proven_qualified':0,
            'publication_authorized':False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-root',required=True,type=Path)
    p.add_argument('--profile',default='defluens-core-1')
    a=p.parse_args(argv)
    print(json.dumps(matrix(a.runtime_root,(a.profile,)),ensure_ascii=False,sort_keys=True,indent=2))
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except (RuntimeMatrixError,ValueError,OSError,KeyError,TypeError) as e:
        print('RUNTIME MATRIX BLOQUE: '+str(e),file=sys.stderr);sys.exit(2)
