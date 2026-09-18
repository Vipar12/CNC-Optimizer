"""Operation and validation models used for semantic grouping and checks."""

from __future__ import annotations

from dataclasses import dataclass, field

from cnc_optimizer.models.commands import GCodeCommand
from cnc_optimizer.models.machine_state import MachinePosition


@dataclass(slots=True)
class Operation:
    """A semantically meaningful region of a CNC program."""

    name: str
    tool: int | None = None
    start_line: int | None = None
    end_line: int | None = None
    commands: list[GCodeCommand] = field(default_factory=list)
    start_position: MachinePosition = field(default_factory=MachinePosition)
    end_position: MachinePosition = field(default_factory=MachinePosition)


@dataclass(slots=True)
class ValidationIssue:
    """A validation finding with severity and rule metadata."""

    severity: str
    rule_id: str
    line_number: int | None
    message: str
    command: GCodeCommand | None = None
