# Migration from the embedded SA prototype

If the earlier embedded runtime-pipeline prototype was copied into SemantiK Architect, remove these paths from the SA repository after this independent repository is adopted:

```text
tools/build_sa_runtime.py
src/semantik_architect/runtime_pipeline/
tests/runtime_pipeline/
docs/reference/RUNTIME_PIPELINE.md
runtime_pipeline.config.example.json
RUNTIME_PIPELINE_VALIDATION.md
RUNTIME_PIPELINE_SHA256SUMS.txt
```

Do **not** remove SA-owned runtime contracts, conformance code, RuntimeReleaseValidator, runtime adapters, schemas, or `tools/build_runtime_manifest.py`. Those remain SemantiK Architect responsibilities.
