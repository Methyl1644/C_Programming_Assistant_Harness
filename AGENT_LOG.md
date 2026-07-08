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

### 下一步

- 进入 writing-plans 技能，把 SPEC 拆成可由 subagent 完成的 task
  列表
- 第一个 task：建 `Makefile` + 项目骨架（`pyproject.toml` /
  `src/cpa_harness/__init__.py`）
- 第二个 task：实现 `LLMProvider` Protocol + `MockLLM`（TDD）

### 偏离 Superpowers 工作流的地方

无。所有阶段按 `brainstorming` 技能要求推进。
