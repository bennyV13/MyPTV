import os
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

# Configuration
# =============
# File mapping: {output_cam_name: input_points_filename}
camera_mapping = {
    'Cam1': 'cam1_cal_points',
    'Cam2': 'cam2_cal_points',
    'Cam3': 'cam3_cal_points',
    'Cam4': 'cam4_cal_points'
}

# Paths
project_root = '/Users/user/Desktop/Research'
cal_dir = os.path.join(project_root, 'Data_Analysis/MyPTV_analysis/20260506_analysis/cal')

def run_calibration():
    print(f"--- MyPTV Calibration Tool (20260506) ---")
    print(f"Working Directory: {cal_dir}")
    print("-" * 50)
    
    for cam_name, points_filename in camera_mapping.items():
        print(f"\nProcessing {cam_name}...")
        points_file = os.path.join(cal_dir, points_filename)
        
        if not os.path.exists(points_file):
            print(f"  Error: Points file not found at {points_file}")
            continue

        # 1. Initialize camera and load the points file
        try:
            # We use the cam_name for the internal name and the points_file for data
            cam = camera_extendedZolof(cam_name, cal_points_fname=points_file)
        except Exception as e:
            print(f"  Error initializing camera: {e}")
            continue
        
        # 2. Setup the calibrator (quadratic=False for full 3rd order polynomial)
        # extendedZolof usually needs 3rd order for water tank refraction
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
    run_calibration()
