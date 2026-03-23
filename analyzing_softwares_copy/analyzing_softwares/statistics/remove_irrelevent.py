import pandas as pd
import numpy as np

def remove_irrelevent(data, roi=None):
    """
    Filters data based on the following rules:
    1. Remove rows starting with -1.
    2. Remove rows where columns 5 to 10 are all zeros.
    3. Remove points outside the ROI if specified.

    Parameters:
    - data (DataFrame): Input DataFrame with trajectory data.
    - roi (dict): Dictionary containing ROI parameters with keys 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'.

    Returns:
    - filtered_data (DataFrame): The filtered DataFrame.
    """
    # Track original frame counts
    original_frames = data['frame'].unique()
    original_frame_counts = data.groupby('frame').size()
    original_points_count=len(data)
    # Step 1: Filter out rows starting with -1
    filtered_data = data[data['particle_id'] != -1]
     
    # Step 2: Filter out rows where velocity and acceleration columns are all zeros
    # Use vectorized operations for better performance
    mask = (
        (filtered_data['ux'] != 0) | 
        (filtered_data['uy'] != 0) | 
        (filtered_data['uz'] != 0) |
        (filtered_data['ax'] != 0) | 
        (filtered_data['ay'] != 0) | 
        (filtered_data['az'] != 0)
    )
    filtered_data = filtered_data[mask]
    
    # Track frames after particle_id filtering
    frames_after_particle_filter = filtered_data['frame'].unique()
    frames_removed_by_particle = set(original_frames) - set(frames_after_particle_filter)
   
    # Track frames after velocity/acceleration filtering
    frames_after_velocity_filter = filtered_data['frame'].unique()
    frames_removed_by_velocity = set(frames_after_particle_filter) - set(frames_after_velocity_filter)
    filtered_points_count=len(filtered_data)
    
    # Step 3: Apply ROI Filter if ROI parameters are provided
    frames_removed_by_roi = set()
    if roi is not None:
        roi_mask = (
            (filtered_data['x'] >= roi['x_min']) & (filtered_data['x'] <= roi['x_max']) &
            (filtered_data['y'] >= roi['y_min']) & (filtered_data['y'] <= roi['y_max']) &
            (filtered_data['z'] >= roi['z_min']) & (filtered_data['z'] <= roi['z_max'])
        )
        
        # Track frames before ROI filtering
        frames_before_roi = filtered_data['frame'].unique()
        
        # Apply ROI filter
        filtered_data = filtered_data[roi_mask]
        
        # Track frames after ROI filtering
        frames_after_roi = filtered_data['frame'].unique()
        frames_removed_by_roi = set(frames_before_roi) - set(frames_after_roi)
    
    # Compile removal statistics
    total_removed_frames = set(original_frames) - set(filtered_data['frame'].unique())
    
    # Print removal statistics
    print(f"\nFrame filtering statistics:")
    print(f"Original frames: {len(original_frames)}")
    print(f"Frames after filtering: {len(filtered_data['frame'].unique())}")
    print(f"Total frames removed: {len(total_removed_frames)}")
    print(f"Total points removed: {original_points_count-filtered_points_count}")
    
    if frames_removed_by_particle:
        print(f"\nFrames removed by particle_id filter: {len(frames_removed_by_particle)}")
        print(f"  First 5 removed frames: {sorted(list(frames_removed_by_particle))[:5]}")
    
    if frames_removed_by_velocity:
        print(f"Frames removed by velocity/acceleration filter: {len(frames_removed_by_velocity)}")
        print(f"  First 5 removed frames: {sorted(list(frames_removed_by_velocity))[:5]}")
    
    if frames_removed_by_roi:
        print(f"Frames removed by ROI filter: {len(frames_removed_by_roi)}")
        print(f"  First 5 removed frames: {sorted(list(frames_removed_by_roi))[:5]}")
    
    # Print frame counts for frames that were completely removed
    if total_removed_frames:
        print("\nFrame counts for completely removed frames:")
        for frame in sorted(list(total_removed_frames))[:10]:  # Show first 10
            print(f"  Frame {frame}: {original_frame_counts.get(frame, 0)} points")
        
        if len(total_removed_frames) > 10:
            print("  ...")
            for frame in sorted(list(total_removed_frames))[-5:]:  # Show last 5
                print(f"  Frame {frame}: {original_frame_counts.get(frame, 0)} points")
    
    return filtered_data
