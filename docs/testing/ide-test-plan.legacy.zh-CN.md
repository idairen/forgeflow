> 历史验收计划：对应 Implement 迁移前的版本，不作为当前发布门禁。

# ForgeFlow IDE 全场景验收测试计划

> 文档类型：IDE 集成与框架行为验收计划
> 适用基线：ForgeFlow Framework 2.20、Artifact Protocol 2.17、Handoff Protocol 2.14、Workflow 2.7–2.15
> 目标适配器：GitHub Copilot、Codex
> 测试方式：在 IDE 中直接调用 `.forgeflow/adapter/<adapter>/forge-*.prompt.md`，不使用 ForgeFlow CLI 编排

## 1. 测试目标

本计划用于验证 ForgeFlow 安装到项目的 `.forgeflow/` 目录后，IDE 是否真正执行 ForgeFlow，而不是退化为 IDE 或模型自身的默认规划、实现或审查行为。

测试覆盖以下能力族：

- 六个 Prompt 的发现、元数据、参数传递和宿主模式隔离；
- Plan、Grill、Solution、Slice、TDD、Review 六个工作流；
- Bootstrap、Handoff、Subsequent Plan、Feature Lane、Recovery 和显式 reset/archive maintenance；
- FORWARD、RETURN、TERMINAL/COMPLETE、TERMINAL/HALTED 四类 Handoff；
- BUSINESS_READY、ENGINEERING_READY、LANE_READY、LANE_DELIVERY_READY、PROJECT_COMPLETE 门禁；
- Artifact 所有权、版本引用、历史归档和不可变 Review attempt；
- 后续需求、Feature 新增/修改/重排/退役以及跨 Feature 影响；
- Artifact History、Reports History 和成对 Project Evidence Rotation；
- Review PASS、FAIL、多所有者返回、插件 PASS/VIOLATION/UNKNOWN/N/A；
- 无效图、过期证据、错误作用域、缺失 Handoff 和宿主默认能力接管；
- IDE 会话重启、无对话记忆恢复、顺序执行和进程清理。

“全场景”在本文中指覆盖当前规范定义的全部行为类别、入口类型、转换类型、工作流所有权和错误类型，而不是穷举所有自然语言表达或所有文件系统故障组合。

当前基线包含 247 个编号测试场景，其中重复出现在执行批次或最小回归集中的编号只计一次。

## 2. 不在本轮范围内

以下内容不作为本轮 IDE 验收结论：

- `forge run`、`forge plan` 等 Python CLI 编排行为；
- `.forgeflow/runtime/` 中的 CLI 运行历史；
- 模型本身的代码正确率或性能基准；
- 未提供专用 Launcher 的 Claude 或 Gemini 宿主集成；
- IDE 扩展自身的账号、授权、计费或网络稳定性；
- 并发分布式 Agent 编排。

如果测试过程中使用 CLI 创建夹具，只能作为文件准备工具，不能把 CLI 结果计入 IDE 行为通过证据。

## 3. 测试原则

### 3.1 每个破坏性场景使用独立副本

禁止在同一个工作区连续执行会破坏 Artifact Graph 的负向用例。每个无效图、版本冲突、退役失败和轮换失败测试都必须从已知有效快照复制出独立工作区。

建议目录：

```text
forgeflow-ide-tests/
├── baseline-empty/
├── baseline-business-ready/
├── baseline-engineering-ready/
├── baseline-delivery-ready/
├── baseline-review-ready/
├── baseline-complete/
└── cases/
    ├── IDE-INV-001/
    ├── IDE-PLAN-001/
    └── ...
```

### 3.2 所有判断以仓库证据为准

每个用例至少保存：

1. IDE、扩展和模型版本；
2. Git commit SHA；
3. 测试前 Artifact/Report 文件清单和校验值；
4. 用户输入和是否从 `/` 菜单选择 Prompt；
5. IDE 完整响应或截图；
6. 测试后的 `git diff -- .forgeflow src tests`；
7. 新增或更新 Artifact 的完整内容；
8. 最终 Handoff，或明确记录“按规范不应有 Handoff”；
9. PASS、FAIL、BLOCKED 或 NOT RUN 结论；
10. 实际结果与期望结果的差异。

### 3.3 不以聊天文本代替通过证据

下面这些现象不能单独证明用例通过：

- Agent 声称“已经遵守 ForgeFlow”；
- 回答中提到 Plan、TDD 或 Review；
- 输出了看起来合理的实施计划；
- 输出了 Handoff，但没有对应的当前 Artifact；
- 手工写入 Artifact 后状态看起来正确；
- CLI 的模拟状态解析通过，但没有真实 IDE 调用证据。

### 3.4 通过条件

一个用例只有在以下条件全部满足时才算 PASS：

- Prompt 确实来自预期的 `.forgeflow/adapter/<adapter>/` 文件；
- IDE 没有用原生 Plan、通用实现或通用 Review 替代 ForgeFlow；
- 入口、工作流和作用域由当前 Artifact Graph/Handoff 授权；
- 只有当前工作流拥有的文件发生允许的变化；
- Artifact 状态、版本和上游引用符合当前协议；
- 如果需要 Handoff，格式、证据、作用域和目标均正确；
- Canonical Handoff Block 后没有任何文本；
- 如果规范要求等待，则没有提前写入制品或发出 Handoff；
- 如果图无效，则没有执行生产性工作。

## 4. 测试环境矩阵

至少完成下表中的 P0 组合。P1 组合可在 P0 稳定后执行。

| 编号 | 宿主 | Adapter | Prompt 来源配置 | 优先级 |
|---|---|---|---|---|
| ENV-01 | VS Code + GitHub Copilot Chat | `copilot` | `.forgeflow/adapter/copilot` | P0 |
| ENV-02 | Codex IDE/编辑器集成 | `codex` | `.forgeflow/adapter/codex` 或宿主实际配置位置 | P0 |
| ENV-03 | VS Code 新窗口/新会话 | `copilot` | 与 ENV-01 相同 | P0 |
| ENV-04 | 宿主升级后的最新版 | 对应 adapter | 与项目配置相同 | P1 |
| ENV-05 | 多根工作区中打开项目根目录 | `copilot` | 明确指向当前项目 | P1 |

每次测试前记录：

```text
Operating system:
IDE and version:
AI extension and version:
Selected model:
Selected chat mode/agent:
Prompt search-path configuration:
ForgeFlow Git SHA:
Project Git SHA:
Test case ID:
```

## 5. Prompt 与测试数据基线

### 5.1 必须存在的 Prompt

两个 Adapter 都必须包含：

```text
forge-plan.prompt.md
forge-grill.prompt.md
forge-solution.prompt.md
forge-slice.prompt.md
forge-tdd.prompt.md
forge-review.prompt.md
```

Copilot Prompt 必须显示或实际应用 `agent: agent`。Codex Prompt 不要求解释 Copilot 专属字段。

### 5.2 推荐测试项目

使用一个可离线运行测试的小型 Python 项目，以便四个内置 Review 插件都能获得实际代码表面。建议准备：

```text
src/inventory_service.py
tests/test_inventory_service.py
pyproject.toml
```

推荐初始用户意图：

> 为现有 Python 服务增加库存预留与释放能力。调用方需要避免重复请求造成重复扣减，并保留必要的操作审计。第一期只提供本地服务能力，不新增 Web UI。

该意图故意保留业务和工程问题，使 Grill 与 Solution 都有机会验证正确的提问边界。

### 5.3 标准状态快照

