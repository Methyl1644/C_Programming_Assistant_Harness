# SPEC · C Programming Assistant Harness (CP-AH)

> **Status**: 草稿（brainstorming 进行中）
> **Author**: Methyl-intelligent
> **Course**: 南京大学 AI4SE 期末项目
> **Last updated**: 2026-07-07

本 SPEC 须与以下两份文件**拼接**阅读：
- `AI4SE_Final_Project_通用要求.md`（课程通用要求）
- `AI4SE_Final_Project_A_Coding_Agent_Harness.md`（项目 A 的专项要求）

完整要求 = 通用要求 + A 文件 + 本文档。

---

## 1. Problem Statement (问题陈述)

### 1.1 Background

C 语言初学者写完一段代码，常常不知道错在哪。`gcc` / `valgrind` 的报错
信息对没系统学过编译原理的学生不友好；现有 LLM 工具（ChatGPT、Claude）
能讲清楚，但有两个隐患：

1. **AI 容易"自作主张"重写学生代码，跳过学习过程**——学生本来想的是
   "为什么我这段错了"，AI 直接丢回一段重写版，学生照抄，下次还会犯。
2. **AI 可能执行危险命令**（`rm -rf /`、`curl | bash`）——一次提示词注
   入或 LLM 幻觉，就会让 AI 误删学生作业或下载恶意代码。

### 1.2 Target users

- **Primary**: 南京大学《C 语言程序设计》大一学生，约 200 人/学期
- **Secondary**: 其他学校 C 语言初学者、自学者
- **Anti-user**: 资深 C 开发者（他们用 IDE + linter 即可，不需要 LLM 教）

### 1.3 Value proposition

> **一句话定位**：一个面向 C 语言初学者的 LLM 教学助手——能讲解你的
> 代码、跑你的测试、找你的内存泄漏，但 **绝不偷偷改你的代码**（必须
> 人批），也 **绝不跑沙箱外的命令**。

### 1.4 Why this project is non-trivial

- A 文件 §A.4-C 的"机制必须可单测"硬标准：每个核心机制替换为 mock LLM
  后仍能用确定性单元测试验证它工作。
- 教学场景下，**"不主动改代码" 是核心 feature**，不是缺失——这正是
  harness 价值所在的护栏。
- valgrind / gcc 输出解析是**结构化反馈**的好材料，能展示"反馈闭环"。

---

## 2. User Stories (≥ 5, INVEST)

| # | 故事 | INVEST 校验 |
|---|------|-------------|
| US-1 | 作为 C 语言初学者，我希望提交 `main.c` 后能问"这段代码哪里错了"，从而得到 **逐行的 gcc 错误解释**，而不是一个笼统的"编译失败"。 | I, N, V, E, S, T ✅ |
| US-2 | 作为 C 语言初学者，我希望 harness 能 **用测试用例跑我的程序** 并告诉我哪一组挂了，从而能区分"语法错"和"逻辑错"。 | I, N, V, E, S, T ✅ |
| US-3 | 作为 C 语言初学者，我希望 valgrind 的报告能被 **翻译成大白话**（"你在第 23 行把内存 free 了两次"），从而不用读 valgrind 的原始输出也能理解内存问题。 | I, N, V, E, S, T ✅ |
| US-4 | 作为 C 语言初学者，我希望 agent 提议的 **每一处代码改动我都能先看到 diff 再决定是否应用**，从而通过理解修改来学习，而不是盲目接受魔法修复。 | I, N, V, E, S, T ✅ |
| US-5 | 作为 C 语言初学者，我希望 agent **永远不能删除或覆盖我原始的 `.c` 文件**，从而即使 LLM 出错，我的作业也安全。 | I, N, V, E, S, T ✅ |
| US-6 | 作为 C 语言初学者，我希望 agent **能跨会话记住** 我正在学指针章节，从而解释能一直匹配我的水平，而不是反复讲基础。 | I, N, V, E, S, T ✅ |
| US-7 | 作为 C 语言初学者，我希望 agent **绝不能发起网络请求、也不能读我工作目录以外的文件**，从而我其他课的作业和个人数据不会被泄露。 | I, N, V, E, S, T ✅ |

---

## 3. Functional Spec (按模块)

Harness 内部分为 6 个模块，对应 A 文件 §A.1 的六个维度（决策 / 工具 /
记忆 / 治理 / 反馈 / 配置）。每个模块用 同样的格式描述。

> 注：6 个模块每个都必须有"可运行的最低实现"。**治理 (guardrails) 模块
> 选为主角维度，深度实现**。详见 §5。

### 3.1 模块一：决策 (Loop / LLM)

