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

✅ Core complete — 81 tests passing, WebUI live, Docker image builds.

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

## Project Structure (planned)

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
│   └── web/              # FastAPI app (WebUI)
├── tests/                # Mock-LLM deterministic unit tests
├── docker/               # Sandbox container image (optional)
├── docs/superpowers/     # Specs, plans, process docs
├── .gitlab-ci.yml        # CI with `unit-test` job
├── Dockerfile            # Distribution
├── AGENT_LOG.md          # Superpowers session log
├── REFLECTION.md         # 1500-2500 word reflection
└── README.md
```

## License

MIT — see [`LICENSE`](LICENSE).
