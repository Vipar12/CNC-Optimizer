"""Low-level command models used by the parser and analysis layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GCodeCommand:
    """A structured representation of one interpreted G-code command."""

    line_number: int
    original_line: str
    kind: str
    code: int | None = None
    letter: str | None = None
    value: float | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    i: float | None = None
    j: float | None = None
    k: float | None = None
    feed_rate: float | None = None
    spindle_speed: float | None = None
    tool: int | None = None
    motion_type: str | None = None
    comment: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind == "motion" and self.code is None:
            self.code = 1
        if self.kind == "arc" and self.code is None:
            self.code = 2