- **输入**: 用户的 goal（自然语言）、当前 context（已累积的对话历史 + 工具结果）
- **行为**: 调 LLM 一次，返回 `(text, action)`；组织 context，迭代直到 done / 步数耗尽
- **输出**: 最终 answer，或循环退出原因
- **边界**: `MAX_STEPS = 30`，超过即停；`MAX_TOKENS = 8000` 触发压缩
- **错误处理**: LLM 抛错 → 把错误回灌 context，让 agent 自己改换路径

### 3.2 模块二：工具 (Tools)

详见 §5.1 工具清单。

### 3.3 模块三：记忆 (Memory)

详见 §5.4。

### 3.4 模块四：治理 (Guardrails) ★ 主角维度

详见 §5.3。

### 3.5 模块五：反馈 (Feedback Sensors)

详见 §5.2。

### 3.6 模块六：配置 (Config)

- 规则文件 `AGENTS.md`（用户可写）
- 默认配置 `src/cpa_harness/config/defaults.yaml`（开发者维护）
- 启动时合并；规则文件覆盖默认值

---

## 4. Non-functional Requirements (非功能性)

### 4.1 性能
- 单次 LLM 调用端到端延迟 < 30s (P95)
- 反馈信号（编译+测试+valgrind） < 10s（P95）

### 4.2 安全 (凭据威胁模型)
- **威胁 1**: 真实 API key 入仓库 → 用 `keyring` 库 + `.env` 仅作本地 fallback
- **威胁 2**: agent 执行 `rm -rf` 误删 → 沙箱 chdir + 路径白名单
- **威胁 3**: agent 通过 `curl` 外泄代码 → 沙箱禁止网络 + 命令黑名单
- **威胁 4**: agent 静默改学生代码 → HITL 状态机强制人批
- **威胁 5**: 注入攻击（用户在 .c 文件里写"忽略之前指令"）→ 提示词分层隔离，文件内容作为 user 消息单条注入，不入 system prompt

### 4.3 可用性
- WebUI 单页应用，学生三步内提交代码（上传 → 提问 → 看反馈）
- CLI 单条命令 `cpa-harness run file.c --goal "..."`

### 4.4 可观测性
- 每轮循环生成一条 trace 记录：(text, action, observation)
- Session 结束 flush 到 `.traces/{session_id}.jsonl`

---

## 5. 领域与机制设计（A 文件 §A.5 强制）

> 本节是 A 文件 §A.5 的额外要求：明确回答"动作 / 反馈 / 危险 / 记忆"四类
> 机制，并说明如何编码实现（呼应 §A.4）。

### 5.1 动作/工具 (Actions / Tools)

| 工具 | 输入 | 输出 | 默认策略 | 触发场景 |
|------|------|------|---------|---------|
| `read_file(path)` | 路径 | 文件内容 | allow | 学生问"这段代码什么意思" |
| `list_dir(path)` | 路径 | 文件列表 | allow | 学生问"目录下有啥" |
| `search_code(pat, path)` | 模式+路径 | 匹配行 | allow | 学生问"我哪用了 malloc" |
| `run_feedback(target)` | 目标 .c | CE/WA/RE/TLE/MLE/AC 结构化报告 | allow | 学生问"我代码对不对" |
| `write_file(path, content)` | 路径+内容 | 写入结果 | **deny** (HITL) | 学生说"帮我改改" |
| `exec_command(cmd, cwd)` | 命令+工作目录 | stdout/stderr/exit_code | **deny** (HITL) | 学生问"为什么编译不过" |
| `take_note(note)` | 文本 | (终态) | allow | agent 主动记笔记 |
| `finish_tutoring(summary)` | 文本 | (终态) | allow | 教学环节结束 |

**实现**: 每个工具是一个 Python 函数，签名 `def tool(args: dict) -> dict`，
注册到 `ToolRegistry`。LLM 通过 OpenAI function calling schema 看到工具
描述（"名片"）。

### 5.2 客观反馈信号 (Feedback Sensors)

| 信号 | 触发条件 | 解析方法 | 回灌字段 |
|------|---------|---------|---------|
| **CE (Compile Error)** | gcc 退出非 0 | 正则 `(.+):(\d+):(\d+): (error|warning): (.+)` | `file, line, col, severity, msg, snippet` |
| **WA (Wrong Answer)** | 运行退出 0，输出与期望不符 | diff | `expected, actual, diff_first_line` |
| **TLE (Time Limit Exceeded)** | 运行超时（`timeout 2` 触发） | 收集 exit_code=124 | `time_used_s, limit_s` |
| **MLE (Memory Limit Exceeded)** | RSS 监控超 64MB / valgrind 报错 | RSS poll / valgrind 解析 | `rss_mb, leak_summary` |
| **RE (Runtime Error)** | 信号 SIGSEGV/SIGFPE/... | waitpid 拿 signal | `signal, backtrace` |
| **AC (Accepted)** | 全通过 | (无) | (无) |

