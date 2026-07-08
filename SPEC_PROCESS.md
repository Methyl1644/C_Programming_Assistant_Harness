# SPEC_PROCESS.md · C Programming Assistant Harness

> **用途**：记录 CP-AH 项目从模糊想法到 SPEC+PLAN 的全过程证据。按
> 通用要求 §4.4 + §4.5，本文件是必交的过程文档。
>
> **当前状态**：§4.4 部分已写（基于 session-1 + AGENT_LOG 提炼）；
> §4.5 部分待冷启动报告回填。
>
> **作者**：Methyl-intelligent，NJU 软件学院大一
> **日期**：2026-07-07
> **主开发 agent**：OpenCode (claude-opus-4.5)
> **关联文件**：
> - SPEC：`docs/superpowers/specs/2026-07-07-cpah-design.md`
> - PLAN：`docs/superpowers/plans/2026-07-07-cpah-plan.md`
> - session 记录：`docs/sessions/2026-07-07-session-1.md`
> - 实施日志：`AGENT_LOG.md`

---

## 1. 5 轮关键 brainstorming 迭代（§4.4 必填）

> 按 §4.4："至少 3 轮关键迭代的对话节选与你的处理决策"。这里
> 提炼 5 轮，**每轮**记录：议题 / AI 提了什么 / 我做了什么决策 / 为什么。

### 迭代 1 · 项目类型选择（A vs B）

| 字段 | 内容 |
|------|------|
| **议题** | 选 A 类（Coding Agent Harness）还是 B 类（应用类）？ |
| **AI 提议** | A 文件是首选，B 文件"非首选"；建议直接选 A |
| **我的决策** | 选 A |
| **理由** | A 文件虽然"难"，但护栏机制能直接服务教学场景（"不主动改学生代码"是核心 feature）；B 类需要自己造一个真实问题，**而教学就是真实问题** |
| **反思** | AI 这次没给我选项，直接按"首选"推荐——这其实是把决策责任又推回来了。我应当自己对比 A vs B 的"评估重心"差异（A 看机制深度，B 看工程完成度），而不是直接接受推荐 |

### 迭代 2 · 范围收缩（C only vs C+Java）

| 字段 | 内容 |
|------|------|
| **议题** | 是否同时支持 C 和 Java？ |
| **AI 提议** | "加 Java 扩展性更好" |
| **我的决策** | **拒绝**。只支持 C |
| **理由** | A 文件 §A.4-D 要求"选一个维度深入"。加 Java 意味着 LLM 工具描述、反馈解析、HITL 模式都要双份——**深度被稀释**。C 语言的 valgrind 反馈已经够丰富了 |
| **后续验证** | PLAN 18 task 已经够多（3337 行），加 Java 估计要 28 task——验证决策正确 |
| **反思** | 这是我**主动推翻 AI 建议**最关键的一次。教训：AI 给"扩展性"建议时，**默认它在用工程惯性思考**（"加 X 看起来更通用"），不一定从你的主角维度出发 |

### 迭代 3 · 主角维度选择（6 维度中选哪个深入）

| 字段 | 内容 |
|------|------|
| **议题** | A 文件 §A.1 列了 6 个维度：决策 / 工具 / 记忆 / 治理 / 反馈 / 配置。要选一个深入 |
| **AI 提议** | 列了"治理 / 反馈闭环 / 扩展（多 agent 编排）"三个推荐 |
| **我的决策** | **选治理与护栏** |
| **理由** | 教学场景下，"不主动改学生代码"是核心 feature 而不是缺失——这恰好是治理维度的核心。**A 文件 §A.4-B 强调"机制必须可单测"**——治理（危险动作分类 + HITL + 沙箱）天然由代码组成，最容易满足硬要求 |
| **取舍** | 反馈闭环（gcc/valgrind 解析）也很有深度，但已经包含在治理里了（CE/MLE 是治理的输入信号），单独做"反馈"会有重叠 |
| **后续验证** | SPEC §5.3 写危险动作分类 + HITL 状态机 + 沙箱 = 3 大块，全部深度实现 |
| **反思** | AI 列的三个推荐里我没选它的第一推荐"反馈闭环"——但理由不是"AI 错了"，而是"我已经选了治理，反馈是治理的一部分"。**这种情况下 AI 的推荐是"另一个好选项"，不是"错选项"** |

