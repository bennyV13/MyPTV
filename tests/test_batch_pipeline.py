import pytest
import os
import yaml
import sys
from myptv.workflow import workflow

def test_batch_pipeline_dry_run(capsys):
    """Verify that do_batch_pipeline correctly sets up and outputs dry run logs without running subprocesses."""
    # Create temporary directories mimicking recording folder structure
    os.makedirs("temp_recs_pipe/rec14", exist_ok=True)
    os.makedirs("temp_recs_pipe/rec17", exist_ok=True)

    params = [
        {"matching": {
            "camera_names": "Cam1, Cam2",
            "ROI": "0,10,0,10,0,10",
            "voxel_size": 0.1,
            "N0": 100,
            "max_err": 0.5,
            "min_cam_match": 2,
            "frame_start": 0,
            "N_frames": 10,
            "march_forwards": True,
            "march_backwards": False,
            "save_name": "temp_results/particles"
        }},
        {"batch_pipeline": {
            "recordings_dir": "temp_recs_pipe",
            "ptv_results_dir": "temp_ptv_results",
            "sub_dir": "particles",
            "results_csv": "temp_ptv_results/pipeline_results.csv",
            "run_if_exists": False,
            "run_matching": True,
            "run_tracking": True,
            "run_smoothing": True,
            "run_orientations": False,
            "recordings": "rec14, rec17",
            "cams": "Cam1, Cam2",
            "dry_run": True
        }}
    ]

    with open("temp_params_pipe_test.yml", "w") as f:
        yaml.dump(params, f)

    # Initialize workflow and execute batch_pipeline
    wf = workflow("temp_params_pipe_test.yml", None)
    wf.do_batch_pipeline()

    captured = capsys.readouterr()

    # Clean up
    if os.path.exists("temp_params_pipe_test.yml"): os.remove("temp_params_pipe_test.yml")
    for d in ["temp_recs_pipe/rec14", "temp_recs_pipe/rec17", "temp_recs_pipe"]:
        if os.path.exists(d): os.rmdir(d)

    assert "DRY RUN: Planned batch pipeline execution" in captured.out
    assert "Recording: rec14" in captured.out
    assert "Recording: rec17" in captured.out
    assert "Matching: RUN" in captured.out
    assert "Tracking: RUN" in captured.out
    assert "Smoothing: RUN" in captured.out
    assert "Orientations: SKIP" in captured.out


def test_batch_pipeline_dry_run_with_orientations(capsys):
    """Verify dry run when orientations are enabled (RUN)."""
    os.makedirs("temp_recs_pipe/rec14", exist_ok=True)

    params = [
        {"matching": {
            "camera_names": "Cam1, Cam2",
            "ROI": "0,10,0,10,0,10",
            "voxel_size": 0.1,
            "N0": 100,
            "max_err": 0.5,
            "min_cam_match": 2,
            "frame_start": 0,
            "N_frames": 10,
            "march_forwards": True,
            "march_backwards": False,
            "save_name": "temp_results/particles"
        }},
        {"batch_pipeline": {
            "recordings_dir": "temp_recs_pipe",
            "ptv_results_dir": "temp_ptv_results",
            "sub_dir": "particles",
            "results_csv": "temp_ptv_results/pipeline_results.csv",
            "run_if_exists": False,
            "run_matching": True,
            "run_tracking": True,
            "run_smoothing": True,
            "run_orientations": True,
            "recordings": "rec14",
            "cams": "Cam1, Cam2",
            "dry_run": True
        }}
    ]

    with open("temp_params_pipe_test.yml", "w") as f:
        yaml.dump(params, f)

    wf = workflow("temp_params_pipe_test.yml", None)
    wf.do_batch_pipeline()

    captured = capsys.readouterr()

    # Clean up
    if os.path.exists("temp_params_pipe_test.yml"): os.remove("temp_params_pipe_test.yml")
    for d in ["temp_recs_pipe/rec14", "temp_recs_pipe"]:
        if os.path.exists(d): os.rmdir(d)

    assert "DRY RUN: Planned batch pipeline execution" in captured.out
    assert "Recording: rec14" in captured.out
    assert "Matching: RUN" in captured.out
    assert "Tracking: RUN" in captured.out
    assert "Smoothing: RUN" in captured.out
    assert "Orientations: RUN" in captured.out

