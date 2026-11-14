# 贡献界定模型的构思方案

本文说明这套评价模型为什么这样设计，以及每一条理论主张的文献依据。

版本 1.0 ｜ 配套规则 R1–R5 ｜ 引用格式 APA 第 7 版

---

## 一、要解决的问题

教师允许或要求学生用 AI 完成作业时，需要知道两件事：

1. 这份作业里，学生自己做了什么；
2. 这些"做了什么"里，哪些算学习。

现成的工具都答不了。AI 检测器只回答"这段像不像机器写的"，而在这个场景里文本本来就主要由 AI 产出，检测不提供信息量；而且通用检测器对非母语写作者存在系统性偏差（Liang et al., 2023），本场景的目标用户恰是英语学习者。

所以模型必须自己定义"贡献"，并且定义方式要能被教师复核。

## 二、三条否定性论证：为什么不能只给一个百分比

### 2.1 单一百分比没有自然单位

"贡献 70%" 需要一个分母，即"这项作业的全部劳动量"。这个量不可观察、不可计数：学生思考了多久、否决过几个念头、在哪里犹豫，都不留痕。构造一个分母再除，得到的是自造指标，不对应任何可观测量。

更直接的证据是构念错配。ICAP 框架测的是学生对学习材料的认知参与深度，其预测是"学习会增加"（Chi & Wylie, 2014, p. 219），不是"谁产出了多少内容"。把 ICAP 等级当成贡献分量，单位就错了。

### 2.2 文本改动量不等于思想贡献

若按"改了多少字"赋权，会出现两类反向错误：

- 学生用一句话否定整段（"这段不该谈价格，要谈安全"），改动近 100%，但只贡献了一个判断；
- 学生口述两百字要点、AI 组织成文，改动 0%，却贡献了全部论点。

第二种情形有理论依据。成熟写作的本质是"内容问题空间"与"修辞问题空间"之间的双向互动，而正是两者的互动构成写作中的反思（Bereiter & Scardamalia, 1987）。按"谁组织语言"判高低，会把内容问题空间的判断判低。

### 2.3 加权求和的前提不成立

若把若干维度加权成一个总分，需要各属性满足偏好独立与加性独立（Keeney & Raiffa, 1976）。而六环节之间存在能力相关——能发现 AI 语法错误的学生，通常也更会设定任务。前提不成立时，线性加总会把性质差异抹平为相同数值。

## 三、模型的三个操作化定义

不做"贡献"，改做三个可分别核验的量（Messick, 1995：把不可观察的构念拆成可分别验证的操作定义，是效度论证的常规路径）。

| 定义 | 回答什么 | 证据类型 |
|---|---|---|
| 文本产出归属 | 这份作业的字是谁写的 | 段落与 AI 输出的文本对齐 |
| 决策与验证记录 | 作业被拆成哪些决策、每个决策谁主导 | 对话原话 + 轮次 |
| 学习证据 | 学生能否解释来源、理由、质量判断 | 追问记录 |

三者并列呈现，互不相加。这个结构参照修订版 Bloom 分类学的做法：该分类学把一维改为"知识维度 × 认知过程维度"两维，理由正是一个维度无法同时表达"学什么"与"怎么想"（Anderson & Krathwohl, 2001）。

教育评价政策也指向同一方向：《深化新时代教育评价改革总体方案》要求"强化过程评价""探索增值评价"，并明确"破除用分数给学生贴标签"（中共中央, 国务院, 2020）。

---

## 四、五组规则的构思与依据

### R1 文本产出归属：七档，按语言情境分叉

**构思**：以段落为单位，判该段相对 AI 输出发生了哪一层级的改动，赋权后按字数加权。

**依据一（分层）**：修订研究把改动分为表层改动（形式改动、意义保持型改动）与文本基础改动（微观结构、宏观结构），并证明可按"是否改变意义"分层编码，编码者间一致率达 90%（Faigley & Witte, 1981）。本模型的七档沿用这一分层逻辑。

**依据二（第 2 档低权重）**：只提要求让 AI 自行修改，对应"简单转述不算学业成果"的规范红线（清华大学, 2025），故给 10%。

**依据三（语言分叉）**：单语言情境下，学生用目标语言口述，已进入修辞问题空间；双语情境下，学生只提供内容，修辞空间中的跨语言转换完全由 AI 承担（Bereiter & Scardamalia, 1987）。按专长逆转效应，落在能力边界之外的支架与边界之内的替代性质不同，不应同权重（Kalyuga et al., 2003）。故第 3 档（25%）低于第 4 档（35%），排序轴是语言参与度而非内容量。