通过真实 IDE 流程逐步生成并冻结以下快照。每个快照必须先人工确认结构有效，再复制给后续用例。

| 快照 | 状态 |
|---|---|
| `S0-CLEAN` | Artifact Root 与 Reports Root 均不存在或为空 |
| `S1-PLANNED` | Planning READY，至少两个 Feature，Requirement 尚不完整 |
| `S2-BUSINESS` | 所有 Requirement 当前且 READY，满足 BUSINESS_READY |
| `S3-ENGINEERING` | Solution Plan 当前且 READY，满足 ENGINEERING_READY |
| `S4-DELIVERY` | 至少一个依赖就绪 Feature 具有当前 READY Slice Plan，满足该 Feature 的 LANE_DELIVERY_READY |
| `S5-REVIEW` | 首个 Slice 的 TDD Record 为 READY_FOR_REVIEW，没有匹配 Review |
| `S6-FAIL` | 当前 TDD attempt 有匹配的 FAIL Review Report |
| `S7-COMPLETE` | 所有 Slice 当前 attempt 都有匹配 PASS Review |

### 5.4 顺序测试变体

从有效快照创建一个独立变体，使 Planning 中声明顺序与标识符数值顺序不同，例如 `F-02` 位于 `F-01` 之前；在其中一个 Slice Plan 中使 `S-02` 位于 `S-01` 之前。该变体只用于验证声明顺序，不能覆盖普通基线。

## 6. 单用例执行模板

每个用例复制并填写以下模板：

```markdown
### <CASE-ID> — <标题>

- 优先级：P0 / P1 / P2
- Adapter：copilot / codex / 两者
- 前置快照：
- 当前聊天模式：
- 调用方式：从 `/` 菜单选择 / 宿主等效方式
- 输入：
- 操作步骤：
- 期望 Artifact 变化：
- 期望 Report 变化：
- 期望 Handoff：
- 禁止出现：
- 实际结果：
- 证据路径：
- 结论：PASS / FAIL / BLOCKED / NOT RUN
```

## 7. Prompt 发现与宿主隔离

| ID | 场景与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-INV-001 | 在 Copilot 输入 `/`，检查六个 `forge-*` Prompt | 六个 Prompt 全部出现，名称唯一，没有缺失或重复 | P0 |
| IDE-INV-002 | 查看每个 Copilot Prompt 的来源 | 来源均为当前工作区 `.forgeflow/adapter/copilot/`，不是用户级或其他仓库文件 | P0 |
| IDE-INV-003 | 将当前聊天模式预先切换为 Copilot 原生 Plan，再从菜单执行 `/forge-plan <intent>` | Prompt 强制以 Agent 模式执行 ForgeFlow Plan；不得输出 Copilot 原生 implementation plan | P0 |
| IDE-INV-004 | 对其余五个 Copilot Prompt 重复上项 | 均使用 `agent: agent`，不会停留在只规划、无文件写入的宿主模式 | P0 |
| IDE-INV-005 | 调用 `/forge-plan` 并附加多行用户意图 | 完整意图被保留为 Plan 输入，但不能覆盖 Artifact/入口授权 | P0 |
| IDE-INV-006 | 调用 `/forge-grill` 并附加澄清答案 | 答案只作为当前 Feature 的业务上下文，不扩大作用域 | P0 |
| IDE-INV-007 | 依次检查 Codex 六个启动器 | 每个启动器读取正确的同名 workflow 文件，不加载 Copilot adapter | P0 |
| IDE-INV-008 | 在 Copilot 中执行 `forge-plan` 文本但不从 `/` 菜单选择 | 记录宿主实际行为；不得把普通文本调用误判为 Prompt 已成功加载 | P1 |
| IDE-INV-009 | 临时把 Prompt 搜索路径改为错误目录后输入 `/forge-plan` | 命令不可发现或按普通文本处理；该结果用于证明发现配置是必要条件 | P1 |
| IDE-INV-010 | 恢复正确搜索路径并开启新 IDE 窗口 | 六个 Prompt 可重新发现，无需依赖旧聊天缓存 | P0 |
| IDE-INV-011 | 查看 Agent/Chat Debug Log | 请求中包含目标 Prompt 正文及四个权威文件读取要求 | P1 |
| IDE-INV-012 | 检查命令描述 | `forge-plan` 明确声明不得调用或委托 Copilot native planning mode | P0 |
| IDE-INV-013 | 根目录 `forgeflow.json` 的 CLI mode 为 `auto`，从 IDE 菜单执行任一 `forge-*` Prompt | IDE 忽略 CLI mode；本次仍只执行一个 Workflow，输出 Handoff 后停止 | P0 |
| IDE-INV-014 | 从 IDE 菜单执行任一 `forge-*` Prompt 并检查 Agent 读取记录 | 完整读取顺序严格为 Framework → Artifact Protocol → Handoff Protocol → 当前 Workflow；不能先读 Workflow 再补协议 | P0 |
| IDE-INV-015 | `/forge-plan` 已成功加载且权威路径可读 | 不读取 Grill 或其他未来 Workflow，不扫描 `~/.copilot`、全局 command/prompt 目录或无关宿主配置；项目检查只使用当前 Workflow 所需仓库证据 | P0 |