**关键**: 这些**全部由代码解析**（re 模块 + waitpid），解析结果结构化
后回灌到 LLM。**不是**让 LLM 自己"看 stderr 然后说"——那是 A 文件
§A.4-B 禁止的"提示词版反馈"。

### 5.3 危险动作分类 (Dangerous Actions) ★ 主角维度

按严重度分四级，**全部由 `classify(action: Action) -> Level` 函数判定**：

| 级别 | 处理 | 例子 |
|------|------|------|
| **L0 总是禁止** | 直接拦截，无 HITL | `rm -rf /`、`mkfs`、`shutdown`、`dd if=/dev/zero` |
| **L1 默认拒绝** | HITL: "是否覆盖？" | `write_file` 覆盖学生已提交 `.c` 文件 |
| **L2 默认拒绝** | HITL: "是否执行？" | 任何 `exec_command`（包括 `gcc`） |
| **L3 默认允许** | 直接放行 | 读、搜索、运行反馈 |

**L2 动作还要再做一次细粒度分类**:

- **L2a** (白名单, 无 HITL): `gcc`、`make`、`./a.out`、`valgrind` —— 反馈必需
- **L2b** (白名单, 需 HITL): `ls`、`cat`、`head` —— 一般允许，但提示
- **L2c** (黑名单, 必拦): `curl`、`wget`、`bash <(...)`、`python3 -c "..."` 涉及外网

**HITL 状态机**:

```
   [agent_idle]
       │
       │ action → classify
       ▼
   [action_classified]  ── L0/L2c ──→ [blocked]  (回灌, continue)
       │
       │ L1 / L2b
       ▼
   [awaiting_approval]  ── approve ──→ [running]
       │                ── reject  ──→ [blocked]
       │                ── edit    ──→ [action_modified] → [awaiting_approval]
       ▼
   [running]  ── done  ──→ [agent_idle]
                  fail  ──→ [failed]
```

> "edit" 含义：学生在 WebUI 上能修改 agent 提议的 args（例如改
> `write_file` 的 content、改 `exec_command` 的 cmd），但不能修改
> 工具名 / 也不能"批准一个 deny 动作"。修改后回到 `awaiting_approval`
> 由学生再点一次 approve。

**沙箱 (Sandbox)**:

