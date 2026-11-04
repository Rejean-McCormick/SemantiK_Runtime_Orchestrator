import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import unesco_candidate_preflight as gate

class GateTests(unittest.TestCase):
    def test_missing_candidate_is_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises((ValueError,FileNotFoundError)):
                gate.inspect_candidate(Path(t))

    def test_locked_candidate_private_only(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);files=('grammar.pgf','bridge.json','lexicon.json','profile.json','conformance.suite.json')
            for name in files:(p/name).write_bytes(b'test-not-real-gf')
            inputs={name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in files}
            lock={'inputs':inputs,'runtime_set_id':'unesco-pilot-fr-1','profile_id':'unesco-pilot-1','language':'fr'}
            suite={'suite_id':'suite:unesco-fr','runtime_set_id':lock['runtime_set_id'],'language':'fr','capability_profile':'unesco-pilot-1'}
            report={**suite,'passed':True,'results':[{'case_id':'one','passed':True}]}
            build={'status':'PGF_BUILT_CANDIDATE_ONLY','pgf_sha256':inputs['grammar.pgf'],'language':'fr'}
            for name,data in [('pipeline.lock.json',lock),('conformance.suite.json',suite),('conformance.report.json',report),('wordbench-build.json',build)]:
                (p/name).write_text(json.dumps(data),encoding='utf-8')
            # conformance suite was serialized after the initial dummy digest
            lock['inputs']['conformance.suite.json']=hashlib.sha256((p/'conformance.suite.json').read_bytes()).hexdigest()
            (p/'pipeline.lock.json').write_text(json.dumps(lock),encoding='utf-8')
            result=gate.inspect_candidate(p)
            self.assertEqual(result['status'],'PRIVATE_CANDIDATE_EVIDENCE_CHECKED_NOT_RELEASED')
            self.assertFalse(result['release_authorized'])
            (p/'bridge.json').write_text('tampered',encoding='utf-8')
            with self.assertRaises(ValueError):gate.inspect_candidate(p)

if __name__=='__main__':unittest.main()
