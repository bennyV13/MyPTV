from scripts.lagrangian_analysis import LagrangianAnalysis
import os

def test_loading():
    data_path = "Data_and_analysis/20260315_frames/smoothed_trajectories"
    if not os.path.exists(data_path):
        print("Data file not found. Skipping test.")
        return
        
    analysis = LagrangianAnalysis()
    analysis.load_data(data_path)
    
    if len(analysis.trajs) > 0:
        print(f"Successfully loaded {len(analysis.trajs)} trajectories.")
        print(f"Sample trajectory shape: {analysis.trajs[0].shape}")
        # Verify columns: id, x, y, z, vx, vy, vz, ax, ay, az, frame
        if analysis.trajs[0].shape[1] == 11:
            print("Trajectory columns count matches (11).")
        else:
            print(f"Unexpected columns count: {analysis.trajs[0].shape[1]}")
    else:
        print("Failed to load trajectories.")

if __name__ == "__main__":
    test_loading()