- **chdir**: 强制切到 `workspaces/{session_id}/`，所有相对路径解析基于此
- **路径白名单**: 任何 `..` 或绝对路径（除了白名单内的）→ 拦截
- **环境清理**: 清空 `HOME`、`PATH`、所有 `*_TOKEN`、`*_KEY` 环境变量
- **资源限制**:
  - Linux/macOS: `resource.setrlimit(RLIMIT_CPU, 5)`、`RLIMIT_AS = 256MB`
  - Windows: **初版（v0.1）**仅做 chdir + env cleanup + 10s timeout；job object
    限制（`pywin32` 的 `win32job` 模块）和 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`
    列入 v0.2 路线。Job objects 是 Windows 上 rlimit 的等价物——`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`
    确保子进程随父进程死亡。**沙箱接口统一，但实现分平台**——通过
    `SandboxBackend` Protocol 抽象，单元测试用 in-memory backend。
  - **初版不含 creationflags 的原因**：避免硬依赖 pywin32；v0.1 优先跑通 mock-driven 单测
    路径，CPU/内存硬限制属于"防御深度"增强而非"安全屏障"必须项（网络/路径拦截才是）
- **网络**: 防火墙规则拒绝所有出站（Linux 用 `nft`/iptables；Windows 用
  `netsh`），子进程继承；或更简单——命令黑名单 + 解析 LLM 想跑什么
- **单文件 vs 多文件**: `run_feedback(target)` 的 `target` 可以是单文件
  路径，也可以是目录路径（递归编译所有 `.c`）。这是 §10.1 AC-1 的前提。

### 5.4 记忆 (Memory)

| 类型 | 存储 | 检索时机 | 首版实现 | 升级路径 |
|------|------|---------|---------|---------|
| 班级约定 | `memory/class.yaml` | 启动 | YAML 读 | 不变 |
| 学生历史 | `memory/{user_id}.json` | 每轮预检索 | 全文 substring 匹配 | SQLite + FTS5 |
| 当次笔记 | 内存 dict | 循环内 `take_note` | dict | 同上 |
| 失败模式库 | `memory/known_bugs.json` | 反馈时相似度匹配 | TF-IDF（手写 mini） | 嵌入向量库 |

**自己实现 `MemoryStore` 类**，不接框架 memory 层（A 文件 §A.4-D 对"以
记忆为重点"的要求；本项目以治理为重点，但记忆仍需自己实现，理由是它
跨过 A 文件 §A.4-C 的单测要求）。

---

## 6. 系统架构 (Architecture)

### 6.1 组件图

```
                   ┌────────────────────────────────────────┐
                   │              WebUI (FastAPI)            │
                   │  浏览器 SPA + WebSocket (HITL 审批)     │
                   └──────────────────┬─────────────────────┘
                                      │ HTTP/WS
                                      │
        ┌─────────────────────────────▼─────────────────────────────┐
        │                   Harness 核心（自实现）                  │
        │                                                            │
        │   ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │
        │   │ AgentLoop  │→ │ LLM Client │→ │ LLM Provider     │    │
        │   │  (主循环)  │  │ (抽象层)   │  │ (OpenAI/Claude/  │    │
        │   │            │  │            │  │  MockLLM)        │    │
        │   └─────┬──────┘  └────────────┘  └──────────────────┘    │
        │         │                                                 │
        │         ▼                                                 │
        │   ┌────────────────────┐   ┌──────────────────────┐      │
        │   │  ToolRegistry      │   │  Action Classifier   │      │
        │   │  (8 个工具)         │   │  (L0/L1/L2/L3 + 细)   │      │
        │   └─────┬──────────────┘   └──────────┬───────────┘      │
        │         │                              │                  │
        │         │         ┌────────────────────┘                  │
        │         ▼         ▼                                       │
        │   ┌──────────────────────────────────────┐                │
        │   │     Guardrail Pipeline                │                │
        │   │  Policy → Sandbox → HITL → Hooks      │                │
        │   └──────────────┬───────────────────────┘                │
        │                  │                                        │
        │   ┌──────────────▼───────────────────────┐                │
        │   │  Feedback Sensors (gcc/valgrind/diff) │                │
        │   └──────────────┬───────────────────────┘                │
        │                  │                                        │
        │   ┌──────────────▼───────────────────────┐                │
        │   │  MemoryStore (4 层) + Tracer          │                │
        │   └──────────────────────────────────────┘                │
        └────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │  外部世界             │
                          │  - OpenAI / Claude   │
                          │  - gcc / valgrind    │
                          │  - keyring           │
                          │  - workspaces/       │
                          └─────────────────────┘
```

### 6.2 数据流（一轮循环）

```
                ┌──────────────────────────────────────┐
                │  上一轮的 (text, action, observation) │
                └──────────────────┬───────────────────┘
                                   ▼
              ┌─────────────────────────────────────────┐
              │  ContextBuilder 拼装                    │
              │  = system + rules + memory.read +       │
              │    retriever.retrieve + 历史            │
              └──────────────────┬──────────────────────┘
                                 ▼
                ┌────────────────────────────────────┐
                │  LLM Provider.chat(messages, menu) │
                │  → (text, action, tool_call?)      │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  决策入上下文  +  Tracer.record     │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  action.type == "done"?  → 退出     │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  ActionClassifier.classify(action) │
                │  → L0/L1/L2/L3  (含 L2a/b/c)       │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  L0 / L2c → 拦截，回灌，继续         │
                │  L1 / L2b → HITL 等审批             │
                │  L2a / L3 → 放行                    │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  Sandbox.run(tool, args)            │
                │  chdir + ulimit + env 清理           │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  Feedback Sensors 解析产物           │
                │  (若 changed_code 触发)              │
                └──────────────────┬─────────────────┘
                                   ▼
                ┌────────────────────────────────────┐
                │  observation 入上下文，下一轮         │
                └────────────────────────────────────┘
```

### 6.3 错误处理

| 错误 | 处理 |
|------|------|
| LLM 调用超时 / 5xx | 重试 2 次，仍失败 → 把错误信息回灌 context，让 agent 决定继续还是退出 |
| LLM 返回非法 JSON | 解析失败 → 把"原始字符串 + 解析错误"回灌，让 agent 改换格式 |
| 沙箱内 subprocess 崩 | exit_code + signal 收集到 observation，不算 harness 错 |
| 学生上传超大文件 (>1MB) | 启动时拒绝，不进入循环 |
| WebUI 断连 | CLI 模式下回退到默认 deny（拒绝所有 L1/L2 动作） |
| keyring 拿不到 key | 引导用户首次录入；非交互环境下报 fatal 退出 |

### 6.4 外部依赖

- **OpenAI Python SDK** (`openai>=1.0`)：调用 LLM
- **keyring** (`keyring>=24`)：跨平台凭据存储
- **FastAPI** + **uvicorn**：WebUI
- **pydantic**：数据模型 / schema
- **pytest** + **pytest-asyncio**：测试
- **ruff** + **mypy**：lint / 类型检查
- **Docker**（可选）：分发形态

---

## 7. 数据模型 (Data Models)

### 7.1 Action (Pydantic model)

```python
class Action(BaseModel):
    type: Literal["call_tool", "use_skill", "take_note",
                  "finish_tutoring", "done"]
    tool: str | None = None
    args: dict = {}
    note: str | None = None
    summary: str | None = None
