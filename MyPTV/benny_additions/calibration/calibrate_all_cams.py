import os
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

# Configuration
# =============
cameras = ['cam1', 'cam2', 'cam3', 'cam4']

# We use absolute paths to ensure the script works regardless of where it is called from
project_root = '/Users/user/Desktop/Research'
cal_params_dir = os.path.join(project_root, 'Data_Analysis/MyPTV_analysis/20260415_analysis/ptv_results/cal_params')
output_dir = cal_params_dir

def run_calibration():
    print(f"--- MyPTV Multi-Camera Calibration Tool ---")
    print(f"Calibration Parameters Directory: {cal_params_dir}")
    print("-" * 45)
    
    for cam_name in cameras:
        print(f"\nProcessing {cam_name}...")
        points_file = os.path.join(cal_params_dir, f'{cam_name}_cal_points')
        
        if not os.path.exists(points_file):
            print(f"  Error: Points file not found at {points_file}")
            continue

        # 1. Initialize camera and load the points file
        try:
            cam = camera_extendedZolof(cam_name, cal_points_fname=points_file)
        except Exception as e:
            print(f"  Error initializing camera: {e}")
            continue
        
        # 2. Setup the calibrator (quadratic=False for 3rd order polynomial)
        cal = calibrate_extendedZolof(cam, cam.image_points, cam.lab_points, quadratic=False)
        
        # 3. Perform the calibration
        print("  Calculating coefficients...")
        cal.calibrate()
        
        # 4. Report the resulting error
        err = cal.mean_squared_err()
        print(f"  Finished with RMS error: {err:.6f} pixels")
        
        # 5. Save the resulting camera parameter file
        print(f"  Saving results...")
        try:
            cam.save(output_dir)
            print(f"  Successfully saved {cam_name} file.")
        except Exception as e:
            print(f"  Error saving {cam_name} file: {e}")

    print("\n" + "=" * 45)
    print("Multi-camera calibration process complete.")

if __name__ == "__main__":
    run_calibration()
