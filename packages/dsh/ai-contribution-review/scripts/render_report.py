#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 analysis.json 渲染成一页 A4 判读报告（HTML，可直接打印为 PDF）。

用法：
    python render_report.py analysis.json [-o out.html]

版式约束见 references/report-spec.md：一页、四区、结论引用具体行为、
页脚固定标注会话 ID / 生成时间 / 规则版本 / 使用边界。
"""

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import (  # noqa: E402
    BUCKET_LABELS,
    BUCKET_ORDER,
    GATE_FAIL_LABELS,
    GATE_NAMES,
    GRADES,
    GRADE_LABELS,
    NOT_ENGAGED,
    PENDING,
    RULE_VERSION,
    STAGE_NAMES,
    compute_attribution,
)

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "report.css"
BUCKET_CLASS = {"ai_direct": "ai", "student_revised": "rev", "student_original": "orig"}


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def esc(v):
    return html.escape(str(v if v is not None else ""))


def pct(v):
    return f"{float(v):.0f}%"


def render_head(d):
    meta = d.get("meta") or {}
    flags = []
    if meta.get("review_status") == "reviewed":
        flags.append('<div class="flag good">已复核</div>')
    else:
        flags.append('<div class="flag">初步判定</div>')
    if meta.get("record_completeness") == "partial":
        flags.append('<div class="flag warn">记录不完整</div>')
    flags.append(f'<div class="flag">规则 v{RULE_VERSION}</div>')

    return f"""
<header class="rpt-head">
  <div>
    <div class="rpt-kicker">AI 使用与自主贡献 · 过程判读</div>
    <h1 class="rpt-title">{esc(meta.get("assignment_title"))}</h1>
    <div class="rpt-meta">
      <span>学生 <b>{esc(meta.get("student_label"))}</b></span>
      <span>日期 <b>{esc(meta.get("date"))}</b></span>
      <span>任务 <b>{esc(meta.get("task_type"))}</b></span>
      <span>目标语言 <b>{esc(meta.get("target_language"))}</b></span>
      <span>会话 <b>{esc(meta.get("session_id"))}</b></span>
    </div>
  </div>
  <div class="flags">{"".join(flags)}</div>
</header>"""


def render_attribution(d, computed):
    bars = []
    for b in BUCKET_ORDER:
        row = computed["buckets"][b]
        width = max(float(row["pct"]), 0.0)
        bars.append(
            f'<div class="bar"><span class="bar-label">{BUCKET_LABELS[b]}</span>'
            f'<div class="track"><div class="fill {BUCKET_CLASS[b]}" style="width:{width:.1f}%"></div></div>'
            f'<span class="bar-val">{pct(row["pct"])}</span></div>'
        )
    unknown = computed["unknown_paragraphs"]
    unknown_kpi = (
        f'<div class="kpi"><div class="k">来源不明</div>'
        f'<div class="v">{unknown}<small> 段 / {computed["unknown_chars"]} 字</small></div></div>'
        if unknown else
        '<div class="kpi"><div class="k">来源不明</div><div class="v">0<small> 段</small></div></div>'
    )
    exclude_note = (
        f"　来源不明 {unknown} 段（{computed['unknown_chars']} 字）未计入分母。"
        if unknown else ""
    )
    return f"""
<div class="sec"><span class="num">一</span>文本产出归属<span class="hint">R1 七档，按字数加权</span></div>
<div class="bars">{"".join(bars)}</div>
<div class="kpis">
  <div class="kpi"><div class="k">加权归属率</div><div class="v">{computed["weighted_rate"]}<small>%</small></div></div>
  <div class="kpi"><div class="k">可溯源覆盖</div><div class="v">{computed["coverage_pct"]}<small>%</small></div></div>
  {unknown_kpi}