```

### 7.2 Observation

```python
class Observation(BaseModel):
    tool: str
    result: str          # 工具原始输出
    exit_code: int | None = None
    signal: int | None = None
    feedback: FeedbackReport | None = None   # 见 7.3
    duration_ms: int
```

### 7.3 FeedbackReport (六类信号)

```python
class FeedbackReport(BaseModel):
    verdict: Literal["AC", "CE", "WA", "TLE", "MLE", "RE"]
    file: str
    line: int | None = None
    col: int | None = None
    severity: Literal["error", "warning"] | None = None
    msg: str
    snippet: str | None = None        # CE: 前后 3 行
    expected: str | None = None       # WA
    actual: str | None = None         # WA
    signal_name: str | None = None    # RE
    rss_mb: float | None = None       # MLE
    leak_summary: str | None = None   # MLE / valgrind
```

### 7.4 MemoryRecord

```python
class MemoryRecord(BaseModel):
    user_id: str
    kind: Literal["note", "history", "lesson", "preference"]
    content: str
    created_at: datetime
    tags: list[str] = []
```

### 7.5 关系

- 一轮循环 = (text, action, observation) 三元组
- 一个 session = 多轮三元组 + 起始 goal
- 一次跨会话记忆 = 多个 MemoryRecord 关联同一 user_id

---

## 8. 凭据与分发 (Credentials & Distribution)

### 8.1 凭据存储（威胁模型见 §12）

| 形态 | 实现 | 适用 |
|------|------|------|
| **主方案** | `keyring` 库（macOS Keychain / Windows Credential Manager / Linux Secret Service） | 全平台默认 |
| **Fallback** | `.env` 文件（明确警告：明文） | 无 GUI 的服务器 / CI |
| **CI 特殊** | 环境变量（来自 CI secret store） | GitHub Actions / GitLab CI |

### 8.2 首次运行引导

- 启动时若拿不到 `OPENAI_API_KEY`，进入交互式引导
- CLI: `cpa-harness setup` → 隐藏输入 → 写入 keyring
- WebUI: 首次访问设置页 → 同上
- 用户可执行 `cpa-harness key status` / `update` / `clear`
- **状态查询时绝不回显明文**

### 8.3 分发形态

**主形态: Docker 镜像**（满足通用要求 §3.2"单条 docker run 可启动"）

```bash
docker build -t cpa-harness .
docker run -it \
  -e CPAH_OPENAI_API_KEY_FILE=/run/secrets/key \
  -v $(pwd)/workspaces:/app/workspaces \
  -p 8000:8000 \
  cpa-harness
