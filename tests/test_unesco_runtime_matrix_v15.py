import importlib.util
from pathlib import Path
import json
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools/unesco_runtime_matrix_v15.py'
spec=importlib.util.spec_from_file_location('unesco_runtime_matrix_v15',SCRIPT)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class RuntimeMatrixTests(unittest.TestCase):
    def test_absent_root_does_not_qualify_languages(self):
        with tempfile.TemporaryDirectory() as t:
            r=mod.matrix(Path(t)/'absent')
            self.assertEqual((r['languages_targeted'],r['profiles_checked']),(14,14))
            self.assertEqual(r['artifact_integrity_ready_profiles'],0)
            self.assertFalse(r['publication_authorized'])
    def test_fake_activation_without_pgf_cannot_qualify(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/'activation.json').write_text(json.dumps({'schema_version':'1.0','bindings':{'fr|defluens-core-1':'candidate'}}))
            r=mod.matrix(p)
            self.assertFalse(r['languages']['fr'][0]['may_attempt_realization'])
            self.assertFalse(r['languages']['fr'][0]['grammar_pgf_verified'])
    def test_all_14_locales_are_covered(self):
        with tempfile.TemporaryDirectory() as t:
            r=mod.matrix(Path(t))
            self.assertEqual(set(r['languages']),set(mod.LOCALES))
    def test_declared_non_target_profile_does_not_imply_en_release(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/'activation.json').write_text(json.dumps({'schema_version':'1.0','bindings':{'fr|konstellation-explorer-2':'run-2'}}))
            r=mod.matrix(p)
            self.assertEqual(len(r['languages']['fr']),2)
            self.assertEqual(len(r['languages']['en']),1)
            self.assertFalse(r['languages']['en'][0]['may_attempt_realization'])

if __name__=='__main__':unittest.main()
