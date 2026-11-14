# -*- coding: utf-8 -*-
"""规则常量与共享计算。规则版本 1.0，与 SKILL.md 中的 R1–R5 一一对应。

本模块只承载「有确定取值」的部分：七档权重、六环节编号、四级标签、四项门槛。
所有命名与 SKILL.md、references/rules.md 保持一致，改动需同步三处。
"""

RULE_VERSION = "1.0"
SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------- R1 七档
# weight 为文本产出归属权重（%），bucket 用于报告中的三段条形图分组。
TIERS = {
    1: {"weight": 0, "bucket": "ai_direct", "label": "直接采用 AI 输出，未改动"},
    2: {"weight": 10, "bucket": "ai_direct", "label": "只提要求、由 AI 自行修改"},
    3: {"weight": 25, "bucket": "student_revised", "label": "口头给出要点，AI 跨语言成文"},
    4: {"weight": 35, "bucket": "student_revised", "label": "指定替换具体内容"},
    5: {"weight": 45, "bucket": "student_revised", "label": "口头给出要点，AI 同语言组织成文"},
    6: {"weight": 80, "bucket": "student_revised", "label": "自己重写该段"},
    7: {"weight": 100, "bucket": "student_original", "label": "自己撰写，AI 未参与"},
}

BUCKET_ORDER = ["ai_direct", "student_revised", "student_original"]
BUCKET_LABELS = {
    "ai_direct": "AI 直接生成",
    "student_revised": "学生改写",
    "student_original": "学生原创",
}

# 第 3 档需教师在布置作业时声明「教学目标包含目标语言产出」方可启用。
LANGUAGE_DEPENDENT_TIERS = {3}

# ---------------------------------------------------------------- R2 六环节
STAGES = [
    ("E1", "任务定义", "题目、对象、字数、文体、禁忌"),
    ("E2", "素材与信息提供", "学生注入的具体信息、例子、经历、数据"),
    ("E3", "结构与论证设计", "段落安排、论点顺序、论证策略"),
    ("E4", "校验与纠错", "指出 AI 的具体错误、否定方案、要求重做"),
    ("E5", "最终取舍与定稿", "明确采纳或否决、比较多个版本"),
    ("E6", "元认知调控", "对自身理解、策略、进度的表述与调整"),
]
STAGE_IDS = [s[0] for s in STAGES]
STAGE_NAMES = {s[0]: s[1] for s in STAGES}

# ---------------------------------------------------------------- R3 四级
GRADES = ["P", "A", "C", "I"]
GRADE_LABELS = {"P": "被动", "A": "主动", "C": "建构", "I": "交互"}
GRADE_ORDER = {"P": 0, "A": 1, "C": 2, "I": 3}
NOT_ENGAGED = "未涉及"
PENDING = "存疑"
VALID_STAGE_GRADES = set(GRADES) | {NOT_ENGAGED, PENDING}

# ---------------------------------------------------------------- R5 四项门槛
GATES = [
    ("K1", "有可复核的校验", "至少一次指出 AI 的具体错误并说明理由（E4 达 I 且有证据）", "未经验证"),
    ("K2", "有内容增量", "至少一处 AI 不可能知道的信息（E2 达 C 且有来源）", "无私有信息"),
    ("K3", "有明确取舍", "至少一次明确指出采纳或否决的理由（E5 达 A 以上且有理由）", "默认全收"),
    ("K4", "有自我监控", "至少一次对自身理解或策略的判断（E6 达 A 以上）", "无自我监控记录"),
]
GATE_IDS = [g[0] for g in GATES]
GATE_NAMES = {g[0]: g[1] for g in GATES}
GATE_FAIL_LABELS = {g[0]: g[3] for g in GATES}

# 结论句禁用的评价性措辞：结论必须引用具体行为，不得下总体评价。
BANNED_IN_CONCLUSION = [
    "表现良好", "优秀", "良好", "很差", "较差", "不合格", "合格",
    "得分", "总分", "综合评分", "值得表扬", "需要批评",
]

# 禁止出现的合成分数字段名（大小写不敏感的子串匹配）。
COMPOSITE_KEY_PATTERNS = [
    "score", "total", "composite", "overall", "综合", "得分", "总分",
    "认知贡献", "贡献率", "contribution",
]


def tier_weight(tier):
    """返回某一档的权重；档位非法时抛 ValueError。"""
    if tier not in TIERS:
        raise ValueError(f"档位必须是 1–7 的整数，收到 {tier!r}")
    return TIERS[tier]["weight"]


def tier_bucket(tier):
    return TIERS[tier]["bucket"]


def compute_attribution(paragraphs):
    """按字数计算文本产出归属。

    参数 paragraphs: [{"chars": int, "tier": 1-7 或 None, "traceable": bool}, ...]
    tier 为 None 或 traceable 为 False 的段落计入「来源不明」，移出分母。

    返回：可溯源字数、来源不明字数与段数、三段分组占比、加权归属率、可溯源覆盖率。
    """
    traceable_chars = 0
    unknown_chars = 0
    unknown_paragraphs = 0
    bucket_chars = {b: 0 for b in BUCKET_ORDER}

    for p in paragraphs:
        chars = int(p.get("chars") or 0)
        tier = p.get("tier")
        is_traceable = p.get("traceable", True) and tier is not None
        if not is_traceable:
            unknown_chars += chars
            unknown_paragraphs += 1
            continue
        if tier not in TIERS:
            raise ValueError(f"段 {p.get('id')} 的档位非法：{tier!r}")
        if chars <= 0:
            raise ValueError(f"段 {p.get('id')} 的字数必须为正数，收到 {chars!r}")
        traceable_chars += chars
        bucket_chars[tier_bucket(tier)] += chars

    total = traceable_chars + unknown_chars
    buckets = {}
    for b in BUCKET_ORDER:
        share = (bucket_chars[b] / traceable_chars * 100) if traceable_chars else 0.0
        buckets[b] = {"chars": bucket_chars[b], "pct": round(share, 1)}

    weighted = 0.0
    if traceable_chars:
        acc = sum(
            int(p["chars"]) * tier_weight(p["tier"])
            for p in paragraphs
            if p.get("traceable", True) and p.get("tier") is not None
        )
        weighted = acc / traceable_chars

    return {
        "traceable_chars": traceable_chars,
        "unknown_chars": unknown_chars,
        "unknown_paragraphs": unknown_paragraphs,
        "buckets": buckets,
        "weighted_rate": round(weighted, 1),
        "coverage_pct": round(traceable_chars / total * 100, 1) if total else 0.0,
    }


def downgrade(initial):
    """R4 降级：C→A，I→C。其余等级不降。"""
    if initial == "C":
        return "A"
    if initial == "I":
        return "C"
    return initial