## 8. Plan 与项目入口场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-PLAN-001 | `S0-CLEAN`，执行 `/forge-plan <initial intent>` | 通过 Bootstrap Entry 创建 Planning；不创建代码、Requirement、Solution 或 Slice Plan | P0 |
| IDE-PLAN-002 | Artifact Root 不存在、Reports Root 为空目录 | 仍是干净 Bootstrap；必要根目录被创建，不产生空备份 | P0 |
| IDE-PLAN-003 | Artifact Root 为空、Reports Root 含任意文件 | Handoff Rule 1 不匹配，不得 Bootstrap；解释需要 reset 并等待明确授权，文件保持不变且无 Handoff | P0 |
| IDE-PLAN-004 | 非空 Artifact Root 中没有 Planning | 不自动 reset 或修复；输出 TERMINAL/HALTED，原文件保持不变 | P0 |
| IDE-PLAN-005 | 用户意图没有可识别交付目标 | 询问并等待是否明确批准空项目；不得从沉默推断 `NONE` | P0 |
| IDE-PLAN-006 | 用户明确批准空项目 | Planning 使用 `Feature IDs = NONE` 和有效 Empty Feature Approval；没有下游制品；输出 COMPLETE | P0 |
| IDE-PLAN-007 | 初始意图包含业务目标和技术偏好 | Planning 只定义当前批准范围、Feature、约束和成功度量；不把数据库、框架配置、认证接线或项目脚手架写成 Assumption、Exclusion 或独立 Feature | P0 |
| IDE-PLAN-008 | 用户要求 Plan 创建代码、测试、数据库表、SQL 决策记录或独立会话计划 | Plan 拒绝越权持久化；正常执行只修改 Planning 及协议要求的历史/轮换表面，不创建影子决策状态 | P0 |
| IDE-PLAN-009 | READY Planning 后提交语义上看似无关的新模块需求 | 默认作为当前软件项目的后续变更合并；不询问项目归属，不轮换 Artifact/Reports | P0 |
| IDE-PLAN-010 | 用户显式请求 reset/archive maintenance 后重新规划 | 使用同一个 UTC 后缀轮换所有非空 Artifact/Reports 根；创建新的空根后再规划 | P0 |
| IDE-PLAN-011 | 用户明确 reset，但两个根都为空 | 不创建空备份；保持/创建空根并开始 Plan | P1 |
| IDE-PLAN-012 | Planning 当前为 DRAFT，并提供了指向 Plan 的有效 Handoff，或仍处于已授权的同作用域连续调用 | Plan 在已授权 Project scope 继续；不得把普通新会话误当成新的无 Handoff 入口 | P0 |
| IDE-PLAN-013 | 当前 PLAN_GAP blocker，开启新聊天执行 `/forge-plan` | 通过 Recovery Entry 恢复同一 Project scope，不伪造 RETURN，不轮换当前项目 | P0 |
| IDE-PLAN-014 | 当前图由其他 blocker 或 FAIL Review 优先控制，执行 `/forge-plan` | 不得绕过当前所有者；无生产性 Plan 改动 | P0 |
| IDE-PLAN-015 | Planning 完成且存在缺失 Requirement | Handoff FORWARD 到 Planning 顺序中的第一个缺失 Feature 的 Grill | P0 |
| IDE-PLAN-016 | 后续 Planning READY | 记录覆盖完整当前范围的 intent-evolution summary，明确 retained/added/modified/reordered/retired，不复制第二份当前契约 | P1 |
| IDE-PLAN-017 | Bootstrap 或后续 Plan 写入 READY Planning | 不写入 `Artifact Protocol Version`；单一标题、完整业务 Metadata、九个有序章节以及表头/ID/Artifact 版本/行集合均有效且写后重读通过；五类通用分解维度均已明确或无关，但不创建额外 checklist、数据库表或决策存储 | P0 |
| IDE-PLAN-018 | Planning READY 且 Rule 5 选择 Grill | 最终输出指向第一个缺失 Feature 的 Canonical Handoff 并立即结束；不得分析该 Feature、创建 Requirement 或自动执行 Grill | P0 |
| IDE-PLAN-019 | 用户要求包含角色访问控制，但未说明身份、角色或组织归属由现有系统提供还是由本项目管理 | Plan 解释该答案会改变 Feature 集合和产品范围，提供有依据选项并等待；不得假设外部提供、增加 Exclusion、写 READY Planning 或发 Handoff | P0 |
| IDE-PLAN-020 | 存在不改变项目范围、Feature 拆分或跨 Feature 契约的任何业务细节问题 | Plan 禁止提问、猜测或写入答案；只询问稳定项目范围与跨 Feature 边界所必需的问题，其余全部留给对应 Feature 的 Grill | P0 |
| IDE-PLAN-021 | 未明确负责人是否等于确认人、平均时长口径或其他共享数据语义 | 若答案跨 Feature 或改变产品体验，Plan 必须询问并等待；Assumptions、Exclusions、Success Measures 和 Feature Outcomes 不得替用户选择答案 | P0 |

## 9. Grill 场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-GRILL-001 | 从 IDE-PLAN-015 的有效 Handoff 执行 `/forge-grill` | 只处理 Handoff 指定的一个 Feature，并创建其 Requirement | P0 |
| IDE-GRILL-002 | 无 Handoff、无 BUSINESS_GAP，直接执行 `/forge-grill` | 不进行生产性工作，不创建或修改 Requirement | P0 |
| IDE-GRILL-003 | 当前 BUSINESS_GAP 指向该 Feature，新聊天直接执行 `/forge-grill` | Recovery Entry 只授权该 Feature；不得处理其他 Feature | P0 |
| IDE-GRILL-004 | 业务规则存在歧义 | 提出业务问题并等待；同一 Feature 保持活动，不发同作用域 Handoff | P0 |
| IDE-GRILL-005 | 澄清答案可能引出后续业务问题 | 在同一作用域继续追问，直到业务行为完整或形成 blocker | P0 |
| IDE-GRILL-006 | 提问需要选数据库、API、HTTP 状态码或测试框架 | 不应向用户提出这些 Grill 越界问题；将其留给 Solution/TDD | P0 |
| IDE-GRILL-007 | 提供建议选项 | 每题 3–5 个以内，最后一项为可自由填写的 Other，不诱导用户选择 | P1 |
| IDE-GRILL-008 | Planning 与现有代码足以确定全部业务行为 | 不强行提问，直接形成 READY Requirement | P1 |
| IDE-GRILL-009 | 用户拒绝提供会改变可观察行为的必要决定 | Requirement 不得 READY；持久化合法 BUSINESS_GAP 或保持等待状态 | P0 |
| IDE-GRILL-010 | 当前 Feature 完成，另一个 Feature Requirement 缺失 | FORWARD 到声明顺序中的下一个 Feature，而不是按文件名/编号排序 | P0 |
| IDE-GRILL-011 | 全部 Requirement 当前且 READY | FORWARD 到 Solution Project scope，满足 BUSINESS_READY | P0 |
| IDE-GRILL-012 | Requirement 已存在且规范内容变化 | 先将旧版本精确归档，再写更高版本；其他工作流制品不被修改 | P0 |
| IDE-GRILL-013 | Handoff 指向 F-02，F-03 仍缺 Requirement | 本轮只生成 F-02 Requirement；输出指向 F-03 的 FORWARD 并立即停止，不分析、提问或生成 F-03 Requirement | P0 |
| IDE-GRILL-014 | 后续 Planning 改变当前 Feature | Requirement 将业务目标、规则和验收证据追踪到当前 Feature boundary 与 Change Set context，不把历史意图当当前约束 | P1 |
| IDE-GRILL-015 | Handoff 只授权 F-02，但 Agent 尝试同时创建或修改 F-03 Requirement | Requirement mutation set 校验失败；不得 READY/FORWARD 或继续 F-03；只有 F-02 路径允许变化 | P0 |

