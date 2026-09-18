from pathlib import Path

from cnc_optimizer.workflow.upload import UploadJob, validate_uploaded_drawing


def test_validate_uploaded_drawing_accepts_supported_formats():
    job = validate_uploaded_drawing(Path("drawing.dxf"), "wordpress-upload")

    assert job.accepted is True
    assert job.extension == ".dxf"
    assert job.source == "wordpress-upload"
    assert job.requires_external_processing is True


def test_validate_uploaded_drawing_rejects_unsupported_format():
    job = validate_uploaded_drawing(Path("drawing.txt"), "wordpress-upload")

    assert job.accepted is False
    assert job.errors
    assert "unsupported" in job.errors[0].lower()


def test_upload_job_tracks_workflow_metadata():
    job = UploadJob.from_path(Path("part.dwg"), "wordpress-upload")

    assert job.extension == ".dwg"
    assert job.workflow == "cad_to_gcode"
    assert job.target_machine == "3-axis-router"
