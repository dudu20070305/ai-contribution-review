#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算文本产出归属（R1）。

用法：
    python compute_attribution.py analysis.json           # 打印结果
    python compute_attribution.py analysis.json --write    # 写回 attribution.computed

输入取 analysis.json 的 attribution.paragraphs，每段需有 id、chars、tier
（tier 为 null 表示来源不明）。加权口径见 references/rules.md 的 R1。
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import BUCKET_LABELS, BUCKET_ORDER, RULE_VERSION, TIERS, compute_attribution  # noqa: E402


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    _stdout_utf8()
    ap = argparse.ArgumentParser(description="按 R1 七档表计算文本产出归属")
    ap.add_argument("analysis", type=Path, help="analysis.json 路径")
    ap.add_argument("--write", action="store_true", help="把结果写回 attribution.computed")
    args = ap.parse_args()

    data = json.loads(args.analysis.read_text(encoding="utf-8"))
    paragraphs = (data.get("attribution") or {}).get("paragraphs") or []
    if not paragraphs:
        print("错误：attribution.paragraphs 为空，无法计算。", file=sys.stderr)
        return 2

    computed = compute_attribution(paragraphs)

    print(f"规则版本 v{RULE_VERSION}　段落数 {len(paragraphs)}")
    print("-" * 62)
    print(f"{'档':<3}{'权重':<7}{'字数':<7}{'段数':<6}说明")
    for tier, meta in sorted(TIERS.items()):
        chars = sum(int(p.get("chars") or 0) for p in paragraphs
                    if p.get("traceable", True) and p.get("tier") == tier)
        count = sum(1 for p in paragraphs
                    if p.get("traceable", True) and p.get("tier") == tier)
        if count == 0:
            continue
        print(f"{tier:<3}{str(meta['weight']) + '%':<7}{chars:<7}{count:<6}{meta['label']}")
    if computed["unknown_paragraphs"]:
        print(f"{'—':<3}{'—':<7}{computed['unknown_chars']:<7}"
              f"{computed['unknown_paragraphs']:<6}来源不明（移出分母）")
    print("-" * 62)
    for b in BUCKET_ORDER:
        row = computed["buckets"][b]
        print(f"{BUCKET_LABELS[b]:<10}{row['chars']:>7} 字　{row['pct']:>5.1f}%")
    print("-" * 62)
    print(f"加权归属率　{computed['weighted_rate']}%")
    print(f"可溯源覆盖率 {computed['coverage_pct']}%"
          f"（可溯源 {computed['traceable_chars']} 字／共 "
          f"{computed['traceable_chars'] + computed['unknown_chars']} 字）")

    if args.write:
        data.setdefault("attribution", {})["computed"] = computed
        args.analysis.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\n已写回 {args.analysis} 的 attribution.computed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
