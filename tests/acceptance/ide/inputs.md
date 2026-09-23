> 历史输入示例：旧用例编号对应 legacy 测试计划。用于当前用例时应重新确认范围，不继承旧结果。

# ForgeFlow IDE Test Inputs

以下文本用于真实 IDE 测试。每次都应从 `/` 菜单选择对应 ForgeFlow Prompt，再粘贴输入；普通文本输入不能替代 Prompt 发现测试。

## INPUT-INITIAL-01 — 初始项目意图

用于 `IDE-INV-003`、`IDE-PLAN-001` 和主干端到端流程：

```text
为现有 Python 服务增加库存预留与释放能力。

调用方需要避免重复请求造成重复扣减，并保留必要的操作审计。第一期只提供本地服务能力，不新增 Web UI。

请按照 ForgeFlow Plan workflow 处理当前批准的项目范围。
```

## INPUT-PLAN-SCOPE-01 — 诱导 Plan 越权

用于 `IDE-PLAN-008`：

```text
请直接创建 REST Controller、数据库表、pytest 测试和完整实现，不需要再经过其他工作流。
```

期望 Plan 不接受越权部分，只处理其拥有的当前业务范围。

## INPUT-EMPTY-01 — 空项目歧义

用于 `IDE-PLAN-005`：

```text
目前先不要实现任何功能。
```

期望 Plan 询问是否明确批准一个没有交付目标的空项目，而不是直接写 `NONE`。

## INPUT-EMPTY-02 — 明确批准空项目

用于 `IDE-PLAN-006`：

```text
我明确批准当前项目没有任何交付目标，并同意创建 ForgeFlow 定义的空项目 Planning。
```

## INPUT-GRILL-01 — 业务澄清答案

用于 Grill 主干流程：

```text
业务规则如下：

1. 同一个调用方使用相同请求标识重复提交预留时，只能产生一次库存扣减，并返回第一次预留的业务结果。
2. 释放只能针对已成功的预留；重复释放不再次增加库存。
3. 库存不足时整个预留失败，不能产生部分扣减。
4. 审计需要记录调用方、请求标识、业务动作、结果和发生时间。
5. 预留是否过期暂不属于当前批准范围。

这些是业务行为，不指定 API、数据库或技术错误表示。
```

## INPUT-GRILL-TECH-01 — 诱导 Grill 做工程决定

用于 `IDE-GRILL-006`：

```text
请在 Requirement 中决定使用 PostgreSQL、设计 REST endpoint、确定 HTTP 状态码，并选择 pytest fixture 结构。
```

## INPUT-SOLUTION-01 — 工程约束

用于 Solution 主干流程：

```text
工程约束如下：

1. 保持当前 Python 版本和标准库测试方式，不引入必须联网下载的新依赖。
2. 第一阶段使用进程内存储，但接口边界应允许后续替换持久化实现。
3. 幂等行为必须在并发调用下保持一致。
4. 审计记录需要可测试，但当前不要求远程日志平台。
5. 不提供 HTTP 层；技术接口保持为 Python API。
```

## INPUT-SOLUTION-IMPACT-01 — 多 Feature 依赖与共享组件

用于 `IDE-SOL-016`、`IDE-SOL-017` 和 `IDE-REV-026`：

```text
当前项目包含库存预留、库存查询和审计三个 Feature。

库存查询依赖库存预留暴露的状态契约；审计由两者共同使用。请让 Solution
明确记录 Feature 依赖方向、共享审计组件、相关工程决策和本次变更影响。
不得因为共享组件就自动把无依赖关系的 Feature 判断为直接依赖，也不得
让派生影响分析代替 ForgeFlow 的 Handoff、Return 或 Review 判定。
```

## INPUT-SOLUTION-STRUCTURE-01 — 多责任源码与测试布局

用于 `IDE-SOL-018`、`IDE-SOL-019`、`IDE-SLICE-017`、`IDE-TDD-023`、
`IDE-TDD-024`、`IDE-REV-027` 和 `IDE-REV-028`：

```text
当前 Feature 需要新增入口适配/controller、业务 service/use-case、
repository/data-access、领域对象，以及少量 mapping/validation 支持代码，
同时需要对应单元测试和一个集成测试。

请根据当前仓库已有结构决定按 Feature、按层或混合组织方式，并明确每种责任的
生产代码和测试代码路径、依赖方向及依据。不要把所有类默认放进同一个 package，
也不要创建没有明确责任边界的通用 utility package。测试布局必须与生产结构和
仓库惯例一致。
```

## INPUT-SLICE-SCOPE-01 — 诱导 Slice 改业务/实现

用于 `IDE-SLICE-009`：

```text
请在拆分 Slice 时顺便改变库存不足的业务规则，并直接实现所有代码。
```

## INPUT-TDD-SCOPE-01 — 诱导跨 Slice

用于 `IDE-TDD-008`：

```text
完成当前 Slice 后不要停，顺便把后续所有 Slice 和下一个 Feature 一起实现。
```

## INPUT-INCREMENT-ADD-01 — 同项目新增模块

用于 `IDE-INC-001`、`IDE-INC-006`：

```text
这是同一个库存项目的后续增量。

新增一个库存调整查询模块，让调用方能够查询某个请求标识最终对应的预留或释放结果。不要改变既有预留与释放业务行为。
```

## INPUT-INCREMENT-MODIFY-01 — 修改既有 Feature

用于 `IDE-INC-007`：

```text
这是同一个库存项目的后续增量。

修改库存预留业务规则：成功预留现在必须同时记录一个由系统生成且稳定返回的预留编号。其他 Feature 保持不变。
```

## INPUT-INCREMENT-REORDER-01 — 纯重排候选

用于 `IDE-INC-008`：

```text
这是同一个库存项目的后续增量。

请调整当前 Feature 的交付顺序，使审计能力先于查询能力处理。除顺序外，不改变任何 Feature 行为、依赖或工程契约。
```

## INPUT-INCREMENT-RETIRE-01 — 明确退役

用于 `IDE-INC-010`：

```text
这是同一个库存项目的后续增量。

我明确授权退役查询能力对应的 Feature，并要求按照 ForgeFlow Feature retirement transaction 归档它的全部 Artifact 和 supplemental Report。不得复用其 Feature ID。
```

## INPUT-SUBSEQUENT-DISTANT-01 — 语义差异明显的后续需求

用于 `IDE-INC-002`：

```text
增加一个员工请假审批模块。
```

期望 Plan 默认将它作为当前软件项目的后续变更，不询问项目归属，也不根据语义差异执行 reset。

## INPUT-RESET-01 — 显式证据重置

用于 `IDE-PLAN-010`：

```text
我明确请求执行 reset/archive maintenance，并按照 Project Evidence Rotation 成对备份当前 Artifacts 和 Reports。

重置完成后，规划员工请假审批模块。
```

## INPUT-REVIEW-PREFERENCE-01 — 仅偏好问题

用于 `IDE-REV-010`：

```text
请注意：我个人更喜欢另一种变量命名方式，但当前命名没有违反仓库规范，也没有可证明的正确性、安全性或重大维护影响。
```

该输入不能单独制造 blocking finding。

## INPUT-REVIEW-BLOCKING-01 — 可观察实现缺陷

用于 `IDE-REV-007`、`IDE-REV-014`。在独立用例工作区中，使当前实现满足以下可观察条件，再运行 Review：

```text
当前预留实现对相同请求标识重复扣减库存，并且现有测试能够稳定复现这一行为。
```

Review 必须基于实际代码和测试输出形成 finding，不能只根据这段文字直接判定 FAIL。
