# WordPress Drag-and-Drop CAD Upload Design

## Goal

Support a WordPress-friendly upload flow where a user drags a drawing file onto a designated upload area and the application identifies it as a candidate for an external CAD-to-G-code workflow.

## Current design

This project does not directly render or convert CAD geometry. Instead, the upload step validates the file and marks it for a future pipeline:

SolidWorks / DXF / DWG / STEP
→ WordPress upload area
→ CNC Optimizer validation
→ external CAD/CAM job (such as FreeCAD CAM)
→ generated G-code
→ parse/analyze/validate/optimize in CNC Optimizer

## Safety model

- Accept only supported file extensions.
- Reject unsupported or malformed files early.
- Keep the CAD/CAM conversion step outside the core CNC parser logic.
- Treat conversion to G-code as an external production step, not as an embedded conversion engine.

## Why this is the correct architecture

The CNC optimizer should remain independently testable and controller-agnostic. CAD conversion is a separate domain with its own tools, file format issues, and process assumptions. This keeps the project maintainable while leaving room for future FreeCAD integration.
