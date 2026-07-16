import pytest
import os
import yaml
import sys
from myptv.workflow import workflow

def test_batch_segmentation_dry_run(capsys):
    """Verify that do_batch_segmentation correctly sets up and outputs dry run logs without running subprocesses."""
    # Create temporary directories mimicking recording folder structure
    os.makedirs("temp_recs/Rec01/Cam1", exist_ok=True)
    os.makedirs("temp_recs/Rec01/Cam2", exist_ok=True)
    os.makedirs("temp_masks", exist_ok=True)
    os.makedirs("temp_bgs/Rec01", exist_ok=True)

    # Save dummy files
    with open("temp_masks/mask_Cam1.tif", "w") as f: f.write("dummy mask")
    with open("temp_bgs/Rec01/bg_Cam1.tif", "w") as f: f.write("dummy bg")

    params = [
        {"segmentation": {
            "plot_result": False,
            "image_extension": ".png",
            "threshold": 10
        }},
        {"batch_segmentation": {
            "recordings_dir": "temp_recs",
            "ptv_results_dir": "temp_ptv_results",
            "sub_dir": "particles",
            "results_csv": "temp_ptv_results/results.csv",
            "run_if_exists": True,
            "save_blobs": False,
            "cams": "Cam1",
            "bg_dir": "temp_bgs",
            "masks_dir": "temp_masks",
            "dry_run": True,
            "blur_sigma": 1.2,
            "min_mass": 30,
            "camera_thresholds": {"Cam1": 15},
            "min_xsize": {"Cam1": 2},
            "min_ysize": {"Cam1": 3},
            "max_xsize": 5,
            "camera_max_masses": {"Cam1": 500}
        }}
    ]

    with open("temp_params_test.yml", "w") as f:
        yaml.dump(params, f)

    # Initialize workflow and execute batch_segmentation
    wf = workflow("temp_params_test.yml", None)
    wf.do_batch_segmentation()

    captured = capsys.readouterr()

    # Clean up
    for p in ["temp_masks/mask_Cam1.tif", "temp_bgs/Rec01/bg_Cam1.tif", "temp_params_test.yml"]:
        if os.path.exists(p): os.remove(p)
    for d in ["temp_recs/Rec01/Cam1", "temp_recs/Rec01/Cam2", "temp_recs/Rec01", "temp_recs", "temp_masks", "temp_bgs/Rec01", "temp_bgs"]:
        if os.path.exists(d): 
            try:
                os.rmdir(d)
            except:
                pass

    assert "DRY RUN" in captured.out
    assert "Rec=Rec01 | Cam=Cam1" in captured.out
    assert "threshold=15" in captured.out
    assert "blur_sigma=1.2" in captured.out
    assert "min_mass=30" in captured.out
    assert "max_mass=500" in captured.out
    assert "min_xsize=2" in captured.out
    assert "min_ysize=3" in captured.out
    assert "max_xsize=5" in captured.out
    assert "max_ysize=Default" in captured.out
    assert "Recording-specific" in captured.out
