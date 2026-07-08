"""MemoryRecord: a single piece of cross-session memory."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

MemoryKind = Literal["note", "history", "lesson", "preference"]


class MemoryRecord(BaseModel):
    user_id: str
    kind: MemoryKind
    content: str
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
