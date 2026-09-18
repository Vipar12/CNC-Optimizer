"""Upload handling and CAD-to-G-code workflow metadata.

This layer does not automate an external CAD system itself. It instead validates
that a user-supplied file is a supported drawing candidate and marks it for a
future CAD-to-G-code processing pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_DRAWING_EXTENSIONS = {".dxf", ".dwg", ".svg", ".step", ".stp"}


@dataclass(slots=True)
class UploadJob:
    """A user-uploaded drawing that is destined for an external CAD workflow."""

    file_name: str
    source: str
    accepted: bool = False
    extension: str = ""
    workflow: str = "cad_to_gcode"
    target_machine: str = "3-axis-router"
    requires_external_processing: bool = True
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: str | Path, source: str) -> "UploadJob":
        candidate = Path(path)
        return validate_uploaded_drawing(candidate, source)


def validate_uploaded_drawing(path: str | Path, source: str) -> UploadJob:
    """Validate an uploaded drawing and return structured workflow metadata."""

    candidate = Path(path)
    extension = candidate.suffix.lower()
    errors: list[str] = []

    if extension not in SUPPORTED_DRAWING_EXTENSIONS:
        errors.append(f"Unsupported file type: {extension or 'no extension'}")

    job = UploadJob(
        file_name=candidate.name,
        source=source,
        accepted=not errors,
        extension=extension,
        workflow="cad_to_gcode",
        target_machine="3-axis-router",
        requires_external_processing=True,
        errors=errors,
    )
    return job
