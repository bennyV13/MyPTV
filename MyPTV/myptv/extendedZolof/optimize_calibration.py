import numpy as np

class PointManager:
    """
    Handles parsing, grouping, and subset selection of calibration points.
    """
    def __init__(self, data):
        """
        data: numpy array of shape (N, 5) with columns:
              x_cam, y_cam, X_lab, Y_lab, Z_lab
        """
        self.data = data
        self.groups = self._group_by_xz()

    def _group_by_xz(self):
        """
        Groups points by unique (X_lab, Z_lab) pairs (columns).
        """
        groups = {}
        for row in self.data:
            # key is (X_lab, Z_lab)
            key = (float(row[2]), float(row[4]))
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        
        # Convert lists to numpy arrays
        for key in groups:
            groups[key] = np.array(groups[key])
        return groups

    def get_groups(self):
        """
        Returns the dictionary of grouped points.
        """
        return self.groups


from myptv.extendedZolof.camera import camera_extendedZolof
from myptv.extendedZolof.calibrate import calibrate_extendedZolof
import itertools


class OptimizerCore:
    """
    Core implementation of the Greedy Calibration Optimizer.
    """
    def __init__(self, cam_name, point_manager, k=3):
        self.cam_name = cam_name
        self.pm = point_manager
        self.k = k
        self.group_keys = self.pm.get_groups().keys()

    def get_mse(self, points):
        """
        Calculates the mean squared error for a given subset of points.
        """
        x_list = points[:, :2] # camera coordinates
        X_list = points[:, 2:] # lab coordinates
        
        # Initialize a temporary camera to avoid side-effects
        # This assumes camera instance can be created just by name for EZ.
        cam = camera_extendedZolof(self.cam_name)
        cal = calibrate_extendedZolof(cam, x_list, X_list)
        cal.calibrate()
        return cal.mean_squared_err()

    def optimize_local(self):
        """
        Runs the greedy search starting from a random subset.
        """
        # Start with a random selection
        current_selection = {}
        for key in self.group_keys:
            group_data = self.pm.groups[key]
            indices = np.random.choice(len(group_data), min(self.k, len(group_data)), replace=False)
            current_selection[key] = indices

        best_mse = self._evaluate_selection(current_selection)
        
        improved = True
        while improved:
            improved = False
            
            # Loop through each group (column)
            for key in self.group_keys:
                group_data = self.pm.groups[key]
                n_points = len(group_data)
                
                # Save the original indices to restore them if needed
                original_indices = current_selection[key]
                
                # Try all possible combinations of k points in this group
                all_combos = list(itertools.combinations(range(n_points), min(self.k, n_points)))
                
                group_best_mse = best_mse
                group_best_indices = original_indices
                
                for combo in all_combos:
                    # Replace only the selection for this group
                    current_selection[key] = combo
                    mse = self._evaluate_selection(current_selection)
                    
                    if mse < group_best_mse:
                        group_best_mse = mse
                        group_best_indices = combo
                
                # If we found a better combo for this group, update and continue
                if group_best_mse < best_mse:
                    best_mse = group_best_mse
                    current_selection[key] = group_best_indices
                    improved = True
                else:
                    # Restore original if no improvement found
                    current_selection[key] = original_indices
                    
        return best_mse, self._get_full_points(current_selection)

    def _evaluate_selection(self, selection_dict):
        points = self._get_full_points(selection_dict)
        return self.get_mse(points)

    def _get_full_points(self, selection_dict):
        all_points = []
        for key, indices in selection_dict.items():
            all_points.append(self.pm.groups[key][list(indices)])
        return np.vstack(all_points)

    def run_multi_start(self, n_starts=10):
        """
        Runs the local optimizer multiple times and returns the overall best.
        """
        best_overall_mse = float('inf')
        best_overall_points = None
        
        for i in range(n_starts):
            mse, points = self.optimize_local()
            if mse < best_overall_mse:
                best_overall_mse = mse
                best_overall_points = points
            print(f"  Start {i+1}/{n_starts}: MSE = {mse:.4f}")
            
        return best_overall_mse, best_overall_points


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Optimize calibration points selection.')
    parser.add_argument('cam_name', type=str, help='Camera name (e.g., cam1)')
    parser.add_argument('points_file', type=str, help='Path to the cam*_cal_points file')
    parser.add_argument('-k', type=int, default=3, help='Points per column (default: 3)')
    parser.add_argument('-m', type=int, default=10, help='Number of random restarts (default: 10)')
    parser.add_argument('-o', '--output', type=str, help='Output file name')

    args = parser.parse_args()

    print(f"Loading points from {args.points_file}...")
    # Load with pandas to handle headers/delimiters better, but then to numpy
    import pandas as pd
    data = pd.read_csv(args.points_file, sep='\t', header=None).values
    
    pm = PointManager(data)
    print(f"Found {len(pm.get_groups())} columns.")
    
    optimizer = OptimizerCore(args.cam_name, pm, k=args.k)
    
    print(f"Starting optimization (k={args.k}, m={args.m})...")
    best_mse, best_points = optimizer.run_multi_start(n_starts=args.m)
    
    print(f"\nOptimization finished!")
    print(f"Best MSE: {best_mse:.6f}")
    
    if args.output:
        out_fname = args.output
    else:
        out_fname = args.points_file + "_optimized"
        
    np.savetxt(out_fname, best_points, fmt='%.2f', delimiter='\t')
    print(f"Optimized points saved to: {out_fname}")


if __name__ == '__main__':
    main()
