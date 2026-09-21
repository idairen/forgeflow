# 概念与架构指南

当前链路为 Plan → Grill → Solution → Slice → Implement → Review。
详见[当前架构](../../ARCHITECTURE.zh-CN.md)、[CLI 入门](../../README.md)和
[权威 Framework](../../.forgeflow/forgeflow.md)。

Grill 可对依赖就绪的独立 Feature 并行执行；全部 Requirement 汇合后进入 Solution，
全部 Slice Plan READY 后才开始 Implement。交付严格遵循声明顺序。一个 Workflow
不能消费自己输出的 Handoff；自动模式由外部 runner 创建并重新验证下一次调用。

Solution 定义验证义务，Slice 映射到交付单元，Implement 执行批准策略、保存真实证据，
Review 独立判断。TDD 只是策略之一，Method 是可选的局部实施方法，不改变范围、所有权或门禁。

Artifact 是持久化权威；Lane Record 协调领取；日志、派生视图、插件报告和历史 PASS
不证明当前完成。旧版 TDD 和交付并行模型的变化见[迁移说明](../maintainers/implement-migration.md)。
