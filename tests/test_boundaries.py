from pathlib import Path

def test_no_product_internal_imports():
    root=Path(__file__).resolve().parents[1]/"src"/"semantik_runtime_orchestrator"
    text="\n".join(p.read_text(encoding="utf-8") for p in root.glob("*.py"))
    assert "import semantik_architect" not in text
    assert "from semantik_architect" not in text
    assert "import gf_wordbench" not in text
    assert "from gf_wordbench" not in text
    assert "import levelupdiag" not in text
    assert "from levelupdiag" not in text
    assert "import encyk" not in text
    assert "from encyk" not in text
    assert "import kompiler" not in text
    assert "from kompiler" not in text
    assert "import koa_mediatheque" not in text
    assert "from koa_mediatheque" not in text
    assert "import interaction_kernel" not in text
    assert "from interaction_kernel" not in text
    assert "import kristal" not in text
    assert "from kristal" not in text


def test_no_shell_true():
    root=Path(__file__).resolve().parents[1]/"src"/"semantik_runtime_orchestrator"
    text="\n".join(p.read_text(encoding="utf-8") for p in root.glob("*.py"))
    assert "shell=True" not in text
