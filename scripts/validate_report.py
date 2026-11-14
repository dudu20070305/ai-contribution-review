#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 analysis.json 是否符合方案 v1.0 的硬约束。

用法：
    python validate_report.py analysis.json [analysis2.json ...]

退出码：0 全部通过（可能有警告）；1 存在错误；2 文件读取失败。

这些检查针对的正是原方案被复审指出、在新版中被明确禁止的几类问题：
合成分数、无证据的等级、无检索范围的门槛判定、缺失的不确定性标注。
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import (  # noqa: E402
    BANNED_IN_CONCLUSION,
    COMPOSITE_KEY_PATTERNS,
    GATE_IDS,
    GRADES,
    LANGUAGE_DEPENDENT_TIERS,
    NOT_ENGAGED,
    PENDING,
    STAGE_IDS,
    VALID_STAGE_GRADES,
    compute_attribution,
    downgrade,
)

EVIDENCE_TYPES = {"来源可溯", "理由可述", "质量可辨"}
META_REQUIRED = [
    "student_label", "assignment_title", "date", "session_id", "target_language",
    "teaching_objective", "target_language_production_is_objective", "task_type",
    "record_completeness", "review_status", "report_mode",
]
UNCERTAINTY_KEYS = ["traceability", "judgement", "input_completeness", "review"]


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _walk_keys(obj, prefix=""):
    """递归遍历所有键名，用于检测合成分数字段。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            yield path, k
            yield from _walk_keys(v, path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_keys(v, f"{prefix}[{i}]")


class Report:
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.warnings = []

    def err(self, code, msg):
        self.errors.append((code, msg))

    def warn(self, code, msg):
        self.warnings.append((code, msg))

    def dump(self):
        for code, msg in self.errors:
            print(f"  ERROR {code}　{msg}")
        for code, msg in self.warnings:
            print(f"  WARN  {code}　{msg}")
        if not self.errors and not self.warnings:
            print("  ✓ 全部检查通过")
        return 1 if self.errors else 0


def validate(data, name="(inline)"):
    r = Report(name)

    # --- 结构 -------------------------------------------------------
    for key in ["schema_version", "rule_version", "meta", "attribution",
                "stages", "gates", "conclusion", "uncertainty"]:
        if key not in data:
            r.err("E01", f"缺少顶层字段 {key}")
    if r.errors:
        return r

    # --- 禁止合成分数 ------------------------------------------------
    for path, key in _walk_keys(data):
        low = str(key).lower()
        for pat in COMPOSITE_KEY_PATTERNS:
            if pat.lower() in low:
                r.err("E14", f"出现疑似合成分数字段 {path}（命中「{pat}」）。"
                             f"方案不设总分、不设综合指数。")
                break

    # --- meta -------------------------------------------------------
    meta = data.get("meta") or {}
    for key in META_REQUIRED:
        if key not in meta or meta[key] in (None, ""):
            r.err("E02", f"meta 缺少必填项 {key}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("date", ""))):
        r.err("E02", f"meta.date 须为 YYYY-MM-DD，收到 {meta.get('date')!r}")
    if meta.get("record_completeness") not in {"complete", "partial"}:
        r.err("E02", "meta.record_completeness 须为 complete 或 partial")
    if meta.get("review_status") not in {"preliminary", "reviewed"}:
        r.err("E02", "meta.review_status 须为 preliminary 或 reviewed")
    premise = bool(meta.get("target_language_production_is_objective"))
    mode = meta.get("report_mode")
    assessed = mode == "assessed"
    if mode not in {"assessed", "no_record"}:
        r.err("E02", "meta.report_mode 须为 assessed 或 no_record")

    # --- R1 归属 ------------------------------------------------------
    paragraphs = (data.get("attribution") or {}).get("paragraphs") or []
    if assessed and not paragraphs:
        r.err("E03", "attribution.paragraphs 为空。若过程记录缺失，应把 "
                     "meta.report_mode 设为 no_record，整份报告改写为「过程记录缺失，无法评价」。")
    if mode == "no_record" and paragraphs:
        r.err("E03", "report_mode 为 no_record 时不应出现段落归属记录（不得在缺证据时推断）")
    for p in paragraphs:
        tier = p.get("tier")
        if tier is None:
            if p.get("traceable", True):
                r.err("E03", f"段 {p.get('id')} 档位为空却标为可溯源")
            continue
        if tier not in {1, 2, 3, 4, 5, 6, 7}:
            r.err("E03", f"段 {p.get('id')} 档位非法：{tier!r}（须为 1–7 或 null）")
        if tier in LANGUAGE_DEPENDENT_TIERS and not premise:
            r.err("E04", f"段 {p.get('id')} 用了第 {tier} 档（跨语言成文），但"
                         f"meta.target_language_production_is_objective 为 false。"
                         f"语言只是载体时该档不得启用。")
        if not p.get("evidence"):
            r.warn("W05", f"段 {p.get('id')} 未记录证据位置，复核时无法定位")

    computed = (data.get("attribution") or {}).get("computed")
    if paragraphs:
        try:
            fresh = compute_attribution(paragraphs)
        except ValueError as exc:
            r.err("E03", str(exc))
            fresh = None
        if fresh:
            if computed is None:
                r.err("E15", "缺少 attribution.computed，请先运行 compute_attribution.py --write")
            else:
                for k in ["traceable_chars", "unknown_chars", "unknown_paragraphs", "weighted_rate"]:
                    if abs(float(computed.get(k, -1)) - float(fresh[k])) > 0.11:
                        r.err("E15", f"computed.{k} 与重算不一致："
                                     f"{computed.get(k)} vs {fresh[k]}")
                for b, row in fresh["buckets"].items():
                    got = (computed.get("buckets") or {}).get(b, {}).get("pct")
                    if got is None or abs(float(got) - row["pct"]) > 0.11:
                        r.err("E15", f"computed.buckets.{b}.pct 与重算不一致：{got} vs {row['pct']}")
            if fresh["coverage_pct"] < 60:
                r.warn("W01", f"可溯源覆盖率仅 {fresh['coverage_pct']}%，"
                              f"百分比可比性下降，报告须显著标注分母范围")

    # --- R2/R3/R4 环节与等级 -------------------------------------------
    stages = data.get("stages") or []
    ids = [s.get("id") for s in stages]
    if sorted(ids) != sorted(STAGE_IDS):
        r.err("E05", f"环节须恰好为 {STAGE_IDS}，收到 {ids}")
    for s in stages:
        sid = s.get("id")
        final = s.get("final_grade")
        initial = s.get("initial_grade")
        engaged = bool(s.get("engaged"))
        if final not in VALID_STAGE_GRADES:
            r.err("E06", f"{sid} 最终等级非法：{final!r}")
            continue
        if mode == "no_record" and engaged:
            r.err("E06", f"report_mode 为 no_record 时 {sid} 不得判为已介入")
        if not engaged:
            if final != NOT_ENGAGED:
                r.err("E06", f"{sid} 标为未介入，最终等级应为「{NOT_ENGAGED}」，收到 {final!r}")
            continue
        if final == NOT_ENGAGED:
            r.err("E06", f"{sid} 标为已介入，最终等级不应为「{NOT_ENGAGED}」")
        if initial not in GRADES:
            r.err("E06", f"{sid} 初判等级非法：{initial!r}（须为 P/A/C/I）")
        if not str(s.get("quote") or "").strip():
            r.err("E07", f"{sid} 已介入但未引用原话（R4 要求等级须有证据）")
        if s.get("turn") in (None, ""):
            r.err("E07", f"{sid} 未记录轮次，无法复核")
        downgraded = initial in GRADES and final in GRADES and initial != final
        if downgraded:
            if final != downgrade(initial):
                r.err("E08", f"{sid} 由 {initial} 改为 {final}，R4 只允许降一级"
                             f"（{initial}→{downgrade(initial)}）")
            if not str(s.get("downgrade_reason") or "").strip():
                r.err("E08", f"{sid} 发生降级但未注明原因")
            if s.get("missing_evidence") not in EVIDENCE_TYPES:
                r.err("E08", f"{sid} 发生降级但缺失的证据类型不在三类之内："
                             f"{s.get('missing_evidence')!r}")
        elif final in {"C", "I"}:
            if s.get("evidence_type") not in EVIDENCE_TYPES:
                r.err("E07", f"{sid} 判为 {final}，须提供三类证据之一"
                             f"（来源可溯／理由可述／质量可辨），否则应降级")
        if final == PENDING and not str(s.get("note") or "").strip():
            r.err("E09", f"{sid} 标为存疑，须在 note 中并列两种读法及理由")

    # --- R5 门槛 --------------------------------------------------------
    gates = data.get("gates") or []
    gids = [g.get("id") for g in gates]
    if sorted(gids) != sorted(GATE_IDS):
        r.err("E09b", f"门槛须恰好为 {GATE_IDS}，收到 {gids}")
    for g in gates:
        gid = g.get("id")
        if not isinstance(g.get("met"), bool):
            if not (mode == "no_record" and g.get("met") is None):
                r.err("E10", f"{gid} 的 met 须为布尔值（无过程记录时可为 null，表示不判定）")
        if g.get("met") and not str(g.get("basis") or "").strip():
            r.err("E10", f"{gid} 判为满足但未给出依据原话")
        if not str(g.get("search_scope") or "").strip():
            r.err("E11", f"{gid} 未说明检索范围（是否通读全部对话）")

    # --- 结论 -----------------------------------------------------------
    conclusion = str(data.get("conclusion") or "").strip()
    if not conclusion:
        r.err("E12", "conclusion 为空")
    else:
        hits = [w for w in BANNED_IN_CONCLUSION if w in conclusion]
        # 「表现良好」会连带命中「良好」，只报最长的一条
        hits = [w for w in hits if not any(w != o and w in o for o in hits)]
        for word in hits:
            r.err("E13", f"结论句含评价性措辞「{word}」。结论须引用具体行为，不下总体评价。")
        if len(conclusion) > 120:
            r.warn("W02", f"结论句 {len(conclusion)} 字，建议压到 120 字以内")

    # --- 不确定性 --------------------------------------------------------
    unc = data.get("uncertainty") or {}
    for key in UNCERTAINTY_KEYS:
        if not str(unc.get(key) or "").strip():
            r.err("E12", f"uncertainty.{key} 为空。四类不确定性必须显式标注。")

    return r


def main():
    _stdout_utf8()
    if len(sys.argv) < 2:
        print("用法：python validate_report.py analysis.json [...]", file=sys.stderr)
        return 2
    worst = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[读取失败] {path}：{exc}")
            worst = max(worst, 2)
            continue
        print(f"[{path.name}]")
        worst = max(worst, validate(data, path.name).dump())
    print()
    print("通过" if worst == 0 else "未通过")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
