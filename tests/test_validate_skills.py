"""结构校验脚本自身的冒烟测试。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate_skills.py"


def test_validate_skills_passes_on_repo():
    result = subprocess.run(
        [sys.executable, str(VALIDATE), "--root", str(ROOT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout or "通过" in result.stdout
