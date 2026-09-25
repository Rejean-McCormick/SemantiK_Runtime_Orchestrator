from __future__ import annotations
import hashlib, json
from pathlib import Path

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def make_wordbench_run(root: Path, *, pgfs: int = 1, status: str = "OK") -> Path:
    root.mkdir(parents=True)
    summary = dump(root / "summary.json", {
        "run": {"run_id": "r1", "mode": "release", "overall_status": status, "execution_state": "completed", "partial": False},
        "release": {"decision": "READY", "release_gates_passed": True, "manifest_verified": True},
    })
    arts=[{"path":"summary.json","role":"machine_summary","required":True,"size_bytes":summary.stat().st_size,"sha256":sha(summary)}]
    for i in range(pgfs):
        p=root/"artifacts"/"pgf"/f"Grammar{i}.pgf"; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(f"PGF-{i}".encode())
        arts.append({"path":p.relative_to(root).as_posix(),"role":"pgf","required":True,"size_bytes":p.stat().st_size,"sha256":sha(p)})
    dump(root/"manifest.json",{"schema_id":"gf-wordbench.artifact-manifest","schema_version":"1.0","run_id":"r1","artifacts":arts})
    return root

def make_inputs(root: Path):
    bridge=dump(root/"bridge.json",{"schema_version":"1.0","contract_version":"1.0","operations":{"clause.transitive_event":{"expression":"X"}}})
    lex=dump(root/"lexicon.json",{"schema_version":"1.0","lexicon_id":"lex","entries":[]})
    profile=dump(root/"profile.json",{"schema_version":"1.0","profile_id":"sa-core","profile_version":1,"required_operations":[],"required_features":[],"required_block_kinds":[]})
    suite=dump(root/"suite.json",{"schema_version":"1.0","suite_id":"suite"})
    return bridge,lex,profile,suite
