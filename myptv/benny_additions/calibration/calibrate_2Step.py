import os
import sys
import numpy as np
import argparse
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

# Default Configuration
# =====================
DEFAULT_CAMERAS = ['Cam1', 'Cam2', 'Cam3', 'Cam4']

def discover_initial_points(data):
    '''
    Automatically selects a non-collinear subset of points for Step 1.
    Handles both matched files (5 columns) and target files (3 columns).
    '''
    # Identify column indices for Lab X, Y, Z
    if data.shape[1] == 5:
        ix, iy, iz = 2, 3, 4
    elif data.shape[1] == 3:
        ix, iy, iz = 0, 1, 2
    else:
        raise ValueError("Data must have 3 (X,Y,Z) or 5 (x,y,X,Y,Z) columns.")

    xz_coords = data[:, [ix, iz]]
    unique_columns = np.unique(xz_coords, axis=0)
    
    selected_indices = []
    
    # Add absolute corners of the volume
    corners = [
        np.argmin(data[:, ix] + data[:, iy]), # Min X, Min Y
        np.argmax(data[:, ix] + data[:, iy]), # Max X, Max Y
        np.argmin(data[:, ix] - data[:, iy]), # Min X, Max Y
        np.argmax(data[:, ix] - data[:, iy])  # Max X, Min Y
    ]
    selected_indices.extend(corners)

    current_shift = 0
    # Step through each column (X, Z pair)
    for i, col in enumerate(unique_columns):
        col_mask = (data[:, ix] == col[0]) & (data[:, iz] == col[1])
        col_indices = np.where(col_mask)[0]
        
        # Sort these points by Y_lab
        sorted_col_indices = col_indices[np.argsort(data[col_indices, iy])]
        num_rows = len(sorted_col_indices)
        
        if num_rows < 3:
            selected_indices.extend(sorted_col_indices)
            continue
            
        # Cumulative shift: increment grows with i (2, 3, 4, 5...)
        increment = (2 + (i - 1)) if i > 0 else 0
        current_shift = (current_shift + increment) % num_rows
        shift = current_shift
        
        # Fixed-gap triplet that 'climbs' the column as X progresses
        gap = num_rows // 3
        
        idx1 = shift
        idx2 = (shift + gap) % num_rows
        idx3 = (shift + 2 * gap) % num_rows
        
        # Log the progress for verification
        # print(f"  Col {i} (X={col[0]:.1f}): Inc {increment:2d} | Total Shift {shift:2d} | Indices {[idx1, idx2, idx3]}")
        
        selected_indices.append(sorted_col_indices[idx1])
        selected_indices.append(sorted_col_indices[idx2])
        selected_indices.append(sorted_col_indices[idx3])
        
    unique_selection = np.unique(selected_indices)
    
    # Ensure we only send exactly 25 points if possible
    target_count = 25
    if len(unique_selection) > target_count:
        # Keep the 4 mandatory corners
        corner_indices = np.array(corners)
        other_indices = np.array([idx for idx in unique_selection if idx not in corner_indices])
        
        # Subsample the remaining points to reach target_count
        num_needed = target_count - len(corner_indices)
        if num_needed > 0:
            # Simple uniform subsampling of the other points
            step = len(other_indices) / float(num_needed)
            subsampled_others = [other_indices[int(i * step)] for i in range(num_needed)]
            unique_selection = np.sort(np.concatenate([corner_indices, subsampled_others]))
        else:
            unique_selection = np.sort(corner_indices)
            
    return unique_selection


def plot_selection_cli(data, selected_indices):
    '''
    Prints an ASCII representation of the selection grid.
    '''
    # Group points by unique columns
    ix, iy, iz = (2, 3, 4) if data.shape[1] == 5 else (0, 1, 2)
    xz_coords = data[:, [ix, iz]]
    unique_cols = np.unique(xz_coords, axis=0)
    
    print("\n  [ ASCII Selection Grid (X-axis progress ->) ]")
    print("  (Rows = vertical Y_lab, X = Selected, . = Unselected)")
    print("-" * 50)
    
    # We'll print rows from Top to Bottom
    max_rows = 0
    for col in unique_cols:
        count = np.sum((data[:, ix] == col[0]) & (data[:, iz] == col[1]))
        max_rows = max(max_rows, count)

    for r in range(max_rows - 1, -1, -1):
        line = f"  {r:2d} | "
        for i, col in enumerate(unique_cols):
            col_mask = (data[:, ix] == col[0]) & (data[:, iz] == col[1])
            col_indices = np.where(col_mask)[0]
            # Sort indices in this column by Y
            sorted_indices = col_indices[np.argsort(data[col_indices, iy])]
            
            if r < len(sorted_indices):
                global_idx = sorted_indices[r]
                if global_idx in selected_indices:
                    line += " X "
                else:
                    line += " . "
            else:
                line += "   "
        print(line)
    
    footer = "     " + "---" * len(unique_cols)
    print(footer)
    print("       " + " ".join([f"C{i}" for i in range(len(unique_cols))]))
    print("-" * 50)


