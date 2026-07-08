"""Tests for WebUI FastAPI backend."""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from cpa_harness.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_index_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "CP-AH" in resp.text or "cpa" in resp.text.lower()


def test_upload_file_returns_session_id(client, tmp_path):
    resp = client.post(
        "/api/upload",
        files={"file": ("main.c", b"int main() { return 0; }", "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_ask_with_mock_returns_result(client):
    # First upload a file
    upload_resp = client.post(
        "/api/upload",
        files={"file": ("main.c", b"int main() { return 0; }", "text/plain")},
    )
    session_id = upload_resp.json()["session_id"]

    # Then ask
    ask_resp = client.post(
        "/api/ask",
        json={"session_id": session_id, "goal": "explain this code"},
    )
    assert ask_resp.status_code == 200
    data = ask_resp.json()
    assert "answer" in data
    assert "steps" in data
    assert "exit_reason" in data


def test_ask_nonexistent_session_returns_404(client):
    resp = client.post(
        "/api/ask",
        json={"session_id": "nonexistent", "goal": "test"},
    )
    assert resp.status_code == 404