**依据四（启用前提）**：仅当教学目标包含目标语言产出时启用第 3 档。若语言只是载体，二语水平属构念无关变异，会污染"贡献"这一构念的测量（Messick, 1995）。

> **支撑强度**：分层有强支撑；档位间比例无支撑，属本方案的经验赋值。

### R2 六个决策环节：可分离、可穷尽、可观察

**构思**：把一次作业拆成六个不重叠的决策环节，逐环节判主导方。

**依据一（阶段结构）**：自我调节学习的第一阶段即"任务定义"，第四阶段为"适应"，即对任务认知、目标与策略的调整（Winne & Hadwin, 1998）。写作研究的三大基本过程包含"计划"与"复查"（Hayes & Flower, 1980）。E1、E3、E4 由此对应。

**依据二（元认知单列）**：三处独立来源指向同一处——内容分析框架把元认知列为与认知并列的维度，含评价、计划、管理、觉察（Henri, 1992）；自我调节模型的第四阶段是适应性调节（Winne & Hadwin, 1998）；分类学把元认知知识列为独立知识类型（Anderson & Krathwohl, 2001）。故补入 E6。

**依据三（E2 单列）**：学生注入的具体信息属内容问题空间（Bereiter & Scardamalia, 1987），与结构安排分属不同问题空间，不能合一。

> **支撑强度**：环节划分有中等支撑（结构同构，非直接移植）；环节权重已取消，改为门槛，故不涉及权重赋值。

### R3 ICAP 四级：借用而非采用

**构思**：每环节判 P／A／C／I 四级，只作序数标签。

**依据**：C 级的判据是原文"产出超出所给学习材料的、外化的输出或产品"；I 级须同时满足"双方发言都必须是建构性的"与"须有足够的轮次交替"（Chi & Wylie, 2014, pp. 222–223）。

由这两条款可直接推出：学生只说"好的""继续"时其发言非建构性，不满足第一条件，故不成立交互，只能计 P。

**为什么不赋分**：ICAP 原文预测的是学习效果随等级递增，即 I > C > A > P 的**顺序**，未给出等级之间的距离（Chi & Wylie, 2014）。因此只保留标签，不做算术。

**必须承认的构念差异**：ICAP 测学习投入的深度，本模型用它判决策的深度，属借用。决策深度是学习深度的必要而非充分条件，故报告不得把等级解释为"学习效果"。

> **支撑强度**：强（原文条款直接对应）。

### R4 证据校验：说不出理由就降一级

**构思**：行为上达到 C 或 I，但无法提供三类证据之一时，降一级。

**依据一（判据逐项对应）**："表层投入"研究提出三项判据：能否解释观点来源、能否说明推理过程、能否辨析证据质量；并指出交互次数、成果完整度、工具调用熟练度都不能单独作为证据（彭婧等, 2026）。本模型的三类证据与之逐项对应。

**依据二（更早源头）**：内容分析框架在认知维度内区分表层加工与深层加工，后者以解释、推断、提供证据、形成方案为标志（Henri, 1992）。

**依据三（旁证）**：新手写作者的文本"在表层上符合题目与文体要求，但仅止于表层"（Bereiter & Scardamalia, 1987）。产出合格不等于过程合格，这是必须另找过程证据的实证理由。

> **支撑强度**：强（判据逐项对应）。

### R5 四项门槛：用合取代替加权

**构思**：设 K1 可复核的校验、K2 内容增量、K3 明确取舍、K4 自我监控，四项独立判定，互不抵消。

**依据（反向推论）**：加性模型要求偏好独立与加性独立（Keeney & Raiffa, 1976）。既然六环节之间存在能力相关、前提不成立，就应改用非补偿性结构。这是从前提失败推出的替代方案，不是折中。

**依据（门槛内容）**：K1 对应写作过程的"复查"（Hayes & Flower, 1980）；K2 对应内容问题空间的判断（Bereiter & Scardamalia, 1987）；K3 对应评价性判断——学生须持有标准并能据此判断作品质量（Sadler, 1989）；K4 对应元认知调控（Henri, 1992; Winne & Hadwin, 1998）。

> **支撑强度**：结构有强支撑（前提失败的逻辑推论）；四项门槛的具体位置属本方案判断。

---

## 五、为什么与本人基线比，不用绝对阈值

专长逆转效应表明：同一辅助措施对新手与熟手可能产生相反效果（Kalyuga et al., 2003）。这意味着任何统一的绝对阈值都同时高估一部分学生、低估另一部分。

