import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
from myptv.segmentation_mod import calculate_BG_image_batch
from myptv.workflow import workflow
import yaml

def test_calculate_bg_image_batch_run_if_exists():
    test_root = 'temp_test_recs_bg'
    output_root = 'temp_test_output_bg'
    
    if os.path.exists(test_root): shutil.rmtree(test_root)
    if os.path.exists(output_root): shutil.rmtree(output_root)
    
    os.makedirs(os.path.join(test_root, 'rec1', 'cam1'))
    os.makedirs(os.path.join(test_root, 'rec1', 'cam2'))
    
    # Create dummy images
    for d in ['rec1/cam1', 'rec1/cam2']:
        with open(os.path.join(test_root, d, 'img_0.tif'), 'w') as f:
            f.write('dummy')
            
    # Create pre-existing output for cam1 but not cam2
    os.makedirs(os.path.join(output_root, 'rec1'), exist_ok=True)
    existing_bg_cam1 = os.path.join(output_root, 'rec1', 'BG_cam1.tif')
    with open(existing_bg_cam1, 'w') as f:
        f.write('existing')

    # Mock calculate_BG_image so it doesn't try to read/write real images
    with patch('myptv.segmentation_mod.calculate_BG_image') as mock_calc:
        # First call with run_if_exists=False: should skip cam1 and only call cam2
        calculate_BG_image_batch(test_root, output_root, '.tif', N_img=10, run_if_exists=False)
        
        # Check that mock_calc was only called for cam2 (since BG_cam1.tif exists)
        expected_save_name_cam2 = os.path.join(output_root, 'rec1', 'BG_cam2.tif')
        
        calls = [c[0] for c in mock_calc.call_args_list]
        
        assert len(calls) == 1
        assert calls[0][2] == expected_save_name_cam2
        
        mock_calc.reset_mock()
        
        # Second call with run_if_exists=True: should process both cam1 and cam2
        calculate_BG_image_batch(test_root, output_root, '.tif', N_img=10, run_if_exists=True)
        
        calls = [c[0] for c in mock_calc.call_args_list]
        assert len(calls) == 2
        save_names = {c[2] for c in calls}
        assert os.path.join(output_root, 'rec1', 'BG_cam1.tif') in save_names
        assert os.path.join(output_root, 'rec1', 'BG_cam2.tif') in save_names

    # Cleanup
    shutil.rmtree(test_root)
    shutil.rmtree(output_root)


def test_workflow_calculate_bg_image_batch(capsys):
    os.makedirs("temp_recs_wf/rec1/cam1", exist_ok=True)
    with open("temp_recs_wf/rec1/cam1/img_0.tif", "w") as f:
        f.write("dummy")

    params = [
        {"calculate_BG_image_batch": {
            "recordings_dir": "temp_recs_wf",
            "output_dir": "temp_output_wf",
            "image_extension": ".tif",
            "raw_format": False,
            "N_img": 10,
            "run_if_exists": False
        }}
    ]

    with open("temp_params_wf.yml", "w") as f:
        yaml.dump(params, f)

    # Pre-create background for cam1
    os.makedirs("temp_output_wf/rec1", exist_ok=True)
    with open("temp_output_wf/rec1/BG_cam1.tif", "w") as f:
        f.write("existing")

    with patch('myptv.segmentation_mod.calculate_BG_image') as mock_calc:
        wf = workflow("temp_params_wf.yml", None)
        wf.do_calculate_BG_image_batch()
        
        # Since run_if_exists=False, it should skip it and mock_calc shouldn't be called
        assert mock_calc.call_count == 0
        
    captured = capsys.readouterr()
    assert "SKIP" in captured.out

    # Cleanup
    if os.path.exists("temp_params_wf.yml"): os.remove("temp_params_wf.yml")
    for d in ["temp_recs_wf/rec1/cam1", "temp_recs_wf/rec1", "temp_recs_wf", 
              "temp_output_wf/rec1/BG_cam1.tif", "temp_output_wf/rec1", "temp_output_wf"]:
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)
