import textwrap
from pathlib import Path

import pytest

from lineaihelper.prompt_engine import PromptEngine


def test_parse_frontmatter() -> None:
    engine = PromptEngine()
    content = textwrap.dedent("""\
        ---
        version: v1
        author: test
        ---
        Hello {{ name }}""")
    metadata, body = engine._parse_frontmatter(content)
    assert metadata["version"] == "v1"
    assert metadata["author"] == "test"
    assert body == "Hello {{ name }}"


def test_parse_no_frontmatter() -> None:
    engine = PromptEngine()
    content = "Hello {{ name }}"
    metadata, body = engine._parse_frontmatter(content)
    assert metadata == {}
    assert body == "Hello {{ name }}"


def test_render_stock_prompt(tmp_path: Path) -> None:
    # 建立臨時 prompt 目錄
    stock_dir = tmp_path / "stock"
    stock_dir.mkdir()
    prompt_file = stock_dir / "latest.md"
    content = textwrap.dedent("""\
        ---
        version: v1
        ---
        Symbol: {{ symbol }}, Price: {{ price }}""")
    prompt_file.write_text(content, encoding="utf-8")

    engine = PromptEngine(prompts_dir=tmp_path)
    rendered = engine.render("stock", {"symbol": "2330", "price": 600})
    assert rendered == "Symbol: 2330, Price: 600"


def test_prompt_not_found() -> None:
    engine = PromptEngine()
    with pytest.raises(FileNotFoundError):
        engine.get_prompt("non_existent")
