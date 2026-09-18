# Phase 1 Architecture Notes

## Goal

The first milestone focuses on parsing and understanding G-code without changing machining behavior. The parser must preserve the machine's modal state and produce a structured internal program representation that can later feed validation, optimization, and export layers.

## Design choices

- The parser uses a lightweight lexical pass to find command words such as G, M, X, Y, Z, F, S, and T.
- Modal state is stored separately from command objects so that the command stream can be reconstructed while still inheriting feed, spindle, and motion-state values from earlier commands.
- The program model keeps a list of structured commands instead of plain strings to make further analysis and validation easier.
- The current scope deliberately avoids optimization logic and controller-specific assumptions.

## Assumptions

- G-code is interpreted as a general router dialect with common modal behavior.
- Omitted axes inherit the previous value when a line is interpreted in absolute mode and tracks the latest known position.
- The initial analyzer reports distances and command counts conservatively rather than claiming physical machine time with controller-specific precision.
