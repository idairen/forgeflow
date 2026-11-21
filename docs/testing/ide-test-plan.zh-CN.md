# ForgeFlow 当前 IDE 验收计划

适用 Framework 3.11 / Artifact 2.22 / Transition 1.9 / Implement 2.16。
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
| IDE-TDD-101 | 新增行为及修 Bug 默认 TDD；对照纯文档、保持行为的重构、混合 Slice、已有代码缺 RED 和明确批准的行为例外 | 行为部分默认必选 TDD 且先有真实 RED；非行为工作记录不适用原因；例外须 Solution 中有明确用户批准及等效覆盖，Slice 映射；Implement 不自行换策略；Review 检查证据；其他策略逐项说明补充价值 | P0 |
| IDE-TDD-102 | Implement 采用直接实现或小步修改 Method | 可选说明写在 Implementation Summary，不新增状态、Attempt 或审批 | P0 |
| IDE-TDD-103 | 必需检查 NOT_RUN、环境缺失或人工验收未取得 | IN_PROGRESS 或 BLOCKED，不进入 READY_FOR_REVIEW | P0 |
| IDE-TDD-104 | 上游修订或重试 | 有界读取历史，先持久化新 Attempt，再修改代码；不得重复推进 | P0 |
| IDE-TDD-105 | Implement 生成候选记录，检查初始写入与 READY 发布；Solution 使用结构标记 | 发布前修正标题前正文、复合 Strategy/Source、PASS 结果值及缺失 placement；逐项核对验证覆盖；结构标记保持 2.11，不能套用协议文档版本 | P0 |
| IDE-REV-101 | 当前 Implement READY_FOR_REVIEW | 独立执行检查和插件，生成一个合法不可变 Review，交接后停止 | P0 |
| IDE-REV-102 | Review FAIL 指向上游 | 返回正确 owner/scope，不执行修复；记录无法闭合的返工路径 | P0 |
| IDE-REV-104 | 当前 READY_FOR_REVIEW 有匹配 FAIL；下一次调用 Implement 消费 Rule 8 RETURN；另测错误 Scope | 正确交接直接进入新 Attempt，不等 Rule 10、不改成 IMPLEMENTATION_GAP，保留 FAIL；错误 Scope 只纠正路由；新 Attempt 后旧 FAIL 不阻塞新记录 | P0 |
| IDE-HO-101 | 缺失、过期或乱序 Handoff 文件 | 自动发现无有效候选时保存纠正文件并停止；显式无效文件报错，不执行匹配目标 | P0 |
| IDE-HO-102 | 换开发者并清空会话，交付代码、框架、artifacts/history、handoffs 和报告，不含 runtime | 从独立文件恢复下一 Workflow，无需聊天；验证过期版本和 Attempt | P0 |
| IDE-HO-103 | Review FAIL 后保存 RETURN，在新会话重新 Implement 并发布下一交接 | 创建新 Attempt，保留失败证据，旧交接不可重复启动已完成工作 | P0 |
| IDE-HO-104 | 并行 Grill Feature 各自发布文件；构造等价和冲突候选 | 不互相覆盖；等价只执行一次，冲突要求显式选择，等待不伪造文件 | P0 |
| IDE-HIS-101 | 明确授权处置格式无效且无阻塞的 Review | 原字节与 SHA256 receipt 保留，旧 Attempt 占号，重走 Implement | P0 |
| IDE-HIS-102 | 隔离快照中破坏 Implement 格式，明确授权仅格式恢复，随后正常返工；另测匹配 PASS 和标准历史冲突 | 原件按摘要保存在 invalid-implement，保持身份与 Attempt，不改 FAIL；后续正常归档无同号冲突；匹配 PASS 或既有冲突不自动修复 | P0 |
| IDE-GRAPH-101 | 活动 TDD 文件或 TDD 路由 | HALTED，不自动迁移或丢弃证据 | P0 |
| IDE-VER-101 | Planning 增删 Feature，旧 Solution 可验证 | 旧 Solution 仅作 stale 基线，不证明工程就绪 | P0 |
| IDE-ORD-101 | 非数字顺序的 Feature/Slice 与 F-100/S-100 | 按声明顺序执行和投影；合法大编号不截断 | P0 |
| IDE-INC-101 | 全部 Slice 当前 PASS | COMPLETE；随后新 intent 仅授权 Subsequent Plan | P0 |
| IDE-PAR-101 | 两套 Adapter 执行同一冻结样例 | 规则、产物与 Handoff 一致，分别记录真实证据 | P0 |
| IDE-REV-103 | 插件无适用技术表面 | N/A、有依据、非阻塞，按注册格式输出报告 | P1 |

Strategy/Method 及恢复失败也必须如实记录；不可通过改写结果或生成模拟产物获得 PASS。

IDE-TDD-105、IDE-REV-104、IDE-HIS-102 是本次实测问题的回归用例，尚无真实宿主
验收证据。必须在隔离测试项目中运行并记录真实响应；不要将历史项目记录改成符合新规则。
