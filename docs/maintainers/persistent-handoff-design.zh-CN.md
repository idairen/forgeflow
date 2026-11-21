# 独立、可交付的 Handoff 文件设计

状态：协议与 CLI 已实施，真实 IDE 跨会话验收待执行。日期：2026-11-18。

本文记录实现依据，不覆盖权威
[Handoff 协议](../../.forgeflow/protocol/handoff.md)。实施规范以链接协议为准；以下保留设计说明，CLI 已使用持久化文件作为交接入口。

## 目标与边界

开发人员在没有前一会话上下文、没有本机 runtime 的情况下，取得同一项目的代码、
框架和完整证据后，可以发现交接、核验状态并开始下一次合法 Workflow 执行。

- 独立 Markdown 文件承载交接；对话只输出结果摘要、文件链接和下一步提示。
- 当前 Artifact Graph 仍决定真实状态。交接文件不是新的业务产物或状态数据库。
- 保留 FORWARD、RETURN、TERMINAL / COMPLETE、TERMINAL / HALTED 四种变体。
- 保留现有五种 Entry、Workflow 所有权、Scope、Attempt 和验证门槛。
- 不引入任务分配服务、分布式锁、自动跳过验证或新的并行执行权限。
- 本轮不设计新的通用断点数据库；阶段中途接手使用已有产物与合法恢复入口。

## 目录与标识

在项目根目录下新增 `.forgeflow/handoffs/`，独立于 artifacts 和本地 runtime。
按来源 Scope 分目录，每次发布生成一个 UUID 文件名；UUID 只负责唯一标识，
不代表时间、先后顺序或有效性。

```text
.forgeflow/handoffs/
  project/<uuid>.md
  feature-01/<uuid>.md
  feature-02/<uuid>.md
  feature-01-slice-01/<uuid>.md
```

目录对应 Source Scope，编号沿用 Artifact Protocol。路由纠正的 Source Scope
为 Project，写入 `project/`。接收者按目标 Workflow/Scope 校验内容，不能从
目录名称推断目标。引用路径必须为项目内相对路径，不能包含个人机器绝对路径。

文件发布后不可修改或覆盖；新交接使用新文件名，旧文件自然成为历史记录。
不设全局 `latest` 文件、不新增可变 `consumed` 标志。并行 Grill Lane 分别写入
自己的目录，不争抢全局计数器；这不授权并行 Implement 或 Review。

## 文件格式

采用普通 Markdown，不要求 YAML 或 CLI 才能阅读。文件包括固定标题、文件级
Metadata 和现有规范 Handoff 表。文件级 Schema Version 与产物 Version 分开。

拟议示例（占位符在实际发布时必须替换）：

```markdown
# ForgeFlow Handoff

## Metadata

| Field | Value |
| --- | --- |
| Schema Version | 1.0 |
| Handoff ID | <与文件名一致的 UUID> |
| Producer | Workflow |
| Source Workflow | Implement |

### Handoff

| Field | Value |
| --- | --- |
| Transition | FORWARD |
| Next Workflow | Review |
| Source Scope | Slice: F-01/S-01 |
| Target Scope | Slice: F-01/S-01 |
| Input Artifacts | <当前 Transition 规则规定的完整、有序文件及版本列表> |
| Reason | 当前 Slice 已满足实施门槛，请独立审查对应产物及验证证据。 |
```

Producer 仅允许 `Workflow` 或 `Routing Correction`；后者 Source Workflow
为 `NONE`。普通发布的 Source Workflow 必须匹配实际执行者及其授权 Scope。
Handoff 表继续使用现有变体的精确字段、顺序和投影，且作为文件最后内容。
不把所有变体的字段合并成一个带空值的宽表。

固定字段保持英文，Reason 等自然语言遵循 Plan 阶段记录的 Communication Language。
交接说明引用原有产物中的决策、阻塞和验证记录，不复制整段聊天或另建重复的任务清单。

