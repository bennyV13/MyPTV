from scipy.spatial import KDTree
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import gaussian_kde
from scipy.stats import kstest, norm


def rand_data(n, x_size, y_size, z_size):
    """
    Generates n random points in a volume and returns their NNDs.
    """
    points = np.random.rand(n, 3) * [x_size, y_size, z_size]
    kdtree = KDTree(points)
    distances, _ = kdtree.query(points, k=2)
    return distances[:, 1]


def plot_nnd_extremes(coords, nnds, frames, n_extremes=100):
    """
    Plots the n_extremes particles with the largest and smallest NNDs in 3D.
    Uses shades of Blue (Smallest) and Red (Largest) to show time evolution.
    """
    # Combine coordinates, NNDs, and frames
    data_stack = np.column_stack((coords, nnds, frames))
    # Sort by NND (the 4th column, index 3)
    sorted_data = data_stack[data_stack[:, 3].argsort()]

    smallest = sorted_data[:n_extremes]
    largest = sorted_data[-n_extremes:]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Plot Smallest NND (Crowded) with Blue shades representing time
    sc_small = ax.scatter(smallest[:, 0], smallest[:, 1], smallest[:, 2], 
                          c=smallest[:, 4], cmap='Blues', 
                          label=f'Smallest {n_extremes} NND (Crowded)', 
                          alpha=0.7, edgecolors='k', linewidths=0.5)
    
    # Plot Largest NND (Isolated) with Red shades representing time
    sc_large = ax.scatter(largest[:, 0], largest[:, 1], largest[:, 2], 
                          c=largest[:, 4], cmap='Reds', 
                          label=f'Largest {n_extremes} NND (Isolated)', 
                          alpha=0.7, edgecolors='k', linewidths=0.5)

    # Add colorbars to show time mapping
    cbar_small = plt.colorbar(sc_small, ax=ax, pad=0.1, shrink=0.6)
    cbar_small.set_label('Frame (Time Evolution - Blue)')
    
    cbar_large = plt.colorbar(sc_large, ax=ax, pad=0.05, shrink=0.6)
    cbar_large.set_label('Frame (Time Evolution - Red)')

    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]')
    ax.set_title(f'Top {n_extremes} NND Extremes: Shading shows Time Evolution')
    ax.legend()
    plt.show()


def remove_irrelevent(data, roi=None):
    """
    Filters data based on the following rules:
    1. Remove rows starting with -1.
    2. Remove rows where columns 5 to 10 are all zeros.
    3. Remove points outside the ROI if specified.
    """
    if data is None:
        return None
        
    original_frames = data['frame'].unique()
    original_frame_counts = data.groupby('frame').size()
    original_points_count=len(data)
    filtered_data = data 
    
    val=1000.0
    cols = ['ux', 'uy', 'uz', 'ax', 'ay', 'az']
    mask = (np.abs(filtered_data[cols]) <= val).all(axis=1)
    filtered_data = filtered_data[mask]
    
    filtered_points_count=len(filtered_data)
    
    if roi is not None:
        roi_mask = (
            (filtered_data['x'] >= roi['x_min']) & (filtered_data['x'] <= roi['x_max']) &
            (filtered_data['y'] >= roi['y_min']) & (filtered_data['y'] <= roi['y_max']) &
            (filtered_data['z'] >= roi['z_min']) & (filtered_data['z'] <= roi['z_max'])
        )
        filtered_data = filtered_data[roi_mask]
    
    return filtered_data

def load_trajectory_data(file_path):
    try:
        data = pd.read_csv(file_path, delimiter=r'\s+', header=None,
                           names=['particle_id', 'x', 'y', 'z', 'ux', 'uy', 'uz', 
                                 'ax', 'ay', 'az', 'frame'])
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

if __name__ == '__main__':
    # This part only runs if the script is executed directly, not when imported.
    file_path = 'Data_and_analysis/Analysis/20260315_analysis/trajecotries_stitched'
    df=load_trajectory_data(file_path)
    if df is not None:
        roi = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 100, 'z_min': -50, 'z_max': 0}
        df=remove_irrelevent(df, roi)
        # ... rest of the original execution logic can be restored here if needed ...