## 10. Solution 场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-SOL-001 | 只有部分 Feature 的 Requirement READY | 拒绝进入 Solution，不产生部分 Solution Plan | P0 |
| IDE-SOL-002 | BUSINESS_READY，使用有效 Handoff | 创建一个覆盖所有当前 Requirement 的 Project 级 Solution Plan | P0 |
| IDE-SOL-003 | 无 Handoff、无 ENGINEERING_GAP，直接执行 `/forge-solution` | 不进行生产性工作 | P0 |
| IDE-SOL-004 | 当前 ENGINEERING_GAP 指向 Project | 新聊天可通过 Recovery Entry 恢复 Solution | P0 |
| IDE-SOL-005 | 工程决策可由现有代码和 Requirements 推断 | 不强行询问用户，直接记录可追溯的工程决定 | P1 |
| IDE-SOL-006 | 存在框架选择、性能/成本取舍或外部部署约束 | 提供有依据的选项并等待用户，不在等待时发 Handoff | P0 |
| IDE-SOL-007 | 缺失的是业务成功/失败语义 | RETURN 到对应 Feature 的 Grill，不自行决定 | P0 |
| IDE-SOL-008 | Requirement 没写 HTTP 状态码等技术表示 | 不错误 RETURN Grill；由 Solution 负责技术表示 | P0 |
| IDE-SOL-009 | 用户要求在 Solution 中拆 Slice 或写代码 | 不越权；Solution Plan 只记录工程基线 | P0 |
| IDE-SOL-010 | 初次 Solution | 为每个当前 Feature 记录 Based On Requirements 和 Feature Engineering Versions | P0 |
| IDE-SOL-011 | 后续需求只影响一个 Feature | Solution 仍读取全部当前 Requirement 和既有工程基线，只推进受影响 Feature 的 engineering version | P0 |
| IDE-SOL-012 | 新需求可复用公共 utility，且横切改动实际影响多个 Feature | 记录 Shared Components and Utilities 与覆盖全部 Feature 的 Cross-Feature Impact；推进所有受影响 Feature，不能把不确定性当兼容 | P0 |
| IDE-SOL-013 | Solution 规范内容变化 | 旧 Solution 精确归档，新版本递增 | P0 |
| IDE-SOL-014 | Solution READY，多个无依赖 Feature 可交付 | 默认 FORWARD 到 Planning 顺序中的第一个 Ready Lane；其他 Ready Lane 可通过独立 Feature Lane Entry 并行启动 | P0 |
| IDE-SOL-015 | 既有工程决策被后续需求替换 | Engineering Decision Register 标明 affected Features、依据及 retains/replaces/supersedes 关系；历史决策不再作为当前决策 | P1 |
| IDE-SOL-016 | 多 Feature 存在调用或数据依赖，并共享公共组件 | Solution 写入 Feature Dependencies、Shared Component IDs、Feature Shared Components、Feature Shared Component Access 和 Feature Decision References；Planning/Solution 依赖联合图无环；共享 WRITE 关系有明确依赖顺序 | P1 |
| IDE-SOL-017 | 旧 Solution 没有结构化影响元数据，后续需求触发 Solution 修订 | 旧 Solution 在迁移读取时仍可作为当前工程证据；新 Solution 版本补齐全部结构化影响字段，不产生部分字段集合 | P1 |
| IDE-SOL-018 | 一个 Feature 需要 controller、service、repository/data-access、domain/support 等多种责任及对应测试 | Solution 根据现有仓库证据选择 package-by-Feature、package-by-layer 或混合策略，并写入完整 Implementation Structure 与 Test Structure；不得把所有责任默认为同一 package | P0 |
| IDE-SOL-019 | 现有仓库已经存在一致且可推断的源码/测试目录惯例 | 直接沿用并记录证据，不因个人偏好强制改成 Java/Spring 分层或制造一类一包；通用 utility 必须改为明确责任或已批准共享组件 | P1 |
| IDE-SOL-020 | Solution 形成工程基线并准备写摘要 | 摘要写入 `.forgeflow/artifacts/solution-plan.md` 的唯一 `## Solution Summary`；不得创建 `solution-plan-summary.md` 或项目根目录副本 | P0 |

## 11. Slice 场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-SLICE-001 | BUSINESS_READY 但 Solution 缺失/过期 | 不创建 Slice Plan，按上游缺口返回/等待 Solution | P0 |
| IDE-SLICE-002 | 有效 Handoff 指向一个 Feature | 只为该 Feature 创建 Slice Plan | P0 |
| IDE-SLICE-003 | 无 Handoff、无 SLICE_VIOLATION，且没有显式匹配 Ready Set 的 Feature Lane Entry | 不进行生产性工作 | P0 |
| IDE-SLICE-004 | 当前 SLICE_VIOLATION 指向该 Feature | Recovery Entry 只恢复该 Feature | P0 |
| IDE-SLICE-005 | 正常拆分 | 每个 Slice 可独立实现、测试、Review，并记录验收证据、依赖、风险和完成条件 | P0 |
| IDE-SLICE-006 | Slice 间存在循环依赖 | 不得标记 READY；报告有效 blocker 或返回需要修复的上游决策 | P0 |
| IDE-SLICE-007 | Requirement 行为没有被任何 Slice 覆盖 | READY quality gate 失败 | P0 |
| IDE-SLICE-008 | Slice 重复或边界重叠 | READY quality gate 失败，不允许模糊归属 | P0 |
| IDE-SLICE-009 | 用户要求 Slice 修改业务行为或重做架构 | 不越权；根据缺口 RETURN Grill 或 Solution | P0 |
| IDE-SLICE-010 | 检查 Slice Plan 字段 | 不包含动态 cursor、PENDING、IN_PROGRESS、COMPLETE 或 Review 结论 | P0 |
| IDE-SLICE-011 | 当前 Feature 完成，解锁一个依赖它的 Feature | FORWARD 到新 Ready Set 中默认顺序的 Feature；不选择依赖仍未完成的 Lane | P0 |
| IDE-SLICE-012 | F-01 Slice Plan READY，F-02 独立但尚无 Slice Plan | F-01 可继续 FORWARD TDD；F-02 可通过独立 Feature Lane Entry 同时执行 Slice，不存在全局 Slice barrier | P0 |
| IDE-SLICE-013 | 两个 Feature 无有效依赖且共享组件均为 READ | 两个 Feature 同时属于 Ready Set，可由两个独立 invocation 分别执行 Slice/TDD/Review | P0 |
| IDE-SLICE-014 | 修改一个 Feature 的拆分 | 只提高该 Slice Plan 版本；该 Feature 旧 TDD/Review 变过期，其他 Feature 不受影响 | P0 |
| IDE-SLICE-015 | Handoff 指向 F-02，F-03 也是 Ready Lane 且仍缺 Slice Plan | 本轮只生成 F-02 Slice Plan并输出 F-02 首个 TDD Handoff；不得生成 F-03 Slice Plan；F-03 由独立 Feature Lane Entry 启动 | P0 |
| IDE-SLICE-016 | Slice 使用共享 utility 或工程决策 | 每个 Slice 引用当前 Solution 中可解析的 engineering decision 和 shared component；不得引用不存在或已 superseded 的决定 | P1 |
| IDE-SLICE-017 | Slice 将创建多个生产责任和测试类型 | Planned File Placement 为每项责任记录 production/test path 或可解析 pattern，并与 Solution 布局一致；不能把 package 决策留给 TDD | P0 |

