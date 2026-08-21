# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Sun Sep 11 17:52:50 2022

@author: ron


A few useful functions to analyze Lagrangian data.

"""
import numpy as np
import pandas as pd



def load_trajs_as_arrays(fname):
    '''
    given a path, fname, this returns a list of arrays, each corresponding
    to a particlular trajectory.
    '''
    from pandas import read_csv
    from numpy import array
    data = read_csv(fname, sep='\t', header=None)
    trajs = [array(sorted(array(g), key=lambda x: x[-1])) 
             for k,g in data.groupby(0) if k!=-1]
    return trajs




def load_samles_vs_time(fname):
    '''
    given a path, fname, this returns a dictionary where keys are
    frame numbers and values are arrays that contain the samples
    of the flow at these frames.
    '''
    from pandas import read_csv
    from numpy import array
    data = read_csv(fname, sep='\t', header=None)
    samples = [(k,array(g)) for k,g in data.groupby(10) if k!=-1]
    return dict(samples)





def is_inside_a_box(tr, xmin, xmax, ymin, ymax, zmin, zmax):
    '''
    given a trajectory (an array with convention as the result of 
    the smoothing function), this returns a list of boolean variable
    saying whether the coordinate at the corresponding time is inside the
    given box domain.
    
    Note that this can be used with numpy.where on a trajectory
    '''
    res = []
    for xi in tr:
        xin = xi[1] < xmax and xi[1] > xmin
        yin = xi[2] < ymax and xi[2] > ymin
        zin = xi[3] < zmax and xi[3] > zmin
        res.append(xin*yin*zin)
    return res




def filter_trajectories(traj_list, roi=None, min_length=2, remove_zero_dynamics=True):
    '''
    Filters a list of trajectories based on:
    1. Region of interest (ROI) boundaries: roi = {'x_min': ..., 'x_max': ..., etc.}
    2. Removal of points with all-zero velocity and acceleration (columns 4-9).
    3. Trajectory length constraints.
    '''
    filtered_trajs = []
    for tr in traj_list:
        tr_filtered = tr.copy()
        
        # 1. Remove rows with all-zero velocity and acceleration
        if remove_zero_dynamics:
            dynamics = tr_filtered[:, 4:10]
            non_zero_mask = np.any(dynamics != 0, axis=1)
            tr_filtered = tr_filtered[non_zero_mask]
            
        if len(tr_filtered) == 0:
            continue
            
        # 2. ROI Filtering
        if roi is not None:
            roi_mask = (
                (tr_filtered[:, 1] >= roi.get('x_min', -np.inf)) & 
                (tr_filtered[:, 1] <= roi.get('x_max', np.inf)) &
                (tr_filtered[:, 2] >= roi.get('y_min', -np.inf)) & 
                (tr_filtered[:, 2] <= roi.get('y_max', np.inf)) &
                (tr_filtered[:, 3] >= roi.get('z_min', -np.inf)) & 
                (tr_filtered[:, 3] <= roi.get('z_max', np.inf))
            )
            tr_filtered = tr_filtered[roi_mask]
            
        # 3. Minimum length check
        if len(tr_filtered) >= min_length:
            filtered_trajs.append(tr_filtered)
            
    return filtered_trajs




def convert_trajs_to_physical_units(traj_list, fps):
    '''
    Converts trajectory data from frame-based units to physical units.
    vx, vy, vz (cols 4,5,6) : mm/frame -> mm/s (multiply by fps)
    ax, ay, az (cols 7,8,9) : mm/frame^2 -> mm/s^2 (multiply by fps^2)
    time (last col)         : frame -> s (divide by fps)
    '''
    dt = 1.0 / fps
    physical_trajs = []
    for tr in traj_list:
        tr_copy = tr.copy()
        tr_copy[:, 4:7] *= fps           # Velocities
        tr_copy[:, 7:10] *= (fps**2)     # Accelerations
        
        if tr_copy.shape[1] == 25:
            tr_copy[:, 13:16] *= fps         # pdot
            tr_copy[:, 16:19] *= (fps**2)    # pddot
            
        tr_copy[:, -1] *= dt             # Time
        physical_trajs.append(tr_copy)
    return physical_trajs




# ============================================================================
#    Lagrangian Velocity Statistics:


def get_velocity_list(traj_list, kind='x'):
    '''
    Takes in a list of trajectories and returns a list of their velocity along
    a given component.
    '''        
    if kind=='x':
        get_component = lambda tr: tr[:,4]
    
    elif kind=='y':
        get_component = lambda tr: tr[:,5]
        
    elif kind=='z':
        get_component = lambda tr: tr[:,6]
        
    elif kind=='KE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,4:7]**2, axis=1))
    
    elif kind=='ax':
        get_component = lambda tr: tr[:,7]
    
    elif kind=='ay':
        get_component = lambda tr: tr[:,8]
        
    elif kind=='az':
        get_component = lambda tr: tr[:,9]
        
    elif kind=='aKE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,7:10]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
            
    lst = [u for tr in traj_list for u in get_component(tr) ]
    
    return lst




def get_trajectory_velocities(traj_list, kind='x'):
    '''
    Takes in a list of trajectories and returns lists of their velocities along
    a given component (i.e. we return a nested list, each sublist is a velocity
    time series of one trajectory).
    '''        
    if kind=='x':
        get_component = lambda tr: tr[:,4]
    
    elif kind=='y':
        get_component = lambda tr: tr[:,5]
        
    elif kind=='z':
        get_component = lambda tr: tr[:,6]
        
    elif kind=='px':
        get_component = lambda tr: tr[:,10]
        
    elif kind=='py':
        get_component = lambda tr: tr[:,11]
        
    elif kind=='pz':
        get_component = lambda tr: tr[:,12]
        
    elif kind=='KE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,4:7]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
        
    lst = [get_component(tr) for tr in traj_list]
    
    return lst




def get_velocity_mean_std(traj_list, kind='x'):
    '''
    For a list of trajectories, this returns the mean and standard deviation 
    of a velocity component. The "kind" parameter defines which component to 
    use: 'x', 'y', 'z' or 'KE' standing for x, y, or z velocity component and 
    KE is the kinetic energy.
    '''
    A = get_velocity_list(traj_list, kind=kind)
    return np.mean(A), np.std(A)



def get_trajectory_velocity_increments(traj, kind='x'):
    '''
    Given a trajectory, this function returns lists of the temporal increments
    of its velocity. The "kind" parameter defines which component to use:
    'x', 'y', 'z' or 'KE' standing for x, y, or z velocity component and KE is 
    the kinetic energy.
    
    We return a nested list where the second sublist
    contains samples of KE(t+1) - KE(t), and the last sublist contains
    KE(t+T) - KE(t) where KE is the kinetic energy and T is the tracking time
    of the trajectory.
    '''
    if kind=='x':
        A = traj[:,4]
    
    elif kind=='y':
        A = traj[:,5]
        
    elif kind=='z':
        A = traj[:,6]
        
    elif kind=='KE':
        A = 0.5*(np.sum(traj[:,4:7]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
        
    increments = [[0]]
    for i in range(1,len(A)):
        increments.append(list(A[i:] - A[:-i]))
    
    return increments




def get_velocity_increments(traj_list, kind='x'):
    '''
    For a list of trajectories, this returns a nested list of all kinetic energy
    increments samples.
    '''
    increments = []
    
    for tr in traj_list:
        inc = get_trajectory_velocity_increments(tr, kind=kind)
        for i in range(len(inc)):
            if len(increments)==i:
                increments.append(inc[i])
            else:
                increments[i] += inc[i]
    return increments




def get_mean_std_time_series(traj_list, kind='x'):
    '''
    From a list of trajectories, this will return statistics of a velocity 
    component as a function of time. The "kind" parameter defines which 
    component to use: 'x', 'y', 'z' or 'KE' standing for x, y, or z velocity 
    component and KE is the kinetic energy.
    
    The statistics retured are: the number of samples, the mean, and std at
    each time frame. The values are returned as an array with fisrt column 
    being the time, second is the number of samples, and the rest are mean and 
    std.
    '''
    
    if kind=='x':
        get_component = lambda tr: tr[:,4]
    
    elif kind=='y':
        get_component = lambda tr: tr[:,5]
        
    elif kind=='z':
        get_component = lambda tr: tr[:,6]
        
    elif kind=='KE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,4:7]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
    
    tm_arr = np.concatenate([tr[:, -1] for tr in traj_list])
    v_arr = np.concatenate([get_component(tr) for tr in traj_list])
    
    vals = pd.DataFrame({'tm': tm_arr, 'v': v_arr})
    grouped = [[k, len(g['v']), np.mean(g['v']), np.std(g['v'])] for k,g in 
               vals.groupby('tm')]
    
    return np.array(grouped)  








def get_mean_velocity_profiles(traj_list, start, stop, nbins, direction, kind):
    '''
    Returns a time averaged velocity profile of a given component along a given 
    direction.
    
    inputs:
    
    traj_list - a list of trajectories
    start - the coordiante value at which the profile begins
    stop - the coordinate at which the profile ends
    nbins - the number of points along the profile
    direction - string ('x', 'y' or 'z') for the axis along which the 
                profile is calculated
    kind - string giving the velocity component ('x', 'y', 'z', or 'KE' for 
           kinetic energy)
    '''
    
    if kind=='x':
        get_component = lambda tr: tr[:,4]
    
    elif kind=='y':
        get_component = lambda tr: tr[:,5]
        
    elif kind=='z':
        get_component = lambda tr: tr[:,6]
        
    elif kind=='KE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,4:7]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
    
    
    if direction=='x':
        get_cordinate = lambda tr: tr[:,1]
    
    elif direction=='y':
        get_cordinate = lambda tr: tr[:,2]
        
    elif direction=='z':
        get_cordinate = lambda tr: tr[:,3]
        
    else:
        raise ValueError('undefined direction "%s"'%direction)
    
    
    cord_arr = np.concatenate([get_cordinate(tr) for tr in traj_list])
    v_arr = np.concatenate([get_component(tr) for tr in traj_list])
    
    bins = ((cord_arr - start)/(stop-start)*nbins).astype('int')
    
    vals = pd.DataFrame({'bins': bins, 'v': v_arr})
    
    avg_V = []
    grouped = dict(list(vals.groupby('bins')))
    for i in range(nbins):
        if i in grouped:
            avg_V.append(np.mean(grouped[i]['v']))
        else:
            avg_V.append(np.nan)
            
    db = (stop-start)/nbins
    axis = [start+db*(i+0.5) for i in range(nbins)]
    
    return np.array([axis, avg_V])







def get_std_velocity_profiles(traj_list, start, stop, nbins, direction, kind):
    '''
    Returns a time averaged velocity profile of a given component along a given 
    direction.
    
    inputs:
    
    traj_list - a list of trajectories
    start - the coordiante value at which the profile begins
    stop - the coordinate at which the profile ends
    nbins - the number of points along the profile
    direction - string ('x', 'y' or 'z') for the axis along which the 
                profile is calculated
    kind - string giving the velocity component ('x', 'y', 'z', or 'KE' for 
           kinetic energy)
    '''
    
    if kind=='x':
        get_component = lambda tr: tr[:,4]
    
    elif kind=='y':
        get_component = lambda tr: tr[:,5]
        
    elif kind=='z':
        get_component = lambda tr: tr[:,6]
        
    elif kind=='KE':
        get_component = lambda tr: 0.5*(np.sum(tr[:,4:7]**2, axis=1))
        
    else:
        raise ValueError('undefined kind "%s"'%kind)
    
    
    if direction=='x':
        get_cordinate = lambda tr: tr[:,1]
    
    elif direction=='y':
        get_cordinate = lambda tr: tr[:,2]
        
    elif direction=='z':
        get_cordinate = lambda tr: tr[:,3]
        
    else:
        raise ValueError('undefined direction "%s"'%direction)
    
    
    cord_arr = np.concatenate([get_cordinate(tr) for tr in traj_list])
    v_arr = np.concatenate([get_component(tr) for tr in traj_list])
    
    bins = ((cord_arr - start)/(stop-start)*nbins).astype('int')
    
    vals = pd.DataFrame({'bins': bins, 'v': v_arr})
    
    std_V = []
    grouped = dict(list(vals.groupby('bins')))
    for i in range(nbins):
        if i in grouped:
            std_V.append(np.std(grouped[i]['v']))
        else:
            std_V.append(np.nan)
            
    db = (stop-start)/nbins
    axis = [start+db*(i+0.5) for i in range(nbins)]
    
    return np.array([axis, std_V])






def list_corelation(arr_list):
    '''
    returns the array of correlation for a list of arrays as a function of
    time lag:
    
              < (arr(t+x) - <arr(t+x)> )*( arr(t) - <arr(t)> ) >
    R  =  ===============================================================
          sqrt( < (arr(t+x) - <arr(t+x)>)^2 > < (arr(t) - <arr(t)>)^2 > )
          
    ( where <> is average over samples and x is a time (index) lag)
    
    
    returns -
    R - array of correlation coefficients
    S - array of standard deviations for R as a funciton of time
    N - array of number of elements used at each time 
    '''
    N_max = max([len(i) for i in arr_list]) if arr_list else 0
    r0 = [[] for _ in range(N_max)]
    r1 = [[] for _ in range(N_max)]
    
    for arr in arr_list:
        if len(arr) == 0: continue
        r0[0].append(arr)
        r1[0].append(arr)
        for i in range(1, len(arr)):
            r0[i].append(arr[:-i])
            r1[i].append(arr[i:])
            
    R, S, counts = [], [], []
    for i in range(N_max):
        if len(r1[i]) == 0:
            R.append(0)
            S.append(0)
            counts.append(0)
            continue
            
        arr0 = np.concatenate(r0[i])
        arr1 = np.concatenate(r1[i])
        if len(arr1) <= 1:
            R.append(0)
            S.append(0)
            counts.append(len(arr1))
        else:
            arr0 = arr0 - np.mean(arr0)
            arr1 = arr1 - np.mean(arr1)
            denominator = np.sqrt(np.mean(arr0**2) * np.mean(arr1**2))
            if denominator == 0:
                R.append(0)
                S.append(0)
            else:
                R.append(np.mean(arr0 * arr1) / denominator)
                S.append(np.std(arr0 * arr1) / denominator)
            counts.append(len(arr0))

    return np.array(R), np.array(S), np.array(counts)




def get_Lagrangian_autocorrelation(traj_list, kind='x'):
    '''
    Returns the autocorrelation of the velocity of Lagrangian particles along
    the trajectory. The kind parameter indicates the velocity component ('x',
    'y', 'z', or 'KE'). 
    '''
    
    v_lst = get_trajectory_velocities(traj_list, kind=kind)
    R, S, N = list_corelation(v_lst)
    return R



# ============================================================================
#    Relative data (different trajectories)





def get_relative_samples(data):
    '''
    Returns a list of relative samples, containing 
    relative positions and relative velocities.
    The first index is a tuple of the trajectory
    ids, indexes 1-3 are selative positions, 4-6
    are relative velocitied, and the last is time.
    '''
    merged = pd.merge(data, data, on=10, suffixes=('_i', '_j'))
    merged = merged[merged['0_i'] < merged['0_j']]
    
    v = merged.values
    dr = v[:, 1:4] - v[:, 12:15]
    dv = v[:, 4:7] - v[:, 15:18]
    
    relative_sample = []
    for i in range(len(v)):
        id_tuple = (v[i, 0], v[i, 11])
        new_sample = [id_tuple] + dr[i].tolist() + dv[i].tolist() + [v[i, 10]]
        relative_sample.append(new_sample)
        
    return relative_sample





def get_binned_relative_velocity_samples(data, r0, rn, n):
    '''
    Returns lists with samples of the relative velocity, binned
    according to their distance.
    
    r0 and rn are the distance limits, 
    n is the number of binnes within the range,
    and data is a DataFrame of the data samples.
    '''
    rel_samps = pd.DataFrame(get_relative_samples(data))
    print(len(rel_samps))
    rel_samps['d'] = np.sum(rel_samps[[1,2,3]]**2, axis=1)**0.5
    rel_samps['dvr'] = np.sum(np.array(rel_samps[[1,2,3]]) * np.array(rel_samps[[4,5,6]]), axis=1) / np.array(rel_samps['d'])
    rel_samps['bin'] = ((np.array(rel_samps['d']) - r0)/(rn-r0)*n).astype(int)
    dv_bins = [list(g['dvr']) for k,g in rel_samps.groupby('bin') if k<n]
    return dv_bins





def get_pairs(traj_list):
    '''
    Returns a list of trajectories of relative position
    and relative velocities at commong time instances.
    
    Input - 
    
    traj_list - a list of arrays that represent single
                particle trajectories. 
    
    Return -
    
    pairs - a list of arrays (n,12). In each array, the 
            indexes 2,3,4 are hte relative position, the
            5,6,7 are relative velocity, the 8,9,10 are
            relative accelerations and 11 is the frame 
            number. Inedx 0 is the id number of particle
            i and 1 is the id of particle j.
    '''
    if len(traj_list) == 0:
        return []
    
    all_data = np.vstack(traj_list)
    df = pd.DataFrame(all_data)
    
    merged = pd.merge(df, df, on=10, suffixes=('_i', '_j'))
    merged = merged[merged['0_i'] < merged['0_j']]
    
    pairs = []
    merged = merged.sort_values(['0_i', '0_j', 10])
    for (id_i, id_j), group in merged.groupby(['0_i', '0_j']):
        v = group.values
        
        rel_pos = v[:, 1:4] - v[:, 12:15]
        rel_vel = v[:, 4:7] - v[:, 15:18]
        rel_acc = v[:, 7:10] - v[:, 18:21]
        
        p_ij = np.hstack([v[:, 0:1], v[:, 11:12], rel_pos, rel_vel, rel_acc, v[:, 10:11]])
        pairs.append(p_ij)
        
    return pairs




def save_trajs_feather(trajs, filename):
    '''
    Saves a list of trajectory arrays (or a single concatenated array/DataFrame)
    to a Feather file for quick loading.
    
    Parameters:
    -----------
    trajs : list of numpy arrays, or numpy array, or pandas DataFrame
        The trajectory data to be saved.
    filename : str
        Path to the output Feather file.
    '''
    def get_col_names(num_cols):
        if num_cols == 11:
            return ['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time']
        elif num_cols == 25:
            return ['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'px', 'py', 'pz', 'pdot_x', 'pdot_y', 'pdot_z', 'pddot_x', 'pddot_y', 'pddot_z', 'cam0', 'cam1', 'cam2', 'cam3', 'error', 'time']
        else:
            return [f'col_{j}' for j in range(num_cols)]

    if isinstance(trajs, list):
        if len(trajs) == 0:
            df = pd.DataFrame(columns=['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time', 'unique_id'])
        else:
            arrays_with_id = []
            for i, tr in enumerate(trajs):
                unique_col = np.full((tr.shape[0], 1), i, dtype=np.float64)
                arrays_with_id.append(np.hstack((tr, unique_col)))
            all_data = np.vstack(arrays_with_id)
            cols = get_col_names(all_data.shape[1] - 1) + ['unique_id']
            df = pd.DataFrame(all_data, columns=cols)
            df['unique_id'] = df['unique_id'].astype(int)
    elif isinstance(trajs, np.ndarray):
        cols = get_col_names(trajs.shape[1])
        df = pd.DataFrame(trajs, columns=cols)
        df['unique_id'] = 0
    elif isinstance(trajs, pd.DataFrame):
        df = trajs.copy()
        if 'unique_id' not in df.columns:
            df['unique_id'] = 0
    else:
        raise TypeError("trajs must be a list of numpy arrays, a numpy array, or a pandas DataFrame")
    
    df.to_feather(filename)
    print(f"Saved {len(df)} points to {filename} in Feather format.")




def load_trajs_feather(filename, as_arrays=True):
    '''
    Loads trajectory data from a Feather file.
    
    Parameters:
    -----------
    filename : str
        Path to the Feather file.
    as_arrays : bool, default True
        If True, returns a list of numpy arrays (grouped by trajectory ID),
        matching the format returned by load_ptv_trajectories.
        If False, returns the raw pandas DataFrame.
    '''
    df = pd.read_feather(filename)
    if not as_arrays:
        return df
    
    if len(df) == 0:
        return []
    
    group_col = 'unique_id' if 'unique_id' in df.columns else 'traj_id'
    
    # Sort by group_col and then by time to ensure correct chronological order
    df_sorted = df.sort_values(by=[group_col, 'time'])
    
    # Extract only the original columns (all except unique_id or group_col)
    original_cols = [c for c in df.columns if c != group_col]
    values = df_sorted[original_cols].values
    
    group_ids = df_sorted[group_col].values
    split_indices = np.where(group_ids[:-1] != group_ids[1:])[0] + 1
    
    trajs = np.split(values, split_indices)
    return trajs


def extract_orientation_pairs(traj_list):
    '''
    Extracts raw pairwise distances and orientation dot products for all pairs 
    of fibers that exist in the exact same frame.
    
    Returns:
    --------
    all_dists : numpy array
        1D array of pairwise Euclidean distances between fibers.
    all_corrs : numpy array
        1D array of the absolute dot products of their orientation unit vectors.
    '''
    if isinstance(traj_list, list):
        if len(traj_list) == 0:
            return np.array([]), np.array([])
        all_data = np.vstack(traj_list)
    elif isinstance(traj_list, np.ndarray):
        all_data = traj_list
    elif hasattr(traj_list, 'values'):
        all_data = traj_list.values
    else:
        raise ValueError("traj_list must be a list of numpy arrays, a numpy array, or a pandas DataFrame")
        
    pos = all_data[:, 1:4]
    ori = all_data[:, 10:13]
    frames = all_data[:, -1]
    
    # Normalize orientation vectors
    norms = np.linalg.norm(ori, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    ori_normed = ori / norms
    
    unique_frames = np.unique(frames)
    
    all_dists = []
    all_corrs = []
    
    for f in unique_frames:
        mask = (frames == f)
        P = pos[mask]
        O = ori_normed[mask]
        
        M = P.shape[0]
        if M < 2:
            continue
            
        # Get unique pairs indices
        idx_i, idx_j = np.triu_indices(M, k=1)
        
        # Calculate distances
        dr = P[idx_i] - P[idx_j]
        dists = np.linalg.norm(dr, axis=1)
        
        # Calculate absolute dot products
        dot_products = np.sum(O[idx_i] * O[idx_j], axis=1)
        abs_dots = np.abs(dot_products)
        
        all_dists.append(dists)
        all_corrs.append(abs_dots)
        
    if len(all_dists) == 0:
        return np.array([]), np.array([])
        
    all_dists = np.concatenate(all_dists)
    all_corrs = np.concatenate(all_corrs)
    
    return all_dists, all_corrs


def bin_orientation_pairs(all_dists, all_corrs, nbins=50, max_dist=None):
    '''
    Bins the raw pairwise distances and correlations.
    
    Returns:
    --------
    bin_centers : numpy array
        Centers of the distance bins.
    bin_means : numpy array
        Averaged absolute dot product of orientations in each bin.
    counts : numpy array
        Number of pairs in each bin.
    '''
    if len(all_dists) == 0:
        return np.array([]), np.array([]), np.array([])
        
    if max_dist is None:
        max_dist = np.max(all_dists) if len(all_dists) > 0 else 1.0
        
    counts, bin_edges = np.histogram(all_dists, bins=nbins, range=(0.0, max_dist))
    sums, _ = np.histogram(all_dists, bins=nbins, range=(0.0, max_dist), weights=all_corrs)
    
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_means = np.zeros_like(bin_centers)
    
    valid = counts > 0
    bin_means[valid] = sums[valid] / counts[valid]
    bin_means[~valid] = np.nan
    
    return bin_centers, bin_means, counts


def get_orientation_correlation_by_distance(traj_list, nbins=50):
    '''
    Calculates the spatial correlation of fiber orientations as a function of 
    distance between pairs of fibers in the same frame.
    
    Formula:
    C(R) = < |n̂₁ · n̂₂| >_R
    where n̂₁ and n̂₂ are the normalized orientation unit vectors of a pair of 
    fibers in the same frame, and R is their distance.
    
    Returns:
    --------
    bin_centers, bin_means, counts
    '''
    all_dists, all_corrs = extract_orientation_pairs(traj_list)
    return bin_orientation_pairs(all_dists, all_corrs, nbins)


def compute_opcf(positions, orientations, box_size, num_bins, max_r):
    """
    Computes g(r) and the orientational correlation <cos(theta)>.
    positions: (N, 3) array in metric units (e.g., meters or millimeters).
    orientations: (N, 3) array of unit vectors representing fiber direction.
    """
    from scipy.spatial.distance import pdist, squareform
    num_particles = len(positions)
    
    # Calculate pairwise Euclidean distances
    dist_matrix = squareform(pdist(positions))
    
    # Calculate dot products of orientation vectors to get cos(theta_12)
    # Using absolute value because fibers are apolar, but the raw formula uses normal dot product
    # The user specifies np.dot(orientations, orientations.T), we will use their exact code but handle abs if needed.
    # We will compute the absolute dot products to handle apolar fiber symmetry as discussed before.
    dot_products = np.abs(np.dot(orientations, orientations.T))
    
    # Setup radial bins in your chosen metric unit
    bins = np.linspace(0, max_r, num_bins + 1)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    
    g_r = np.zeros(num_bins)
    orient_corr = np.zeros(num_bins)
    counts = np.zeros(num_bins)
    
    # Ideal gas density
    rho = num_particles / (box_size**3)
    
    for i in range(num_bins):
        # Find pairs within the current radial bin
        mask = (dist_matrix >= bins[i]) & (dist_matrix < bins[i+1])
        np.fill_diagonal(mask, False) # Ignore self-pairs
        
        # Count pairs for standard g(r)
        pair_count = np.sum(mask)
        counts[i] = pair_count
        
        # Normalize g(r) by ideal shell volume
        shell_volume = (4.0 / 3.0) * np.pi * (bins[i+1]**3 - bins[i]**3)
        g_r[i] = pair_count / (num_particles * rho * shell_volume)
        
        # Calculate average orientational correlation <cos(theta_12)>
        if pair_count > 0:
            orient_corr[i] = np.mean(dot_products[mask])
            
    return bin_centers, g_r, orient_corr, counts






