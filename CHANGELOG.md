# Changelog

## 1.2.0 — 2026-10-03

- Declared compatibility with SemantiK Architect `1.3.0-alpha.2`.
- Aligned ecosystem documentation to Kristal/Kristall `7.0.0-draft.3.2` while keeping semantic contracts completely outside RuntimeSet release orchestration.
- Normalized the human integration name to **DaaT** / machine id `daat`.
- Explicitly excludes DaaT/IK, Kompiler, EncyK and Médiathèque state from promotion/rollback/activation authority.
- Strengthened product-boundary tests so runtime code cannot import the connected ecosystem products.
- Preserved `sa_version_range >=1.0,<2.0` and all existing release transaction contracts.

## 1.1.2 — 2026-10-01

- Declared compatibility with SemantiK Architect 1.2.0.
- Kept the RuntimeSet release orchestrator intentionally independent of Kristal v6 knowledge/actionability semantics.
- Preserved the existing `>=1.0,<2.0` SA compatibility range and fail-closed release gates.


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


## 1.1.1 — 2026-09-28

- Added direct prebuilt-PGF release mode; Wordbench is no longer mandatory.
- Preserved Wordbench release mode unchanged.
- Direct PGF inputs are hash-verifiable and still pass through SA conformance, validation, promotion and activation.