## 12. TDD 场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-TDD-001 | 目标 Feature 尚未达到 LANE_DELIVERY_READY | 不得开始该 Feature 的实现；其他独立 Ready Lane 不受影响 | P0 |
| IDE-TDD-002 | 有效 Handoff 指向 `Slice: F-XX/S-XX` | 只实现该 Slice，不处理未来 Slice | P0 |
| IDE-TDD-003 | 无 Handoff、无 IMPLEMENTATION_GAP，且请求不匹配有效 Feature Lane Entry | 不修改代码、测试或 TDD Record | P0 |
| IDE-TDD-004 | 当前 IMPLEMENTATION_GAP 指向该 Slice | 新聊天通过 Recovery Entry 恢复同一 Slice | P0 |
| IDE-TDD-005 | Handoff Target Scope 与解析结果不一致 | 拒绝执行，不猜测正确 Slice | P0 |
| IDE-TDD-006 | 上游版本引用过期 | 忽略旧 READY_FOR_REVIEW 证据，按当前图重新执行/返回正确所有者 | P0 |
| IDE-TDD-007 | 正常实现，当前 Slice 包含代码或已批准的数据库 schema/migration/table/SQL 数据变更 | TDD 可完成这些应用实现并记录 RED、GREEN、migration/SQL 验证、修改文件和残余风险；不得把数据库用于 ForgeFlow 决策或进度状态 | P0 |
| IDE-TDD-008 | 用户要求顺便实现下一个 Slice | 拒绝扩大作用域；git diff 只包含当前 Slice 允许的变化 | P0 |
| IDE-TDD-009 | 实现中发现缺少业务政策 | RETURN Grill 到受影响 Feature | P0 |
| IDE-TDD-010 | 实现中发现缺少工程决定 | RETURN Solution 到 Project | P0 |
| IDE-TDD-011 | 实现中发现 Slice 拆分无效 | RETURN Slice 到受影响 Feature | P0 |
| IDE-TDD-012 | 本地实现/测试缺陷可在当前调用修复 | 保持同一 TDD scope，无同作用域 Handoff，修复后继续 | P0 |
| IDE-TDD-013 | 本地缺陷跨调用仍阻塞 | 持久化 IMPLEMENTATION_GAP；Recovery 只恢复同一 Slice | P0 |
| IDE-TDD-014 | Review readiness self-check 发现阻塞问题 | 不得设置 READY_FOR_REVIEW，先修复或 RETURN | P0 |
| IDE-TDD-015 | self-check 无阻塞 | TDD Record 为 READY_FOR_REVIEW，但不得创建 Review Report 或给出 PASS/FAIL | P0 |
| IDE-TDD-016 | 首次送审 | Attempt 为 1，FORWARD Review 同一 Slice | P0 |
| IDE-TDD-017 | 上一次当前 attempt 为 FAIL，修复后重送 | TDD Record attempt 加 1，旧 TDD Record 按协议归档，旧 FAIL Review 保留 | P0 |
| IDE-TDD-018 | 连续运行多个测试命令 | 复用同一终端/会话并顺序执行；不为每条命令创建新终端 | P1 |
| IDE-TDD-019 | Slice 需要短时启动服务 | 记录必要并发原因，并在 Handoff 前终止所有启动进程 | P0 |
| IDE-TDD-020 | F-02 依赖 F-01 且 F-01 尚未全部 PASS | F-02 不属于 Ready Set；不得实现。无依赖的 F-03 可独立并行，不受 Planning 位置限制 | P0 |
| IDE-TDD-021 | 当前 Slice 达到 READY_FOR_REVIEW | 只写当前 TDD Record 并 FORWARD Review；本轮不得执行 Review 或开始下一个 Slice | P0 |
| IDE-TDD-022 | 实现触及共享 utility 或偏离 Solution | TDD Record 记录实际实现的工程决策、受影响共享组件及 deviation owner；上游偏差必须 RETURN | P1 |
| IDE-TDD-023 | 当前 Slice 创建 controller、service、repository 和支持类及其单元测试 | 每个类和测试进入 Solution/Slice 批准的责任 package/module；测试遵循 Test Structure；TDD Record 的 File Placement Conformance 覆盖所有新增/移动路径 | P0 |
| IDE-TDD-024 | 多角色实现需要 package/test 布局，但 Solution 未定义或 Slice 未映射 | 缺 Solution 决策时 RETURN Solution/ENGINEERING_GAP；缺 Slice 映射时 RETURN Slice/SLICE_VIOLATION；不得先把文件堆在同一 package 再继续 | P0 |

## 13. Review 与插件场景

| ID | 前置与操作 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-REV-001 | 无 incoming Handoff 且请求不匹配 Ready Set 的 Feature Lane Entry，直接执行 `/forge-review` | Review 不支持 Bootstrap/Incremental/Recovery；不得评审或写报告 | P0 |
| IDE-REV-002 | 有效 Handoff 指向当前 READY_FOR_REVIEW attempt | 只审查该 Slice 和 attempt | P0 |
| IDE-REV-003 | attempt 已有同名 Review Report | 拒绝覆盖；新评审必须使用新的 TDD attempt | P0 |
| IDE-REV-004 | Review 发现代码问题 | 不修改代码、测试、TDD Record 或上游制品，只写 Review 证据 | P0 |
| IDE-REV-005 | 零 blocking、零 non-blocking findings | PASS；Findings 保留表头和分隔行，无数据行 | P0 |
| IDE-REV-006 | 零 blocking、存在 non-blocking findings | 仍为 PASS；计数与表中行一致 | P0 |
| IDE-REV-007 | 至少一个 blocking finding | FAIL，Return Workflow/Scope 必须存在并匹配 findings | P0 |
| IDE-REV-008 | blocking owners 同时包含 TDD 与 Slice | Return Workflow 选择更上游的 Slice | P0 |
| IDE-REV-009 | blocking owners 同时包含 Grill、Solution、TDD | Return Workflow 选择 Grill；Return Scope 使用其一条 blocking finding 的 Feature scope | P0 |
| IDE-REV-010 | 只有偏好性意见，没有正确性/合规/重大维护影响 | 不能因此 FAIL，应记录为 non-blocking 或不形成 finding | P0 |
| IDE-REV-011 | 启用全部内置插件 | 按 priority/dependency 顺序执行，不能按目录枚举顺序 | P0 |
| IDE-REV-012 | 项目没有某插件适用技术表面 | 插件/规则为 N/A，并记录可观察原因；N/A 不导致 FAIL | P0 |
| IDE-REV-013 | 证据不足 | 记录 UNKNOWN 和原因；单独 UNKNOWN 默认不阻塞 | P0 |
| IDE-REV-014 | 插件发现满足阻塞阈值的 VIOLATION | 转换为 canonical Findings 中的 blocking 行，并参与 FAIL | P0 |
| IDE-REV-015 | 插件发现低于阻塞阈值的 VIOLATION | 作为 non-blocking 证据，不错误触发 FAIL | P1 |
| IDE-REV-016 | architecture 插件执行 | 生成 md/html/csv；MD 与 CSV 严格匹配 Registry 的规范模板、规则顺序、计数和结果；其他插件仅生成注册表声明的格式 | P0 |
| IDE-REV-017 | 同逻辑路径补充报告已存在 | 写新报告前将旧内容存入 Reports History，使用下一个 revision 后缀 | P0 |
| IDE-REV-018 | Reports History 中有旧 VIOLATION | 历史报告不参与当前 Review 结论 | P0 |
| IDE-REV-019 | Review 运行测试/检查 | 顺序复用终端，不因“独立 Review”开启并行重复进程 | P1 |
| IDE-REV-020 | Review 启动了长运行进程 | Handoff 前全部终止，不能把进程隐式交给下一工作流 | P0 |
| IDE-REV-021 | PASS 后仍有未完成 Slice | FORWARD 到 Resolver 选出的下一 TDD Slice | P0 |
| IDE-REV-022 | 最后一个 Slice PASS | 输出 TERMINAL/COMPLETE，Completed Scope 为 Project | P0 |
| IDE-REV-023 | FAIL 后修复并生成新 TDD attempt | 旧 FAIL 保留但不再控制新 attempt；新 Review 独立判断 | P0 |
| IDE-REV-024 | 当前 Slice PASS 且 Resolver 选出下一 Slice | 只写当前 Review Report 并 FORWARD TDD；本轮不得实现下一 Slice | P0 |
| IDE-REV-025 | Review 检查端到端知识链 | 当前 Feature/Solution/Slice/TDD 版本与决策引用必须可解析；历史证据只能解释演进，不能满足当前 Gate | P1 |
| IDE-REV-026 | 当前 Solution 提供结构化影响模型 | Review 验证实现依赖、共享组件和决策引用符合目标 Feature 映射；派生影响查询不能替代 canonical Review 判定或授权下一 Scope | P1 |
| IDE-REV-027 | TDD 将 Solution 明确分离的生产或测试责任放入同一错误 package/module | architecture ARC-003/ARC-009 产生 P1 blocking finding，Review FAIL 并 RETURN TDD；测试通过不能覆盖布局违约 | P0 |
| IDE-REV-028 | 代码符合明确布局契约，但 Review 偏好另一种 package 组织方式 | 只能作为 ARC-008 P2 non-blocking 建议或不形成 finding；不得以个人偏好 FAIL | P1 |

