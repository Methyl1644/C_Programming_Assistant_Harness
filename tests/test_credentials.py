"""Tests for credential storage — keyring primary + file fallback."""
import os
import pytest
from cpa_harness.credentials.storage import (
    mask_key, _keyring_path,
)


def test_mask_key_hides_middle():
    assert mask_key("sk-1234567890abcdef") == "sk-1...cdef"


def test_mask_key_handles_short():
    assert mask_key("abc") == "***"
    assert mask_key("") == "(empty)"
    assert mask_key(None) == "(empty)"


def test_store_and_get_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("CPAH_TEST_KEYRING_BACKEND", "file")
    monkeypatch.setenv("CPAH_KEYRING_PATH", str(tmp_path / "kr.json"))
    from cpa_harness.credentials import storage
    storage._backend = None  # reset cache
    storage.store_api_key("sk-test-1234567890")
    assert storage.get_api_key() == "sk-test-1234567890"
    storage.clear_api_key()
    assert storage.get_api_key() is None
