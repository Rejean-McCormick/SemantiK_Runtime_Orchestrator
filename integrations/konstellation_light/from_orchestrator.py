"""Read-only inventory of declared language capabilities (not release qualification).

Export the caller's externally assembled run configuration. Never infers that a
RuntimeSet is activated or that a public definition has been authorized.
"""
import argparse
import json
from pathlib import Path
from contract import LOCALE,ContractError,save

def export(capabilities):
    # A sidecar for build-system planning, NOT a definition pack.
    if not isinstance(capabilities,dict) or not isinstance(capabilities.get('locales'),list):
        raise ContractError('Explicit locales list required; no guessing from RuntimeSets')
    locales=capabilities['locales']
    if len(locales)>256 or len(locales)!=len(set(locales)) or any(not isinstance(v,str) or not LOCALE.fullmatch(v) for v in locales):
        raise ContractError('Invalid/duplicate locales')
    runtime_id=capabilities.get('runtime_set_id')
    if not isinstance(runtime_id,str) or not runtime_id.strip():raise ContractError('Runtime identifier required')
    return {'format':'konstellation.multilingual-capabilities/1.0','runtime_set_id':runtime_id,
            'locales':locales,'status':'declared_only','qualification_verified':False,
            'publication_authorized':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args()
    result=export(json.loads(Path(a.input).read_text(encoding='utf-8')))
    target=Path(a.out)
    if target.exists():raise ContractError('Refusing to overwrite existing inventory')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(target)
