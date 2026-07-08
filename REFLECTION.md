# REFLECTION.md — CP-AH 项目反思报告

> 课程：AI4SE（南京大学）| 项目：C Programming Assistant Harness (CP-AH)
> 主开发智能体：OpenCode (claude-opus-4.5) | 冷启动智能体：Claude Code (deepseek-v4-pro)

---

## 1. 项目概述

CP-AH 是一个**护栏优先**（guardrail-first）的 Coding Agent Harness，面向 C 语言初学者。它的核心设计目标不是"让 AI 更聪明"，而是"让 AI 更安全"——具体而言，确保 AI 在帮助学生调试 C 代码时：

1. **不擅自重写学生代码**（scope fence 机制：写操作必须经 HITL 审批）
2. **不执行危险命令**（命令分类器 + 进程级沙箱：`rm -rf`、`curl | bash` 被拦截）
3. **不泄漏密钥**（沙箱清理子进程环境变量中的 `OPENAI_API_KEY` 等）

项目完成了 20 个 task、81 个测试通过（7 个 POSIX-only 在 Windows 上 skip），包含 WebUI（FastAPI + Linear 风格前端）、Docker 镜像、完整的 SPEC/PLAN/SPEC_PROCESS 文档链。

---

## 2. 关键设计决策与反思

### 2.1 进程级沙箱 vs Docker 沙箱

**决策**：用 Python `subprocess` + `chdir` + `ulimit` + 环境变量清理实现进程级沙箱，不引入 Docker 作为沙箱。

**理由**：(1) 跨平台（Windows/Linux/macOS）；(2) 代码可控（约 200 行 Python）；(3) 可单测（MockSandbox 直接 mock）——满足 A 文件 §A.4-C 的 mock-driven 确定性测试硬要求。

**反思**：这是一个**有得有失**的工程 trade-off。得：避开 Docker 外部依赖，学生机器上 `pip install` 即可用，CI 测试更快。失：Windows 上 CPU/内存硬限制难做（`job object` 是 `rlimit` 的等价物，但需要 `pywin32` 硬依赖），v0.1 只做了 `chdir` + env cleanup + 10s timeout。**算工程折中，不算设计错误**——网络/路径拦截才是安全屏障的必须项，CPU/内存限制属于"防御深度"增强。

### 2.2 Mock-LLM 确定性测试

**决策**：所有 agent loop 测试用 `MockLLM`（预设脚本驱动），不调真 LLM。

**理由**：A 文件 §A.4-C 明确要求"mock-driven deterministic tests"。真 LLM 每次返回不同内容，无法做断言。

**反思**：这是本项目**最正确的设计决策之一**。MockLLM 让 agent loop 的测试和真 LLM 的测试完全解耦——81 个测试全绿不代表真 LLM 能跑通，但至少证明 harness 逻辑正确。代价是：MockLLM 脚本需要手动维护，且无法覆盖 LLM "不按格式返回" 的 edge case。未来可加 "fuzz LLM response" 测试。

### 2.3 凭据治理：keyring + 文件 fallback

**决策**：优先用系统 keyring（macOS Keychain / Windows Credential Manager / Linux SecretService），失败时 fallback 到 `.keyring.json` 文件。

**反思**：这个决策在实施时**踩了坑**。Windows 上 `keyring` 库的 Credential Manager 后端不稳定——用户在 WebUI 保存 API key 时 500 错误。最终修复方式是 Windows 上直接禁用 keyring，走文件存储。**教训**：跨平台库的"跨平台"不等于"跨平台都好用"——每个平台的后端都要实测。

---

## 3. AI 协作模式反思

### 3.1 brainstorming 阶段：5 轮迭代，11 采纳，6 推翻

SPEC_PROCESS.md §2 记录了 5 轮 brainstorming 迭代，AI 提了 17 条建议，我采纳 11 条、推翻 6 条。从中提炼出 3 个"AI 协作常见模式"：

| 模式 | AI 倾向 | 我的对策 |
|------|---------|---------|
| "AI 推通用方案" | 加 Java、Docker、LangChain | 强制问"这会稀释主角维度吗" |
| "AI 推简单方案" | 环境变量存密钥 | 强制问"生产环境下还简单吗" |
| "AI 推流行方案" | LangChain、GitHub Actions | 先查课程硬约束 |

**核心教训**：AI 给"扩展性"建议时，**默认它在用工程惯性思考**（"加 X 看起来更通用"），不一定从你的主角维度出发。开发者必须有**主动推翻 AI 的能力**——这不是"不听劝"，而是"分清建议的适用边界"。

### 3.2 冷启动验证：两次，3 个文档漏洞

课程 §4.5 要求用不同 agent 做冷启动验证。我做了两次：

- **第一次**（扩展式）：Claude Code 跑了 6 个 task（违反 §4.5 "1-2 个"），但发现了 `pyproject.toml` 缺 dependencies。
- **第二次**（补充式）：worktree 隔离，只测 Task 7，3 个 commit（红/绿/重构），发现了 2 个真卡点：(1) PLAN 用 `try/except ImportError` 吞了 TDD 的红阶段；(2) SPEC §5.3 和 PLAN Task 7 对 `creationflags` 的描述矛盾。

