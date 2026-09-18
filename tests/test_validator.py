from cnc_optimizer.parser.parser import parse_program
from cnc_optimizer.validator.validator import validate_program


def test_validate_program_flags_missing_start_and_rapid_z_risk():
    program = parse_program(
        """G21
G90
G0 Z-200
G1 X0 Y0
"""
    )

    issues = validate_program(program)

    assert any(issue.rule_id == "Z001" for issue in issues)
    assert any(issue.rule_id == "F001" for issue in issues)


def test_validate_program_reports_empty_program():
    program = parse_program("")
    issues = validate_program(program)

    assert any(issue.rule_id == "P001" for issue in issues)
