import os
import sys
import copy
import yaml
import csv
import subprocess
import re
import argparse

"""
batch_segmentation.py

Runs MyPTV segmentation for every (Recording, Camera) pair under recordings_dir.
For each run it updates only the 'segmentation' block in the base params file,
executes:  python workflow.py <temp_params.yml> segmentation
parses 'blobs found: N' from stdout, and writes results to CSV.

master_config.yml must contain:
  params_file: "path/to/params_file.yml"
  recordings_dir: "D:/.../GROUP_DIR"         # contains Rec*/Cam* image folders
  blobs_save_path: "D:/.../analysis/blobs"   # where to store blobs output
  results_csv: "D:/.../batch_results.csv"
  cams: ["Cam2","Cam4"]                      # optional filter list
  camera_thresholds:                         # optional, for camera-specific thresholds
    Cam3: 5
    Cam4: 8

Usage:
  python batch_segmentation.py master_config.yml
  python batch_segmentation.py master_config.yml --dry-run

Possible reasons for getting stuck:
- There's a blob file with the same name as the save_name, so the workflow asks for overwrite confirmation.
- The plot is set to True.
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
    cmd = [sys.executable, "workflow.py", params_path, "segmentation"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Workflow failed for {params_path}")
        print(result.stderr.strip())
        raise RuntimeError("workflow.py returned non-zero exit code")
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
    blobs_save_path  = master_config["blobs_save_path"]
    cams_filter      = master_config.get("cams") 
    camera_thresholds = master_config.get("camera_thresholds")

    # load base params once
    base_params = ensure_list_of_dicts(load_yaml_config(base_params_path))

    # DRY RUN: just list planned pairs and exit
    if dry_run:
        planned = []
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
        print("DRY RUN: would process the following pairs:")
        for rec, cam, cam_img_dir in planned:
            # Check for a specific threshold to display in the dry run
            threshold_info = ""
            if camera_thresholds and cam in camera_thresholds:
                threshold_info = f" | threshold={camera_thresholds[cam]}"
            print(f"  Rec={rec} | Cam={cam} | images_folder={cam_img_dir}{threshold_info}")
        return

    # real run: ensure CSV dir exists
    os.makedirs(os.path.dirname(results_csv_path) or ".", exist_ok=True)

    with open(results_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Recording", "Camera", "Threshold", "BlobCount"])
        csvfile.flush()

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

                # Destination for this (rec, cam)
                out_dir = os.path.join(blobs_save_path, rec)
                os.makedirs(out_dir, exist_ok=True)
                save_name = os.path.join(out_dir, f"blobs_{cam}")

                # clone and set segmentation block
                params = copy.deepcopy(base_params)
                seg = find_block(params, "segmentation")
                seg["images_folder"] = cam_img_dir.replace("\\", "/")
                seg["save_name"]     = save_name.replace("\\", "/")

                # Apply camera-specific threshold if provided
                if camera_thresholds and cam in camera_thresholds:
                    new_threshold = camera_thresholds[cam]
                    seg["threshold"] = new_threshold
                    print(f"Applying custom threshold for {cam}: {new_threshold}")

                # Get the threshold that will be used for logging
                threshold_used = seg.get("threshold", "N/A")

                # write temp params and run workflow
                temp_params_file = "temp_params.yml"
                save_yaml_config(params, temp_params_file)

                print(f"Running segmentation | Rec={rec} | Cam={cam} | save_name={seg['save_name']}")
                stdout, stderr = run_segmentation_workflow(temp_params_file)

                # parse and record
                count = extract_blob_count(stdout)
                writer.writerow([rec, cam, threshold_used, count])
                csvfile.flush()
                print(f"Done | Rec={rec} | Cam={cam} | blobs: {count}")

# ------------- entrypoint -------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Batch MyPTV segmentation over Rec*/Cam*")
    ap.add_argument("master_config", help="Path to master_config.yml")
    ap.add_argument("--dry-run", action="store_true",
                    help="List (Rec, Cam) pairs that would be processed and exit")
    args = ap.parse_args()

    try:
        master_config = load_yaml_config(args.master_config)
    except Exception as e:
        print(f"Failed to load master config: {e}")
        sys.exit(1)

    process_recordings(master_config, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"Batch segmentation completed. Results -> {master_config['results_csv']}")
