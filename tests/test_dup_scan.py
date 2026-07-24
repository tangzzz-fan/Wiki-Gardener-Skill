"""dup_scan.py 单元 / 集成测试。

运行：
    pip install -r requirements-dev.txt
    python -m pytest tests/test_dup_scan.py -v
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "wiki-gardener" / "scripts" / "dup_scan.py"
FIXTURE_VAULT = ROOT / "tests" / "fixtures" / "sample-vault"


def load_dup_scan():
    spec = importlib.util.spec_from_file_location("dup_scan", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def dup_scan():
    return load_dup_scan()


def test_collect_notes_skips_system_and_archive(dup_scan):
    notes = dup_scan.collect_notes(FIXTURE_VAULT)
    rels = {str(p.relative_to(FIXTURE_VAULT)) for p in notes}

    assert not any(r.startswith("00_系统") for r in rels)
    assert not any(r.startswith("90_archive") for r in rels)
    assert "20_领域/iOS/BLE 配网流程.md" in rels
    assert "10_inbox/BLE配网重复草稿.md" in rels
    assert "20_领域/_未归类/孤立的天气随笔.md" in rels


def test_near_duplicate_ble_notes_detected():
    """流程 / 踩坑 / inbox 草稿三者高度重合，应落在同一重复簇。"""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURE_VAULT),
            "--threshold",
            "0.7",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["note_count"] >= 5

    # 至少应检出「流程」与「inbox 草稿」这对近似重复
    pair_names = {(p["a"], p["b"]) for p in data["pairs"]}
    flat = {a for a, _ in pair_names} | {b for _, b in pair_names}
    assert any("BLE 配网流程" in n for n in flat)
    assert any("BLE配网重复草稿" in n or "踩坑" in n for n in flat)

    # 天气随笔应与 BLE 主题低相关——不应单独与 BLE 成簇主导
    weather_pairs = [
        p
        for p in data["pairs"]
        if "天气" in p["a"] or "天气" in p["b"]
    ]
    for p in weather_pairs:
        assert p["similarity"] < 0.85, p


def test_archive_notes_not_scanned():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURE_VAULT),
            "--threshold",
            "0.5",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    blob = json.dumps(data, ensure_ascii=False)
    assert "90_archive" not in blob
    assert "旧版BLE配网" not in blob


def test_cluster_union_find(dup_scan):
    pairs = [
        ("a.md", "b.md", 0.9),
        ("b.md", "c.md", 0.88),
        ("d.md", "e.md", 0.91),
    ]
    clusters = dup_scan.cluster(pairs)
    assert sorted(clusters) == [["a.md", "b.md", "c.md"], ["d.md", "e.md"]]


def test_missing_vault_exits_nonzero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "/tmp/does-not-exist-vault-xyz"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
