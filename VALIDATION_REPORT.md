# Validation addendum — 1.1.1 — 2026-09-28

Direct prebuilt-PGF mode added; pytest suite passes after the change. Historical 1.1.0 report follows.

# Validation Report — SemantiK Runtime Orchestrator 1.1.0

Validation date: 2026-09-27

## Result

PASS for independent orchestration, lexical contract validation, release pinning, and packaging surface.

## Verified

- 25 automated tests pass.
- Python source/tests compile.
- 2 orchestrator JSON schemas are valid Draft 2020-12 schemas.
- Lexical artifact schema 1.0 remains accepted; v1.1 is admitted and validated.
- Candidate `pipeline.lock.json` pins lexical precedence.
- Released `runtime.manifest.json` pins the same lexical precedence.
- Knowledge-only `lexeme_ref` records are rejected if declared executable bindings.
- The orchestrator still imports no SemantiK Architect or GF Wordbench internals.
- Existing release locking, atomic promotion, rollback, conformance identity and last-step activation behavior remain covered.

Default pinned lexical policy:

`request_override > domain > project > wikidata > gf_generic`

Wikidata Lexemes are lexical-knowledge authority; GF/RGL remains grammar/morphology authority and generic GF lexicons remain realization fallback.

## Inventory

- Python source modules: 15
- Test modules: 8
- JSON schemas: 2
