"""Basic semantic operation detection for a G-code program."""

from __future__ import annotations

from cnc_optimizer.models.machine_state import MachinePosition
from cnc_optimizer.models.operations import Operation
from cnc_optimizer.models.program import GCodeProgram


def detect_operations(program: GCodeProgram) -> list[Operation]:
    """Partition a program into tool-based operations with conservative boundaries."""

    operations: list[Operation] = []
    current_commands: list = []
    current_tool: int | None = None
    start_position = MachinePosition()
    position = MachinePosition()
    start_line: int | None = None

    for command in program.commands:
        if command.kind == "tool_change" and command.tool is not None:
            if current_commands:
                op = Operation(
                    name=f"Operation {len(operations) + 1}",
                    tool=current_tool,
                    start_line=start_line,
                    end_line=command.line_number - 1,
                    commands=current_commands,
                    start_position=start_position,
                    end_position=position,
                )
                operations.append(op)
            current_tool = command.tool
            current_commands = []
            start_line = command.line_number
            start_position = position
            continue

        if command.kind in {"motion", "arc"}:
            if current_tool is None:
                current_tool = program.modal_state.tool
            if start_line is None:
                start_line = command.line_number
                start_position = position
            current_commands.append(command)
            if command.x is not None:
                position.x = command.x
            if command.y is not None:
                position.y = command.y
            if command.z is not None:
                position.z = command.z

        elif command.kind in {"misc"}:
            if command.code == 5 and current_commands:
                op = Operation(
                    name=f"Operation {len(operations) + 1}",
                    tool=current_tool,
                    start_line=start_line,
                    end_line=command.line_number,
                    commands=current_commands,
                    start_position=start_position,
                    end_position=position,
                )
                operations.append(op)
                current_commands = []
                start_line = command.line_number + 1
                start_position = position
            else:
                current_commands.append(command)

    if current_commands:
        operations.append(
            Operation(
                name=f"Operation {len(operations) + 1}",
                tool=current_tool,
                start_line=start_line,
                end_line=program.commands[-1].line_number if program.commands else None,
                commands=current_commands,
                start_position=start_position,
                end_position=position,
            )
        )

    if not operations and program.commands:
        operations.append(
            Operation(
                name="Operation 1",
                tool=program.modal_state.tool,
                start_line=program.commands[0].line_number,
                end_line=program.commands[-1].line_number,
                commands=program.commands,
                start_position=MachinePosition(),
                end_position=position,
            )
        )

    return operations
