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
       │                ── modify  ──→ [action_modified] → [awaiting_approval]
       ▼
   [running]  ── done  ──→ [agent_idle]
                  fail  ──→ [failed]
```

**沙箱 (Sandbox)**:

- **chdir**: 强制切到 `workspaces/{session_id}/`，所有相对路径解析基于此
- **路径白名单**: 任何 `..` 或绝对路径（除了白名单内的）→ 拦截
- **环境清理**: 清空 `HOME`、`PATH`、所有 `*_TOKEN`、`*_KEY` 环境变量
- **资源限制**: `ulimit -t 5`（CPU 5秒）、`ulimit -v 262144`（256MB 虚拟内存）
- **网络**: 防火墙规则拒绝所有出站（Linux 用 `nft`/iptables；Windows 用
  `netsh`），子进程继承；或更简单——命令黑名单 + 解析 LLM 想跑什么

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

（待写：组件图、数据流、错误处理、依赖）

---

## 7. 数据模型 (Data Models)

（待写：Action / Observation / Memory 三元组）

---

## 8. 凭据与分发 (Credentials & Distribution)

（待写：keyring 方案、Docker 镜像、CI/CD）

---

## 9. 技术选型与理由 (Tech Choices)

（待写：Python 3.11、FastAPI、OpenAI SDK、pytest）

---

## 10. 验收标准 (Acceptance Criteria)

（待写：每个功能"完成"的客观判定标准；含 §A.6 的机制演示要求）

---

## 11. 风险与未决问题 (Risks & Open Questions)

（待写）

---

## 12. 凭据威胁模型 (Credentials Threat Model)

（待写：与 §4.2 安全 对应）

---

## 13. 反思 (Reflection)

（待项目结束后在 REFLECTION.md 中写）

---

> **接下来要做的**：写完 §6-§12 的内容，然后 SPEC 自检 → 你审阅 → 进入
> writing-plans。
