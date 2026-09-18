# CNC Optimizer

A lightweight Python project for parsing, analyzing, validating, and safely comparing 3-axis CNC G-code. The design stays modular, conservative, and testable so it can grow without hard-coding a single controller or CAM workflow.

## Project status

This repository currently includes the following working layers:

- Python package structure and project configuration
- G-code models for commands, machine state, and program structure
- lexer and parser for common router-style G-code
- modal state tracking for inherited feed, spindle, and position data
- operation detection based on tool and state boundaries
- analyzer for distance, bounding box, and time estimates
- validation for suspicious or malformed programs
- safe optimization framework for redundant modal commands only
- G-code export for round-tripping parsed programs
- upload validation for CAD files designed for future conversion workflows
- CLI entry points for analysis and comparison

## Architecture

The design keeps parsing, analysis, validation, optimization, and output generation separate and intentionally conservative.

Core modules:

- `src/cnc_optimizer/parser/` for lexical parsing and modal tracking
- `src/cnc_optimizer/analyzer/` for program metrics and comparisons
- `src/cnc_optimizer/validator/` for structural and safety warnings
- `src/cnc_optimizer/optimizer/` for state-safe optimization rules
- `src/cnc_optimizer/exporter/` for writing G-code back out
- `src/cnc_optimizer/workflow/` for upload validation and CAD-to-G-code workflow metadata

## CLI

Basic analysis is available via:

```bash
cnc-optimizer analyze tests/fixtures/gcode/sample.nc
```

Comparison between two programs is also available:

```bash
cnc-optimizer compare original.nc optimized.nc
```

## WordPress / drag-and-drop CAD workflow

This project does not directly convert DWG or CAD geometry into G-code. Instead, it includes a conservative upload-validation layer intended for a future workflow such as:

- user drag-and-drop upload onto a WordPress or custom web form
- file validation for supported drawing types
- handoff to an external CAD/CAM workflow such as FreeCAD CAM or another conversion tool
- G-code returned to CNC Optimizer for parse, analyze, validate, and compare

This keeps the CNC core independent from proprietary CAD software and makes the upload stage testable without assuming a specific conversion pipeline.

## Safe design rules

- Never optimize purely for shorter text output
- Never change machining behavior without an explicitly modeled safety reason
- Keep optimization rules conservative and independently testable
- Treat potentially unsafe transformations as opportunities to report, not automatic edits

## Assumptions

- The initial implementation targets a generic 3-axis router dialect instead of a single vendor controller.
- Feed and spindle state is modal and inherited when omitted from later lines.
- Time and distance estimates are intentionally simple and conservative.
- High-end CAD conversion is handled by external tooling, not embedded directly in the CNC optimizer.

## Testing

The project uses pytest and includes regression tests for parsing, analysis, validation, optimization, export, and upload workflow checks.

```bash
python -m pytest -q
```