```

**次形态: PyPI 包**

```bash
pip install cpa-harness
cpa-harness serve   # 启动 WebUI
```

README 须写清：获取方式、运行命令、key 在目标机如何安全配置、已知限制（平台 / 架构 / 依赖前提）。

### 8.4 云部署

候选：阿里云 / 腾讯云（学生免费额度）+ Docker 镜像。

部署架构：
- 1 台轻量级 ECS（2 vCPU / 2GB）跑 WebUI
- keyring 改为读环境变量（云上无系统 keychain）
- 反向代理 nginx + HTTPS

---

## 9. 技术选型与理由 (Tech Choices)

| 选择 | 选项 | 决定 | 理由 |
|------|------|------|------|
| 语言 | Python 3.11+ / TypeScript / Go / Rust | **Python 3.11** | LLM 生态最成熟（OpenAI SDK、pydantic）；学生有过一点 Python 基础；与 §A.4 强调的"自己实现 harness"不冲突——harness 本身不依赖任何 agent 框架 |
| Web 框架 | Flask / FastAPI / Django | **FastAPI** | 异步、WebSocket 一等公民、pydantic 集成、auto OpenAPI 文档 |
| LLM 客户端 | openai-sdk / langchain / 直接 HTTP | **openai-sdk** | 官方 SDK、覆盖 OpenAI 兼容接口（DeepSeek / 硅基流动 / Azure） |
| LLM Provider 抽象 | 不抽象 / 自己写 | **自己写**（`LLMProvider` Protocol + `MockLLM` / `OpenAILLM`） | A 文件 §A.4-A 硬要求"可注入 mock"；可单测 |
| 测试框架 | pytest / unittest | **pytest** | 简洁、fixture 强大、CI 标准 |
| 沙箱 | Docker / chroot / 进程级 | **进程级**（subprocess + chdir + ulimit + 命令黑名单） | 跨平台、代码可控、满足 A 文件 §A.4-C 的单测要求 |
| 凭据 | 环境变量 / keyring / 自建 | **keyring 优先 + .env fallback** | 跨平台明文风险最小 |
| 进程内分发 | Docker / PyPI / Homebrew | **Docker + PyPI 双形态** | Docker 满足"一条命令跑起来"；PyPI 满足 §3.2 多种形态 |
| Open Design | 必填 | **不适用**（CLI 后端项目，豁免） | §3.6 允许纯 CLI / 纯后端项目豁免 |

---

## 10. 验收标准 (Acceptance Criteria)

每条标准都是**客观、可验证**的——评阅人跑一遍就知道过没过。

### 10.1 功能验收

| ID | 标准 | 验证方式 |
|----|------|---------|
| AC-1 | 学生上传 `main.c`，30s 内拿到 CE 报告（精确到行号） | 端到端 demo：故意写一段错代码，验证 |
| AC-2 | 学生代码有内存泄漏，10s 内拿到 MLE 报告 | 端到端 demo：故意 `malloc` 不 `free`，验证 |
| AC-3 | 学生在 WebUI 看到 agent 提议的 diff，**必须点 "Approve" 才会写入** | 端到端 demo：拒绝 → 文件未变；批准 → 文件改变 |
| AC-4 | agent 试图跑 `rm -rf /`，**harness 直接拦截**，不弹 HITL | 单元测试：构造危险 action，断言被拦 |
| AC-5 | agent 试图读 `/etc/passwd`，**harness 拦截** | 单元测试 |
| AC-6 | agent 提议的 `write_file` 覆盖学生原 `.c`，**WebUI 弹 L1 HITL** | 端到端 demo |
| AC-7 | LLM 给出错误答案（WA），agent 收到反馈后**下一轮调整代码** | 端到端 demo + 单元测试 |
| AC-8 | 同一 user_id 第二次提问，agent **记得上次讨论的概念** | 端到端 demo（重启 server 后再问） |

### 10.2 A 文件 §A.6 机制演示（必交）

提交一个**确定性可重复**的演示脚本，覆盖：

1. **护栏拦截** — 注入危险命令，断言 harness 拦截
2. **反馈闭环** — 注入失败，反馈回灌后 agent 改变下一步
3. **主角维度（治理）的确定性行为** — 例如：HITL 状态机在拒绝时正确回退、不写入、不污染上下文

### 10.3 单元测试验收

- 替换为 `MockLLM` 后，所有 harness 核心机制仍可通过 pytest
- 覆盖率 ≥ 80%（`pytest --cov=cpa_harness`）
- 不依赖网络、不依赖真实 LLM
- 详细测试策略与一键测试命令见 §11

### 10.4 文档验收

- `SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md`、`AGENT_LOG.md`、`REFLECTION.md` 全部存在
- README 含：项目简介 / 安装 / 运行 / 分发 / 目录结构 / 安全边界
- CI 中存在 `unit-test` job，且最后一次跑必须 pass

### 10.5 部署验收

- `docker build` 成功
- `docker run` 启动后 WebUI 可访问
- 公网 URL 可在截止前访问

---

## 11. 测试策略 (Test Strategy)

> **本节是 A 文件 §A.4-C 与通用要求 §3.6 的具体落地**：TDD 强制 +
> 一键测试 + 机制可单测。

### 11.1 测试金字塔

```
         ╱  ╲
        ╱ E2E ╲         ← 端到端（WebUI/CLI 真跑）
       ╱────────╲
      ╱ 集成测试  ╲       ← 多个模块协作（带 mock LLM）
     ╱──────────────╲
    ╱   单元测试      ╲   ← 单个函数/类（带 mock LLM）
   ╱════════════════════╲
