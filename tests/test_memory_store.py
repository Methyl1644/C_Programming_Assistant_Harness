"""Tests for MemoryStore — file-backed per-user memory."""
from datetime import datetime
from cpa_harness.memory.store import MemoryStore
from cpa_harness.memory.record import MemoryRecord


def test_write_and_read_note(tmp_path):
    store = MemoryStore(base_dir=tmp_path, user_id="alice")
    store.write(MemoryRecord(
        user_id="alice", kind="note",
        content="student is on pointer chapter",
        created_at=datetime.now(),
    ))
    notes = store.read(kind="note")
    assert len(notes) == 1
    assert "pointer" in notes[0].content


def test_read_filters_by_kind(tmp_path):
    store = MemoryStore(base_dir=tmp_path, user_id="bob")
    store.write(MemoryRecord(user_id="bob", kind="note", content="n1", created_at=datetime.now()))
    store.write(MemoryRecord(user_id="bob", kind="history", content="h1", created_at=datetime.now()))
    assert len(store.read(kind="note")) == 1
    assert len(store.read(kind="history")) == 1
    assert len(store.read()) == 2


def test_search_substring(tmp_path):
    store = MemoryStore(base_dir=tmp_path, user_id="alice")
    store.write(MemoryRecord(user_id="alice", kind="history",
                             content="debugged segfault in malloc",
                             created_at=datetime.now()))
    store.write(MemoryRecord(user_id="alice", kind="history",
                             content="asked about pointers",
                             created_at=datetime.now()))
    results = store.search("malloc")
    assert len(results) == 1
    assert "malloc" in results[0].content


def test_persistence_across_instances(tmp_path):
    store1 = MemoryStore(base_dir=tmp_path, user_id="alice")
    store1.write(MemoryRecord(user_id="alice", kind="note", content="x", created_at=datetime.now()))
    store2 = MemoryStore(base_dir=tmp_path, user_id="alice")
    assert len(store2.read()) == 1