### 迭代 4 · 凭据方案（keyring 优先 vs .env 优先）

| 字段 | 内容 |
|------|------|
| **议题** | 凭据怎么存？keyring 优先还是 .env 优先？ |
| **AI 提议** | "用环境变量最简单" |
| **我的决策** | **拒绝 AI 提议**。keyring 优先 + .env fallback + 环境变量最后手段 |
| **理由** | 环境变量会进 shell history、CI 日志、`/proc/*/environ`——**全部明文**。keyring 走系统钥匙串（Windows Credential Manager / macOS Keychain / Linux Secret Service），明文风险最小。`.env` 文件作为 fallback 但要明确警告"明文风险" |
| **后续验证** | 通用要求 §3.1 明确要求"至少实现一种安全存储"——keyring 是首选方案 |
| **反思** | AI 提"环境变量最简单"是因为它**默认你在跑 demo**，不是生产环境。**生产环境的凭据治理是 A 文件 §4.2 的硬要求**，AI 没强调。教训：AI 提"最简单"方案时，要追问"生产环境下还简单吗" |

### 迭代 5 · 沙箱实现（Docker vs 进程级）

| 字段 | 内容 |
|------|------|
| **议题** | 沙箱用什么实现？Docker 容器、chroot、还是进程级？ |
| **AI 提议** | "Docker 隔离性最好" |
| **我的决策** | **拒绝**。选进程级（subprocess + chdir + ulimit + 环境清理） |
| **理由** | Docker 引入了**外部依赖**（学生机器上可能没装 Docker；CI 跑测试也更慢）。进程级沙箱：(1) 跨平台（Windows / Linux / macOS）；(2) 代码可控（200 行 Python）；(3) **可单测**（MockSandbox 直接 mock）——满足 A 文件 §A.4-C 硬要求 |
| **风险** | Windows 上 `pywin32` job object 集成可能不稳（已记为 R2 风险）。**缓解**：沙箱接口 `SandboxBackend` 已抽象为 Protocol，初版可仅在 Linux 跑 E2E |
| **反思** | 这次决策**有得有失**。得：避开 Docker 依赖，更易单测。失：Windows 上 CPU/内存硬限制难做（plan Task 7 已用 job object 折中）。**算工程 trade-off，不算错** |

---

## 2. AI 建议采纳 / 推翻总结（§4.4 必填）

### 2.1 采纳清单（AI 提了且我接受）

| # | 建议 | 出处 | 接受理由 |
|---|------|------|---------|
| 1 | 选 A 类（Coding Agent Harness）| brainstorming 阶段 | 护栏机制直接服务教学场景 |
| 2 | Python 3.11 | 选型阶段 | LLM 生态最成熟（OpenAI SDK / pydantic）|
| 3 | OpenAI 兼容接口 | 选型阶段 | 一份代码适用 OpenAI/DeepSeek/硅基流动 |
| 4 | FastAPI 框架 | 选型阶段 | 异步 / WebSocket 一等公民 / pydantic 集成 |
| 5 | TDD 严格 | 工具流 | A 文件硬要求 |
| 6 | MockLLM 跑所有 CI 测试 | 工具流 | 不依赖网络，可离线 |
| 7 | HITL 用状态机 | 机制设计 | 课程 §4.5 类比 Cursor agent mode |
| 8 | CLI + WebUI 双形态 | 分发 | 通用要求 §3.4 至少 3 个模块 |
| 9 | Docker + PyPI 双分发 | 分发 | "单条 docker run 可启动" + "pip install 可装" |
| 10 | MIT License | 选型 | 最自由，学生项目首选 |

### 2.2 推翻/修正清单（AI 提了但我改了）