## 14. Handoff 与转换场景

| ID | 场景 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-HO-001 | 正常跨 workflow/scope 前进 | 输出且只输出一个 FORWARD Handoff | P0 |
| IDE-HO-002 | 下游发现上游缺口 | 输出 RETURN，目标 owner/scope/category 与协议一致 | P0 |
| IDE-HO-003 | 当前 workflow/scope 继续工作 | 不输出同授权 RETURN 或 FORWARD | P0 |
| IDE-HO-004 | 等待用户澄清 | 不输出 Handoff，不把等待本身持久化为 blocker | P0 |
| IDE-HO-005 | 同一 workflow 转到另一个 Feature scope | 输出 FORWARD，而不是同作用域继续 | P0 |
| IDE-HO-006 | 有效空项目完成 | 输出 TERMINAL/COMPLETE | P0 |
| IDE-HO-007 | 非空项目仅 Planning READY | 不得提前 COMPLETE | P0 |
| IDE-HO-008 | 图矛盾 | 输出 TERMINAL/HALTED，category 为 GRAPH_CONTRADICTION | P0 |
| IDE-HO-009 | Handoff 后附加解释、执行 SQL/命令、调用工具或更新任务/记忆状态 | 用例 FAIL；Canonical Handoff 必须同时是最终内容和当前执行的最终动作 | P0 |
| IDE-HO-010 | Handoff 字段改名、缺失、增加或乱序 | 用例 FAIL；接收方不得执行生产性工作 | P0 |
| IDE-HO-011 | Input Artifacts 使用目录路径、重复项或错误版本 | Handoff 无效；接收方拒绝执行 | P0 |
| IDE-HO-012 | Target Scope 不符合目标 workflow | Handoff 无效；不得推断或修正目标 | P0 |
| IDE-HO-013 | Handoff 与执行后 Artifact Graph 不一致 | 接收方以图为准并拒绝错误 Handoff | P0 |
| IDE-HO-014 | 在新聊天中提供上一步有效 Handoff | 重新读取当前图并验证，不依赖旧聊天记忆 | P0 |
| IDE-HO-015 | 在新聊天中提供旧版本 Handoff | 因证据过期拒绝执行 | P0 |
| IDE-HO-016 | Handoff 缺少固定标题/表格，使用 `<transition>`、XML、YAML、普通键值行，或把 Workflow 名写进 Source Scope | 视为无效 Handoff；只接受 `### Handoff` 固定 Markdown 模板和规范 Scope，不执行生产性工作 | P1 |
| IDE-HO-017 | 当前执行解析出不同 Workflow 或 Target Scope | 仅输出对应 Canonical Handoff 并停止；不得在同一执行中预先消费目标 Scope | P0 |
| IDE-HO-018 | IDE Workflow 已输出有效 Handoff，Agent/宿主具备继续执行或委派能力 | 当前 invocation 仍立即结束；只有用户或宿主发起的新 invocation 才能验证并消费该 Handoff | P0 |

## 15. Blocker 与 Recovery 场景

对下表每一行，分别验证“当前调用内发现后路由”和“关闭聊天后通过 Recovery Entry 恢复”。

| ID | Category | Owner | Scope | 期望恢复行为 | 优先级 |
|---|---|---|---|---|---|
| IDE-BLK-001 | PLAN_GAP | Plan | Project | 只恢复 Plan Project | P0 |
| IDE-BLK-002 | BUSINESS_GAP | Grill | Feature | 只恢复被记录的 Feature | P0 |
| IDE-BLK-003 | ENGINEERING_GAP | Solution | Project | 只恢复 Solution Project | P0 |
| IDE-BLK-004 | SLICE_VIOLATION | Slice | Feature | 只恢复被记录的 Feature | P0 |
| IDE-BLK-005 | IMPLEMENTATION_GAP | TDD | Slice | 只恢复被记录的 Slice | P0 |
| IDE-BLK-006 | REVIEW_BLOCKER | Findings 决定 | 对应 owner scope | 通过 FAIL Review/Rule 8 RETURN，不作为普通 BLOCKED Artifact Recovery | P0 |

补充组合用例：

| ID | 场景 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-BLK-007 | 同时存在多个当前 blocker | 按 Plan > Grill > Solution > Slice > TDD 选择 owner | P0 |
| IDE-BLK-008 | 同 owner 多 Feature blocker | 按 Planning 声明位置，不按 F 编号排序 | P0 |
| IDE-BLK-009 | 同 owner 同 Feature 多 Slice blocker | 按 Slice Plan 声明位置，不按 S 编号排序 | P0 |
| IDE-BLK-010 | downstream blocker 的上游链已过期 | 保留文件但不允许它授权 RETURN 或 Recovery | P0 |
| IDE-BLK-011 | Recovery 后 blocker 尚未解决 | 保持同 workflow/scope，无同授权 RETURN | P0 |
| IDE-BLK-012 | Review 尝试无 Handoff 使用 Recovery | 必须拒绝，因为 Review 没有持久 BLOCKED Artifact 所有权 | P0 |

## 16. 后续需求与增量演进场景

以下用例均从 `S2-BUSINESS`、`S3-ENGINEERING` 或 `S7-COMPLETE` 的独立副本开始。

| ID | 场景与输入 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-INC-001 | 直接提交一个新模块需求并执行 `/forge-plan`，不使用“同项目”或“incremental”字样 | Subsequent Plan Entry 默认授权 Plan；不需要合成 incoming Handoff | P0 |
| IDE-INC-002 | 新需求与现有 Planning 在语义上无明显关联 | 仍作为当前软件项目的后续变更处理；不询问项目归属，不执行 Project Evidence Rotation | P0 |
| IDE-INC-003 | 当前图存在 contradiction | Subsequent Plan Entry 被拒绝，不得借后续需求修复无效图 | P0 |
| IDE-INC-004 | 当前有 actionable blocker | Subsequent Plan Entry 被拒绝，先路由 blocker owner | P0 |
| IDE-INC-005 | 当前有匹配 FAIL Review | Subsequent Plan Entry 被拒绝，先处理 Review RETURN | P0 |
| IDE-INC-006 | 新增 Feature | 保留全部旧 Feature ID；新 Feature 使用从未使用过的 ID；Change Set 记录 added | P0 |
| IDE-INC-007 | 修改一个 Feature 的业务行为 | 只推进该 Feature Contract Version；Change Set 记录 modified | P0 |
| IDE-INC-008 | 纯重排且不改变依赖/契约 | Change Set 记录 reordered；Feature Contract Version 不无故变化 | P0 |
| IDE-INC-009 | 重排同时改变依赖契约 | 受影响 Feature Contract Version 按实际影响推进 | P1 |
| IDE-INC-010 | 用户明确退役一个 Feature | 事务性归档其 Requirement/Slice/TDD/Review 和 supplemental Reports；Planning 移除该 ID | P0 |
| IDE-INC-011 | 用户只在新意图中遗漏旧 Feature | 不把遗漏当退役，必须要求明确授权 | P0 |
| IDE-INC-012 | 尝试复用已退役 Feature ID | 拒绝复用，分配从未使用的新 ID | P0 |
| IDE-INC-013 | 新增 Feature 不影响旧 Feature | 旧 Requirement、Slice、TDD、PASS Review 保持当前有效 | P0 |
| IDE-INC-014 | Solution 发现横切影响旧 Feature | 只让明确受影响的 Feature Engineering Version 前进，并使其下游证据过期 | P0 |
| IDE-INC-015 | 增量执行全过程 | Artifact Root、Reports Root 以及两个 history 根始终保留，不执行 Project Evidence Rotation | P0 |
| IDE-INC-016 | 增量 Plan 没有产生规范变化 | 不伪造版本增长；保持图不变，并按当前 Plan 与 Transition 契约产生合法等待或终态结果 | P1 |

