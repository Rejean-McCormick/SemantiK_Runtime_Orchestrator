import json
from pathlib import Path
import jsonschema

def test_example_config_matches_schema():
    root=Path(__file__).resolve().parents[1]
    schema=json.loads((root/"schemas/orchestrator-config.schema.json").read_text())
    example=json.loads((root/"examples/runtime-orchestrator.example.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(example)