| # | AI 建议 | 我改成什么 | 原因 |
|---|---------|-----------|------|
| 1 | "加 Java 范围更好" | **只做 C** | 深度优先，Java 会稀释主角维度 |
| 2 | "环境变量存 key 最简单" | **keyring 优先 + .env fallback + env var 最后** | 安全优先，环境变量全部明文 |
| 3 | "Docker 沙箱最安全" | **进程级沙箱** | 跨平台 / 可单测 / 不引外部依赖 |
| 4 | "用 LangChain 跑 agent" | **自己写主循环** | A 文件 §A.4-A 硬禁止高层 agent 框架 |
| 5 | "GitHub Actions 跑 CI" | **GitLab CI**（课程要求 unit-test job 名字）| 通用要求 §五明确 `.gitlab-ci.yml` + `unit-test` job |
| 6 | "随机选一个 LLM 供应商" | **OpenAI 兼容接口（多供应商一份代码）** | DeepSeek / 硅基流动 / OpenAI 都能用 |

### 2.3 模式总结

观察上面 11 条 + 6 条，可以提炼 AI 协作的**三个常见模式**：

1. **"AI 推通用方案"**（加 Java、Docker）→ 总是和"主角维度深度"冲突。**对策**：每次 AI 提"扩展性更好"时，强制问自己"这会稀释主角维度吗"
2. **"AI 推简单方案"**（环境变量、最少代码）→ 总是和"生产环境"冲突。**对策**：每次 AI 提"最简单"时，强制问"生产环境下还简单吗"
3. **"AI 推流行方案"**（LangChain、GitHub Actions）→ 总是和"课程硬约束"冲突。**对策**：每次 AI 提"业界标准"时，先查 A 文件 / 通用要求里有没有硬约束

---

## 3. brainstorming 技能反思（§4.4 必填）

### 3.1 做得好

- **追问了 8 轮**，从项目类型到主角维度到技术栈——每轮都逼我"想清楚再走"
- **明确要求至少 5 个用户故事 + INVEST 校验**——避免了"伪需求"
- **SPEC 14 章结构是它给的**——避免了我漏写"威胁模型"或"测试策略"
- **每次 commit 前要求"自检 commit message"**——避免了"先写了一大段再补 commit"的混乱

### 3.2 让人不满

- **没主动要求做"冷启动验证"**——这是课程 §4.5 的硬要求，但 brainstorming 技能里没强调。
  - **根因**：Superpowers 是个**通用框架**，不是**课程专用框架**。课程的"冷启动"是为了弥补单人项目"无同侪评审"的弱点——这是 NJU AI4SE 课程的特化设计
  - **对策**：已经在 AGENTS.md 里加"必做冷启动"硬约束
- **机制演示的"确定性"强调不够**——A 文件 §A.6 明确要 mock-driven deterministic 演示，但 brainstorming 阶段只在 §11 测试策略里间接提了一下
  - **对策**：PLAN Task 17 专门写了 `tests/demo_mechanisms.py`
- **TDD 顺序由 implementer 决定**——brainstorming 不强求 task 内部的"红→绿→重构"三步走，靠 implementer 自觉
  - **对策**：在 PLAN 每个 task 里**显式列了 3 步**，并在 AGENTS.md §3.1 强调

### 3.3 对 Superpowers 整套方法论的批判

**它假设了什么**：

- 假设开发者有"主角维度"——这是 Superpowers 的核心。如果开发者**没想清楚**选哪个维度深入，brainstorming 会"温柔"地放过
- 假设 task 之间是松耦合——18 task 看起来独立，但实际 Task 4 (classifier) → Task 5 (HITL) → Task 13 (loop) 有强顺序依赖。Superpowers 不强制"先想依赖"
- 假设开发者会用 subagent——这是技能框架的核心。**但 subagent 在 OpenCode / Claude Code / Cursor 里是"启动一个独立上下文"，开发者要**自己学怎么用**——这层学习曲线没在 brainstorming 阶段提示

**这些假设在我的项目里成立吗**：

- ✅ 主角维度：想清楚了（治理）
- ⚠️ 任务依赖：PLAN 写了顺序，但实施时还要靠人脑记住——**更安全的做法是 plan 顶部加"依赖图"**
- ⚠️ subagent 学习：第一次用 OpenCode 时确实懵了一会儿；如果是第一次用 subagent 的同学，可能卡更久

---

## 4. 冷启动验证记录（§4.5）

> 课程通用要求 §4.5："正式实现前，用一个与主开发智能体不同的 agent，
> 在不向其提供你与主 agent 对话历史的前提下，仅凭 SPEC.md + PLAN.md
> 尝试实现 1–2 个 task"。
>
> 本节记录**两次**冷启动：第一次"扩展式"（跑 6 task 出错）、第二次"补充式"（worktree 隔离、只测 Task 7）。

