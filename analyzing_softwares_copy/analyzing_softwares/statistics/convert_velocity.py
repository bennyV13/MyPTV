import pandas as pd

def convert_velocity_to_mm_per_sec(data, frame_rate):
    """
    Convert velocity from mm/frame to mm/sec.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing the trajectory data
    frame_rate : float
        Frame rate in frames per second
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with converted velocities
    """
    # Use vectorized operations for better performance
    data['ux'] = data['ux'] * frame_rate
    data['uy'] = data['uy'] * frame_rate
    data['uz'] = data['uz'] * frame_rate
    data['ax'] = data['ax'] * frame_rate
    data['ay'] = data['ay'] * frame_rate
    data['az'] = data['az'] * frame_rate
    
    return data
