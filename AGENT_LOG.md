# AGENT_LOG.md · CP-AH 实施过程日志

> 通用要求 §4.9 规定的"过程证据"。每个 task 至少有一条记录。

---

## 2026-07-07 · 阶段：brainstorming + SPEC 起草

### 任务 0：项目立项与 SPEC 起草

| 字段 | 值 |
|------|---|
| **时间** | 2026-07-07 下午 |
| **task 编号** | T0 |
| **触发的 Superpowers 技能** | `brainstorming` |
| **所用编码智能体** | OpenCode (claude-opus-4.5) |
| **关键 commit** | `e696127` / `beab007` / `c170863` / `71477d3` / `0f15461` / `6b2c36a` |
| **用户角色** | 大一学生，NJU AI4SE 课程；C / Java 系统学过，Python 基础 |

### 关键节点与决策

1. **范围确定**：学生选择"教学场景" + "C 语言学习者" + "治理与护栏
   为主角维度" + "WebUI + CLI 双形态" + "Python 3.11 实现" + "OpenAI
   兼容接口" + "进程级沙箱"
2. **范围收缩**：用户问"加 Java 会不会偏太多"，答会。决定首版只
   支持 C，扩展留给未来。
3. **主角维度**：**治理与护栏**（HITL 状态机 + 危险动作分类 + 沙箱
   + 范围围栏）——这是评审人最看重的部分，深度实现。
4. **测试策略**：明确 TDD 三步（红 / 绿 / 重构），用 MockLLM 实现
   "移除真 LLM 后仍能跑测试"的硬要求。
5. **事故与恢复**：用户本地曾误删 §11 测试策略（章号压缩成 13），
   通过 `git restore` 回到 0f15461 commit。**教训**：见 §"学到的
   教训"。

### 学到的教训

- **教训 L1（编码协作）**：当用户说"我看不到"时，先用 `git status` +
  `git diff --stat` 检查**是否有未保存修改**，再下结论"文件没问题"。
  本次差点因为 PowerShell 终端 GBK 编码导致的乱码误判。
- **教训 L2（SPEC 写作）**：明确章节编号 + 在 commit message 里写
  明"§11-§14"，避免后续章号压缩的误会。
- **教训 L3（工作流）**：项目级 `AGENTS.md` 必须尽早写——它是
  cross-session context 的"重启文件"。
- **教训 L4（用户）**：用户是大一学生，**概念解释要具体、避免
  抽象**；技术决策要给"为什么" + 替代选项。

---

## 2026-07-07 · 阶段：writing-plans

### 任务 0.5：PLAN 起草

| 字段 | 值 |
|------|---|
| **时间** | 2026-07-07 傍晚 |
| **task 编号** | T0.5 |
| **触发的 Superpowers 技能** | `writing-plans` |
| **关键 commit** | `67f3e2c` |
| **产出** | `docs/superpowers/plans/2026-07-07-cpah-plan.md` |

### 关键决策

1. **18 个 task**，每个独立 TDD 循环（红 / 绿 / 重构）
2. **三个 subagent-driven tasks 不在 plan 里**：冷启动验证、SPEC_PROCESS.md、REFLECTION.md、finishing-a-development-branch——这些在实施阶段产生
3. **主角维度深度**：Task 4（分类器）、Task 5（HITL）、Task 6/7（沙箱）、Task 13（loop 集成）— 共 4 个 task 服务于治理
4. **self-review 发现的 5 个缺口**：WA/TLE/RE 解析、WebUI、Dockerfile、tracer、WebUI↔HITL 集成 — 列为 follow-up PR

### 进度（截至 18:00）

| 阶段 | 完成 / 总数 |
|------|-----------|
| Brainstorming | 8 / 8 ✅ |
| Writing Plans | 1 / 1 ✅ |
| 实现 | 0 / 18 ⏳ |
| 验证 + 文档 + 部署 + 反思 | 0 / 8 ⏳ |
| **总进度** | **9 / 35** |

### 下一步（用户视角）

1. 用户开加速器跑 `git push -u origin main`，把 8 个 commit 推到 GitHub
2. AI 在 GitHub 上建 issue 看板（Task 1-3 / Task 4-7 主角维度 / Task 19 WebUI）
3. 改天新会话：新 AI 读 AGENTS.md + SPEC + PLAN + git log，直接进 subagent-driven-development 跑 Task 1
4. 每个 task 完成后：commit + 开 PR + 用户开加速器 push

### 学到的教训

- **教训 L5（plan 写作）**：分块写入比单次 write 大文件更稳——上次单次写入 100KB 文件触发 JSON 错误。改用 `edit` 追加 + 验证行数
- **教训 L6（spec 与 plan 的关系）**：spec 描述"做什么 + 为什么"，plan 描述"怎么做 + 步骤"；spec 14 章 vs plan 18 task 是合理映射

---

## 2026-07-07 · 阶段：git push 准备

### 任务 0.6：本地 commit 与 push 准备

| 字段 | 值 |
|------|---|
| **时间** | 2026-07-07 18:00 |
| **task 编号** | T0.6 |
| **关键 commit** | 已有 8 个 commit (e696127 → 67f3e2c) |
| **下一步** | 用户开加速器后 push |

### push 手册（给用户）

```powershell
cd D:\Desktop\Homework\AI_agent\C_Programming_Assistant_Harness
git status                    # 应是 "nothing to commit"
git log --oneline             # 8 个 commit
git push -u origin main       # 第一次 push
```

### push 之后

- 打开 https://github.com/Methyl1644/C_Programming_Assistant_Harness
- 验证 8 个 commit + 文件结构
- 告诉 AI push 状态，AI 帮你建 issue 看板

---

## 2026-07-07 · 阶段：会话保存

### 任务 0.7：写 RESUMING.md + 会话记录 + 收尾

| 字段 | 值 |
|------|---|
| **时间** | 2026-07-07 18:30 |
| **task 编号** | T0.7 |
| **关键 commit** | 即将 commit（最后一个） |
| **产出文件** | `RESUMING.md` + `docs/sessions/2026-07-07-session-1.md` |

### 目的

让**任何** AI / **任何** 时间接手项目时，能在 5 分钟内：
1. 读 `RESUMING.md` 了解项目是什么
2. 读 `AGENTS.md` 知道工作规则
3. 读 SPEC + PLAN 知道设计 + 实施步骤
4. 跑 `git log --oneline` 看历史
5. 问用户"接下来做什么"

### 用户视角

本次会话从零到 SPEC+PLAN+GitHub 全部就绪。用户在 Steam++ 加速器下成功 push 9 个 commit。

### 下次会话

1. 读 `RESUMING.md` → 知道做什么
2. 读 SPEC §5.3 + PLAN Task 4-5 → 知道主角维度怎么实现
3. 用 subagent-driven-development 跑 Task 1，按 TDD 三步走

### 状态（截至 18:30）

| 阶段 | 完成 / 总数 | 百分比 |
|------|-----------|--------|
| Brainstorming | 8 / 8 | 100% |
| Writing Plans | 1 / 1 | 100% |
| Git Push | 1 / 1 | 100% |
| 实现 (Task 1-18) | 0 / 18 | 0% |
| 冷启动验证 + 文档 | 0 / 4 | 0% |
| WebUI + Docker + 部署 + 反思 | 0 / 4 | 0% |
| **总进度** | **10 / 36** | **28%** |


