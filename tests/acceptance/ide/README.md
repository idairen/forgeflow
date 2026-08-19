# ForgeFlow IDE Acceptance Test Assets

本目录把 `docs/testing/ide-test-plan.zh-CN.md` 中的 220 个场景转化为可执行的 IDE 测试资产。

## 设计原则

- 测试必须通过真实 IDE Prompt 调用完成。
- S1–S7 快照必须由真实 IDE 流程生成，不能提交人工伪造的“通过”制品。
- 每个破坏性用例使用独立工作区副本。
- `manage.py` 只准备、复制和检查测试资产，不执行 ForgeFlow 工作流。
- `.forgeflow/artifacts/` 始终是测试项目的权威状态；结果记录不能代替 Artifact 证据。

## 目录

```text
tests/acceptance/ide/
├── README.md
├── manage.py
├── inputs.md
├── fixtures/python-project/
├── results/
├── snapshots/       # 本地生成，默认不提交
└── workspaces/      # 本地生成，默认不提交
```

## 1. 校验测试资产

```bash
python3 tests/acceptance/ide/manage.py verify
```

期望输出：

```text
Verified 220 IDE cases and 12 workflow Prompts (P0=199, P1=21, P2=0).
```

## 2. 查看用例

```bash
python3 tests/acceptance/ide/manage.py list --priority P0
python3 tests/acceptance/ide/manage.py list --area INV
python3 tests/acceptance/ide/manage.py show IDE-INV-003
python3 tests/acceptance/ide/manage.py export
```

`list` 和 `show` 直接读取权威测试计划，不维护第二份容易过期的用例清单。
仓库同时保存生成后的 `forgeflow-ide-test-cases.csv`，方便使用 Excel、Numbers
或测试管理平台执行和记录结果。计划发生变化后，可用 `export` 重新生成 CSV。

## 3. 创建干净测试工作区

Copilot：

```bash
python3 tests/acceptance/ide/manage.py init \
  --adapter copilot \
  --output tests/acceptance/ide/workspaces/copilot-happy
```

该命令会：

- 复制最小 Python 项目；
- 安装当前仓库中的 Framework、Protocols、Workflows、Rules 和 Adapters；
- 创建空 Artifact Root 和 Reports Root；
- 写入 VS Code `chat.promptFilesLocations`，启用 `.forgeflow/adapter/copilot`；
- 不创建任何 Planning 或下游 Artifact。

Codex：

```bash
python3 tests/acceptance/ide/manage.py init \
  --adapter codex \
  --output tests/acceptance/ide/workspaces/codex-happy
```

Codex 的 Prompt 发现方式由实际宿主配置；工具不会虚构 Codex IDE 注册文件。

## 4. 执行 Prompt 接管测试

1. 在 IDE 中打开新建工作区根目录。
2. 确认 `/` 菜单显示六个 `forge-*` Prompt。
3. 把 Copilot 当前模式切换到 native Plan。
4. 从 `/` 菜单选择 `/forge-plan`。
5. 粘贴 `inputs.md` 的 `INPUT-INITIAL-01`。
6. 保存完整响应、截图和 `git diff`。
7. 确认生成的是 `.forgeflow/artifacts/planning.md`，而不是 Copilot implementation plan。

优先执行测试计划的批次 A。

## 5. 生成真实状态快照

在真实 IDE 中完成每个门禁后关闭正在运行的进程，并从仓库根目录执行：

```bash
python3 tests/acceptance/ide/manage.py snapshot \
  --source tests/acceptance/ide/workspaces/copilot-happy \
  --output tests/acceptance/ide/snapshots/S1-PLANNED-copilot
```

依次保存：

```text
S1-PLANNED
S2-BUSINESS
S3-ENGINEERING
S4-DELIVERY
S5-REVIEW
S6-FAIL
S7-COMPLETE
```

快照命令会排除 `.git`、缓存和 `.forgeflow/runtime/`，但保留代码、Artifacts、Reports 和两个 history 根。

## 6. 准备一个独立用例

```bash
python3 tests/acceptance/ide/manage.py prepare IDE-GRAPH-002 \
  --adapter copilot \
  --source tests/acceptance/ide/snapshots/S1-PLANNED-copilot \
  --output tests/acceptance/ide/workspaces/IDE-GRAPH-002-copilot
```

命令会：

- 拒绝覆盖已有目录；
- 拒绝复制包含符号链接的工作区；
- 创建独立工作区；
- 在工作区旁边生成结果记录文件；
- 打印推荐的前置快照。

工具不会自动注入矛盾、修改 Artifact 或执行 Prompt。按照测试计划只引入当前用例描述的一个变化，避免多个错误干扰 primary contradiction 判断。

## 7. 记录结果

默认结果文件示例：

```text
tests/acceptance/ide/workspaces/IDE-GRAPH-002-copilot.IDE-GRAPH-002.result.md
```

填写：

- IDE、扩展、模型和模式版本；
- Prompt 是否从命令菜单选择以及来源；
- 用户输入；
- 执行前后文件清单；
- Artifact、Report 和 Handoff 证据；
- PASS/FAIL/BLOCKED/NOT RUN；
- 缺陷编号。

结果文件位于测试工作区之外，避免被 Agent 当作项目需求或 Review 输入。

## 8. 推荐执行顺序

```text
1. manage.py verify
2. 创建 Copilot 与 Codex 干净工作区
3. 执行批次 A：Prompt 接管
4. 执行批次 B：生成 S1–S7
5. 从快照复制批次 C/D/E 用例
6. 执行 Adapter parity
7. 汇总发布准出结果
```

完整期望结果、优先级和准出规则以 `docs/testing/ide-test-plan.zh-CN.md` 为准。
