import os
import sys
import copy
import yaml
import csv
import subprocess
import re
import argparse
from datetime import datetime

# Does this rotate the mask as well?

"""
batch_segmentation_ptv_results.py

Runs MyPTV segmentation for every (Recording, Camera) pair under recordings_dir.
Saves results to: <ptv_results_dir>/<Rec>_data/<sub_dir>/blobs_<cam>

master_config.yml should contain:
  params_file: "path/to/params_file.yml"
  recordings_dir: "path/to/recordings"         # contains Rec*/Cam* image folders
  ptv_results_dir: "path/to/ptv_results"      # base directory for results
  sub_dir: "particles"                        # e.g., "particles" or "fibers"
  results_csv: "path/to/batch_results.csv"
  run_if_exists: true/false                   # If false, skip if blob file exists
  save_blobs: true/false                      # If false, delete after counting
  cams: ["Cam1","Cam2","Cam3","Cam4"]         # optional filter list
  camera_thresholds:                         # optional, for camera-specific thresholds
    Cam1: 5
    Cam2: 5
    ...
"""

# ---------------- utils ----------------

def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_yaml_config(data, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def run_segmentation_workflow(params_path):
    """Run: python workflow.py <params_path> segmentation"""
    # Use absolute path for workflow.py
    workflow_path = "/Users/user/Desktop/Research/Data_Analysis/MyPTV_analysis/workflow.py"
    
    # Use absolute path for params to ensure robust logging directory resolution
    abs_params_path = os.path.abspath(params_path)
    cwd = os.path.dirname(abs_params_path)
    
    cmd = [sys.executable, workflow_path, abs_params_path, "segmentation"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"ERROR: Workflow failed for {params_path}")
        print(result.stderr.strip())
        return result.stdout, result.stderr
    return result.stdout, result.stderr

def extract_blob_count(stdout_text):
    m = re.search(r"blobs found:\s*(\d+)", stdout_text)
    return int(m.group(1)) if m else 0

def ensure_list_of_dicts(y):
    if isinstance(y, list):
        return y
    if isinstance(y, dict):
        return [{k: v} for k, v in y.items()]
    raise TypeError("params file must be a list-of-dicts or a dict")

def get_existing_file_case_insensitive(directory, filename):
    """Returns the existing filename in the directory that matches case-insensitively, or None."""
    if not os.path.exists(directory):
        return None
    files = os.listdir(directory)
    filename_lower = filename.lower()
    for f in files:
        if f.lower() == filename_lower:
            return os.path.join(directory, f)
    return None

def find_block(params, name):
    for d in params:
        if name in d:
            return d[name]
    new = {}
    params.append({name: new})
    return new

# ------------- main work -------------

def process_recordings(master_config, dry_run=False):
    base_params_path = master_config["params_file"]
    recordings_dir   = master_config["recordings_dir"]
    results_csv_path = master_config["results_csv"]
    ptv_results_dir  = master_config["ptv_results_dir"]
    sub_dir          = master_config.get("sub_dir", "particles")
    run_if_exists    = master_config.get("run_if_exists", True)
    save_blobs       = master_config.get("save_blobs", True)
    cams_filter      = master_config.get("cams") 
    camera_thresholds = master_config.get("camera_thresholds")
    masks_dir        = master_config.get("masks_dir")

    if masks_dir and not os.path.exists(masks_dir):
        print(f"ERROR: masks_dir does not exist: {masks_dir}")
        sys.exit(1)

    # load base params once
    base_params = ensure_list_of_dicts(load_yaml_config(base_params_path))

    # Identify planned pairs
    planned = []
    if not os.path.exists(recordings_dir):
        print(f"ERROR: recordings_dir does not exist: {recordings_dir}")
        return

    for rec in sorted(os.listdir(recordings_dir)):
        rec_path = os.path.join(recordings_dir, rec)
        if not (os.path.isdir(rec_path) and rec.lower().startswith("rec")):
            continue
        for cam in sorted(os.listdir(rec_path)):
            cam_img_dir = os.path.join(rec_path, cam)
            if not (os.path.isdir(cam_img_dir) and cam.lower().startswith("cam")):
                continue
            if cams_filter and cam not in cams_filter:
                continue
            planned.append((rec, cam, cam_img_dir))

    if not planned:
        print("No (Rec, Cam) pairs found.")
        return

    if dry_run:
        print(f"DRY RUN: (run_if_exists={run_if_exists}, save_blobs={save_blobs}, sub_dir={sub_dir})")
        for rec, cam, cam_img_dir in planned:
            threshold_info = ""
            if camera_thresholds and cam in camera_thresholds:
                threshold_info = f" | threshold={camera_thresholds[cam]}"
            
            mask_info = ""
            if masks_dir:
                mask_filename = f"mask_{cam}.tif"
                mask_path = get_existing_file_case_insensitive(masks_dir, mask_filename)
                if mask_path:
                    mask_info = f" | mask={os.path.basename(mask_path)}"
                else:
                    mask_info = f" | mask=MISSING({mask_filename})"

            # Destination logic
            out_dir = os.path.join(ptv_results_dir, f"{rec}_data", sub_dir)
            target_name = f"blobs_{cam}"
            save_name = os.path.join(out_dir, target_name)
            
            existing_path = get_existing_file_case_insensitive(out_dir, target_name)
            
            status = ""
            if existing_path:
                if not run_if_exists:
                    status = f" [WILL SKIP - {os.path.basename(existing_path)} exists]"
                else:
                    status = f" [WILL SAVE TO TMP - {os.path.basename(existing_path)} exists]"
            elif not save_blobs:
                status = " [WILL RUN BUT NOT SAVE (save_blobs=False)]"

            print(f"  Rec={rec} | Cam={cam} | images_folder={cam_img_dir}{threshold_info}{mask_info}{status}")
            if "SAVE TO TMP" in status:
                timestamp = "YYYYMMDD_HHMMSS"
                print(f"    -> would have saved to: {os.path.join(out_dir, 'tmp', f'blobs_{cam}_{timestamp}')}")
            elif not save_blobs and not existing_path:
                print(f"    -> save_name: (TEMPORARY - will be deleted)")
            else:
                print(f"    -> save_name={save_name}")
        return

    # real run: ensure CSV dir exists
    os.makedirs(os.path.dirname(results_csv_path) or ".", exist_ok=True)

    with open(results_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Recording", "Camera", "Threshold", "BlobCount"])
        csvfile.flush()

        for rec, cam, cam_img_dir in planned:
            # Destination: ptv_results/Rec*_data/<sub_dir>/blobs_cam*
            out_dir = os.path.join(ptv_results_dir, f"{rec}_data", sub_dir)
            os.makedirs(out_dir, exist_ok=True)
            target_name = f"blobs_{cam}"
            save_name = os.path.join(out_dir, target_name)

            existing_path = get_existing_file_case_insensitive(out_dir, target_name)
            
            # If blob file exists, handle according to run_if_exists
            is_backup = False
            if existing_path:
                if not run_if_exists:
                    print(f"SKIP: {existing_path} already exists and run_if_exists=False.")
                    continue
                
                tmp_dir = os.path.join(out_dir, "tmp")
                os.makedirs(tmp_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = os.path.join(tmp_dir, f"blobs_{cam}_{timestamp}")
                print(f"INFO: {existing_path} already exists. Saving to tmp: {save_name}")
                is_backup = True

            # Logic for not saving blobs: 
            actual_save_name = save_name
            delete_after = False
            if not save_blobs:
                delete_after = True
                if not is_backup:
                    # We still need to save it somewhere to count it
                    actual_save_name = os.path.join(out_dir, f"temp_blobs_{cam}_{datetime.now().strftime('%H%M%S')}")
                print(f"INFO: save_blobs=False. {actual_save_name} will be deleted after counting.")

            # clone and set segmentation block
            params = copy.deepcopy(base_params)
            seg = find_block(params, "segmentation")
            seg["images_folder"] = cam_img_dir.replace("\\", "/")
            seg["save_name"]     = actual_save_name.replace("\\", "/")

            # Apply mask if masks_dir is provided
            if masks_dir:
                mask_filename = f"mask_{cam}.tif"
                mask_path = get_existing_file_case_insensitive(masks_dir, mask_filename)
                if not mask_path:
                    print(f"ERROR: Mask file not found for {cam} in {masks_dir} (expected {mask_filename})")
                    sys.exit(1)
                seg["mask"] = os.path.abspath(mask_path).replace("\\", "/")
                print(f"Applying mask for {cam}: {seg['mask']}")

            # Apply camera-specific threshold if provided
            if camera_thresholds and cam in camera_thresholds:
                new_threshold = camera_thresholds[cam]
                seg["threshold"] = new_threshold
                print(f"Applying custom threshold for {cam}: {new_threshold}")

            # Get the threshold that will be used for logging
            threshold_used = seg.get("threshold", "N/A")

            # write temp params in the same directory as the base params
            # so that relative paths (like masks/) resolve correctly
            params_dir = os.path.dirname(os.path.abspath(base_params_path))
            temp_params_file = os.path.join(params_dir, f"temp_params_batch_{cam}.yml")
            save_yaml_config(params, temp_params_file)

            print(f"Running segmentation | Rec={rec} | Cam={cam} | save_name={seg['save_name']}")
            stdout, stderr = run_segmentation_workflow(temp_params_file)

            # parse and record
            count = extract_blob_count(stdout)
            writer.writerow([rec, cam, threshold_used, count])
            csvfile.flush()
            print(f"Done | Rec={rec} | Cam={cam} | blobs: {count}")
            
            # Clean up temp files
            if os.path.exists(temp_params_file):
                os.remove(temp_params_file)
            
            if delete_after and os.path.exists(actual_save_name):
                os.remove(actual_save_name)
                print(f"INFO: Deleted temporary blob file: {actual_save_name}")

# ------------- entrypoint -------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Batch MyPTV segmentation over Rec*/Cam* saving to ptv_results structure")
    ap.add_argument("master_config", help="Path to master_config.yml")
    ap.add_argument("--dry-run", action="store_true",
                    help="List (Rec, Cam) pairs that would be processed and exit")
    args = ap.parse_args()

    try:
        m_config = load_yaml_config(args.master_config)
    except Exception as e:
        print(f"Failed to load master config: {e}")
        sys.exit(1)

    process_recordings(m_config, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"Batch segmentation completed. Results -> {m_config['results_csv']}")
