"""Action: what the LLM wants the harness to do this turn."""
from typing import Literal
from pydantic import BaseModel, Field

ActionType = Literal["call_tool", "use_skill", "take_note", "finish_tutoring", "done"]


class Action(BaseModel):
    type: ActionType
    tool: str | None = None
    args: dict = Field(default_factory=dict)
    note: str | None = None
    summary: str | None = None