Metadata 不声明 PASS、READY 或新的执行授权；输入产物版本也不能由接手者自动改写。
文件只能表明一次交接声明，不能证明发布者身份或替代代码仓库的访问控制与审查。

## 发布顺序与故障恢复

1. 按当前 Workflow 的规则保存其产物，完成必需的验证和已有事务。
2. 根据保存后的当前图计算 Transition 及精确 Input Artifacts 投影。
3. 对会产生 Handoff 的结果，构造完整文件并校验 schema、来源和图一致性。
4. 在同目录完成临时写入，再以不覆盖已有文件的方式发布；发现同名不同内容应失败。
5. 发布成功后，对话给出相对路径和下一步摘要，结束当前执行。

临时文件不参与发现。目标 Workflow 必须由后续独立执行启动，发布者不能消费自己
刚生成的交接。CLI 外部编排可以启动下一次执行，但必须重新验证文件和当前图。

如果产物保存成功而交接发布失败，应明确报告交接未完成，保留已保存的产物，
不能回滚成虚假旧状态或声称已完成交接。后续调用通过现有路由纠正规则生成新的
交接文件，然后停止；不能仅因目标匹配就直接开始生产性工作。

现有“只读路由纠正”需明确允许唯一新增写入：发布交接文件。它仍不得修改业务
产物、申请 Lane、分配 Attempt 或执行目标工作。名称和说明应避免暗示文件系统零写入。

等待用户、同授权等待和 Grill join-pending 仍不生成 Handoff。
HALTED 和 COMPLETE 可以持久化终止交接，但终止文件不授权继续某个 Workflow。

## 接收、自动发现与重复执行

显式指定文件时，严格验证该文件；无效时不能悄悄改选另一个文件。
未指定时，先判定现有 Bootstrap、Subsequent Plan、Lane、Recovery 等合法入口，
只有需要 Handoff Entry 时才发现交接文件。旧终止记录不能阻止合法的新 Plan。

发现与接收流程：

1. 验证当前 Artifact Graph，确定本次允许的 Workflow、Scope 和 Transition。
2. 从交接目录读取已发布的规范文件，过滤目标 Workflow/Scope；不能选择修改时间最新者。
3. 验证文件格式、ID/路径、来源、变体、输入文件及版本、完整有序投影，并使用当前
   图核对 Attempt、Lane、依赖、阻塞与完成条件。
4. 没有有效候选时走既有纠正或等待路径。无效文件保留，说明具体原因，不为它修补版本。
5. 多个候选的规范交接字段与来源完全相同，可视为同一次有效路由的等价声明；
   按文件名排序确定展示路径。它们只允许启动一次本次执行，不逐文件执行。
6. 若多个有效候选并非等价，不按时间或 UUID 猜测；报告歧义，要求明确文件或
   重新纠正。显式选择也不能绕过图校验。

交接不是“一次性令牌”。重复调用必须重新解析图，并依靠原有 Attempt、Lane 和
状态门槛防止重复执行已完成工作；如果先前调用尚未改变任何状态，合法重试仍可使用
同一文件。文件发布本身不提供执行锁，两个开发者不能据此并发进入同一个 Scope。

交接元数据 ID 不能用来识别项目世代。显式项目 reset/证据轮换必须连同 handoffs
一起归档，且失败回滚覆盖同一组目录，防止新项目同名版本误用旧记录。
普通 Subsequent Plan 不清空历史，旧交接通过当前图与版本检查失效。

## 换人、换机器与中途接手

标准交付集包括：

| 材料 | 用途 |
| --- | --- |
| 同一代码基线及未合并工作的可恢复内容 | 避免交接证据与实际实现不一致 |
| 安装的框架、版本和非秘密配置 | 保证接手者使用一致的规则及产物根目录 |
| 当前 artifacts 和图验证所需的不可变历史、恢复 receipts | 恢复状态、版本和 Attempt 连续性 |
| handoffs 目录 | 找到交接入口及历史路由 |
| 被验证记录引用的必要报告和证据 | 支持独立复核，不能只有 PASS 摘要 |
| 环境准备与尚未执行验证的说明 | 明确新机器的运行条件和证据边界 |

