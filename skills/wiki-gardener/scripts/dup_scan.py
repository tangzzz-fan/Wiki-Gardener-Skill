#!/usr/bin/env python3
"""
dup_scan.py — 知识库重复簇检测

基于 TF-IDF（字符级 n-gram，兼容中英文）计算库内 Markdown 笔记两两余弦相似度，
输出相似度超过阈值的笔记对与聚簇，供园艺审计的去重协议使用。

用法：
    python3 dup_scan.py <vault路径> [--threshold 0.7] [--json]

排除：00_系统/（系统资产）与 90_archive/（已归档）。
依赖：scikit-learn。
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    sys.exit("缺少依赖 scikit-learn，请先安装：pip install scikit-learn")

SKIP_DIRS = {"00_系统", "90_archive", ".obsidian", ".git", ".trash"}


def collect_notes(vault: Path) -> list[Path]:
    notes = []
    for p in sorted(vault.rglob("*.md")):
        rel = p.relative_to(vault)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        notes.append(p)
    return notes


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def cluster(pairs: list[tuple[str, str, float]]) -> list[list[str]]:
    """把相似笔记对做并查集聚簇。"""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b, _ in pairs:
        union(a, b)

    groups = {}
    for node in parent:
        groups.setdefault(find(node), []).append(node)
    return [sorted(g) for g in groups.values() if len(g) > 1]


def main():
    ap = argparse.ArgumentParser(description="知识库重复簇检测")
    ap.add_argument("vault", help="知识库根目录")
    ap.add_argument("--threshold", type=float, default=0.7, help="相似度阈值，默认 0.7")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()

    vault = Path(args.vault)
    if not vault.is_dir():
        sys.exit(f"路径不存在或不是目录：{vault}")

    notes = collect_notes(vault)
    if len(notes) < 2:
        sys.exit("笔记不足两篇，无需检测。")

    texts = [read_text(p) for p in notes]
    labels = [str(p.relative_to(vault)) for p in notes]

    # 字符级 2–3 gram：中文无需分词，对短笔记也稳健
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3), min_df=1)
    mat = vec.fit_transform(texts)
    sim = cosine_similarity(mat)

    pairs = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            s = round(float(sim[i][j]), 3)
            if s >= args.threshold:
                pairs.append((labels[i], labels[j], s))
    pairs.sort(key=lambda x: -x[2])

    clusters = cluster(pairs)

    if args.json:
        print(json.dumps(
            {"threshold": args.threshold, "note_count": len(labels),
             "pairs": [{"a": a, "b": b, "similarity": s} for a, b, s in pairs],
             "clusters": clusters},
            ensure_ascii=False, indent=2))
    else:
        print(f"扫描笔记 {len(labels)} 篇，阈值 {args.threshold}\n")
        if not pairs:
            print("未发现超过阈值的重复笔记。")
            return
        for idx, c in enumerate(clusters, 1):
            print(f"重复簇 {idx}：")
            for n in c:
                print(f"  - {n}")
            related = [(a, b, s) for a, b, s in pairs if a in c and b in c]
            top = max(related, key=lambda x: x[2])
            hint = ("完全重复，建议归档副本" if top[2] > 0.95
                    else "近似重复，建议走合并协议" if top[2] > 0.85
                    else "互补重叠，建议抽公共部分成独立笔记")
            print(f"  → 最高相似度 {top[2]}，{hint}\n")


if __name__ == "__main__":
    main()
