# ForgeFlow 架构

本页对应 Framework 3.8 / Artifact 2.19 / Transition 1.8，发布状态仍为 Technical Preview。

规范优先级：[Framework](./.forgeflow/forgeflow.md) → [Artifact](./.forgeflow/protocol/artifact.md)
→ [Transition](./.forgeflow/protocol/transition.md) → [Handoff](./.forgeflow/protocol/handoff.md)
→ 单个 Workflow → Adapter。核心在设计上是 Agent-agnostic；专用 launcher 为 Codex 和 Copilot。
Handoff 不会让 Artifact 自动变为真实，真实 IDE Acceptance 必须独立取得。

## 入门术语

| 术语 | 含义 |
| --- | --- |
| Feature | Planning 中具有稳定标识的业务成果。 |
| Slice | Feature 内由 Slice Plan 定义的交付单元。 |
| Artifact | 持久化的规范记录，需结合产物图校验有效性、版本和当前性。 |
| Handoff | 发给下一次调用的最终路由消息，本身不能证明引用证据有效。 |
| Lane | 对一个 eligible Feature 的 Grill 执行范围领取，不是 Implement 交付通道。 |
| Attempt | 与版本引用一起区分当前执行、重试及历史的执行标识。 |
| Barrier | 对相关完整集合的就绪条件，例如全部 Requirement READY 后才能进入 Solution。 |
| Strategy / Method | 带有证据义务的验证方式 / 组织已授权实施工作的可选指导。 |

以上是入门摘要。精确定义和有效性规则仍以权威契约为准，不新增状态或字段。

## 执行链

Plan → 按 Planning 依赖并行 Grill → 全部 Requirement READY → Solution → 全部 Feature
Slice Plan READY → 按声明顺序 Implement / Review → 全部当前 Slice PASS。

Lane 仅用于 Grill，由 ACTIVE/COMPLETE Record、Attempt、版本与 Claim Evidence 协调。
旧版交付阶段的 Feature 并行调度、共享组件 READ/WRITE 调度契约已取消。
Plan 必须等待 ACTIVE Lane 释放；中断恢复必须明确确认旧执行停止，并使用受保护事务。
CLI 读取并路由 Lane，不把顺序文件写入当成原子多文件事务，也不并行启动 Agent。

## CLI 分层

- ArtifactParser：规范路径、元数据、验证表格、有界历史及无效 Review receipt 检查。
- StateResolver：全局屏障、Grill eligibility、阻塞优先级、Rule 1–11 和精确有序输入投影。
- HandoffParser：四种消息格式的解析及只读路由输出。
- ForgeRunner：新鲜图校验、一次 Agent 调用、输出校验与可丢弃运行日志。
- Knowledge/Impact：派生视图，无状态机权威。

Implement 在批准范围内选择验证策略和局部实施 Method，不能改变上游义务与通过标准。
TDD 是十种验证策略之一，Method 是可选说明，不新增状态或审批。CLI 能检查记录结构、
引用和结果，不能证明模型声称的执行真实，也不能代替 Review 判断业务正确性和覆盖充分性。

## 策略与方法的选择

[Implement Workflow](.forgeflow/workflow/implement.md) 拥有具体选择步骤。
Solution 定义验证义务、通过标准与证据来源；Slice 映射到每个交付单元。
Implement 检查现有行为、测试、授权路径与环境，保留全部必需检查，只有在批准的
替代条件成立时才选替代策略。修改实现前先记录策略与义务映射。缺少工程政策返回
Solution，缺少 Slice 映射返回 Slice；常规执行选择不要求用户挑选策略名称。

策略可以组合，一项检查成功不能抵消另一项义务。TDD 需要修改前真实的行为 RED；
BEHAVIORAL_TEST 不声称历史 RED；行为刻画和性能比较保留必需基线；人工验收需要
指定验收人的真实结果。完整策略清单和证据表以
[Artifact Protocol](.forgeflow/protocol/artifact.md) 为准。

方法包括直接实现、先复现再修复、保持行为的重构、小步修改并频繁验证、最小差异修复、
机械转换。这些是可组合的指导，作为可选说明写入 Implementation Summary，不新增
Artifact、Attempt 或审批，也不改变业务政策、工程契约和 Slice 边界。

## 入口与恢复

Transition 定义 Bootstrap、Subsequent Plan、Handoff、Lane、Recovery 五种入口。
Review 仅接受 Handoff。缺少或无效的 Handoff 且无其他合法入口时，只读解析当前路由
并停止，不授权实施或修复产物。接收方重新核验完整当前图和精确有序输入投影；
发出 Handoff 即结束本次执行。

无效 Review 恢复是单独授权的维护操作。仅符合条件的格式缺陷可在受保护事务中保留
原始字节和 SHA256 回执后移出活动路径；已知阻塞或有效 PASS/FAIL 不适用。
旧 Attempt 永久占号，后续 Implement/Review 仍需新鲜授权和验证。只有显式要求时
才加载[可选恢复程序](.forgeflow/protocol/review-recovery.md)。

## 兼容与发布

旧 Solution 只有在 Planning、Requirement 历史可验证时才可作为 stale 基线。
纯 prose 的旧 Slice 验证计划需要补成结构化表格，CLI 不猜测隐含义务。
活动 TDD 文件会 HALT，必须单独授权迁移；历史 Attempt 保持占号，旧 PASS 不自动继承。

当前没有独立的 `update` 命令。Python 和 npm 的 `init --force` 刷新框架、清理已退役 TDD
launcher，并保留 artifacts/reports/history。npm 仅安装框架，Python 提供 `forge`。
旧 IDE 结果与本版结果隔离；静态测试和包安装成功不能代替本版真实宿主验收。

详见[英文架构](ARCHITECTURE.md)、[迁移说明](docs/maintainers/implement-migration.md)和
[发布流程](docs/maintainers/releasing.md)。
