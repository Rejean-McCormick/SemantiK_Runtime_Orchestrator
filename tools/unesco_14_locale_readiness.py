"""Fail-closed UNESCO Educational Policy 14-locale RuntimeSet availability report.

Uses the production orchestrator's existing inspect_profile hash/conformance
checks. Never infers a working grammar from GF source files or a locale name.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

try:
    from semantik_runtime_orchestrator.readiness import inspect_profile
except ImportError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
    from semantik_runtime_orchestrator.readiness import inspect_profile

LOCALES=('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')


def audit(root:Path, *,profile='defluens-core-1'):
    result=[inspect_profile(root,language=lang,profile_id=profile) for lang in LOCALES]
    attemptable=sum(x['can_attempt_realization'] is True for x in result)
    # Artifact readiness is not proof of a successful SemantiK->Spek realization.
    return {'format':'semantik.unesco-14-locale-readiness/1.0',
            'branch':'unesco-mt1-10','profile_id':profile,'requested_locales':list(LOCALES),
            'runtime_artifact_attemptable':attemptable,
            'runtime_artifact_blocked':len(result)-attemptable,
            'realization_qualified_locales':0,'projection_generated':0,
            'public_release_authorized':False,'status':'PREFLIGHT_ONLY',
            'locales':result}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-root',type=Path,required=True)
    p.add_argument('--profile',default='defluens-core-1')
    p.add_argument('--out',type=Path)
    a=p.parse_args(argv)
    v=audit(a.runtime_root,profile=a.profile)
    body=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if a.out:
        if a.out.exists() or any((p/'.git').exists() for p in a.out.resolve().parents):
            raise SystemExit('Output must be new and outside Git')
        a.out.parent.mkdir(parents=True,exist_ok=True)
        with a.out.open('x',encoding='utf8') as f:f.write(body)
    else:print(body,end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
