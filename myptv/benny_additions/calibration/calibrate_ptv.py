import os
import argparse
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

# Default Configuration
# =====================
DEFAULT_CAMERAS = ['Cam1', 'Cam2', 'Cam3', 'Cam4']

def run_calibration(cal_dir, suffix='_cal_points'):
    print(f"--- MyPTV Calibration Tool ---")
    print(f"Working Directory: {cal_dir}")
    print(f"Point file suffix: {suffix}")
    print("-" * 50)
    
    if not os.path.exists(cal_dir):
        print(f"Error: Directory {cal_dir} does not exist.")
        return

    for cam_name in DEFAULT_CAMERAS:
        # Construct the points filename (lowercase cam name + suffix)
        points_filename = f"{cam_name.lower()}{suffix}"
        print(f"\nProcessing {cam_name}...")
        points_file = os.path.join(cal_dir, points_filename)
        
        if not os.path.exists(points_file):
            print(f"  Error: Points file not found at {points_file}")
            continue

        # 1. Initialize camera and load the points file
        try:
            cam = camera_extendedZolof(cam_name, cal_points_fname=points_file)
        except Exception as e:
            print(f"  Error initializing camera: {e}")
            continue
        
        # 2. Setup the calibrator (quadratic=False for full 3rd order polynomial)
        cal = calibrate_extendedZolof(cam, cam.image_points, cam.lab_points, quadratic=False)
        
        # 3. Perform the calibration
        print(f"  Calculating coefficients from {len(cam.image_points)} points...")
        cal.calibrate()
        
        # 4. Report the resulting error
        err = cal.mean_squared_err()
        print(f"  Finished with RMS error: {err:.6f} pixels")
        
        # 5. Save the resulting camera parameter file
        print(f"  Saving parameter file to: {os.path.join(cal_dir, cam_name)}")
        try:
            cam.save(cal_dir)
            print(f"  Successfully saved {cam_name}.")
        except Exception as e:
            print(f"  Error saving {cam_name}: {e}")

    print("\n" + "=" * 50)
    print("Calibration process complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate MyPTV cameras.")
    parser.add_argument("--dir", default='Data_Analysis/MyPTV_analysis/20260506_analysis/cal',
                        help="Directory containing the calibration point files")
    parser.add_argument("--suffix", default='_cal_points',
                        help="Suffix for the point files (e.g., _indexed or _cal_points)")
    
    args = parser.parse_args()
    
    # Resolve absolute path if needed
    work_dir = args.dir
    if not os.path.isabs(work_dir):
        # We assume relative to project root if not absolute
        project_root = '/Users/user/Desktop/Research'
        work_dir = os.path.join(project_root, work_dir)
        
    run_calibration(work_dir, suffix=args.suffix)
