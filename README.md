# C Programming Assistant Harness (CP-AH)

A guardrail-first Coding Agent Harness that helps **C language beginners**
debug and learn. Built as the final project for the AI4SE course at Nanjing
University.

> **One-line pitch**: An LLM that explains your C code, runs your tests, and
> finds your memory leaks — but **never silently rewrites your code**, and
> **never runs a command outside its sandbox**.

## Why

C 语言的报错信息对初学者很难读懂；现有 LLM 工具（ChatGPT / Claude）能讲
清楚，但有两个隐患：

1. AI 容易"自作主张"重写学生代码，跳过学习过程
2. AI 可能执行危险命令（`rm -rf`、`curl | bash`）误删学生作业

CP-AH 用**护栏优先**的 harness 解决这两点。

## Status

✅ Core complete — 126 tests passing, WebUI live, Docker image builds.

See [`docs/superpowers/specs/`](docs/superpowers/specs/) for the design doc.

## Quick Start

### Docker (recommended)

```bash
docker build -t cpa-harness .
docker run -p 8000:8000 cpa-harness
# open http://localhost:8000
```

### Local dev

```bash
pip install -e ".[dev]"
uvicorn cpa_harness.web.app:app --reload
```

### Run tests

```bash
pytest
```

## Project Structure

```
.
├── src/cpa_harness/      # Harness core (own implementation, no LangChain)
│   ├── loop.py           # Main agent loop
│   ├── llm/              # LLM abstraction (real + mock)
│   ├── tools/            # Tool registry (read_file, exec_command, ...)
│   ├── guardrails/       # Sandbox + HITL + scope fence (main focus)
│   ├── feedback/         # gcc / valgrind / test result parsers
│   ├── memory/           # Cross-session memory store
│   ├── config/           # Declarative rule loader
│   ├── credentials/      # API key storage (keyring + file fallback)
│   └── web/              # FastAPI app (WebUI)
├── tests/                # Mock-LLM deterministic unit tests
├── docs/superpowers/     # Specs, plans, process docs
├── SPEC.md               # Design document
├── PLAN.md               # Implementation plan (20 tasks)
├── SPEC_PROCESS.md       # Process doc (brainstorming + cold-start)
├── AGENT_LOG.md          # Superpowers session log
├── REFLECTION.md         # 1500-2500 word reflection
├── .gitlab-ci.yml        # CI with `unit-test` job
├── Dockerfile            # Distribution
└── README.md
```

## API Key 安全配置

### 本地开发

```bash
# 方式 1：通过 WebUI 设置页面（推荐）
uvicorn cpa_harness.web.app:app --reload
# 打开 http://localhost:8000 → 点击「设置」→ 输入 key

# 方式 2：环境变量（明文，仅开发用）
export OPENAI_API_KEY="sk-..."
```

### Docker 部署

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." cpa-harness
```

> **明文风险说明**：环境变量为明文，进程内可见（`/proc/<pid>/environ`）。
> 生产环境建议通过 WebUI 设置页面录入，key 存储在 `.keyring.json`
> （文件权限 600）。Windows 上 keyring 后端不稳定，已禁用，统一走文件存储。

## 安全边界

| 边界 | 机制 | 实现 |
|------|------|------|
| 危险命令拦截 | L0 正则 + L1 分类器 | `rm -rf /`、`curl | bash` 等被 BLOCKED |
| 写操作审批 | HITL 状态机 | 覆盖学生 `.c` 文件时暂停等审批 |
| 沙箱隔离 | 进程级沙箱 | `chdir` + env cleanup + 10s timeout |
| 密钥保护 | 子进程 env 清理 | `OPENAI_API_KEY` 不传入子进程 |
| 范围围栏 | scope fence | agent 只能操作 workspace 内文件 |

## 已知限制

- **Windows 沙箱**：v0.1 仅做 chdir + env cleanup + timeout，无 job object 硬限制（CPU/内存）
- **POSIX 沙箱**：完整 `ulimit` + `chroot` 支持，6 个测试在 Linux 上运行
- **valgrind**：Windows 上不可用，Linux/macOS 上完整支持
- **LLM 供应商**：当前接 OpenAI API，可通过 `LLMProvider` 抽象层扩展
- **Python >= 3.11**：使用了 `type | None` 等 3.10+ 语法

## License

MIT — see [`LICENSE`](LICENSE).
