"""Simple G-code writer for round-tripping parsed programs."""

from __future__ import annotations

from cnc_optimizer.models.program import GCodeProgram


class GCodeWriter:
    """Exports a parsed program back to a text-based G-code representation."""

    def write_program(self, program: GCodeProgram) -> str:
        lines: list[str] = []
        for command in program.commands:
            if command.kind in {"motion", "arc"}:
                prefix = f"G{command.code}" if command.code is not None else "G1"
                values: list[str] = []
                for axis in ("X", "Y", "Z"):
                    value = getattr(command, axis.lower())
                    if value is not None:
                        values.append(f"{axis}{value:g}")
                if command.feed_rate is not None:
                    values.append(f"F{command.feed_rate:g}")
                if command.spindle_speed is not None:
                    values.append(f"S{command.spindle_speed:g}")
                if values:
                    lines.append(f"{prefix} {' '.join(values)}")
                else:
                    lines.append(prefix)
                continue

            if command.kind == "tool_change":
                if command.tool is not None:
                    lines.append(f"T{command.tool}")
                continue

            if command.kind == "misc":
                if command.code is not None:
                    lines.append(f"M{command.code}")
                continue

            if command.kind == "command":
                if command.code is not None:
                    lines.append(f"G{command.code:g}")
                continue

        return "\n".join(lines) + ("\n" if lines else "")
