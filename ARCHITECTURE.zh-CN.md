# ForgeFlow 架构

本页对应 Framework 3.8 / Artifact 2.19 / Transition 1.8，发布状态仍为 Technical Preview。

规范优先级：[Framework](./.forgeflow/forgeflow.md) → [Artifact](./.forgeflow/protocol/artifact.md)
→ [Transition](./.forgeflow/protocol/transition.md) → [Handoff](./.forgeflow/protocol/handoff.md)
→ 单个 Workflow → Adapter。核心在设计上是 Agent-agnostic；专用 launcher 为 Codex 和 Copilot。
Handoff 不会让 Artifact 自动变为真实，真实 IDE Acceptance 必须独立取得。

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

## 兼容与发布

旧 Solution 只有在 Planning、Requirement 历史可验证时才可作为 stale 基线。
纯 prose 的旧 Slice 验证计划需要补成结构化表格，CLI 不猜测隐含义务。
活动 TDD 文件会 HALT，必须单独授权迁移；历史 Attempt 保持占号，旧 PASS 不自动继承。

当前没有独立的 `update` 命令。Python 和 npm 的 `init --force` 刷新框架、清理已退役 TDD
launcher，并保留 artifacts/reports/history。npm 仅安装框架，Python 提供 `forge`。
旧 IDE 结果与本版结果隔离；静态测试和包安装成功不能代替本版真实宿主验收。

详见[英文架构](ARCHITECTURE.md)、[迁移说明](docs/maintainers/implement-migration.md)和
[发布流程](docs/maintainers/releasing.md)。