政策层面亦要求"探索增值评价"（中共中央, 国务院, 2020）。故模型改为与本人既往报告比较，主报纵向变化，绝对阈值一律删除。

## 六、为什么不做 AI 文本检测

**依据**：GPT 类检测器对非母语写作者的误判率显著更高，会把人类写作判为 AI 生成（Liang et al., 2023）。

**推论**：本场景的用户正是英语学习者，检测偏差会直接转化为对他们的系统性不利。加之文本主要由 AI 产出，检测结果无区分度。故模型明确拒绝使用检测器。

## 七、证据、复核与使用边界

**证据分级**：直接证据（学生原话 + 轮次）支撑环节判定与门槛判定；间接证据（文本对齐）支撑文本归属；缺失证据只能输出"无法判定"，不得用于推断。

**复核**：报告须记录规则版本与会话标识，判定逐条留原话，教师可抽查（Messick, 1995：分数解释需可追溯到证据）。

**信度**：若做多评判者对照，报告 Cohen's kappa（Cohen, 1960），但须说明其界值为惯用而非绝对，且受类别数与样本量影响（Landis & Koch, 1977）；不得以最大化 kappa 为目标调参。分析单元须固定为段落与环节，否则评分者间信度无法计算（Newman et al., 1995; Marra et al., 2004）。

**使用边界**：报告不用于处分、评优、升学或学生间比较。理由是后果的严重性与证据强度不匹配——自证材料经不起高利害决定的效度要求（Messick, 1995）。这也与"破除用分数给学生贴标签"的政策取向一致（中共中央, 国务院, 2020）。

---

## 八、支撑强度总表

| 规则 | 理论主张 | 主要文献 | 支撑性质 |
|---|---|---|---|
| 三定义分列 | 单一维度不足以表达两类信息 | Messick (1995); Anderson & Krathwohl (2001) | 强 |
| R1 分层 | 改动可按是否改变意义分层 | Faigley & Witte (1981) | 强 |
| R1 语言分叉 | 内容空间与修辞空间可分；支架与替代性质不同 | Bereiter & Scardamalia (1987); Kalyuga et al. (2003) | 中（同构迁移） |
| R1 启用前提 | 无关变异会污染构念 | Messick (1995) | 强 |
| R2 环节 | 阶段结构可对应决策环节 | Winne & Hadwin (1998); Hayes & Flower (1980) | 中（结构同构） |
| R2 元认知 | 元认知为独立维度 | Henri (1992); Anderson & Krathwohl (2001) | 强 |
| R3 四级 | 四级判据的原文表述 | Chi & Wylie (2014) | 强 |
| R3 序数 | 框架只给顺序，不给距离 | Chi & Wylie (2014) | 强 |
| R4 三证据 | 三项判据逐项对应 | 彭婧等 (2026); Henri (1992) | 强 |
| R4 降级 | 表层符合不等于过程合格 | Bereiter & Scardamalia (1987) | 中 |
| R5 合取 | 加性独立不成立则须非补偿 | Keeney & Raiffa (1976) | 强（反向推论） |
| R5 门槛内容 | 复查／内容／评价判断／元认知各有出处 | Hayes & Flower (1980); Sadler (1989); 等 | 中 |
| 纵向比较 | 专长逆转使统一阈值失效 | Kalyuga et al. (2003); 中共中央, 国务院 (2020) | 强 |
| 拒绝检测器 | 检测器对非母语者有系统性偏差 | Liang et al. (2023) | 强 |
| 信度报告 | kappa 的方法与界值性质 | Cohen (1960); Landis & Koch (1977); Marra et al. (2004) | 强 |
| 使用边界 | 后果效度不匹配 | Messick (1995); 清华大学 (2025) | 强 |

**必须如实说明的一句**：分层、分环节、分级、分门槛均有文献支撑；**档与档之间的具体比例、门槛的具体位置没有文献支撑**，属本方案的经验赋值，需要按班级实际标定。把"分层有据"写成"赋值有据"是过度归属。

## 九、本方案未经验证的部分

1. 未做构念效度、聚合效度、判别效度检验；
2. 未做多评判者信度检验，无 kappa 数据；
3. 规则参照的三份真实对话来自同一人、同一周、同一学段，中小学场景未验证；
4. 六环节能否穷尽覆盖写作决策，未做编码试测。

这些不是可以靠引文献补上的缺口，只能靠实测样本补。

---

## 十、参考文献（APA 第 7 版）

Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.

Bereiter, C., & Scardamalia, M. (1987). *The psychology of written composition*. Lawrence Erlbaum Associates. https://doi.org/10.4324/9780203812310