</div>
<div class="note">加权归属率 = Σ（段字数 × 该档权重）÷ 可溯源字数，仅用于与本人基线比较，不与其他学生比较。{exclude_note}</div>"""


def render_matrix(d):
    stages = d.get("stages") or []
    rows, notes = [], []
    for s in stages:
        sid = s.get("id")
        final, initial = s.get("final_grade"), s.get("initial_grade")
        cells = []
        for g in GRADES:
            if final == g:
                cells.append('<td><span class="dot"></span></td>')
            elif initial == g and initial != final and final in GRADES:
                cells.append('<td><span class="dot hollow"></span></td>')
            else:
                cells.append("<td></td>")
        tag = ""
        if final == NOT_ENGAGED:
            tag = '<span class="tag">未涉及</span>'
        elif final == PENDING:
            tag = '<span class="tag">存疑</span>'
        rows.append(
            f'<tr><th><span class="gid">{esc(sid)}</span>{esc(STAGE_NAMES.get(sid, ""))}{tag}</th>'
            f'{"".join(cells)}</tr>'
        )
        if initial in GRADES and final in GRADES and initial != final:
            why = s.get("downgrade_reason") or "未提供理由"
            miss = s.get("missing_evidence") or "—"
            notes.append(f"{sid}　{initial}→{final}（{esc(why)}；缺「{esc(miss)}」）")
        if final == PENDING and s.get("note"):
            notes.append(f"{sid}　存疑：{esc(s.get('note'))}")

    note_html = ""
    if notes:
        note_html = '<div class="note">判定说明：' + "；".join(notes) + "</div>"

    return f"""
<div class="sec"><span class="num">二</span>决策与验证<span class="hint">六环节 × 四级，只记等级不作加总</span></div>
<table class="matrix">
  <thead><tr><th>环节</th><th>P {GRADE_LABELS["P"]}</th><th>A {GRADE_LABELS["A"]}</th>
  <th>C {GRADE_LABELS["C"]}</th><th>I {GRADE_LABELS["I"]}</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
<div class="note">● 最终等级；○ 初判等级（因缺证据降级）；P/A/C/I 为序数标签，不换算为分数。</div>{note_html}"""


def render_gates(d):
    items = []
    for g in d.get("gates") or []:
        gid = g.get("id")
        met = g.get("met")
        name = GATE_NAMES.get(gid, gid)
        if met is True:
            mark, cls, title = "✓", "ok", name
            detail = g.get("basis") or ""
        elif met is False:
            mark, cls = "✗", "no"
            title = GATE_FAIL_LABELS.get(gid, name)
            detail = g.get("basis") or "全部对话中未检出"
        else:
            mark, cls, title = "—", "no", name
            detail = "未判定"
        items.append(
            f'<div class="gate {cls}"><span class="mk">{mark}</span><div>'
            f'<div class="t">{esc(gid)} {esc(title)}</div>'
            f'<div class="d">{esc(detail)}</div></div></div>'
        )
    return f"""
<div class="sec"><span class="num">三</span>门槛判定<span class="hint">四项独立，互不抵消</span></div>
<div class="gates">{"".join(items)}</div>"""


def render_longitudinal(d):
    lo = d.get("longitudinal") or {}
    if not lo.get("available"):
        return """
<div class="sec"><span class="num">四</span>纵向比较<span class="hint">与本人既往报告对照</span></div>
<div class="note">无历史基线，本次不与既往报告比较。</div>"""
    rows = "".join(
        f'<tr><td>{esc(i.get("metric"))}</td><td class="n">{esc(i.get("baseline"))}</td>'
        f'<td class="n">{esc(i.get("current"))}</td><td class="n">{esc(i.get("delta"))}</td></tr>'
        for i in lo.get("items") or []
    )
    return f"""
<div class="sec"><span class="num">四</span>纵向比较<span class="hint">{esc(lo.get("baseline") or "")}</span></div>
<table class="mini">
  <thead><tr><th>指标</th><th class="n">基线</th><th class="n">本次</th><th class="n">变化</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def render_supplementary(d):
    """补充观察不进判定，也不单列一区，作为一行注记附在纵向比较之后。"""
    items = d.get("supplementary") or []
    if not items:
        return ""
    txt = "；".join(str(x) for x in items)
    return f'<div class="note">补充观察：{esc(txt)}</div>'


def render_tail(d):
    unc = d.get("uncertainty") or {}
    return f"""
<div class="concl"><span class="lb">一句话结论</span>{esc(d.get("conclusion"))}</div>
<div class="unc">
  <div><b>溯源</b>　{esc(unc.get("traceability"))}</div>
  <div><b>判定</b>　{esc(unc.get("judgement"))}</div>
  <div><b>输入</b>　{esc(unc.get("input_completeness"))}</div>
  <div><b>复核</b>　{esc(unc.get("review"))}</div>
</div>"""


def render_foot(d):
    meta = d.get("meta") or {}
    status = "已复核" if meta.get("review_status") == "reviewed" else "初步判定（未经教师复核）"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
