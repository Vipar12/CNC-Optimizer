from cnc_optimizer.analyzer.operations import detect_operations
from cnc_optimizer.parser.parser import parse_program
from cnc_optimizer.validator.validator import validate_program


def test_detect_operations_splits_on_tool_changes_and_retracts():
    program = parse_program(
        """T1 M6
M3 S1200
G0 Z5
G1 X0 Y0
X10 Y0
G0 Z20
T2 M6
M3 S1500
G1 X0 Y10
X10 Y10
"""
    )

    operations = detect_operations(program)

    assert len(operations) >= 2
    assert operations[0].tool == 1
    assert operations[1].tool == 2
    assert operations[0].start_position.z <= operations[0].end_position.z


def test_validate_program_reports_missing_feed_for_cutting_motion():
    program = parse_program(
        """G21
G90
G1 X0 Y0 Z0
G1 X10 Y10
"""
    )

    issues = validate_program(program)

    assert any(issue.rule_id == "F001" for issue in issues)
    assert any(issue.severity == "WARNING" for issue in issues)
