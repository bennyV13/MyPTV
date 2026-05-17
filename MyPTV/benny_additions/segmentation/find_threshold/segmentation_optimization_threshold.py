import os
import sys
import copy
import yaml        # PyYAML module for reading/writing YAML files
import csv        # CSV module for writing results
import subprocess # To execute the external segmentation command
import re         # Regex for parsing output text
import logging   # For logging functionality
from datetime import datetime

"""
segmentation_optimization_threshold.py
----------------------

Description:
    This script automates the segmentation workflow across multiple recordings,
    cameras, and threshold values. For each combination, it runs the external
    `workflow.py` script in "segmentation" mode, extracts the number of blobs
    detected, and saves the results into a CSV file. Logging output is written
    both to the console and a timestamped log file.

Usage:
    python segmentation_optimization_threshold.py <master_config.yml>

Arguments:
    <master_config.yml> : Path to the master configuration YAML file that must
                          include:
                          - params_file: path to base segmentation parameters YAML
                          - recordings_dir: directory containing recordings
                          - results_csv: output CSV path
                          - thresholds: dict of cameras -> list of thresholds
                          - images: dict of cameras -> EQ/BG settings

Output:
    - A CSV file with the columns:
        [Recording, Camera, Threshold, BlobCount]
    - A log file named "batch_segmentation_<timestamp>.log" with detailed output

Notes:
    - Requires Python 3 and the following packages: PyYAML
    - Calls `workflow.py` for each segmentation run
    - Temporary parameters are saved to 'temp_params.yml' during execution
"""



# ----- Configuration and Utility Functions -----

def setup_logging(log_file):
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_yaml_config(config_path):
    """Load a YAML file from the given path and return its contents as a Python dictionary."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml_config(data, path):
    """Save a Python dictionary `data` as a YAML file at the given path."""
    with open(path, 'w') as f:
        yaml.safe_dump(data, f)

def run_segmentation_workflow(params_path):
    """
    Run the segmentation workflow using the given parameter file.
    Executes the command `python workflow.py <params_path> segmentation` and returns the output (stdout).
    """
    # Run the external workflow command and capture its output
    result = subprocess.run(
        ["python", "workflow.py", params_path, "segmentation"],
        capture_output=True, text=True
    )
    # Check for errors in execution
    if result.returncode != 0:
        # If needed, handle errors (here we simply print and exit)
        logging.error(f"Error: Workflow returned code {result.returncode} for parameters {params_path}")
        logging.error(f"Error output: {result.stderr}")
        sys.exit(1)
    return result.stdout, result.stderr

def extract_blob_count(output_text):
    """
    Parse the workflow output text to find the blob count.
    Looks for a line in the format 'blobs found: <number>' and returns the number as an integer.
    """
    match = re.search(r"blobs found:\s*(\d+)", output_text)
    if match:
        return int(match.group(1))
    else:
        # If not found, return 0 or raise an error as appropriate
        return 0

# ----- Main Processing Function -----

def process_recordings(master_config):
    """
    Process all recordings and cameras as specified in the master configuration.
    For each recording and each camera threshold, run segmentation and record the blob count.
    """
    base_params_path = master_config["params_file"]
    recordings_dir = master_config["recordings_dir"]
    results_csv_path = master_config["results_csv"]
    camera_thresholds = master_config["thresholds"]

    # Load the base parameters YAML file once
    base_params = load_yaml_config(base_params_path)

    # Open the results CSV file for writing and set up the CSV writer
    csvfile = open(results_csv_path, mode='w', newline='')
    writer = csv.writer(csvfile)
    # Write header row
    writer.writerow(["Recording", "Camera", "Threshold", "BlobCount"])
    csvfile.flush()  # Ensure header is written immediately

    try:
        # Iterate over each recording directory in the recordings base directory
        for recording_name in os.listdir(recordings_dir):
            recording_path = os.path.join(recordings_dir, recording_name)
            if not os.path.isdir(recording_path):
                continue  # Skip if it's not a directory

            # For each camera (cam1, cam2, etc.) defined in the thresholds config
            for camera_name, thresholds in camera_thresholds.items():
                camera_path = os.path.join(recording_path, camera_name)
                if not os.path.isdir(camera_path):
                    continue  # Skip this camera if the directory doesn't exist in the recording

                # Iterate over each threshold value for this camera
                for threshold in thresholds:
                    # Create a fresh copy of the base parameters for this run
                    params_copy = copy.deepcopy(base_params)
                    
                    # Find and update the segmentation parameters
                    for param_dict in params_copy:
                        if "segmentation" in param_dict:
                            param_dict["segmentation"]["images_folder"] = camera_path
                            param_dict["segmentation"]["threshold"] = threshold
                            param_dict["segmentation"]["equilization_map"] = master_config["images"][camera_name]["EQ"]
                            param_dict["segmentation"]["remove_background"] = master_config["images"][camera_name]["BG"]
                            break

                    # Save the updated parameters to a temporary YAML file
                    temp_params_file = "temp_params.yml"
                    save_yaml_config(params_copy, temp_params_file)

                    # Execute the segmentation workflow with the temporary params
                    output, error_output = run_segmentation_workflow(temp_params_file)
                    
                    # Log the complete output
                    logging.info(f"Processing {recording_name} | {camera_name} | Threshold {threshold}")
                    logging.info("Workflow output:")
                    logging.info(output)
                    if error_output:
                        logging.info("Error output:")
                        logging.info(error_output)
                    
                    # Extract the blob count from the output
                    blob_count = extract_blob_count(output)

                    # Write the results as a new row in the CSV file
                    writer.writerow([recording_name, camera_name, threshold, blob_count])
                    csvfile.flush()  # Ensure data is written after each threshold
                    
                    # Print progress to console for monitoring
                    logging.info(f"{recording_name} | {camera_name} | Threshold {threshold} -> Blobs Found: {blob_count}")

    finally:
        csvfile.close()

# ----- Script Execution -----

if __name__ == "__main__":
    # Ensure the script is called with the path to the master YAML config file
    if len(sys.argv) != 2:
        print("Usage: python batch_segmentation.py <master_config.yml>")
        sys.exit(1)
    
    master_config_path = sys.argv[1]
    
    # Set up logging with timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"batch_segmentation_{timestamp}.log"
    setup_logging(log_file)
    
    # Load master configuration and start processing
    try:
        master_config = load_yaml_config(master_config_path)
    except Exception as e:
        logging.error(f"Failed to load master config file: {e}")
        sys.exit(1)
    
    # Process all recordings as per the master config
    process_recordings(master_config)
    logging.info(f"Batch segmentation completed. Results saved to {master_config['results_csv']}")
