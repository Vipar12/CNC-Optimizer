"""Parser for a conservative subset of common G-code dialects."""

from __future__ import annotations

from pathlib import Path

from cnc_optimizer.models.commands import GCodeCommand
from cnc_optimizer.models.program import GCodeProgram
from cnc_optimizer.parser.lexer import GCodeLexer
from cnc_optimizer.parser.modal_state import ModalStateTracker


class GCodeParser:
    """Parses a file or string into structured `GCodeCommand` objects."""

    def __init__(self) -> None:
        self.modal_state = ModalStateTracker()

    def _parse_line(self, line: str, line_number: int) -> GCodeCommand | None:
        tokens = GCodeLexer.tokenize_line(line, line_number)
        if not tokens:
            return None

        values: dict[str, float | int | str | None] = {}
        for token in tokens:
            values[token.kind] = float(token.value)

        has_motion_axis = any(letter in {"X", "Y", "Z"} for letter in values)
        motion_code = None
        g_value = values.get("G")
        if g_value is not None:
            g_code = int(g_value)
            if g_code in {0, 1, 2, 3}:
                motion_code = g_code
        elif has_motion_axis:
            motion_code = self.modal_state.current_motion_code()

        command = GCodeCommand(
            line_number=line_number,
            original_line=line,
            kind="command",
            code=(int(g_value) if g_value is not None else motion_code),
            letter="G" if g_value is not None or motion_code is not None else None,
            value=float(g_value) if g_value is not None else float(motion_code) if motion_code is not None else None,
        )

        if motion_code is not None:
            command.kind = "arc" if motion_code in {2, 3} else "motion"
            command.motion_type = "rapid" if motion_code == 0 else "cutting"
            command.letter = "G"
            command.value = float(motion_code)

        if "M" in values:
            command.code = int(values["M"])
            command.kind = "misc"
            command.letter = "M"
            command.value = float(values["M"])
            if command.code == 6:
                command.kind = "tool_change"

        if "T" in values:
            command.tool = int(values["T"])
            command.code = int(values["T"])
            command.kind = "tool_change"
            command.letter = "T"
            command.value = float(values["T"])

        if "F" in values:
            command.feed_rate = float(values["F"])
        if "S" in values:
            command.spindle_speed = float(values["S"])

        if "X" in values or "Y" in values or "Z" in values:
            command.x = values.get("X")
            command.y = values.get("Y")
            command.z = values.get("Z")
            command.i = values.get("I")
            command.j = values.get("J")
            command.k = values.get("K")

            if command.kind == "motion" or command.kind == "arc":
                current = self.modal_state.state.current_position
                next_x = current.x if values.get("X") is None else float(values["X"])
                next_y = current.y if values.get("Y") is None else float(values["Y"])
                next_z = current.z if values.get("Z") is None else float(values["Z"])

                if not self.modal_state.state.absolute_positioning:
                    next_x = current.x + (0.0 if values.get("X") is None else float(values["X"]))
                    next_y = current.y + (0.0 if values.get("Y") is None else float(values["Y"]))
                    next_z = current.z + (0.0 if values.get("Z") is None else float(values["Z"]))

                command.x = next_x
                command.y = next_y
                command.z = next_z

        # Apply any modal settings from the line before updating position.
        for letter, value in values.items():
            self.modal_state.apply_value(letter, value)

        if command.kind in {"motion", "arc"}:
            if command.x is not None or command.y is not None or command.z is not None:
                self.modal_state.update_position({
                    "X": command.x,
                    "Y": command.y,
                    "Z": command.z,
                })

        if command.kind == "tool_change" and command.tool is not None:
            self.modal_state.state.tool = command.tool

        if command.feed_rate is None:
            command.feed_rate = self.modal_state.state.feed_rate
        if command.spindle_speed is None:
            command.spindle_speed = self.modal_state.state.spindle_speed

        return command

    def parse_program(self, text: str, file_path: str | Path | None = None) -> GCodeProgram:
        program = GCodeProgram(file_path=file_path, modal_state=self.modal_state.state.copy())
        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith(";"):
                continue

            command = self._parse_line(raw_line, line_number)
            if command is not None:
                program.add_command(command)
                program.modal_state = self.modal_state.state.copy()

        return program


def parse_program(text: str) -> GCodeProgram:
    parser = GCodeParser()
    return parser.parse_program(text)


def parse_file(path: str | Path) -> GCodeProgram:
    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8")
    return parse_program(content)