## 17. 历史、报告与轮换场景

| ID | 场景 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-HIS-001 | 替换 Planning/Requirement/Solution/Slice/TDD 当前文件 | 写入新版本前将旧文件精确复制到 Artifact History | P0 |
| IDE-HIS-002 | 修改已归档 Artifact | 必须视为违规；History 应保持不可变 | P0 |
| IDE-HIS-003 | 创建 Review attempt 2 | attempt 1 Review 仍直接位于 Artifact Root，不移动到 Artifact History | P0 |
| IDE-HIS-004 | 重写同一插件/Feature/Slice/attempt/format 报告 | 原文件先进入 Reports History，revision 单调增加 | P0 |
| IDE-HIS-005 | 当前 Reports 与 Reports History 同时存在 | 只有当前 Reports 参与本次 Review 证据 | P0 |
| IDE-HIS-006 | 显式 reset/archive maintenance，Artifacts 与 Reports 都非空 | 两个根使用完全相同的 UTC 后缀轮换 | P0 |
| IDE-HIS-007 | 只有 Artifact Root 非空 | 只备份非空根，但创建两个新的空当前根 | P0 |
| IDE-HIS-008 | 只有 Reports Root 非空 | 只备份非空根，但创建两个新的空当前根 | P0 |
| IDE-HIS-009 | 预期 backup path 已存在 | 在移动任何根之前停止，不覆盖、不合并、不删除 | P0 |
| IDE-HIS-010 | Artifact Root 或 Reports Root 是符号链接/非目录 | 停止并报告 blocker，不沿链接操作 | P0 |
| IDE-HIS-011 | 模拟第二个 move 失败 | 回滚第一个成功 move；不能留下半轮换状态 | P1 |
| IDE-HIS-012 | 模拟 rollback 也失败 | 报告所有保留的 current/backup 路径，停止 Plan | P1 |
| IDE-HIS-013 | Feature retirement 目标目录已存在 | 整个退役事务停止，不覆盖或合并已有目录 | P0 |
| IDE-HIS-014 | Feature retirement 中途失败 | 恢复所有已移动 evidence，旧 Planning 继续生效 | P1 |

## 18. 无效 Artifact Graph 场景

每个用例都应从有效快照复制，然后只引入表中一个主要矛盾。预期统一为：不执行生产性工作，输出 TERMINAL/HALTED，Blocker Category 为 `GRAPH_CONTRADICTION`，Reason 以确定的错误代码和 `: ` 开始，Input Artifacts 只包含证明主要矛盾所需的规范文件。

| ID | 注入的矛盾 | 期望主要错误代码 | 优先级 |
|---|---|---|---|
| IDE-GRAPH-001 | Artifact Root 是文件或不可用路径 | `artifact_root_invalid` | P0 |
| IDE-GRAPH-002 | 非空 Artifact Root 没有有效 Planning | `planning_missing` | P0 |
| IDE-GRAPH-003 | Artifact 缺少 Version/Metadata/必填结构 | `artifact_invalid` | P0 |
| IDE-GRAPH-004 | Version 缺失、重复或不是 `major.minor` | `artifact_invalid`，投影版本为 `INVALID_VERSION` | P0 |
| IDE-GRAPH-005 | Planning `Feature IDs = NONE` 但存在下游制品 | `empty_project_contradiction` | P0 |
| IDE-GRAPH-006 | Requirement 引用未声明 Feature | `identifier_reference_invalid` | P0 |
| IDE-GRAPH-007 | TDD/Review 引用未声明 Slice | `identifier_reference_invalid` | P0 |
| IDE-GRAPH-008 | BLOCKED Affected Scope 不可解析 | `routing_scope_invalid` | P0 |
| IDE-GRAPH-009 | Review finding Affected Scope 与 owner 不匹配 | `routing_scope_invalid` 或规范定义的首个更早 artifact 错误 | P0 |
| IDE-GRAPH-010 | FAIL Return Scope 不可解析 | `routing_scope_invalid` | P0 |
| IDE-GRAPH-011 | Review 缺失/重复/格式错误的 canonical Findings 表 | `artifact_invalid` | P0 |
| IDE-GRAPH-012 | Review metadata counts 与 Findings 行数不一致 | `artifact_invalid` | P0 |
| IDE-GRAPH-013 | PASS 含 blocking finding 或 Return 字段 | `artifact_invalid` | P0 |
| IDE-GRAPH-014 | FAIL 没有 blocking finding 或缺 Return 字段 | `artifact_invalid` | P0 |
| IDE-GRAPH-015 | FAIL Return Workflow 不是最高上游 blocking owner | `artifact_invalid` | P0 |
| IDE-GRAPH-016 | 下游制品引用冲突的上游版本 | `artifact_invalid` 或关系校验定义的首个错误 | P0 |
| IDE-GRAPH-017 | 同一规范作用域出现重复 active contract | `artifact_invalid` | P1 |
| IDE-GRAPH-018 | 同一 Slice attempt 出现重复 Review evidence | `artifact_invalid` | P1 |
| IDE-GRAPH-019 | 多个矛盾同时存在 | 按规范校验顺序稳定选择同一个 primary contradiction，不因目录枚举变化 | P1 |
| IDE-GRAPH-020 | HALTED 投影为空 | Input Artifacts 精确为 `NONE`；其他 Handoff variant 不得使用 `NONE` | P1 |

## 19. 版本新鲜度与顺序场景

| ID | 场景 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-VER-001 | Planning 外层版本增加，但某 Feature Contract Version 保持 | 该 Feature 的 Requirement 仍可保持当前 | P0 |
| IDE-VER-002 | 某 Feature Contract Version 增加 | 只使该 Feature 的旧 Requirement 及依赖链过期 | P0 |
| IDE-VER-003 | Solution 外层版本增加，但某 Feature Engineering Version 保持 | 该 Feature 的 Slice/TDD/Review 仍可使用 | P0 |
| IDE-VER-004 | 某 Feature Engineering Version 增加 | 只使该 Feature 的 Slice/TDD/Review 过期 | P0 |
| IDE-VER-005 | Slice Plan 版本增加 | 该 Feature 对应旧 TDD/Review 过期 | P0 |
| IDE-VER-006 | READY_FOR_REVIEW TDD 引用旧上游版本 | 不进入 Review，TDD 在当前边界重新执行 | P0 |
| IDE-VER-007 | PASS Review 没有匹配当前 TDD Record | 不证明完成 | P0 |
| IDE-VER-008 | 旧 FAIL attempt 与当前更高 TDD attempt 并存 | 旧 FAIL 保留历史意义，但不控制当前 attempt | P0 |
| IDE-ORD-001 | `F-02` 与 `F-01` 都在 Ready Set 且 F-02 位于 Planning 前 | 默认 Resolver 先选择 F-02；F-01 仍可通过 Feature Lane Entry 并行启动 | P0 |
| IDE-ORD-002 | `S-02` 在 Slice Plan 中位于 `S-01` 前 | Resolver 先处理 S-02 | P0 |
| IDE-ORD-003 | 调换文件创建时间和目录枚举顺序 | 解析结果不变 | P1 |
| IDE-ORD-004 | 对话先讨论后置 Feature | 对话顺序不改变声明顺序 | P0 |

