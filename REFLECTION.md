# REFLECTION.md — CP-AH 项目反思报告

> 课程：AI4SE（南京大学）| 项目：C Programming Assistant Harness (CP-AH)
> 主开发智能体：OpenCode (claude-opus-4.5) | 冷启动智能体：Claude Code (deepseek-v4-pro)

---

## 1. 项目概述

CP-AH 是一个**护栏优先**的 Coding Agent Harness，面向 C 语言初学者。核心目标不是"让 AI 更聪明"，而是"让 AI 更安全"：不擅自重写学生代码（HITL 审批）、不执行危险命令（分类器 + 沙箱）、不泄漏密钥（env 清理）。

项目完成 20 个 task、126 个测试通过（6 个 POSIX-only skip），含 WebUI、Docker 镜像、完整文档链。

## 2. 关键设计决策

**进程级沙箱 vs Docker**：用 `subprocess` + `chdir` + `ulimit` + env 清理，不引入 Docker 沙箱。理由：跨平台、代码可控、可单测（满足 §A.4-C）。代价：Windows 上无 job object 硬限制，v0.1 仅做 chdir + env cleanup + timeout。算工程折中——网络/路径拦截才是安全必须项，CPU/内存限制属防御深度。

**Mock-LLM 确定性测试**：所有 agent loop 测试用 `MockLLM`（预设脚本），不调真 LLM。这是最正确的决策之一——harness 逻辑与 LLM 质量完全解耦，126 个测试确定性通过。

**凭据治理**：keyring + 文件 fallback。Windows 上 keyring 后端不稳定（500 错误），最终禁用 keyring 走文件存储。教训：跨平台库的"跨平台"≠"跨平台都好用"。

## 3. AI 协作反思

**brainstorming**：5 轮迭代，17 条建议，采纳 11 条、推翻 6 条。提炼出 3 个模式：AI 推"通用方案"时稀释主角维度、推"简单方案"时忽略生产环境、推"流行方案"时冲突课程硬约束。核心教训：AI 给扩展性建议时默认用工程惯性思考，开发者必须能分清建议的适用边界。

**冷启动验证**：两次，发现 3 个文档漏洞（pyproject 缺 deps、try/except 吞 TDD 红阶段、SPEC/PLAN creationflags 矛盾）。第一次 prompt 留歧义导致跑飞 6 task，第二次加 5 条硬边界后严守 1 task。教训：prompt 对 agent 行为的影响远大于 agent 本身的判断力。

**TDD 纪律**：红→绿→重构，3 commit per task。踩过的坑：PLAN 用 `try/except ImportError` 吞了红阶段。教训：TDD 的红必须真红，吞异常 = 流程结构性缺陷。

## 4. 做得好

1. 文档链完整，决策可追溯
2. 测试覆盖度高（126 passed），机制演示 3/3 通过
3. 冷启动闭环：发现漏洞 → 修订文档 → 反哺流程
4. Docker 一条命令启动

## 5. 做得不好

1. WebUI 开发偏晚，API key 配置踩坑来不及做端到端测试
2. AGENT_LOG 进度表滞后（停在 50%，实际 100%）
3. Windows 沙箱无 job object 硬限制
4. 未做云部署

## 6. 对 Superpowers 方法论的批判

它假设开发者有"主角维度"（成立✅）、task 间松耦合（部分成立⚠️，有强顺序依赖）、开发者会用 subagent（学习曲线未提示⚠️）。它没覆盖课程硬约束（冷启动、mock 测试、机制演示）——单一技能框架 ≠ 课程要求。

## 7. 总结

CP-AH 的价值不在"做了 C 语言辅导 AI"，而在完整展示了从需求到交付的 AI 协作工程流程：brainstorming 推翻 6 条建议、20 task TDD、冷启动测出 3 个漏洞、mock-driven 126 测试通过、Docker 一条命令启动。

最重要的教训：AI 是工程协作伙伴，不是权威。开发者的核心能力不是"会用 AI"，而是"能判断 AI 的建议在什么语境下适用、什么语境下该推翻"。
