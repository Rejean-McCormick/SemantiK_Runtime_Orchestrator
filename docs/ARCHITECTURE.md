# Architecture

## Product boundary

SemantiK Runtime Orchestrator is an independent release-control product. It coordinates external authorities but owns none of their linguistic, semantic, diagnostic, or observational truth.

```text
GF language repository
       ↓
GF Wordbench ───────────────┐
       ↓                    │
finalized PGF + evidence    │
       ↓                    │
SemantiK Runtime Orchestrator
       ├──→ SemantiK Architect conformance/validation
       ├──→ LevelUpDiag gate
       └──→ GF Observatory hook (optional)
       ↓
transactional RuntimeSet promotion
       ↓
activation.json
```

## Authority

- GF Wordbench owns GF compilation, language validation, PGF production, and its release evidence.
- SemantiK Architect owns SA↔GF, lexical, capability, conformance, RuntimeSet, and semantic-faithfulness contracts.
- LevelUpDiag owns independent diagnostics of the SA repository/runtime surface.
- GF Observatory owns observation and evidence aggregation.
- This repository owns only ordering, transactionality, integrity transfer, promotion, rollback, and activation sequencing.

## Dependency rule

The `semantik_runtime_orchestrator` package imports **none** of the connected products. Integrations are filesystem contracts and argv-only process adapters. This prevents circular dependencies such as `SA → LevelUpDiag → SA`.

## Transaction

The expensive and independent work happens before the release lock: Wordbench inspection, candidate assembly, SA conformance, metadata generation, and SA candidate validation. The lock covers only the shared final runtime root while promotion, configured external gates, and activation are performed.

A required post-promotion gate failure or an activation failure removes the newly promoted runtime. Existing RuntimeSet IDs are never overwritten. `activation.json` is written atomically and only after all required gates pass.

## No hidden behavior

The orchestrator never:

- compiles GF itself;
- chooses language-specific behavior;
- guesses lexemes or synonyms;
- substitutes another PGF;
- bypasses failed conformance;
- shells command strings;
- imports private implementation modules from connected repositories.


## Lexical boundary

Runtime releases pin lexical policy explicitly. Wikidata Lexemes are the default generic lexical knowledge authority; GF/RGL remains grammar/morphology authority, and generic GF lexical artifacts are realization fallback. The orchestrator validates/stages these artifacts but does not interpret linguistic meaning.
