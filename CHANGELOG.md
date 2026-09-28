# Changelog

## 1.1.0 — 2026-09-27

- Added lexical artifact v1.1 validation while retaining v1.0 compatibility.
- Pins explicit lexical-source precedence into candidate locks and RuntimeSet manifests.
- Establishes Wikidata Lexemes as generic lexical knowledge authority and GF generic lexicons as realization fallback.
- Rejects knowledge-only `lexeme_ref` entries when misdeclared as executable bindings.

## 1.0.0 — 2026-09-25

- Extracted the runtime release pipeline from SemantiK Architect into an independent repository.
- Removed all Python imports of SemantiK Architect, GF Wordbench, LevelUpDiag, and GF Observatory internals.
- Added argv-only external process adapters with timeouts and stable fail-closed errors.
- Added strict Wordbench READY-release and artifact integrity validation.
- Added isolated candidate assembly and conformance evidence identity checks.
- Added SA validation as an external contract gate.
- Added runtime-root release locking, atomic promotion, rollback, and last-step activation.
- Added optional LevelUpDiag and GF Observatory gates.
- Added read-only `plan` and config validation commands.
- Added JSON schemas, migration guidance, tests, and packaging.
