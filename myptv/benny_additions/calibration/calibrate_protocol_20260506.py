import os
import sys
import numpy as np
from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof

# Configuration
# =============
camera_names = ['Cam1', 'Cam2', 'Cam3', 'Cam4']

# Paths
project_root = '/Users/user/Desktop/Research'
cal_dir = os.path.join(project_root, 'Data_Analysis/MyPTV_analysis/20260506_analysis/cal')

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
        print(f"  Col {i} (X={col[0]:.1f}): Inc {increment:2d} | Total Shift {shift:2d} | Indices {[idx1, idx2, idx3]}")
        
        selected_indices.append(sorted_col_indices[idx1])
        selected_indices.append(sorted_col_indices[idx2])
        selected_indices.append(sorted_col_indices[idx3])
        
    unique_selection = np.unique(selected_indices)
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


def visualize_discovery(file_path, show_plt=True):
    '''
    Runs the discovery logic on a file and plots the results.
    '''
    print(f"--- Dry Run Visualization ---")
    print(f"File: {file_path}")
    
    data = np.loadtxt(file_path)
    indices = discover_initial_points(data)
    selected = data[indices]
    
    # Show CLI plot
    plot_selection_cli(data, indices)
    
    if not show_plt:
        print(f"Total points in file: {len(data)}")
        print(f"Points selected for Step 1: {len(selected)}")
        print(f"Discovery complete (CLI plot only).")
        return

    # Import matplotlib only when needed
    import matplotlib.pyplot as plt
    
    # Identify Lab columns
    ix, iy, iz = (2, 3, 4) if data.shape[1] == 5 else (0, 1, 2)
    
    fig = plt.figure(figsize=(15, 5))
    
    # 1. 3D Plot
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.scatter(data[:, ix], data[:, iy], data[:, iz], c='lightgrey', alpha=0.3, label='Unselected')
    ax1.scatter(selected[:, ix], selected[:, iy], selected[:, iz], c='red', s=50, label='Selected')
    ax1.set_xlabel('X Lab')
    ax1.set_ylabel('Y Lab')
    ax1.set_zlabel('Z Lab')
    ax1.set_title('3D Distribution')
    
    # 2. XY Projection (Top Down) - Checking for lines
    ax2 = fig.add_subplot(132)
    ax2.scatter(data[:, ix], data[:, iy], c='lightgrey', alpha=0.5)
    ax2.scatter(selected[:, ix], selected[:, iy], c='red', s=40)
    ax2.set_xlabel('X Lab')
    ax2.set_ylabel('Y Lab')
    ax2.set_title('XY Projection (Non-Collinearity Check)')
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # 3. XZ Projection (Side View) - Checking Volume Spanning
    ax3 = fig.add_subplot(133)
    ax3.scatter(data[:, ix], data[:, iz], c='lightgrey', alpha=0.5)
    ax3.scatter(selected[:, ix], selected[:, iz], c='red', s=40)
    ax3.set_xlabel('X Lab')
    ax3.set_ylabel('Z Lab')
    ax3.set_title('XZ Projection (Depth Span)')
    ax3.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Save the plot in the same location as the target file
    output_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    save_path = os.path.join(output_dir, f"{base_name}_discovery_dryrun.png")
    plt.savefig(save_path, dpi=150)
    print(f"Plot saved to: {save_path}")
    
    plt.show()
    
    print(f"Total points in file: {len(data)}")
    print(f"Points selected for Step 1: {len(selected)}")
    print(f"Discovery complete.")


def run_two_step_calibration():
    print(f"--- MyPTV Automated Two-Step Calibration (20260506) ---")
    print(f"Working Directory: {cal_dir}")
    print("=" * 60)
    
    for cam_name in camera_names:
        print(f"\n>>> PROCESSING {cam_name} <<<")
        
        full_points_file = os.path.join(cal_dir, f"{cam_name.lower()}_cal_points")
        if not os.path.exists(full_points_file):
            print(f"  [Error] Full calibration points file not found: {full_points_file}")
            continue
            
        # Output directory is where the blobs are
        output_dir = os.path.dirname(full_points_file)
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
        np.savetxt(temp_manual_file, initial_subset, fmt='%.1f', delimiter='\t')
        
        try:
            cam = camera_extendedZolof(cam_name, cal_points_fname=temp_manual_file)
            cal_init = calibrate_extendedZolof(cam, cam.image_points, cam.lab_points, quadratic=True)
            print(f"  Solving with {len(initial_subset)} discovered points...")
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
            cal_final = calibrate_extendedZolof(cam_final, cam_final.image_points, cam_final.lab_points, quadratic=False)
            print(f"  Refining with {len(full_data)} points...")
            cal_final.calibrate()
            print(f"  Final RMS Error: {cal_final.mean_squared_err():.6f} pixels")
            cam_final.save(output_dir)
            print(f"  Success: Final .cam file updated in {output_dir}")
        except Exception as e:
            print(f"  Error in Step 2: {e}")

    print("\n" + "=" * 60)
    print("Automated protocol sequence complete.")


if __name__ == "__main__":
    if "--plotcli" in sys.argv:
        # Dry run visualization on the small target file
        target_path = '/Users/user/Desktop/Research/Data_Analysis/MyPTV_analysis/20260506_analysis/cal/target_file_small'
        if os.path.exists(target_path):
            visualize_discovery(target_path, show_plt=False)
        else:
            print(f"Error: Target file not found at {target_path}")
    else:
        # Full calibration sequence
        run_two_step_calibration()

