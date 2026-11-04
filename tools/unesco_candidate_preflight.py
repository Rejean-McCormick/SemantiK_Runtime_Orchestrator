"""Read-only evidence gate for a private UNESCO candidate, *not* a release gate.

No runtime activation, mutation, publication or promotion is done.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect_candidate(candidate:Path)->dict:
    p=candidate.resolve(strict=True)
    if not p.is_dir() or p.is_symlink():raise ValueError('candidate directory missing or symbolic')
    base={'format':'semantik.unesco-candidate-readiness/1.0','candidate':str(p),
          'release_authorized':False,'publication_authorized':False,'runtime_activated':False}
    def read(name):
        f=p/name
        if f.is_symlink() or not f.is_file() or f.stat().st_size>5_000_000:
            raise ValueError('unsafe or absent evidence: '+name)
        return json.loads(f.read_text(encoding='utf-8'))
    lock=read('pipeline.lock.json')
    expected={'grammar.pgf','bridge.json','lexicon.json','profile.json','conformance.suite.json'}
    inputs=lock.get('inputs',{})
    if not expected <= set(inputs):raise ValueError('missing locked input')
    for name in expected:
        f=p/name
        if f.is_symlink() or not f.is_file() or sha(f)!=inputs[name]:
            raise ValueError('sha256 mismatch: '+name)
    suite=read('conformance.suite.json')
    report=read('conformance.report.json')
    build=read('wordbench-build.json')
    if (report.get('passed') is not True or
            not report.get('results') or
            any(row.get('passed') is not True for row in report['results']) or
            any(report.get(k)!=suite.get(k) for k in ('suite_id','runtime_set_id','language','capability_profile'))):
        raise ValueError('SemantiK conformance is not verified')
    if (build.get('status')!='PGF_BUILT_CANDIDATE_ONLY' or
            build.get('pgf_sha256')!=sha(p/'grammar.pgf') or
            build.get('language')!=lock.get('language')):
        raise ValueError('Wordbench compilation evidence missing or mismatched')
    if (suite.get('runtime_set_id')!=lock.get('runtime_set_id') or
            suite.get('language')!=lock.get('language') or
            suite.get('capability_profile')!=lock.get('profile_id')):
        raise ValueError('Suite/lock identity mismatch')
    return {**base,'status':'PRIVATE_CANDIDATE_EVIDENCE_CHECKED_NOT_RELEASED',
            'runtime_set_id':lock['runtime_set_id'], 'pgf_sha256':sha(p/'grammar.pgf'),
            'conformance_cases':len(report['results'])}

def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--candidate',type=Path,required=True)
    a.add_argument('--output',type=Path)
    args=a.parse_args(argv)
    try:
        out=inspect_candidate(args.candidate);rc=0
    except (OSError,KeyError,ValueError,TypeError) as exc:
        out={'status':'BLOCKED','reason':f'{type(exc).__name__}: {exc}',
             'release_authorized':False,'publication_authorized':False};rc=2
    rendered=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
    if args.output: args.output.write_text(rendered,encoding='utf-8')
    print(rendered,end='')
    return rc

if __name__=='__main__':raise SystemExit(main())
