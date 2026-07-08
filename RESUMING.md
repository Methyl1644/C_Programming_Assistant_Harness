# RESUMING.md · C Programming Assistant Harness

> **如果你是一个新 AI 接手这个项目，第一件事就是读这个文件。**
> 它会告诉你：项目是什么 / 我们做到了哪里 / 下一步做什么 / 怎么干活。

---

## 1. 30 秒速览

**项目**：C Programming Assistant Harness（CP-AH）— 面向 C 语言初学者的护栏优先 Coding Agent Harness。

**核心价值**：
- 能读学生代码、跑测试、找 valgrind 内存问题
- **绝不偷偷改学生代码**（HITL 强制人批）
- **绝不跑沙箱外命令**

**主角维度**（A 文件 §A.4-D 强制要求"选一个深入"）：**治理与护栏**
- 危险动作分类（L0/L1/L2/L3）
- HITL 状态机
- 进程级沙箱

**当前阶段**：brainstorming + writing-plans **已完成**，代码实现 **0/18 task**。

---

## 2. 必读文件清单（按顺序读）

| # | 文件 | 为什么读 |
|---|------|---------|
| 1 | `RESUMING.md` | 就是这个文件 |
| 2 | `AGENTS.md` | 项目级 AI 协作规则（硬性约束） |
| 3 | `docs/superpowers/specs/2026-07-07-cpah-design.md` | 14 章 SPEC，整个项目设计 |
| 4 | `docs/superpowers/plans/2026-07-07-cpah-plan.md` | 18 个 task 的具体实施步骤 |
| 5 | `AGENT_LOG.md` | 实施过程日志（持续更新） |
| 6 | `docs/sessions/2026-07-07-session-1.md` | 上次会话的完整记录 |
| 7 | `git log --oneline` | 看 commit 历史 |

**完整目录结构**：

```
.
├── AGENTS.md                 # 项目级 AI 规则（硬性）
├── AGENT_LOG.md              # 实施过程日志
├── RESUMING.md               # 这个文件（接手指南）
├── README.md                 # 项目介绍
├── LICENSE                   # MIT
├── .gitignore
├── docs/
│   ├── superpowers/
│   │   ├── specs/2026-07-07-cpah-design.md     # 14 章 SPEC
│   │   └── plans/2026-07-07-cpah-plan.md       # 18 task 实施计划
│   └── sessions/2026-07-07-session-1.md        # 上次会话记录
└── (代码目录在 Task 1 之后才创建)
```

---

## 3. 关键决策摘要

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **项目范围** | 只支持 C 语言 | 加 Java/Python 会让主角维度做不深 |
| **技术栈** | Python 3.11+ | LLM 生态最成熟 |
| **主角维度** | 治理与护栏 | 教学场景下"不主动改代码"是核心 feature |
| **LLM Provider** | OpenAI 兼容接口 | 一份代码适用 OpenAI/DeepSeek/硅基流动 |
| **沙箱实现** | 进程级（subprocess + ulimit + env 清理） | 跨平台、代码可控、可单测 |
| **HITL 实现** | 二维状态机 | 类似 Cursor agent mode，弹 WebUI 审批 |
| **测试策略** | TDD + MockLLM | 满足 A 文件 §A.4-C 的硬要求 |
| **License** | MIT | 最自由 |

---

## 4. 9 个 commit 是什么

```
4c30a66  docs(log): add T0.5 (writing-plans) and T0.6 (git push prep) entries
67f3e2c  docs(plan): implementation plan for CP-AH (18 tasks, TDD-driven)
4d00be5  docs: bootstrap AGENT_LOG.md with brainstorming session summary (T0)
6b2c36a  docs: add project-level AGENTS.md for cross-session AI handoff
0f15461  docs(spec): fix typo in §14 placeholder
71477d3  docs(spec): add §11 test strategy (TDD + MockLLM + 一键测试)
c170863  docs(spec): fill in SPEC sections 6-10 (architecture, data model, ...)
beab007  docs(spec): draft SPEC for CP-AH sections 1-5
e696127  chore: initialise repository with MIT license, .gitignore, README
```

