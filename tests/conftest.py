"""Shared pytest fixtures for CP-AH."""
import pytest


@pytest.fixture
def tmp_workspace(tmp_path):
    """Provide a fresh workspace directory for a test session."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace
