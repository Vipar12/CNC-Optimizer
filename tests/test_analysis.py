from cnc_optimizer.analyzer.analyzer import compare_programs, summarize_program
from cnc_optimizer.parser.parser import parse_program


def test_summarize_program_reports_bounding_box_and_time_estimates():
    program = parse_program(
        """G21
G90
M3 S1200 F200
G0 X0 Y0 Z10
G1 X20 Y0 Z10 F200
G1 X20 Y15 Z10
M5
"""
    )

    stats = summarize_program(program)

    assert stats["total_lines"] == 7
    assert stats["rapid_moves"] == 1
    assert stats["cutting_moves"] == 2
    assert stats["min_x"] == 0.0
    assert stats["max_x"] == 20.0
    assert stats["min_y"] == 0.0
    assert stats["max_y"] == 15.0
    assert stats["bounding_box"] == {"min_x": 0.0, "max_x": 20.0, "min_y": 0.0, "max_y": 15.0, "min_z": 10.0, "max_z": 10.0}
    assert "estimated_time_seconds" in stats


def test_compare_programs_returns_measurable_deltas():
    original = parse_program(
        """G21
G90
G0 X0 Y0 Z0
G1 X10 Y0 F100
G1 X10 Y10 F100
"""
    )
    optimized = parse_program(
        """G21
G90
G0 X0 Y0 Z0
G1 X10 Y0 F100
G1 X10 Y10 F100
"""
    )

    comparison = compare_programs(original, optimized)

    assert comparison["rapid_distance_delta"] == 0.0
    assert comparison["cutting_distance_delta"] == 0.0
    assert comparison["estimated_time_delta_seconds"] == 0.0