**全是文档**——SPEC + PLAN + AGENTS + AGENT_LOG。**没有代码**。

---

## 5. 怎么"接续"（给下次 AI 的步骤）

**第 1 步：上下文恢复**
1. 读完这 4 个文件（AGENTS / SPEC / PLAN / AGENT_LOG）
2. 跑 `git log --oneline` 看历史
3. **问用户**："你想继续 Task 1 还是其它？"

**第 2 步：开始 TDD**

按 PLAN 里 Task 1-18 的顺序。每个 task：
1. 写失败的测试（红）→ commit `test(...): add failing test for ...`
2. 写最少实现（绿）→ commit `feat(...): implement ...`
3. 重构 → commit `refactor(...): ...`
4. **绝不允许** "先写实现再补测试"

**第 3 步：用 subagent**

按 Superpowers 工作流：
- 大多数 task 派一个新 subagent 跑
- 自己（lead AI）做评审、整合
- **注意**："新 subagent" 不等于"新对话"——同一会话内开 subagent 也是新 context

**第 4 步：每次 commit 后问用户**
- 让用户在 PowerShell 跑 `git push`（用 Steam++，已经验证过能通）
- 用户开加速器 → 推 → 关加速器（省流量）

---

## 6. 重要约束（必读）

按 A 文件 + 通用要求：

- ❌ **不能**用 LangChain / AutoGen / CrewAI / LlamaIndex agent 框架
- ❌ **不能**用 Claude Agent SDK / OpenAI Assistants API 的内建 agent loop
- ❌ **不能** hardcode API key
- ❌ **不能**让学生代码被偷偷改（这是护栏的核心）
- ✅ **必须** 写测试在写实现之前（TDD）
- ✅ **必须** 用 mock LLM 跑 CI（不依赖网络）
- ✅ **必须** 每次 commit 消息带 type 和 scope（Conventional Commits）
- ✅ **必须** 主循环 + 工具 + 治理 + 反馈 + 记忆 + 配置 6 个维度都有（不深也必须有）

---

## 7. 下次 AI 的第一个问题

无论你接手时多新，请**先问用户这个**：

> "我读完了 AGENTS / SPEC / PLAN / AGENT_LOG / git log。
> 当前 commit 是 `4c30a66`（push 成功），代码 0/18 task。
> 你想现在跑 Task 1 (项目骨架) 还是先做其它？"

如果用户说"跑 Task 1"，打开 `docs/superpowers/plans/2026-07-07-cpah-plan.md` 找到 Task 1，按那里的步骤走（TDD 红→绿→重构）。

如果用户说"我想 X 但不是 Task 1"，先停下来确认 X 是什么再行动。

**不要**：
- 不要凭印象改 SPEC（除非用户明确说）
- 不要从 Task 5/6/13 跳着做（顺序依赖：先有数据模型才能有分类器）
- 不要在 harness 核心里加 LangChain 之类高层框架

---

## 8. Steam++ 备忘

下次 push 时记得：
- Steam++ 默认是 TUN 模式（不需代理端口）
- 如果之前设过 git 代理，先 `git config --global --unset http.proxy`
- 如果 push 报 "remote contains work that you do not have locally"，跑 `git fetch` 后用 `--force-with-lease`

---

## 9. 联系信息

- **GitHub repo**: https://github.com/Methyl1644/C_Programming_Assistant_Harness
- **本地路径**: `D:\Desktop\Homework\AI_agent\C_Programming_Assistant_Harness`
- **课程**: NJU AI4SE 期末项目
- **作者**: Methyl-intelligent（大一大二，NJU 软件学院）

---

> 严格遵守本文件。违反约束 = bug。
> 任何时候有疑问，回到 SPEC.md / PLAN.md / AGENTS.md。
