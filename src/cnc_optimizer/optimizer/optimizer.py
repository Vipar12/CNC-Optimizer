"""Minimal, safety-first optimizer framework.

This layer intentionally implements only transformations that are provably safe
in terms of machine state semantics. It does not reorder operations or alter the
motion path itself.
"""

from __future__ import annotations

from cnc_optimizer.models.commands import GCodeCommand
from cnc_optimizer.models.program import GCodeProgram


def _remove_redundant_modal_commands(program: GCodeProgram) -> tuple[GCodeProgram, int]:
    """Remove duplicate explicit modal commands that do not change machine state."""

    new_commands: list[GCodeCommand] = []
    last_feed: float | None = None
    last_spindle: float | None = None
    removed = 0

    for command in program.commands:
        is_redundant_feed = (
            command.kind == "command"
            and command.feed_rate is not None
            and last_feed == command.feed_rate
        )
        is_redundant_spindle = (
            command.kind == "command"
            and command.spindle_speed is not None
            and last_spindle == command.spindle_speed
        )

        if is_redundant_feed or is_redundant_spindle:
            removed += 1
            continue

        if command.kind == "command" and command.feed_rate is not None:
            last_feed = command.feed_rate
            new_commands.append(command)
            continue

        if command.kind == "command" and command.spindle_speed is not None:
            last_spindle = command.spindle_speed
            new_commands.append(command)
            continue

        if command.kind in {"motion", "arc", "tool_change", "misc"}:
            new_commands.append(command)
            continue

        new_commands.append(command)

    optimized = GCodeProgram(commands=new_commands, modal_state=program.modal_state.copy(), file_path=program.file_path)
    return optimized, removed


def optimize_program(program: GCodeProgram) -> dict[str, object]:
    """Apply only the safe, redundant-modal command optimization rule."""

    optimized, removed = _remove_redundant_modal_commands(program)
    rule_names: list[str] = []
    if removed > 0:
        rule_names.append("remove_redundant_modal_commands")

    return {
        "optimized_program": optimized,
        "changes_applied": removed,
        "rule_names": rule_names,
        "safety_classification": "safe",
    }