### 4.1 冷启动 agent 元信息

| 项 | 第一次冷启动 | 第二次冷启动（补充）|
|---|---|---|
| **agent 类型** | Claude Code (deepseek-v4-pro) | Claude Code (deepseek-v4-pro) |
| **与主 agent 关系** | 不同 ✓ | 不同 ✓ |
| **session** | 全新 ✓ | 全新 ✓ |
| **输入** | 仅 SPEC + PLAN | 仅 SPEC + PLAN（在 worktree 隔离目录里）|
| **测的 task 数** | 6（违反 §4.5 "1-2"）| 1（Task 7，遵守 §4.5）|
| **commit 数** | 7 | 3（红+绿+重构）|
| **测试结果** | 37 passed / 6 skipped | 41 passed / 6 skipped |
| **耗时** | ~ 2 小时 | ~ 15 分钟 |
| **工作目录** | 主项目 `D:\Desktop\Homework\AI_agent\C_Programming_Assistant_Harness` | Worktree `D:\Desktop\Homework\AI_agent\_coldstart_task7` 分支 `_coldstart/task-7-rerun` |

### 4.2 卡点清单（按发现顺序）

> 两次冷启动共发现 **3 个 SPEC/PLAN 漏洞**：

| # | 漏洞 | 来源 | 修复位置 | 状态 |
|---|------|------|---------|------|
| 1 | **pyproject.toml 缺 `dependencies` 字段** | 第一次冷启动 | T1.1 commit 4860b36 漏写 | ✅ 已在 commit 0ccd003 补全 |
| 2 | **PLAN Task 7 Step 1 用 `try/except ImportError` 包裹 `from ... import WindowsSandbox`**——模块缺失时变成 `HAS_WIN32=False`，测试 skip 而非 FAIL。**违反 TDD 硬要求**（红阶段必须真红）| 第二次冷启动 | PLAN Task 7 Step 1 | ✅ 已修正：直接 import，让 RED 阶段产生 ImportError collection error；guard 后移到 REFACTOR |
| 3 | **SPEC §5.3 vs PLAN Task 7 矛盾**——SPEC §5.3 写"Windows 用 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` + `job object` 限制"，但 PLAN Task 7 代码完全不含 `creationflags`。两文档对"初版是否含 creationflags"无一致说法 | 第二次冷启动 | SPEC §5.3 | ✅ 已修正：明确"初版（v0.1）不含 creationflags"，列 v0.2 路线 |

### 4.3 解读差异清单

> 第二次冷启动与主项目 Task 7（**实际上主项目当时未实现 Task 7**，所以对比改为"冷启动实现 vs PLAN 预设代码"）。

| # | PLAN 预设写法 | 冷启动实现写法 | 哪个对？| 处理 |
|---|-------------|--------------|-------|------|
| 1 | RED 测试用 `try/except ImportError` 包裹 import → RED 阶段测试 skip 而非 fail | RED 测试直接 `from ... import WindowsSandbox`（无 guard）→ 产生 ImportError collection error（真红）| **冷启动对** | TDD 要求真红；PLAN 修正 |
| 2 | 测试文件只列 2 个测试（echo + secret env）| 写了 4 个测试（echo + secret env + workspace chdir + nonzero exit）| **冷启动对** | 对标 POSIX 测试套件（Task 6 写了 6 个测试）覆盖度 |
| 3 | PLAN 未提更新 `sandbox/__init__.py` | REFACTOR 阶段更新 `__init__.py` 导出 `WindowsSandbox` | **冷启动对** | 保持与其他 backend（PosixSandbox, InMemorySandbox）导出风格一致 |
| 4 | `HAS_WIN32` 变量名（暗示检测 pywin32）| `WindowsSandbox = None` fallback 模式 | **冷启动对** | PLAN 变量名误导——实际检测的是模块是否存在，不是 pywin32 |

### 4.4 SPEC / PLAN 修订 diff

#### 修订 1：SPEC §5.3 资源限制

