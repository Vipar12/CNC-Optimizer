from cnc_optimizer.optimizer.optimizer import optimize_program
from cnc_optimizer.parser.parser import parse_program


def test_optimize_program_removes_redundant_modal_commands():
    program = parse_program(
        """G21
G90
M3 S1200
F100
G1 X0 Y0
F100
G1 X10 Y0
"""
    )

    result = optimize_program(program)

    assert result["changes_applied"] >= 1
    assert result["rule_names"]
    assert len(result["optimized_program"].commands) < len(program.commands)


def test_optimize_program_reports_no_change_when_safe_rules_do_not_apply():
    program = parse_program(
        """G21
G90
M3 S1200
G1 X0 Y0 F100
G1 X10 Y0 F100
"""
    )

    result = optimize_program(program)

    assert result["changes_applied"] == 0
    assert result["optimized_program"].commands == program.commands