Chi, M. T. H., & Wylie, R. (2014). The ICAP framework: Linking cognitive engagement to active learning outcomes. *Educational Psychologist*, *49*(4), 219–243. https://doi.org/10.1080/00461520.2014.965823

Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, *20*(1), 37–46. https://doi.org/10.1177/001316446002000104

Faigley, L., & Witte, S. (1981). Analyzing revision. *College Composition and Communication*, *32*(4), 400–414. https://doi.org/10.58680/ccc198115887

Hayes, J. R., & Flower, L. S. (1980). Identifying the organization of writing processes. In L. W. Gregg & E. R. Steinberg (Eds.), *Cognitive processes in writing* (pp. 3–30). Lawrence Erlbaum Associates.

Henri, F. (1992). Computer conferencing and content analysis. In A. R. Kaye (Ed.), *Collaborative learning through computer conferencing: The Najaden papers* (pp. 117–136). Springer. https://doi.org/10.1007/978-3-642-77684-7_8

Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. *Educational Psychologist*, *38*(1), 23–31. https://doi.org/10.1207/S15326985EP3801_4

Keeney, R. L., & Raiffa, H. (1976). *Decisions with multiple objectives: Preferences and value tradeoffs*. Wiley. https://doi.org/10.1017/CBO9781139174084

Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, *33*(1), 159–174. https://doi.org/10.2307/2529310

Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., & Zou, J. (2023). GPT detectors are biased against non-native English writers. *Patterns*, *4*(7), Article 100779. https://doi.org/10.1016/j.patter.2023.100779

Marra, R. M., Moore, J. L., & Klimczak, A. K. (2004). Content analysis of online discussion forums: A comparative analysis of protocols. *Educational Technology Research and Development*, *52*(2), 23–40. https://doi.org/10.1007/BF02504837

Messick, S. (1995). Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning. *American Psychologist*, *50*(9), 741–749. https://doi.org/10.1037/0003-066X.50.9.741

Newman, D. R., Webb, B., & Cochrane, C. (1995). A content analysis method to measure critical thinking in face-to-face and computer supported group learning. *Interpersonal Computing and Technology*, *3*(2), 56–77.

Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences*, *20*(9), 676–688. https://doi.org/10.1016/j.tics.2016.07.002

Sadler, D. R. (1989). Formative assessment and the design of instructional systems. *Instructional Science*, *18*(2), 119–144. https://doi.org/10.1007/BF00117714

Winne, P. H., & Hadwin, A. F. (1998). Studying as self-regulated learning. In D. J. Hacker, J. Dunlosky, & A. C. Graesser (Eds.), *Metacognition in educational theory and practice* (pp. 291–318). Lawrence Erlbaum Associates. https://doi.org/10.4324/9781410602350-19

刘梦君, 邹文龙, 宗敏, 杨兵. (2025). 生成式人工智能何以赋能教学——中学生英语写作教学实证研究 [An empirical study of generative AI-enabled English writing instruction in secondary schools]. *中国电化教育*, *2025*(6), 70–79.

彭婧, 张凌, 曹艳. (2026). 数智时代人机协同学习的表层投入：内涵、表征、生成逻辑与评价调控 [Surface engagement in human–AI collaborative learning: Connotations, representations, generative logic, and evaluative regulation]. *开放教育研究*, *32*(5), 89–98.

清华大学. (2025). *清华大学人工智能教育应用指导原则*. https://www.tsinghua.edu.cn/info/1176/122770.htm

沈彬, 任伟. (2026). 中国语境下生成式人工智能辅助二语写作研究的议题结构与发展趋向 [Research on generative AI-assisted second language writing in the Chinese context: Issue structure and development trends]. *外语教育研究前沿*.

孙发勤, 李娜娜, 沈霞娟, 冯锐. (2026). 认知增强抑或认知债务：生成式人工智能影响认知的双重机制 [Cognitive enhancement or cognitive debt: The dual mechanism of generative AI's impact on cognition]. *电化教育研究*, *2026*(9).

王帆, 王诗琪, 史芹芹. (2026). 破解大学生生成式人工智能过度依赖的原理与策略——适度认知卸载区构建与实现路径 [Mechanisms and strategies for addressing over-reliance on generative AI among university students: Constructing a moderate cognitive offloading zone]. *电化教育研究*, *2026*(8), 71–79.

中共中央, 国务院. (2020). *深化新时代教育评价改革总体方案*. https://www.gov.cn/zhengce/2020-10/14/content_5551132.htm
