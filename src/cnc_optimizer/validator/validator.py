"""Conservative validation checks for basic machine and program safety."""

from __future__ import annotations

from cnc_optimizer.models.operations import ValidationIssue
from cnc_optimizer.models.program import GCodeProgram


def validate_program(program: GCodeProgram) -> list[ValidationIssue]:
    """Return warnings/errors for suspicious or malformed program structure."""

    issues: list[ValidationIssue] = []
    last_feed = None
    last_spindle = None

    for command in program.commands:
        if command.kind in {"motion", "arc"}:
            if command.z is not None and command.z < -100.0:
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        rule_id="Z001",
                        line_number=command.line_number,
                        message="Z axis appears below a typical safe working envelope.",
                        command=command,
                    )
                )

        if command.kind in {"motion", "arc"} and command.code in {1, 2, 3}:
            if command.feed_rate is None:
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        rule_id="F001",
                        line_number=command.line_number,
                        message="Cutting motion is missing a feed-rate value; the program depends on a modal feed that may not be active.",
                        command=command,
                    )
                )

        if command.kind in {"motion", "arc"} and command.code == 0:
            if command.z is not None and command.z < -200.0:
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        rule_id="Z002",
                        line_number=command.line_number,
                        message="Rapid Z movement occurs far below the configured safe Z height.",
                        command=command,
                    )
                )

        if command.kind == "tool_change" and command.tool is None:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    rule_id="T001",
                    line_number=command.line_number,
                    message="Tool command is missing a tool number.",
                    command=command,
                )
            )

        if command.kind == "misc" and command.code is not None and command.code == 5:
            if not any(other.kind == "tool_change" for other in program.commands[: program.commands.index(command)]):
                issues.append(
                    ValidationIssue(
                        severity="INFO",
                        rule_id="M005",
                        line_number=command.line_number,
                        message="Spindle stop occurs without an explicit tool-change boundary; treat as a state change only.",
                        command=command,
                    )
                )

        if command.spindle_speed is not None:
            last_spindle = command.spindle_speed

        if command.feed_rate is not None:
            last_feed = command.feed_rate

    if not program.commands:
        issues.append(
            ValidationIssue(
                severity="INFO",
                rule_id="P001",
                line_number=None,
                message="Program is empty.",
                command=None,
            )
        )

    if not any(command.kind in {"motion", "arc"} for command in program.commands):
        issues.append(
            ValidationIssue(
                severity="WARNING",
                rule_id="P002",
                line_number=None,
                message="Program contains no motion commands.",
                command=None,
            )
        )

    return issues