```diff
- - Windows: 用 subprocess 的 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`
-   + `job object` 限制（`pywin32` 的 `win32job` 模块，或退回 `timeout`
-   杀进程 + RSS 轮询）。**沙箱接口统一，但实现分平台**——通过
-   `SandboxBackend` Protocol 抽象，单元测试用 in-memory backend。
+ - Windows: **初版（v0.1）**仅做 chdir + env cleanup + 10s timeout；job object
+   限制（`pywin32` 的 `win32job` 模块）和 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`
+   列入 v0.2 路线。Job objects 是 Windows 上 rlimit 的等价物——`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`
+   确保子进程随父进程死亡。**沙箱接口统一，但实现分平台**——通过
+   `SandboxBackend` Protocol 抽象，单元测试用 in-memory backend。
+ - **初版不含 creationflags 的原因**：避免硬依赖 pywin32；v0.1 优先跑通 mock-driven 单测
+   路径，CPU/内存硬限制属于"防御深度"增强而非"安全屏障"必须项（网络/路径拦截才是）
```

理由：消除 SPEC/PLAN 关于 creationflags 的矛盾；明确 v0.1 / v0.2 边界。

#### 修订 2：PLAN Task 7 Step 1 测试设计

```diff
- try:
-     from cpa_harness.guardrails.sandbox.windows import WindowsSandbox
-     HAS_WIN32 = True
- except ImportError:
-     HAS_WIN32 = False
-
- @pytest.mark.skipif(not HAS_WIN32, reason="pywin32 not installed")
- def test_echo_runs_on_windows(tmp_path): ...
- @pytest.mark.skipif(not HAS_WIN32, reason="pywin32 not installed")
- def test_secret_env_stripped_on_windows(tmp_path): ...
+ # 直接 import，无 try/except —— 缺失即真红（TDD 硬要求）
+ from cpa_harness.guardrails.sandbox.windows import WindowsSandbox
+
+ def test_echo_runs_on_windows(tmp_path): ...
+ def test_secret_env_stripped_on_windows(tmp_path): ...
+ def test_sandbox_runs_in_workspace(tmp_path): ...
+ def test_sandbox_captures_nonzero_exit(tmp_path): ...
```

理由：TDD 硬要求"红"必须真红；4 个测试对齐 POSIX 覆盖度。

### 4.5 整体清晰度评价

| 维度 | 第一次冷启动后 | 第二次冷启动后 |
|------|---------------|---------------|
| SPEC 清晰度 | 7/10 | **8/10**（修订 1 后）|
| PLAN 清晰度 | 6/10 | **7/10**（修订 2 后）|
| 冷启动 agent 整体表现 | 6/10（6 task 偏离协议）| **9/10**（严守 1 task 边界）|
| 最严重的 SPEC 漏洞 | §5.3 creationflags 矛盾 | （已修复）|
| 最严重的 PLAN 漏洞 | T1.1 缺 deps | Task 7 try/except 吞红（已修复）|

### 4.6 给后续工作的启示

1. **TDD 测试模板硬约束**：所有跨平台 task 的测试**禁止**用 `try/except ImportError` 吞红。已加进 `AGENTS.md §3.1`。
2. **SPEC / PLAN 必须一致**：每写一个 task，im 应**逐行对齐** SPEC 的设计意图与 PLAN 的代码。如有冲突，先改文档再写代码。
3. **冷启动 prompt 的硬边界**：第一次冷启动 prompt 缺边界导致 6 task 跑飞；第二次加 5 条硬约束后严守 1 task 边界——证明 prompt 模板对 agent 行为的影响**远大于** agent 本身的"判断力"。
4. **worktree 隔离是冷启动的物理保障**：主分支的实现是"作弊线索"——即使 agent 自觉不读，存在就是污染源。worktree + 文件清理是**必要**的。

---

## 5. 维护说明

- 本文件**不**走 git push 流程——它是项目元文档，由用户手动维护
- 每完成一次冷启动 / 一次重大 SPEC 修订，就更新 §4
- 反思章节（§3）每完成一个阶段更新一次
- 最终交付前，由 `finishing-a-development-branch` 技能确认本文件完整

---

> 本文件满足课程通用要求 §4.4 + §4.5 的硬性交付要求。
> 冷启动部分（§4）已由两次冷启动 + 修订闭环填完。