## 20. 会话重启与无记忆恢复

| ID | 场景 | 期望结果 | 优先级 |
|---|---|---|---|
| IDE-RST-001 | 完成 Plan 后关闭聊天，开启新聊天并提供有效 Handoff | Grill 从 Artifact Graph 和 Handoff 恢复，不要求旧聊天历史 | P0 |
| IDE-RST-002 | TDD 中断后关闭 IDE，当前 TDD Record 为 IN_PROGRESS | 新会话从当前证据判断状态，不使用记忆中的 cursor | P0 |
| IDE-RST-003 | 当前存在合法 BLOCKED artifact，不提供旧 Handoff | 对应 owner 可通过 Recovery Entry 恢复 | P0 |
| IDE-RST-004 | 当前没有 blocker、Handoff，也没有匹配 Ready Set 的 Feature Lane Entry，直接调用非 Plan workflow | 拒绝生产性执行 | P0 |
| IDE-RST-005 | `.forgeflow/runtime/` 含旧 CLI 状态 | IDE 决策不受 runtime cursor 或 last-handoff 影响 | P0 |
| IDE-RST-006 | 对话声称完成，但 Artifact Graph 未完成 | 不输出 COMPLETE，按图选择下一工作流 | P0 |
| IDE-RST-007 | 对话声称某旧版本仍有效 | 以当前 Artifact 版本边为准，忽略对话记忆 | P0 |

## 21. Adapter 一致性场景

在相同项目快照上分别使用 Codex 和 Copilot Adapter。内容措辞可以不同，但规范结果必须一致。

| ID | 对比项 | 一致性要求 | 优先级 |
|---|---|---|---|
| IDE-PAR-001 | 六个 workflow 的权威文件读取顺序 | 完全一致 | P0 |
| IDE-PAR-002 | 同一 Artifact Graph 的 workflow/scope 选择 | 完全一致 | P0 |
| IDE-PAR-003 | Artifact 所有权和版本变化 | 完全一致 | P0 |
| IDE-PAR-004 | Handoff variant、目标和 evidence | 完全一致 | P0 |
| IDE-PAR-005 | 后续 Plan 变更的失效范围 | 完全一致 | P0 |
| IDE-PAR-006 | Review PASS/FAIL 和 Return owner | 完全一致 | P0 |
| IDE-PAR-007 | 无效图的 primary error 与 HALTED 投影 | 完全一致 | P0 |
| IDE-PAR-008 | 宿主专属元数据 | 仅 Copilot 需要 `agent: agent`；该差异不能改变框架语义 | P0 |

## 22. 建议执行批次

### 批次 A：Prompt 接管验证

先执行：

```text
IDE-INV-001 ~ IDE-INV-007
IDE-PLAN-001
IDE-PLAN-007
IDE-PLAN-008
```

只有确认 `/forge-plan` 不再被 Copilot native Plan 接管后，才继续后续测试。

### 批次 B：主干端到端

按真实 Handoff 顺序完成：

```text
Plan
-> Grill（全部 Feature）
-> Solution
-> Slice（全部 Feature）
-> TDD / Review（逐 Slice）
-> TERMINAL / COMPLETE
```

该批次产生 `S1` 到 `S7` 的标准快照。

### 批次 C：阻塞、RETURN 与恢复

执行全部 `IDE-BLK-*`，并结合 Grill、Solution、Slice、TDD、Review 的 RETURN 场景。

### 批次 D：增量与历史

从 `S7-COMPLETE` 副本执行全部 `IDE-INC-*`、`IDE-HIS-*` 和 `IDE-VER-*`。

### 批次 E：失败关闭

从独立副本执行全部 `IDE-GRAPH-*` 和 malformed Handoff 场景。该批次不得复用主干工作区。

### 批次 F：Adapter parity

选择至少一个 happy path、一个 Recovery、一个 incremental、一个 FAIL Review 和一个 HALTED 用例，在 Codex/Copilot 上交叉执行。

## 23. 缺陷严重级别

| 级别 | 定义 | 示例 |
|---|---|---|
| P0 | 破坏权威状态、越权修改、错误推进或宿主接管 | `/forge-plan` 执行 native Plan；Review 修改代码；无效图继续实现 |
| P1 | 证据、历史、确定性或恢复行为错误 | 旧报告未归档；按编号而非声明顺序选择 |
| P2 | 不影响语义的可用性或表达问题 | description 不清晰；错误提示不够易懂 |

出现任何 P0 时停止发布，并从该用例的干净快照复现。不得通过人工补写 Artifact 将失败改记为通过。

## 24. 测试结果汇总表

```markdown
| Case ID | Adapter | Result | Evidence | Defect | Notes |
|---|---|---|---|---|---|
| IDE-INV-001 | copilot | NOT RUN | — | — | — |
```

建议分别统计：

```text
P0 total / passed / failed / blocked / not run
P1 total / passed / failed / blocked / not run
P2 total / passed / failed / blocked / not run
Copilot total / passed
Codex total / passed
```

仓库提供本地汇总和准出命令：

```bash
python3 tests/acceptance/ide/manage.py summary
python3 tests/acceptance/ide/manage.py release-gate
```

`release-gate` 不执行 IDE 或 Agent。它只检查结果目录中的真实执行记录，
拒绝仍含 `TODO` 的 PASS，并要求所有 P0 都通过；已记录的 P1 FAIL/BLOCKED
同样阻止发布。

## 25. 发布准出标准

只有同时满足以下条件，才能认为当前 ForgeFlow IDE 核心框架通过验收：

1. 所有 P0 用例执行完成且通过；
2. `/forge-plan` 在 Copilot 原生 Plan 预选状态下仍执行 ForgeFlow Plan；
3. 两个 Adapter 都至少完成一次真实端到端流程；
4. 六个工作流均验证了所有权边界；
5. 四个 Handoff variant 均有真实 IDE 证据；
6. 五种非 Review blocker 和 REVIEW_BLOCKER 均完成路由验证；
7. Subsequent Plan Entry 的新增、修改、重排、退役和拒绝条件全部通过；
8. Artifact History、Reports History 和 Project Evidence Rotation 全部通过；
9. Review PASS、FAIL、N/A、UNKNOWN、blocking/non-blocking 均有证据；
10. 至少六类 Graph Error Code/主要矛盾均验证失败关闭；
11. 新会话能够仅凭 Artifact Graph 与有效 Handoff/Recovery 恢复；
12. Codex 与 Copilot 在相同图上的 workflow、scope、Artifact 和 Handoff 结果一致；
13. 没有遗留 P0/P1 缺陷；
14. 测试报告明确区分真实 IDE 调用、人工夹具准备和任何辅助脚本结果。

## 26. 最小回归集

后续只修改 Prompt 时，至少重复：

```text
IDE-INV-001
IDE-INV-003
IDE-INV-007
IDE-PLAN-001
IDE-PLAN-014
IDE-GRILL-004
IDE-SOL-006
IDE-SLICE-012
IDE-TDD-002
IDE-TDD-015
IDE-REV-004
IDE-REV-007
IDE-HO-009
IDE-INC-001
IDE-INC-015
IDE-GRAPH-002
IDE-RST-001
IDE-PAR-002
```

修改 Framework、Artifact Protocol、Handoff Protocol、workflow 或 Review registry 时，必须执行全部 P0 用例，而不能只运行最小回归集。