**核心教训**：**prompt 对 agent 行为的影响远大于 agent 本身的"判断力"**。第一次 prompt 留歧义 → 跑飞 6 task；第二次加 5 条硬边界 → 严守 1 task。冷启动不是"换个 agent 跑一遍"，而是"用不同 agent 测文档的清晰度"。

### 3.3 TDD 纪律：红 → 绿 → 重构

项目严格走 TDD：每个 task 先写失败测试（红），再写实现（绿），再重构。3 个 commit per task，Conventional Commits 格式。

**踩过的坑**：PLAN Task 7 的测试模板用了 `try/except ImportError` 包裹 import——模块缺失时测试 skip 而非 fail，**吞了 TDD 的红阶段**。这是冷启动发现的，已修正为直接 import。

**教训**：TDD 的"红"必须真红。`try/except` 吞异常 = TDD 流程结构性缺陷。已加进 AGENTS.md §3.1 作为硬约束。

---

## 4. 做得好的地方

1. **文档链完整**：SPEC → PLAN → SPEC_PROCESS → AGENT_LOG → QUESTIONS → REFLECTION，每一步都有决策记录和理由。评审人可以追溯"为什么选进程级沙箱"的完整推理链。
2. **测试覆盖度高**：81 个测试，覆盖 action/observation/loop、8 个工具、3 个沙箱 backend、gcc/valgrind 解析器、HITL、分类器、凭据存储、WebUI。7 个 skip 全是 POSIX-only 在 Windows 上的预期跳过。
3. **冷启动闭环**：发现 3 个文档漏洞 → 修订 SPEC/PLAN → 回填 SPEC_PROCESS §4 → 加进 AGENTS.md 硬约束。不是"做完就忘"，而是"做完反哺流程"。
4. **Docker 镜像可用**：`docker build` + `docker run -p 8000:8000` 一条命令启动 WebUI，gcc + valgrind 预装。

---

## 5. 做得不好的地方

1. **WebUI 开发偏晚**：PLAN 原本只有 18 个 task，WebUI 是后补的 Task 19。导致 WebUI 的 API key 配置功能在最后阶段才做，踩了 keyring Windows 的坑，来不及做完整的端到端测试。
2. **AGENT_LOG 进度表滞后**：AGENT_LOG.md 的进度表停在 50%（Task 7），实际已完成 20/20 task。原因是后期开发节奏加快，没及时回填。**过程文档的实时性是弱项**。
3. **Windows 沙箱功能不完整**：v0.1 只有 chdir + env cleanup + timeout，没有 job object 的 CPU/内存限制。虽然列了 v0.2 路线，但作为"护栏优先"的项目，资源限制缺失是个短板。
4. **未做云部署**：Docker 镜像本地跑通了，但没有部署到云平台获取公网 URL。课程 §3.2 要求"单条 docker run 可启动"，本地满足，但公网访问是加分项。

---

## 6. 对 Superpowers 方法论的批判

### 它假设了什么

- **假设开发者有"主角维度"**：brainstorming 的核心。如果开发者没想清楚选哪个维度深入，brainstorming 会"温柔"地放过。
- **假设 task 之间是松耦合**：18 task 看起来独立，但 Task 4（分类器）→ Task 5（HITL）→ Task 13（loop）有强顺序依赖。Superpowers 不强制"先想依赖图"。
- **假设开发者会用 subagent**：这是技能框架的核心，但 subagent 在不同 harness（OpenCode / Claude Code / Cursor）里用法不同，学习曲线没在 brainstorming 阶段提示。

### 这些假设在我的项目里成立吗

- ✅ 主角维度：想清楚了（治理）
- ⚠️ 任务依赖：PLAN 写了顺序，但实施时还要靠人脑记住——更安全的做法是 plan 顶部加"依赖图"
- ⚠️ subagent 学习：第一次用 OpenCode 时确实懵了一会儿

### 它没覆盖的

- **课程硬约束**：冷启动验证（§4.5）、mock-driven 确定性测试（§A.4-C）、机制演示（§A.6）——这些是 NJU AI4SE 课程的特化要求，Superpowers 作为通用框架不会覆盖。**单一技能框架 ≠ 课程要求**。
- **跨平台实测**：Superpowers 假设"库声明跨平台 = 跨平台好用"。实际上 `keyring` 在 Windows 上踩了坑。

---

## 7. 总结

CP-AH 项目的核心价值不在于"做了一个 C 语言辅导 AI"——市面上已有更好的工具。它的价值在于**完整展示了从需求到交付的 AI 协作工程流程**：

- 用 brainstorming 技能做 5 轮需求探索，推翻 6 条 AI 建议
- 用 writing-plans 技能拆 20 个 task，每个 task 3 步 TDD
- 用冷启动验证测出 3 个文档漏洞，闭环修订
- 用 mock-driven 测试保证 81 个测试确定性通过
- 用 Docker 镜像实现"一条命令启动"

**最重要的教训**：AI 是工程协作伙伴，不是权威。它给的建议在"通用工程"语境下通常合理，但在"你的项目主角维度"和"课程硬约束"语境下可能偏航。开发者的核心能力不是"会用 AI"，而是"能判断 AI 的建议在什么语境下适用、什么语境下该推翻"。
