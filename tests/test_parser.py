from pathlib import Path

from cnc_optimizer.analyzer.analyzer import summarize_program
from cnc_optimizer.parser.parser import parse_file, parse_program


def test_parse_program_handles_modal_commands_and_inherited_values():
    program = parse_program(
        """G21
G90
G1 X10 Y20 F100
X20
Y30
"""
    )

    assert program.total_lines == 5
    assert len(program.commands) == 5
    assert program.commands[2].kind == "motion"
    assert program.commands[2].x == 10
    assert program.commands[2].y == 20
    assert program.commands[2].feed_rate == 100

    assert program.commands[3].kind == "motion"
    assert program.commands[3].x == 20
    assert program.commands[3].y == 20
    assert program.commands[3].feed_rate == 100

    assert program.commands[4].kind == "motion"
    assert program.commands[4].x == 20
    assert program.commands[4].y == 30
    assert program.commands[4].feed_rate == 100

    assert program.modal_state.absolute_positioning is True
    assert program.modal_state.feed_rate == 100


def test_parse_program_handles_arcs_comments_and_tool_commands():
    program = parse_program(
        """G17
M3 S1500
G1 X0 Y0 Z0
G2 X10 Y10 I5 J0 F300
; comment
T1 M6
"""
    )

    assert len(program.commands) == 5
    assert program.commands[3].kind == "arc"
    assert program.commands[3].x == 10
    assert program.commands[3].y == 10
    assert program.commands[3].i == 5
    assert program.commands[3].j == 0
    assert program.commands[3].feed_rate == 300
    assert program.modal_state.spindle_speed == 1500
    assert program.modal_state.tool == 1


def test_parse_file_and_summarize_program():
    fixture = Path(__file__).parent / "fixtures" / "gcode" / "sample.nc"
    program = parse_file(fixture)
    stats = summarize_program(program)

    assert program.total_lines == 10
    assert stats["motion_commands"] >= 4
    assert stats["rapid_moves"] >= 1
    assert stats["cutting_moves"] >= 1
    assert stats["tools_used"] == {1}
