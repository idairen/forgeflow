# ForgeFlow 当前 IDE 验收计划

适用 Framework 3.8 / Artifact 2.19 / Transition 1.8 / Implement 2.13。
所有用例需要真实宿主调用，Python 或 Markdown 静态测试不能替代这些证据。
旧计划见 [历史计划](ide-test-plan.legacy.zh-CN.md)；旧 results 保留不变。
本版结果使用 `tests/acceptance/ide/results/current/`，初始全部 NOT RUN。

| ID | 场景与操作 | 期望结果 | 优先级 |
| --- | --- | --- | --- |
| IDE-INV-001 | Copilot 调用 forge-plan | 读取五份权威文件，不进入原生 Plan，不消费自己的 Handoff | P0 |
| IDE-INV-007 | Codex 调用 forge-plan | 读取五份权威文件，仅执行 Plan；发现 launcher 按宿主配置 | P0 |
| IDE-PLAN-101 | 空项目且 Reports Root 为空 | Bootstrap 仅创建批准的 Planning，交接后停止 | P0 |
| IDE-PLAN-102 | 缺少业务决策或有 ACTIVE Lane | 等待，不写 READY Planning，不解除其他执行的 claim | P0 |
| IDE-GRILL-101 | 两个独立 Feature 同时 Grill | 原子领取不同 Lane；只写各自 Requirement；最后完成者进入 Solution | P0 |
| IDE-GRILL-102 | 依赖 Requirement 尚未 READY | 目标 Feature 不可领取；可选择独立的 eligible Feature | P0 |
| IDE-GRILL-103 | 同一 Lane 竞争领取或旧执行恢复写入 | 仅一个领取成功；旧执行不能覆盖新 claim | P0 |
| IDE-BLK-101 | BUSINESS_GAP 后补充答案并明确确认旧执行停止 | 精确恢复该 claim，Attempt 前进，保留历史；记录协议冲突，不自行放宽规则 | P0 |
| IDE-BLK-102 | 中断 ACTIVE Lane 或项目 blocker | 无明确确认不恢复；release-only 不开展业务工作 | P0 |
| IDE-SOL-101 | 全部 Requirement READY 后设计 Solution | 完整验证义务和通过标准，不替 Grill 决定业务规则 | P0 |
| IDE-SLICE-101 | F-01 Slice READY、F-02 尚缺 Slice Plan | 继续 Slice F-02，不提前执行 Implement | P0 |
| IDE-TDD-101 | Implement 选择已允许的 TDD 或 BEHAVIORAL_TEST | 保留必需策略和检查；TDD 有真实 RED；行为测试不伪造 RED | P0 |
| IDE-TDD-102 | Implement 采用直接实现或小步修改 Method | 可选说明写在 Implementation Summary，不新增状态、Attempt 或审批 | P0 |
| IDE-TDD-103 | 必需检查 NOT_RUN、环境缺失或人工验收未取得 | IN_PROGRESS 或 BLOCKED，不进入 READY_FOR_REVIEW | P0 |
| IDE-TDD-104 | 上游修订或重试 | 有界读取历史，先持久化新 Attempt，再修改代码；不得重复推进 | P0 |
| IDE-REV-101 | 当前 Implement READY_FOR_REVIEW | 独立执行检查和插件，生成一个合法不可变 Review，交接后停止 | P0 |
| IDE-REV-102 | Review FAIL 指向上游 | 返回正确 owner/scope，不执行修复；记录无法闭合的返工路径 | P0 |
| IDE-HO-101 | 缺失、过期或乱序 Handoff | 只读纠正并停止，不执行匹配目标；下一调用才能消费 | P0 |
| IDE-HIS-101 | 明确授权处置格式无效且无阻塞的 Review | 原字节与 SHA256 receipt 保留，旧 Attempt 占号，重走 Implement | P0 |
| IDE-GRAPH-101 | 活动 TDD 文件或 TDD 路由 | HALTED，不自动迁移或丢弃证据 | P0 |
| IDE-VER-101 | Planning 增删 Feature，旧 Solution 可验证 | 旧 Solution 仅作 stale 基线，不证明工程就绪 | P0 |
| IDE-ORD-101 | 非数字顺序的 Feature/Slice 与 F-100/S-100 | 按声明顺序执行和投影；合法大编号不截断 | P0 |
| IDE-INC-101 | 全部 Slice 当前 PASS | COMPLETE；随后新 intent 仅授权 Subsequent Plan | P0 |
| IDE-PAR-101 | 两套 Adapter 执行同一冻结样例 | 规则、产物与 Handoff 一致，分别记录真实证据 | P0 |
| IDE-REV-103 | 插件无适用技术表面 | N/A、有依据、非阻塞，按注册格式输出报告 | P1 |

Strategy/Method 及恢复失败也必须如实记录；不可通过改写结果或生成模拟产物获得 PASS。
