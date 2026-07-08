"""FastAPI app: serves static frontend + API endpoints + WebSocket HITL."""
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cpa_harness.action import Action
from cpa_harness.llm.mock import MockLLM, MockTurn
from cpa_harness.llm.openai_provider import OpenAILLM
from cpa_harness.llm.provider import LLMProvider
from cpa_harness.tools.registry import ToolRegistry
from cpa_harness.tools import (
    read_file, list_dir, search_code, write_file,
    exec_command, take_note, finish_tutoring, run_feedback,
)
from cpa_harness.guardrails.sandbox.in_memory import InMemorySandbox
from cpa_harness.guardrails.sandbox.posix import PosixSandbox
from cpa_harness.guardrails.sandbox.windows import WindowsSandbox
from cpa_harness.loop import AgentLoop
from cpa_harness.credentials import get_api_key

app = FastAPI(title="CP-AH", description="C Programming Assistant Harness")

_STATIC_DIR = Path(__file__).parent / "static"
_WORKSPACES_DIR = Path.cwd() / "workspaces"
_WORKSPACES_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

_sessions: dict[str, dict] = {}


def _build_sandbox(workspace: str):
    """Use a real sandbox so gcc/valgrind actually run."""
    if sys.platform == "win32":
        try:
            return WindowsSandbox(workspace=workspace)
        except Exception:
            pass
    try:
        return PosixSandbox(workspace=workspace)
    except Exception:
        return InMemorySandbox()


def _build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    def schema(name):
        return {"name": name, "description": name, "parameters": {"type": "object"}}
    for mod, name in [
        (read_file, "read_file"),
        (list_dir, "list_dir"),
        (search_code, "search_code"),
        (write_file, "write_file"),
        (exec_command, "exec_command"),
        (take_note, "take_note"),
        (finish_tutoring, "finish_tutoring"),
        (run_feedback, "run_feedback"),
    ]:
        reg.register(name, mod.run, schema(name))
    return reg


def _build_llm(goal: str, filename: str) -> tuple[LLMProvider, bool]:
    """Build LLM: real if API key exists, mock otherwise.

    Returns (llm, is_mock).
    """
    api_key = get_api_key()
    if api_key:
        return OpenAILLM(api_key=api_key, model="gpt-4o-mini"), False

    # Mock: at least run real compile feedback so user gets something useful
    mock = MockLLM(script=[
        MockTurn(
            text=f"我来读一下 {filename}",
            action=Action(type="call_tool", tool="read_file",
                          args={"path": filename}),
        ),
        MockTurn(
            text=f"让我编译并测试 {filename}",
            action=Action(type="call_tool", tool="run_feedback",
                          args={"target": filename}),
        ),
        MockTurn(
            text="分析完成。以上是编译和内存检查的反馈。",
            action=Action(type="done"),
        ),
    ])
    return mock, True


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = _STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>CP-AH</h1><p>static/index.html not found</p>")


@app.post("/api/upload")
async def upload_file(file: bytes = b""):
    session_id = uuid.uuid4().hex[:12]
    workspace = _WORKSPACES_DIR / session_id
    workspace.mkdir(parents=True, exist_ok=True)
    filename = "main.c"
    (workspace / filename).write_bytes(file)
    _sessions[session_id] = {
        "workspace": str(workspace),
        "filename": filename,
    }
    return {"session_id": session_id, "filename": filename}


class AskRequest(BaseModel):
    session_id: str
    goal: str = "explain this code"


@app.post("/api/ask")
async def ask(req: AskRequest):
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    sess = _sessions[req.session_id]
    workspace = sess["workspace"]
    filename = sess["filename"]

    llm, is_mock = _build_llm(req.goal, filename)
    sandbox = _build_sandbox(workspace)

    loop = AgentLoop(
        llm=llm,
        tools=_build_registry(),
        sandbox=sandbox,
        goal=req.goal,
        workspace=workspace,
        max_steps=10,
    )
    result = loop.run()
    return {
        "answer": result.answer,
        "steps": result.steps,
        "exit_reason": result.exit_reason,
        "history": loop.history,
        "is_mock": is_mock,
    }


@app.websocket("/ws/hitl")
async def ws_hitl(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "approve":
                await ws.send_json({"type": "approved", "action": msg.get("action")})
            elif msg.get("type") == "reject":
                await ws.send_json({"type": "rejected"})
            else:
                await ws.send_json({"type": "unknown", "msg": msg})
    except WebSocketDisconnect:
        pass
