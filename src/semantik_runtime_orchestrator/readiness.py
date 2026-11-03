"""Strict, read-only runtime availability check for a Spek language/profile pair.

A directory with GF sources, a manifest or a fake PGF does not constitute a
qualified RuntimeSet. This check verifies files/hashes and declared evidence;
it never generates language or promotes a runtime candidate.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

SAFE_NAME=re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$')
HASH=re.compile(r'^[0-9a-f]{64}$')


def _read(root: Path, rel: str):
    if not isinstance(rel,str) or not SAFE_NAME.fullmatch(rel):
        return None
    p=root/rel
    if p.is_symlink() or not p.is_file() or p.stat().st_size>5_000_000:
        return None
    try:
        obj=json.loads(p.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        return None
    return obj if isinstance(obj,dict) else None


def inspect_profile(runtime_root: Path, *, language: str, profile_id: str) -> dict:
    root=Path(runtime_root)
    reasons=[]
    base={'format':'semantik.runtime-readiness/1.0','language':language,
          'profile_id':profile_id,'status':'BLOCKED','runtime_set_id':None,
          'grammar_pgf_verified':False,'conformance_evidence_verified':False,
          'can_realize':False,'can_attempt_realization':False,'publication_authorized':False}
    if not re.fullmatch(r'[a-z]{2,3}',language or '') or not re.fullmatch(r'[a-z][a-z0-9-]*-[0-9]+',profile_id or ''):
        return {**base,'reasons':['invalid_language_or_profile']}
    if root.is_symlink() or not root.is_dir():
        return {**base,'reasons':['runtime_directory_missing']}
    activation=_read(root,'activation.json')
    if not activation or activation.get('schema_version')!='1.0' or not isinstance(activation.get('bindings'),dict):
        return {**base,'reasons':['no_valid_activation']}
    runtime_id=activation['bindings'].get(language+'|'+profile_id)
    if not isinstance(runtime_id,str) or not SAFE_NAME.fullmatch(runtime_id):
        return {**base,'reasons':['profile_not_activated']}
    base['runtime_set_id']=runtime_id
    folder=root/runtime_id
    if folder.is_symlink() or not folder.is_dir():
        return {**base,'reasons':['runtime_set_missing']}
    manifest=_read(folder,'runtime.manifest.json')
    capabilities=_read(folder,'capabilities.json')
    if not manifest or manifest.get('schema_version')!='1.0' or manifest.get('runtime_set_id')!=runtime_id or manifest.get('status')!='RELEASED':
        reasons.append('runtime_manifest_not_released')
    if not capabilities or capabilities.get('schema_version')!='1.0' or capabilities.get('runtime_set_id')!=runtime_id:
        reasons.append('capabilities_missing_or_wrong')
    else:
        channel=capabilities.get('languages',{}).get(language)
        profiles=channel.get('profiles',[]) if isinstance(channel,dict) else []
        if (not isinstance(channel,dict) or channel.get('status')!='RELEASED' or
            not isinstance(profiles,list) or not any(isinstance(p,dict) and p.get('profile_id')==profile_id and p.get('status')=='RELEASED' for p in profiles)):
            reasons.append('profile_not_released')
    if manifest and capabilities:
        expected=manifest.get('capability_manifest_sha256')
        if not HASH.fullmatch(expected or '') or _digest(folder/'capabilities.json')!=expected:
            reasons.append('capability_manifest_digest_mismatch')
    artifacts=manifest.get('artifacts') if isinstance(manifest,dict) else None
    if not isinstance(artifacts,list):
        reasons.append('artifact_list_missing')
    else:
        kinds=set()
        for artifact in artifacts:
            if not isinstance(artifact,dict) or not isinstance(artifact.get('path'),str):
                reasons.append('artifact_invalid'); continue
            filename=artifact['path'];kind=artifact.get('artifact_type')
            if not SAFE_NAME.fullmatch(filename):
                reasons.append('unsafe_artifact_path');continue
            path=folder/filename
            expected=artifact.get('sha256')
            if not HASH.fullmatch(expected or '') or _digest(path)!=expected:
                reasons.append('artifact_missing_or_digest_mismatch:'+str(kind));continue
            if kind=='grammar' and filename=='grammar.pgf':
                base['grammar_pgf_verified']=True
            kinds.add(kind)
        if not base['grammar_pgf_verified']:
            reasons.append('compiled_grammar_pgf_missing_or_unverified')
        if not {'lexical','grammar','other'}.issubset(kinds):
            reasons.append('required_artifacts_not_complete')
    if isinstance(manifest,dict):
        evidence_refs=manifest.get('conformance_evidence_refs')
        evidence_digests=manifest.get('conformance_evidence_sha256')
        if not isinstance(evidence_refs,list) or not evidence_refs or not isinstance(evidence_digests,dict):
            reasons.append('conformance_evidence_missing')
        else:
            good=True
            for filename in evidence_refs:
                if not isinstance(filename,str) or not SAFE_NAME.fullmatch(filename):
                    good=False;break
                expected=evidence_digests.get(filename)
                evidence=_read(folder,filename)
                if not HASH.fullmatch(expected or '') or _digest(folder/filename)!=expected or not evidence or evidence.get('passed') is not True:
                    good=False;break
            base['conformance_evidence_verified']=good
            if not good: reasons.append('conformance_evidence_unverified')
    if reasons:
        return {**base,'reasons':sorted(set(reasons))}
    return {**base,'status':'LOCAL_ARTIFACTS_VERIFIED_EXECUTION_NOT_PROVEN',
            'can_realize':False, 'can_attempt_realization':True, 'reasons':[], 'publication_authorized':False}


def _digest(path: Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size==0 or path.stat().st_size>100_000_000:
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()
