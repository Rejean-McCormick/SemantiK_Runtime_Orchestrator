import importlib.util,pathlib,tempfile,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'tools'/'unesco_14_locale_readiness.py'
s=importlib.util.spec_from_file_location('coverage',p);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class TestAudit(unittest.TestCase):
 def test_absent_runtimes_are_all_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   x=c.audit(pathlib.Path(d))
   self.assertEqual(len(x['locales']),14)
   self.assertEqual(x['runtime_artifact_attemptable'],0)
   self.assertEqual(x['runtime_artifact_blocked'],14)
   self.assertFalse(x['public_release_authorized'])
 def test_absent_root_not_crash(self):
  x=c.audit(pathlib.Path('/intentionally/absent/unesco-runtime'))
  self.assertEqual(x['realization_qualified_locales'],0)
if __name__=='__main__':unittest.main()
