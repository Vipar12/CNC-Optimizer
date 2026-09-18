"""Command-line entry point for Phase 2 analysis and comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

from cnc_optimizer.analyzer.analyzer import compare_programs, summarize_program
from cnc_optimizer.parser.parser import parse_file


def _render_summary(path: Path) -> None:
    program = parse_file(path)
    stats = summarize_program(program)
    print(f"Program: {path}")
    print(f"Lines: {stats['total_lines']}")
    print(f"Motion commands: {stats['motion_commands']}")
    print(f"Rapid moves: {stats['rapid_moves']}")
    print(f"Cutting moves: {stats['cutting_moves']}")
    print(f"Rapid distance: {stats['rapid_distance']:.2f} mm")
    print(f"Cutting distance: {stats['cutting_distance']:.2f} mm")
    print(f"Tool changes: {stats['tool_changes']}")
    print(f"Tools used: {sorted(stats['tools_used'])}")
    print(f"Feed-rate changes: {stats['feed_changes']}")
    print(f"Spindle changes: {stats['spindle_changes']}")
    print(f"Bounding box: {stats['bounding_box']}")
    print(f"Estimated time: {stats['estimated_time_seconds']:.2f} s")


def _render_comparison(original_path: Path, optimized_path: Path) -> None:
    original = parse_file(original_path)
    optimized = parse_file(optimized_path)
    comparison = compare_programs(original, optimized)
    print(f"Original: {original_path}")
    print(f"Optimized: {optimized_path}")
    print(f"Rapid distance delta: {comparison['rapid_distance_delta']:.2f} mm")
    print(f"Cutting distance delta: {comparison['cutting_distance_delta']:.2f} mm")
    print(f"Estimated time delta: {comparison['estimated_time_delta_seconds']:.2f} s")


def main() -> None:
    parser = argparse.ArgumentParser(prog="cnc-optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a G-code file")
    analyze.add_argument("path")

    compare = subparsers.add_parser("compare", help="Compare two G-code programs")
    compare.add_argument("original")
    compare.add_argument("optimized")

    args = parser.parse_args()

    if args.command == "analyze":
        _render_summary(Path(args.path))
    elif args.command == "compare":
        _render_comparison(Path(args.original), Path(args.optimized))
    else:
        parser.error(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
