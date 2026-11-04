"""Read-only rejection/triage of Defluens practical evidence as a release input.

Practical GF probes are useful for language engineering but are not a WordBench
READY release and do not carry a compiled immutable PGF or SA conformance.
"""
from __future__ import annotations
import json
from pathlib import Path


def inspect_development_handoff(path: Path) -> dict:
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data,dict) or data.get('schema_id')!='defluens.wordbench-sa-development-handoff' or data.get('schema_version')!='1.0':
        raise ValueError('Not a Defluens development handoff')
    if any(data.get(k) is not False for k in ('release_ready','publication_authorized','sa_conformance_passed')):
        raise ValueError('Development handoff cannot declare a passing release gate')
    rows=data.get('rows')
    if not isinstance(rows,list) or len(rows)>3000:raise ValueError('Invalid handoff rows')
    return {'status':'BLOCKED','schema_id':'semantik.runtime-development-admission',
            'schema_version':'1.0','publication_authorized':False,'runtime_set_activated':False,
            'reason':'development_handoff_not_wordbench_ready_release',
            'wordbench_practical_candidates':data.get('gf_candidates',0),
            'instructions':('First produce and validate a WordBench READY release with PGF; '
                            'then run SA candidate conformance and the normal release transaction.')}