```

| 层 | 数量 | 速度 | 覆盖什么 | 是否需要真 LLM |
|---|------|------|---------|---------------|
| **单元** | 多数 | < 1s / 个 | ActionClassifier、HITL 状态机、FeedbackParser、MemoryStore、SandboxBackend | 不需要（MockLLM） |
| **集成** | 一些 | 几秒 | 完整一轮 loop、危险动作被拦截的端到端路径 | 不需要（MockLLM 编程回放） |
| **E2E** | 少量 | 30s+ | WebUI 上传、CLI 一条命令跑 | **需要**真 LLM（仅手动跑，不进 CI） |

**核心原则**：CI 跑单元 + 集成（不依赖网络、可离线），E2E 单独跑
（手测或 nightly job）。

### 11.2 TDD 流程（每个 task 强制执行）

按 `test-driven-development` 技能的标准三步：

1. **红 (Red)**: 写一个失败的测试，明确表达"这个功能应该如何行为"
   - 例如：`test_classify_blocks_rm_rf_root()` 断言
     `classify("rm -rf /")` 返回 `Level.BLOCKED`
   - 运行 → 看到 FAIL（红）
   - **commit**: `test(guardrail): add failing test for rm -rf / classification`
2. **绿 (Green)**: 写**最少代码**让测试通过
   - 加一个正则匹配 `/rm\s+-rf\s+\//` 返回 `BLOCKED`
   - 运行 → 看到 PASS（绿）
   - **commit**: `feat(guardrail): implement L0 pattern matcher for rm -rf`
3. **重构 (Refactor)**: 改进代码可读性、可扩展性，**测试保持绿**
   - 把正则提到 `L0_PATTERNS` 常量、加注释
   - 运行 → 仍然 PASS
   - **commit**: `refactor(guardrail): extract L0 patterns to constant`

**绝对禁止** "先写实现再补测试"——一旦发现，task 视为未完成。

### 11.3 MockLLM：单测能不依赖真 LLM 的关键

`LLMProvider` 是个 Protocol。`MockLLM` 是其中一个实现，**接收预编程
的对话序列**，每轮按序列返回下一个 `(text, action)`：

```python
class MockLLM(LLMProvider):
    def __init__(self, script: list[MockTurn]):
        self.script = script
        self.index = 0

    def chat(self, messages, menu) -> tuple[str, Action]:
        turn = self.script[self.index]
        self.index += 1
        if turn.raise_:
            raise turn.raise_
        return turn.text, turn.action
```

测试时：

```python
def test_guardrail_blocks_dangerous_command():
    mock = MockLLM(script=[
        MockTurn(text="我先看看", action=Action(
            type="call_tool", tool="exec_command",
            args={"cmd": "rm -rf /", "cwd": "/tmp"})),
    ])
    h = build_harness(llm=mock, ...)
    h.run("清理一下")
    assert mock.index == 1   # agent 一轮就拿到拦截结果
    # 验证：拦截原因被回灌、文件未删
```

**关键好处**：测试**确定性**——同一个 script，每次跑结果一样，CI 不会
偶发失败。

### 11.4 一键测试命令

| 形态 | 命令 | 跑什么 |
|------|------|--------|
| **开发** | `make test` 或 `pytest` | 单元 + 集成 |
| **看覆盖率** | `make test-cov` 或 `pytest --cov=cpa_harness --cov-report=term-missing` | 单元 + 集成 + 覆盖率 |
| **特定模块** | `pytest tests/test_guardrail.py` | 单文件 |
| **特定函数** | `pytest tests/test_guardrail.py::test_classify_blocks_rm_rf_root` | 单测点 |
| **E2E（手动）** | `make e2e` 或 `pytest tests/e2e/ --run-e2e` | 真 LLM，需 `OPENAI_API_KEY` |

`Makefile` 是项目入口，**初版 PLAN 第一个 task 就是建它**。

### 11.5 机制演示（满足 A 文件 §A.6）

提交 `tests/demo_mechanisms.py`，覆盖：

1. **护栏拦截** — `MockLLM` 编程发出 `rm -rf /`，断言
   `ActionClassifier.classify` 返回 `BLOCKED`，harness 把"被拦截"
   回灌，下一轮 LLM 改换策略
2. **反馈闭环** — `MockLLM` 编程先发 `write_file` 写错代码；`MockSandbox`
   返回 `FeedbackReport(verdict=CE, line=5)`；下一轮 `MockLLM` 编程发
   `write_file` 修第 5 行；断言第二次 `write_file` 的 content **确实改了
   第 5 行**（不是别的位置）
3. **主角维度（治理）的确定性行为** — `MockLLM` 发 `write_file` 覆盖
   学生原 `.c`；断言 harness 进入 `awaiting_approval` 状态；学生
   `reject`；断言 harness 进入 `blocked` 状态、文件**未变**、context
   被回灌"被学生拒绝"

演示**必须**用 mock 跑，不依赖网络，CI 里必过。

### 11.6 覆盖率策略

- **必须 ≥ 80%**: `pytest --cov=cpa_harness --cov-fail-under=80`
- **重点覆盖**（90%+）:
  - `cpa_harness.guardrails` (主角维度)
  - `cpa_harness.feedback` (解析逻辑)
  - `cpa_harness.tools` (工具分发)
