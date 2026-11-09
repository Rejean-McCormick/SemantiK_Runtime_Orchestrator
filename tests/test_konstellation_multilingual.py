import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integrations'/'konstellation_light'))
from contract import new_document,validate,ContractError
DIGEST='sha256:'+'a'*64
class ContractTests(unittest.TestCase):
    def test_locale_without_fixed_supported_languages(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'ja',[
            {'node_id':'KQ1','label':'星', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'review:1'}}])
        self.assertEqual(validate(doc,require_reviewed=True)['locale'],'ja')
    def test_candidate_never_published_by_reader(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'fr-CA',[
            {'node_id':'KQ1','definition':'Note candidate.', 'provenance':{'provider':'editorial','source_refs':['source:1'], 'review_status':'candidate'}}])
        with self.assertRaises(ContractError):validate(doc,require_reviewed=True)
    def test_reject_duplicate_identity(self):
        row={'node_id':'KQ1','label':'Term', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'r1'}}
        with self.assertRaises(ContractError):new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'en',[row,row])

from from_orchestrator import export
class RuntimeAdapterTests(unittest.TestCase):
    def test_language_capabilities_are_declared_only(self):
        out=export({'runtime_set_id':'demo-only','locales':['fr-CA','en','ja','ar']})
        self.assertEqual(out['status'],'declared_only')
        self.assertFalse(out['qualification_verified'])
        self.assertFalse(out['publication_authorized'])
    def test_duplicate_languages_rejected(self):
        with self.assertRaises(ContractError):export({'runtime_set_id':'x','locales':['en','en']})