通过业务项目 Git 或受控交付包传递这组材料；不要求提交秘密、原始聊天或整个 runtime。
框架源码仓库的忽略规则不等于下游项目的共享策略。实施时更新安装与团队交付指南，
检查 Git 跟踪或交付包清单；不能静默修改业务项目的忽略规则并公开已有证据。
已有策略见[业务项目的 Git 与团队交接](../existing-projects.md#git-and-team-handoff)。

接手者取得完整材料后，从文件读取入口，核验图，再发起下一 Workflow；无需前任会话。
若缺少必需材料，应指出缺失项，不能从自然语言摘要补造产物或判为 PASS。

阶段中途换人不伪造 FORWARD。原开发者先保存允许持久化的进度、Open Issues、
验证结果与待办并停止活动进程；接手者遵守原有恢复入口。Grill ACTIVE Lane 仍须
确认旧执行已停止。没有合法恢复入口时维持等待或纠正，不把本设计扩展成任意续跑许可。

## IDE 与 CLI 的统一边界

- IDE：框架协议规定写文件及自动发现；对话末尾不再强制包含完整 Handoff 表。
- CLI：同一 schema 和接收规则；保留显式 `--handoff <file>`，省略参数时按上述规则发现。
- Runner：只在发布并验证成功后报告交接成功；不能只解析回复就假定文件已经存在。
- `.forgeflow/runtime/last-handoff.json`：可保留为派生诊断缓存，不能作为恢复的唯一入口。
- `forge handoff`：拟改为展示持久化候选及其当前有效性，不能只读取本机 runtime。
- `forge run`：各次执行通过同一文件协议交接；不得保留一条仅信任聊天文本的旁路。

新旧协议切换属于显式升级：更新版本表、协议、适配器说明、解析器和测试。
不在同一次执行中同时接受文件与聊天作为两个平行权威。旧项目升级时不扫描聊天
自动制造历史交接；没有新格式文件就根据当前图执行一次纠正并发布文件。
已有 artifacts 和原始证据保持不变。

## 实施顺序与验收

1. 先增加失败测试，确定文件 schema、解析和当前图接收规则，再修改规范协议。
2. 更新所有 Workflow、框架入口与适配器的发布/接收说明，避免只改 Implement。
3. 实现 CLI 发布、发现、显式选择、诊断读取和 reset 轮换，并让自动与单步入口共用规则。
4. 更新交付指南、教学样例、契约版本、变更日志和 IDE 验收用例。
5. 跑相关单元、集成、Markdown 契约、文档和安装检查，再进行真实 IDE 跨会话验收。

必须覆盖的行为：

- 四种变体的文件写入与读取；损坏 schema、错路径/ID、重复字段及多 Handoff 块被拒绝。
- 新会话/另一开发者在无聊天、无 runtime 的交付副本中找到正确下一步。
- 输入缺失、版本过期、Attempt 变化、旧终止记录及重复调用不会获得错误授权。
- 两个 Grill Feature 发布互不覆盖；等价重复记录不重复启动，冲突候选不猜测。
- 等待与 join-pending 不生成虚假交接；FAILED/NOT_RUN 验证不变成通过。
- 产物保存后发布中断能纠正恢复；临时文件不可被接收；同名记录不可被覆盖。
- reset 归档包含 handoffs，失败时恢复旧证据；普通升级不重写历史。
- 显式文件和自动发现遵循相同校验；IDE 与 CLI 不依赖聊天末尾的表格。
- 真实 IDE 验收执行一次 FORWARD、一次 Review FAIL → RETURN → 新 Attempt，
  并在接收前清除会话上下文；单元测试或模拟 Agent 不替代此证据。

本草案选择最小的持久化交接机制，不新增全局索引、任务所有者数据库或消费回执。
若后续实测发现同 Scope 并发执行需要新的协调能力，应单独设计并验证，不能用
Handoff 文件名或 Git 分支假装已经解决执行互斥。
