# 报告规格与 analysis.json 字段

报告的版式由 `scripts/render_report.py` 与 `assets/report.css` 决定，不要手写 HTML。你只需要把判定写成 `analysis.json`。

## 一、版式（一页 A4）

自上而下四区，教师 30 秒读完：

```
页头  学生 / 作业 / 日期 / 任务 / 目标语言 / 会话 ID ＋ 状态标（初步判定·已复核·记录不完整·规则版本）
一    文本产出归属      三条横条（AI 直接生成／学生改写／学生原创）＋ 加权归属率 / 覆盖率 / 来源不明
二    决策与验证        六环节 × 四级的点阵矩阵，附降级与存疑说明
三    门槛判定          四项标签，✓ 或 ✗，各附一句依据
四    纵向比较          与本人前三次中位数对照；无基线时明确写「无历史基线」
结论  一句话，必须引用具体行为
不确定  溯源 / 判定 / 输入 / 复核，四类必须都填
页脚  规则版本 · 会话 ID · 生成时间 · 模型 ＋ 使用边界声明
```

**版式硬约束**

- 不超过一页。内容超长时优先压缩结论与补充观察，不要删不确定性。
- 结论句引用具体行为，不写「表现良好」「优秀」「良好」「得分」这类评价性措辞。校验器会拦。
- 页脚固定保留：*本报告反映过程结构，不等同于对学业成果的最终评价；不用于处分、评优、升学或学生间比较，不向第三方提供。*
- 矩阵用点表示等级，**不出现数字**。○ 表示初判等级（因缺证据降级），● 表示最终等级。

## 二、analysis.json 字段

### meta

| 字段 | 类型 | 说明 |
|---|---|---|
| `student_label` | string | 脱敏代号，如「学生A」。不写真实姓名 |
| `assignment_title` | string | 作业标题 |
| `date` | string | `YYYY-MM-DD` |
| `session_id` | string | 会话标识，教师据此核对记录。**必填** |
| `target_language` | string | 如「英语」 |
| `teaching_objective` | string | 教师声明的教学目标原文 |
| `target_language_production_is_objective` | bool | 教学目标是否含目标语言产出。决定第 3 档能否启用 |
| `task_type` | string | 写作／阅读／语法练习等 |
| `model` | string | 生成报告的模型标识，不明写「未记录」 |
| `record_completeness` | `complete` \| `partial` | 记录是否完整。`partial` 会在页眉显示「记录不完整」 |
| `review_status` | `preliminary` \| `reviewed` | 未经教师复核填 `preliminary` |
| `report_mode` | `assessed` \| `no_record` | 过程记录缺失时用 `no_record` |

### attribution

```json
"attribution": {
  "paragraphs": [
    {"id": 1, "chars": 42, "tier": 5, "traceable": true,
     "source_turn": 2, "evidence": "学生第 1 轮：第三段写包饺子"}
  ]
}
```

| 字段 | 说明 |
|---|---|
| `id` | 段号，从 1 起 |
| `chars` | 该段字数（正整数）。按字符数计，中英文同等对待 |
| `tier` | 1–7 的整数；来源不明填 `null` |
| `traceable` | 能否匹配到 AI 输出。`tier` 为 `null` 时必须为 `false` |
| `source_turn` | 对应的 AI 输出轮次 |
| `evidence` | 证据位置（哪一轮的哪句），复核时据此定位 |

`attribution.computed` 由 `compute_attribution.py --write` 写入，**不要手填**。校验器会重算并比对。

### stages

```json
{"id": "E4", "engaged": true, "initial_grade": "I", "final_grade": "C",
 "evidence_type": null, "missing_evidence": "理由可述",
 "quote": "这段不对，换掉", "turn": 11,
 "downgrade_reason": "只说「不对」，未说明错在哪",
 "note": "否定动作成立，但缺判断依据"}
```

| 字段 | 说明 |
|---|---|
| `engaged` | 该环节是否有介入 |
| `initial_grade` | `P`/`A`/`C`/`I`；未介入填 `null` |
| `final_grade` | 最终等级；未介入填 `"未涉及"`；判不准填 `"存疑"` |
| `evidence_type` | 最终为 C/I 且**未降级**时必填，取「来源可溯／理由可述／质量可辨」 |
| `missing_evidence` | **发生降级**时必填，填缺失的那一类 |
| `quote` | 原话。已介入时必填，不得改写 |
| `turn` | 轮次。已介入时必填 |
| `downgrade_reason` | 降级原因 |
| `note` | 补充说明；标「存疑」时必须在此并列两种读法 |

降级只允许一级：`I→C`、`C→A`。写 `I→A` 会被校验器拦下。

### gates

```json
{"id": "K1", "met": true, "basis": "E4 指出 … 并给出正确形式", "search_scope": "全部 12 轮"}
```

`met` 为布尔值；`no_record` 模式下为 `null`（不判定）。`search_scope` **任何情况都不能空**——没写检索范围的门槛判定不算数。

### 其余

| 字段 | 说明 |
|---|---|
| `longitudinal` | `{"available": bool, "baseline": "本人前三次中位数", "items": [{"metric","baseline","current","delta"}]}`。无历史报告时 `available: false` |
| `conclusion` | 一句话结论，≤120 字，引用具体行为 |
| `uncertainty` | 四个键全部必填：`traceability`／`judgement`／`input_completeness`／`review` |
| `supplementary` | 字符串数组。补充观察，不进判定，渲染为一行注记 |
| `disputes` | 数组，学生异议与教师答复的记录 |

## 三、怎么写出好的结论句

结论句回答「**谁做了什么**」，不回答「**好不好**」。

- 好：「AI 承担了语言组织，学生承担了内容设定、一次语法纠错与版本选择；未出现对自身学习状态的判断。」
- 好：「文本以 AI 生成为主，学生在素材与写作策略上有明确判断，但没有形成可复核的纠错；取舍环节证据不足，标存疑。」
- 差：「学生表现良好，能较好地使用 AI。」——无具体行为，且属总体评价。

## 四、打印

浏览器打开 HTML → 打印 → 目标另存为 PDF，纸张 A4、边距选「无」、关闭页眉页脚。样式已按 A4 调好，无需缩放。

若用命令行批处理：

```bash
msedge --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=report.pdf file:///path/to/report.html
```