def run_two_step_calibration(cal_dir, suffix='_cal_points', target_cam=None, alpha=0.001, step1_quadratic=False, step2_quadratic=False):
    print(f"--- MyPTV Automated Two-Step Calibration ---")
    print(f"Working Directory: {cal_dir}")
    print(f"Point file suffix: {suffix}")
    print("=" * 60)
    
    cams_to_process = [target_cam] if target_cam else DEFAULT_CAMERAS
    
    for cam_name in cams_to_process:
        print(f"\n>>> PROCESSING {cam_name} <<<")
        
        points_filename = f"{cam_name.lower()}{suffix}"
        full_points_file = os.path.join(cal_dir, points_filename)
        
        if not os.path.exists(full_points_file):
            print(f"  [Error] Points file not found: {full_points_file}")
            continue
            
        output_dir = cal_dir
        full_data = np.loadtxt(full_points_file)
        
        # ---------------------------------------------------------------------
        # STEP 1: INITIAL CALIBRATION (Automated Discovery)
        # ---------------------------------------------------------------------
        print("\nStep 1: Automated Discovery & Initial Solve")
        
        indices = discover_initial_points(full_data)
        initial_subset = full_data[indices]
        
        # Show selection grid
        plot_selection_cli(full_data, indices)
        
        temp_manual_file = os.path.join(output_dir, f"{cam_name.lower()}_temp_manual")
        np.savetxt(temp_manual_file, initial_subset, fmt='%.3f', delimiter='\t')
        
        try:
            cam = camera_extendedZolof(cam_name, cal_points_fname=temp_manual_file)
            cal_init = calibrate_extendedZolof(cam, cam.image_points, cam.lab_points, quadratic=step1_quadratic, alpha=alpha)
            order_str = "Quadratic" if step1_quadratic else "3rd Order"
            print(f"  Solving with {len(initial_subset)} discovered points ({order_str}, alpha={alpha})...")
            cal_init.calibrate()
            print(f"  Initial RMS Error: {cal_init.mean_squared_err():.6f} pixels")
            cam.save(output_dir)
        except Exception as e:
            print(f"  Error in Step 1: {e}")
            continue
        finally:
            if os.path.exists(temp_manual_file): os.remove(temp_manual_file)

        # ---------------------------------------------------------------------
        # STEP 2: FINAL CALIBRATION (Refinement)
        # ---------------------------------------------------------------------
        print("\nStep 2: High-Precision Refinement (Full Grid)")
        try:
            cam_final = camera_extendedZolof(cam_name, cal_points_fname=full_points_file)
            cam_final.load(output_dir)
            # quadratic=False uses 3rd order polynomial
            cal_final = calibrate_extendedZolof(cam_final, cam_final.image_points, cam_final.lab_points, quadratic=step2_quadratic, alpha=alpha)
            order_str = "Quadratic" if step2_quadratic else "3rd Order"
            print(f"  Refining with {len(full_data)} points ({order_str}, alpha={alpha})...")
            cal_final.calibrate()
            print(f"  Final RMS Error: {cal_final.mean_squared_err():.6f} pixels")
            cam_final.save(output_dir)
            print(f"  Success: Final .cam file updated in {output_dir}")
        except Exception as e:
            print(f"  Error in Step 2: {e}")

    print("\n" + "=" * 60)
    print("Automated protocol sequence complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 2-step MyPTV calibration.")
    parser.add_argument("--dir", required=True, help="Directory containing point files")
    parser.add_argument("--suffix", default='_cal_points', help="Point file suffix")
    parser.add_argument("--cam", help="Specific camera to process (e.g., Cam2)")
    parser.add_argument("--alpha", type=float, default=0.001, help="Regularization parameter alpha (default: 0.001)")
    parser.add_argument("--step1-quadratic", action="store_true", help="Force Step 1 initial solve to use quadratic fit instead of cubic")
    parser.add_argument("--step2-quadratic", action="store_true", help="Force Step 2 refinement to use quadratic fit instead of cubic")
    
    args = parser.parse_args()
    
    work_dir = args.dir
    if not os.path.isabs(work_dir):
        project_root = '/Users/user/Desktop/Research'
        work_dir = os.path.join(project_root, work_dir)
        
    run_two_step_calibration(work_dir, suffix=args.suffix, target_cam=args.cam, alpha=args.alpha, step1_quadratic=args.step1_quadratic, step2_quadratic=args.step2_quadratic)

