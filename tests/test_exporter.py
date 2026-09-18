from cnc_optimizer.exporter.gcode_writer import GCodeWriter
from cnc_optimizer.parser.parser import parse_program


def test_gcode_writer_round_trips_basic_program():
    program = parse_program(
        """G21
G90
M3 S1200
G1 X0 Y0 F100
X10 Y0
"""
    )

    writer = GCodeWriter()
    exported = writer.write_program(program)
    round_trip = parse_program(exported)

    assert len(round_trip.commands) == len(program.commands)
    assert round_trip.commands[0].kind == program.commands[0].kind
    assert round_trip.commands[-1].x == 10
    assert round_trip.commands[-1].y == 0
