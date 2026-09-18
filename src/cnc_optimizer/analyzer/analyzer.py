"""Program analysis and summary generation for safe analyzer metrics."""

from __future__ import annotations

from math import hypot

from cnc_optimizer.models.program import GCodeProgram


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return hypot(b[0] - a[0], hypot(b[1] - a[1], b[2] - a[2]))


def summarize_program(program: GCodeProgram) -> dict[str, object]:
    """Return conservative program statistics, bounding-box data, and time estimates."""

    rapid_moves = 0
    cutting_moves = 0
    motion_commands = 0
    rapid_distance = 0.0
    cutting_distance = 0.0
    tool_changes = 0
    tools_used: set[int] = set()
    spindle_changes = 0
    feed_changes = 0
    previous_position = (0.0, 0.0, 0.0)
    previous_feed = None
    previous_spindle = None

    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")
    min_z = float("inf")
    max_z = float("-inf")

    for command in program.commands:
        if command.kind in {"motion", "arc"}:
            motion_commands += 1
            current_position = (
                command.x if command.x is not None else previous_position[0],
                command.y if command.y is not None else previous_position[1],
                command.z if command.z is not None else previous_position[2],
            )

            move_distance = _distance(previous_position, current_position)
            if command.code == 0:
                rapid_moves += 1
                rapid_distance += move_distance
            elif command.code in {1, 2, 3}:
                cutting_moves += 1
                cutting_distance += move_distance

            previous_position = current_position
            min_x = min(min_x, current_position[0])
            max_x = max(max_x, current_position[0])
            min_y = min(min_y, current_position[1])
            max_y = max(max_y, current_position[1])
            min_z = min(min_z, current_position[2])
            max_z = max(max_z, current_position[2])

        if command.kind == "tool_change":
            tool_changes += 1
            if command.tool is not None:
                tools_used.add(command.tool)

        if command.spindle_speed is not None and previous_spindle is not None:
            if command.spindle_speed != previous_spindle:
                spindle_changes += 1
        previous_spindle = command.spindle_speed if command.spindle_speed is not None else previous_spindle

        if command.feed_rate is not None and previous_feed is not None:
            if command.feed_rate != previous_feed:
                feed_changes += 1
        previous_feed = command.feed_rate if command.feed_rate is not None else previous_feed

    if min_x == float("inf"):
        min_x = 0.0
        max_x = 0.0
        min_y = 0.0
        max_y = 0.0
        min_z = 0.0
        max_z = 0.0

    total_travel = rapid_distance + cutting_distance
    rapid_time_seconds = rapid_distance / 600.0 if rapid_distance > 0 else 0.0
    cutting_time_seconds = cutting_distance / 200.0 if cutting_distance > 0 else 0.0
    estimated_time_seconds = rapid_time_seconds + cutting_time_seconds

    stats: dict[str, object] = {
        "total_lines": program.total_lines,
        "motion_commands": motion_commands,
        "rapid_moves": rapid_moves,
        "cutting_moves": cutting_moves,
        "rapid_distance": rapid_distance,
        "cutting_distance": cutting_distance,
        "tool_changes": tool_changes,
        "tools_used": tools_used,
        "spindle_changes": spindle_changes,
        "feed_changes": feed_changes,
        "total_xy_travel": total_travel,
        "total_xyz_travel": total_travel,
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": min_z,
        "max_z": max_z,
        "bounding_box": {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
        },
        "estimated_time_seconds": estimated_time_seconds,
        "estimated_rapid_time_seconds": rapid_time_seconds,
        "estimated_cutting_time_seconds": cutting_time_seconds,
    }
    return stats


def compare_programs(original: GCodeProgram, optimized: GCodeProgram) -> dict[str, float]:
    """Compare two program summaries for a conservative before/after report."""

    original_stats = summarize_program(original)
    optimized_stats = summarize_program(optimized)

    rapid_delta = float(optimized_stats["rapid_distance"]) - float(original_stats["rapid_distance"])
    cutting_delta = float(optimized_stats["cutting_distance"]) - float(original_stats["cutting_distance"])
    time_delta = float(optimized_stats["estimated_time_seconds"]) - float(original_stats["estimated_time_seconds"])

    return {
        "rapid_distance_delta": rapid_delta,
        "cutting_distance_delta": cutting_delta,
        "estimated_time_delta_seconds": time_delta,
    }
