"""Top-level program model for parsed G-code."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .commands import GCodeCommand
from .machine_state import ModalState


@dataclass(slots=True)
class GCodeProgram:
    """Parsed G-code program with embedded modal state and command stream."""

    commands: list[GCodeCommand] = field(default_factory=list)
    modal_state: ModalState = field(default_factory=ModalState)
    file_path: str | Path | None = None

    @property
    def total_lines(self) -> int:
        return len(self.commands)

    def add_command(self, command: GCodeCommand) -> None:
        self.commands.append(command)
