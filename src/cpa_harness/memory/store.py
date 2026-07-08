"""MemoryStore: file-backed per-user memory."""
import json
from pathlib import Path
from cpa_harness.memory.record import MemoryRecord


class MemoryStore:
    def __init__(self, base_dir: Path, user_id: str):
        self.base_dir = Path(base_dir)
        self.user_id = user_id
        self.path = self.base_dir / f"{user_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def _load(self) -> list[MemoryRecord]:
        return [MemoryRecord(**item) for item in json.loads(self.path.read_text())]

    def _save(self, records: list[MemoryRecord]) -> None:
        self.path.write_text(json.dumps(
            [r.model_dump(mode="json") for r in records], indent=2
        ))

    def write(self, record: MemoryRecord) -> None:
        records = self._load()
        records.append(record)
        self._save(records)

    def read(self, kind: str | None = None) -> list[MemoryRecord]:
        records = self._load()
        if kind is None:
            return records
        return [r for r in records if r.kind == kind]

    def search(self, query: str) -> list[MemoryRecord]:
        return [r for r in self._load() if query.lower() in r.content.lower()]
