"""Static check: no hardcoded API keys in source."""
import re
from pathlib import Path

import pytest

_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"),
]


@pytest.mark.parametrize("path", list(Path("src").rglob("*.py")))
def test_no_hardcoded_api_keys(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for pat in _SECRET_PATTERNS:
        assert not pat.search(text), f"hardcoded key in {path}"
