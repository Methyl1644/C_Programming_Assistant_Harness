# AGENTS.md · C Programming Assistant Harness

> 本文件是**项目级 AI 协作规则**——任何新 AI（Claude Code / Codex /
> Cursor / OpenCode / Gemini CLI）接手本项目时，第一份必读文件。
> 配合课程要求的全局规则（`~/.config/opencode/AGENTS.md`）使用。

---

## 1. 项目是什么

**CP-AH (C Programming Assistant Harness)** 是一个面向 C 语言初学者的
**护栏优先** Coding Agent Harness。核心价值：

- 能读学生代码、跑测试、找 valgrind 内存问题
- **绝不偷偷改学生代码**（HITL 强制人批）
- **绝不跑沙箱外的命令**

完整规约见 `docs/superpowers/specs/2026-07-07-cpah-design.md`（14 章，
571 行，0f15461 commit）。

---

## 2. 当前进度

| 阶段 | 状态 | commit |
|------|------|--------|
| 仓库初始化 (LICENSE / .gitignore / README) | ✅ | e696127 |
| SPEC §1-§5（立项 / 用户故事 / 功能 / 非功能 / 机制） | ✅ | beab007 |
| SPEC §6-§10（架构 / 数据 / 凭据 / 技术 / 验收） | ✅ | c170863 |
| SPEC §11 测试策略（TDD / MockLLM / 一键测试） | ✅ | 71477d3 |
| SPEC §12-§14 风险 / 凭据威胁 / 反思 | ✅ | 0f15461 |
| **SPEC 自检与用户复审** | ✅ | — |
| writing-plans（拆成 subagent 任务） | ✅ | 6665997 |
| 代码实现 (TDD: 红→绿→重构, Task 1-18) | ✅ | 81 passed / 7 skipped |
| 冷启动验证（两次, 3 个文档漏洞已修订） | ✅ | 6198c62 |
| SPEC_PROCESS.md / AGENT_LOG.md / REFLECTION.md | ✅ | 4628090 |
| WebUI (FastAPI + Linear 前端) | ✅ | 5381d2b |
| Docker 分发 (Dockerfile + .dockerignore) | ✅ | 9997925 |
| CI (`.gitlab-ci.yml` 含 `unit-test` job) | ✅ | (已有) |
| 云部署 + 公网 URL | N/A（本地 Docker 部署） | — |

---

## 3. 工作约定（硬性）

### 3.1 TDD 强制

- 任何 task 必先写失败的测试（**红**）
- 写最少代码让它过（**绿**）
- 再重构（不破坏测试）
- 三个 commit 各自独立，**不接受 "先写实现再补测试"**

### 3.2 一个 commit 一件事

- commit message 格式：`<type>(<scope>): <subject>`（参考 Conventional Commits）
- 例子：`test(guardrail): add failing test for rm -rf / classification`
- 例子：`feat(guardrail): implement L0 pattern matcher`

### 3.3 PR 工作流

- 每个 task 对应一个 worktree、一个分支、一个 PR
- 写完一个 task 等用户开加速器后再 push
- PR description 标注：由哪个 subagent 完成、人工改了什么

### 3.4 不允许的依赖

按 A 文件 §A.4-A，**harness 核心不能寄生于**：
- LangChain / LangGraph AgentExecutor
- AutoGen
- CrewAI
- LlamaIndex agent
- Claude Agent SDK / OpenAI Assistants API 的"内建 agent loop"
- 任何"一键启动 agent" 的高层框架

**允许的底层零件**：
- OpenAI Python SDK（LLM 补全 API）
- FastAPI / pydantic / pytest
- keyring（凭据）
- subprocess（沙箱）
- pydantic（数据模型）

### 3.5 护栏优先

任何"省事" 的实现都先问一句："这个能不能用 mock LLM 验证？"
能验证 → 编码；不能验证 → **不写**，找替代方案。

### 3.6 凭据安全

- **绝不在**源码、commit message、终端输出、日志里出现真实 key
- 用 `keyring` 库；CI 用 env var + `::add-mask::`
- 详见 `docs/superpowers/specs/2026-07-07-cpah-design.md` §13

---

## 4. 主角维度：治理与护栏

- §5.3 危险动作分类（L0/L1/L2/L3 + L2a/L2b/L2c）
- §5.3 HITL 状态机
- §5.3 进程级沙箱（chdir + ulimit/job object + env 清理）
- §10.1 AC-3, AC-4, AC-5, AC-6 验证

这是评审人**最看重的部分**，深度实现。

---

## 5. 目录约定

```
.
├── docs/superpowers/
│   ├── specs/2026-07-07-cpah-design.md     # 规约
│   └── plans/2026-07-07-cpah-plan.md       # 实现计划 (待写)
├── src/cpa_harness/                       # 源代码
│   ├── loop.py                             # AgentLoop (主循环)
│   ├── llm/                                # LLM 抽象
│   ├── tools/                              # 8 个工具
│   ├── guardrails/                         # ★ 主角维度
│   ├── feedback/                           # gcc / valgrind 解析
│   ├── memory/                             # 4 层记忆
│   ├── config/                             # 规则文件加载
│   ├── web/                                # FastAPI WebUI
│   └── cli.py                              # CLI 入口
├── tests/                                  # mock-LLM 单测
├── docker/                                 # 沙箱相关 (可选)
├── .gitlab-ci.yml                          # CI (必须含 unit-test job)
├── Dockerfile                              # 分发
├── AGENT_LOG.md                            # 实施过程日志
├── REFLECTION.md                           # 1500-2500 字反思
└── README.md
```

---

## 6. 怎么"接续"（给新 AI 看的）

如果你在**新 session** 接手这个项目，请：

1. `cd` 到项目目录
2. **读这份文件**（项目级 `AGENTS.md`）
3. **读** `~/.config/opencode/AGENTS.md`（全局语言规则）
4. **读** `docs/superpowers/specs/2026-07-07-cpah-design.md`（14 章 SPEC）
5. **读** `git log --oneline`（看 commit 历史）
6. **读** `AGENT_LOG.md`（如果存在，了解实施过程）
7. **问用户**：当前在哪个 task？下一步做什么？

**不要**：
- 不要凭印象修改 SPEC（除非用户明确说要改）
- 不要往 harness 核心里加 LangChain / CrewAI 等高层框架
- 不要把测试代码和实现代码混在同一个 commit

---

## 7. 一键命令速查

| 任务 | 命令 |
|------|------|
| 跑所有测试 | `make test` 或 `pytest` |
| 看覆盖率 | `make test-cov` 或 `pytest --cov=cpa_harness --cov-report=term-missing` |
| 单测一个文件 | `pytest tests/test_guardrail.py` |
| 单测一个函数 | `pytest tests/test_guardrail.py::test_classify_blocks_rm_rf_root` |
| 启动 WebUI（开发） | `uvicorn cpa_harness.web.app:app --reload` |
| 启动 CLI | `python -m cpa_harness.cli run file.c --goal "..."` |
| Lint | `ruff check src/ tests/` |
| 类型检查 | `mypy src/cpa_harness/` |
| 跑 E2E（需真 LLM） | `pytest tests/e2e/ --run-e2e` |

---

> 严格遵守本文件。违反任意一条视为 bug。