<footer class="foot">
  <div class="f1">
    <span>规则 v{RULE_VERSION}　会话 {esc(meta.get("session_id"))}　生成 {stamp}　模型 {esc(meta.get("model") or "未记录")}</span>
    <span>{status}</span>
  </div>
  <div class="f2">本报告反映过程结构，不等同于对学业成果的最终评价；不用于处分、评优、升学或学生间比较，不向第三方提供。</div>
</footer>"""


def render_empty(d):
    meta = d.get("meta") or {}
    completeness = {"complete": "完整", "partial": "不完整"}.get(
        meta.get("record_completeness"), "未记录")
    rows = [
        ("会话记录", f"{completeness}；未见生成与修改过程"),
        ("段落溯源", "全部段落无法匹配到本会话内的 AI 输出"),
        ("文本产出归属", "不出读数（分母不可建立）"),
    ]
    prot = "".join(f"<div class='row'><span>{k}</span><span>{v}</span></div>" for k, v in rows)

    # 方案 §8.3：环节全部标「未涉及」，门槛不判定。这里照样铺出矩阵，
    # 让教师能看出「不是判成低分，而是没有证据可判」。
    stage_rows = "".join(
        f'<tr><th><span class="gid">{esc(s.get("id"))}</span>'
        f'{esc(STAGE_NAMES.get(s.get("id"), ""))}<span class="tag">未涉及</span></th>'
        f'{"<td></td>" * len(GRADES)}</tr>'
        for s in d.get("stages") or []
    )
    gate_items = "".join(
        f'<div class="gate no"><span class="mk">—</span><div>'
        f'<div class="t">{esc(g.get("id"))} {esc(GATE_NAMES.get(g.get("id"), ""))}</div>'
        f'<div class="d">不判定</div></div></div>'
        for g in d.get("gates") or []
    )

    return f"""
<div class="sec"><span class="num">一</span>判定状态</div>
<div class="empty">
  <div class="big">过程记录缺失，无法评价</div>
  <div class="sub">本会话内没有可用于溯源的生成与修改过程，按方案不出任何读数。一份如实说「不知道」的报告，比一份编造的百分比更有价值。</div>
</div>
<div class="protocol">{prot}</div>

<div class="sec"><span class="num">二</span>决策与验证<span class="hint">全部环节未涉及，不作判定</span></div>
<table class="matrix">
  <thead><tr><th>环节</th><th>P {GRADE_LABELS["P"]}</th><th>A {GRADE_LABELS["A"]}</th>
  <th>C {GRADE_LABELS["C"]}</th><th>I {GRADE_LABELS["I"]}</th></tr></thead>
  <tbody>{stage_rows}</tbody>
</table>

<div class="sec"><span class="num">三</span>门槛判定<span class="hint">过程记录缺失，四项均不判定</span></div>
<div class="gates">{gate_items}</div>

<div class="concl"><span class="lb">一句话结论</span>{esc(d.get("conclusion"))}</div>
<div class="unc">
  <div><b>溯源</b>　{esc((d.get("uncertainty") or {}).get("traceability"))}</div>
  <div><b>判定</b>　{esc((d.get("uncertainty") or {}).get("judgement"))}</div>
  <div><b>输入</b>　{esc((d.get("uncertainty") or {}).get("input_completeness"))}</div>
  <div><b>复核</b>　{esc((d.get("uncertainty") or {}).get("review"))}</div>
</div>"""


def render(d):
    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
    meta = d.get("meta") or {}
    mode = meta.get("report_mode", "assessed")

    if mode == "no_record":
        body = render_empty(d)
    else:
        computed = (d.get("attribution") or {}).get("computed")
        if not computed:
            computed = compute_attribution((d.get("attribution") or {}).get("paragraphs") or [])
        body = (
            render_attribution(d, computed)
            + render_matrix(d)
            + render_gates(d)
            + render_longitudinal(d)
            + render_supplementary(d)
            + render_tail(d)
        )

    title = f'{meta.get("student_label", "")} · {meta.get("assignment_title", "")} 判读报告'
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
{css}
</style>
</head>
<body>
<div class="page">
{render_head(d)}
{body}
{render_foot(d)}
</div>
</body>
</html>
"""


def main():
    _stdout_utf8()
    ap = argparse.ArgumentParser(description="渲染一页 A4 判读报告")
    ap.add_argument("analysis", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="输出路径，默认与输入同名的 -report.html")
    args = ap.parse_args()

    data = json.loads(args.analysis.read_text(encoding="utf-8"))
    out = args.out or args.analysis.with_name(args.analysis.stem + "-report.html")
    out.write_text(render(data), encoding="utf-8")
    print(f"已生成 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
