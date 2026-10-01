# SemantiK Runtime Orchestrator 1.1.2

Independent fail-closed release orchestrator for SemantiK Architect RuntimeSets. Version 1.1.2 is aligned with **SemantiK Architect 1.2.0** and intentionally remains outside the Kristal v6 semantic boundary.

The orchestrator owns release coordination only:

```text
GF / Wordbench artifacts
  -> SA conformance + validation
  -> diagnostics/evidence
  -> transactional promotion / rollback
  -> RuntimeSet activation
```

Kristal v6 `record_role`, `valuations`, `applicability`, and `actionability` are communication-input semantics handled by the SemantiK ecosystem ACL, not RuntimeSet release criteria. This repository therefore does not import Kristal, Da’at, Orgo, or SemantiK Architect internals.

Existing `sa_version_range = ">=1.0,<2.0"` remains compatible with SA 1.2.0.

After a real `Konstellation.pgf` has been compiled in the SemantiK Architect profile-3 directory, `examples/konstellation-fr-3.json` can be used with the direct prebuilt-PGF path. Production release gates remain fail-closed.

Run:

```bash
python -m pytest -q
```