- **可适度降低**（60%+）:
  - `cpa_harness.web` (FastAPI 路由层，集成测试覆盖)
  - `cpa_harness.cli` (入口，集成测试覆盖)

### 11.7 测试与实现的对应关系

每个 §5/§6 设计的机制，**在写实现之前**就要在 `tests/` 下有对应
的测试文件存在（即使它是红的状态）：

| 机制 | 测试文件 |
|------|---------|
| ActionClassifier | `tests/test_guardrail_classifier.py` |
| HITL 状态机 | `tests/test_hitl_state_machine.py` |
| Sandbox (chdir + ulimit) | `tests/test_sandbox.py` |
| Sandbox 跨平台 (job object) | `tests/test_sandbox_windows.py` (条件 skip) |
| gcc 错误解析 | `tests/test_feedback_gcc.py` |
| valgrind 解析 | `tests/test_feedback_valgrind.py` |
| MemoryStore | `tests/test_memory_store.py` |
| AgentLoop (完整一轮) | `tests/test_agent_loop.py` |
| 机制演示 | `tests/demo_mechanisms.py` |

---

## 12. 风险与未决问题 (Risks & Open Questions)

- **R1**: LLM 在 `function_calling` 模式下偶发不调工具、直接给文本答
  案 → 风险：循环中规中矩触发不到反馈；缓解：让 `MockLLM` 测试覆盖
  这种 case
- **R2**: Windows 上 `pywin32` 安装链路不稳 → 缓解：沙箱接口已抽象为
  Protocol，沙箱在 Windows 上的实现可后期插入；初版可仅在 Linux 跑
  E2E
- **R3**: 阿里云 / 腾讯云学生额度到 2026 年政策可能调整 → 缓解：保留
  Docker 本地运行作为基础保障
- **R4**: OpenAI 兼容接口的各家模型对 function calling 支持差异 → 缓
  解：选 1-2 家主推模型（OpenAI 官方 + DeepSeek），不强求兼容所有
- **R5**: 学生同时上传 10 个文件 → 单测覆盖少量文件场景即可，大规模
  E2E 不在首版范围

---

## 13. 凭据威胁模型 (Credentials Threat Model)

与 §4.2 / §8 对应。

| 威胁 ID | 威胁 | 攻击路径 | 对策 | 残留风险 |
|---------|------|---------|------|---------|
| T-1 | 真实 API key 入 Git 仓库 | 写代码时把 key 粘进字符串字面量 | pre-commit hook 跑 `gitleaks`；CI 跑 `gitleaks detect`；`.env` / `*.key` 在 `.gitignore` | 误用环境变量名打印到日志 |
| T-2 | keyring 拿不到 key（首次运行） | 学生第一次启动 | 引导流程：`cpa-harness setup` 隐藏输入；明确写明"key 存在哪、谁能看" | 学生误把 key 通过不安全的渠道传同学 |
| T-3 | `.env` 文件泄漏（备选方案） | 部署到云上时挂错目录 | Dockerfile 不带 `.env`；部署时用 `docker run -e KEY=...` 或 docker secret | 中间人能看到 env |
| T-4 | 凭据查询时回显明文 | `cpa-harness key status` 写错 | 状态只显示前缀（`sk-xxxx...abcde`），绝不打印完整 key | 社工骗完整 key |
| T-5 | CI 日志泄漏 secret | CI 配错把 env 打印出来 | CI job 不打印 `$OPENAI_API_KEY`；用 `::add-mask::` 标记 | 第三方包未 mask 误打 |
| T-6 | 进程 fork 泄漏 key 给子进程 | sandbox 子进程继承 env | sandbox 启动前 `os.environ` 清掉 `*_KEY` / `*_TOKEN` | 学生未察觉子进程也是 harness 启动的 |

**对策落地位置**（每条都要有代码 + 测试）：

- T-1: `tests/test_no_hardcoded_secrets.py` + pre-commit + CI
- T-2: `src/cpa_harness/credentials/setup.py`
- T-3: `.dockerignore` + Dockerfile 校验
- T-4: `src/cpa_harness/credentials/status.py` + 单测
- T-5: `.gitlab-ci.yml` 不 `set -x`，敏感变量用 `::add-mask::`
- T-6: `src/cpa_harness/sandbox/env.py` + 沙箱单测

---

## 14. 反思 (Reflection)

> 反思报告在 `REFLECTION.md` 中独立写，§14 仅放标题占位。
> 反思内容按通用要求 §五的"反思报告（REFLECTION.md）建议内容"展开。

---
