"""禁 emoji 检查冒烟。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_no_emoji.py"


def test_no_emoji_in_skill_packages():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
