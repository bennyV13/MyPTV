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
    time (col 10)           : frame -> s (divide by fps)
    '''
    dt = 1.0 / fps
    physical_trajs = []
    for tr in traj_list:
        tr_copy = tr.copy()
        tr_copy[:, 4:7] *= fps           # Velocities
        tr_copy[:, 7:10] *= (fps**2)     # Accelerations
        tr_copy[:, 10] *= dt             # Time
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
    
    tm_lst = []
    
    v_lst = []
    
    for tr in traj_list:
        tm_lst += list(tr[:,-1])
        v_lst += list(get_component(tr))
    
    vals = pd.DataFrame({'tm': tm_lst, 'v': v_lst})
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
    
    
    cord_lst = []
    v_lst = []
    
    for tr in traj_list:
        cord_lst += list(get_cordinate(tr))
        v_lst += list(get_component(tr))
    
    bins = ((np.array(cord_lst) - start)/(stop-start)*nbins).astype('int')
    
    vals = pd.DataFrame({'bins': bins, 'v': v_lst})
    
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
    
    
    cord_lst = []
    v_lst = []
    
    for tr in traj_list:
        cord_lst += list(get_cordinate(tr))
        v_lst += list(get_component(tr))
    
    bins = ((np.array(cord_lst) - start)/(stop-start)*nbins).astype('int')
    
    vals = pd.DataFrame({'bins': bins, 'v': v_lst})
    
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
    N = max( [len(i) for i in arr_list] )
    r = [  [ [],[] ]   for i in range(N)]
    
    for arr in arr_list:
        for val in arr:
            r[0][0].append(val)
            r[0][1].append(val)
        for i in range(1,len(arr)):
            for val in arr[:-i]:
                r[i][0].append(val)
            for val in arr[i:]:
                r[i][1].append(val) 
    R,S,N = [],[],[]
    for i in r:
        if len(i[1]) <= 1:
            R.append(0)
            S.append(0)
            N.append(1)
        else:
            r1 = np.array(i[0]) - np.mean(i[0])
            r2 = np.array(i[1]) - np.mean(i[1])
            R.append( np.mean(r1*r2) / np.sqrt(np.mean(r1**2) * np.mean(r2**2) ) )
            S.append( np.std(r1*r2) / np.sqrt(np.mean(r1**2) * np.mean(r2**2) ) )
            N.append(len(r1))

    return np.array(R), np.array(S), np.array(N)




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
    # group the data according to frames
    by_time = [np.array(g) for k,g in data.groupby(10)]
    relative_sample = []
    
    for lst in by_time:
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                id_ = (lst[i][0], lst[j][0])
                dr = list(lst[i][1:4] - lst[j][1:4])
                dv = list(lst[i][4:7] - lst[j][4:7])
                new_sample = [id_] + dr + dv + [lst[i][-1]]
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
    from numpy import intersect1d, where, hstack, ones
    
    def in_list(arr, lst):
        return [arr[i] in lst for i in range(len(arr))]
        
    pairs = []
    for i in range(len(traj_list)):
        
        for j in range(i+1, len(traj_list)):
            
            common_times = intersect1d(traj_list[i][:,-1], traj_list[j][:,-1])
            
            if len(common_times)>0:
                
                ind_i = where(in_list(traj_list[i][:,-1], common_times))[0]
                ind_j = where(in_list(traj_list[j][:,-1], common_times))[0]
                p_ij = traj_list[i][ind_i, 1:10] - traj_list[j][ind_j, 1:10] 
                
                p_ij = hstack([traj_list[i][ind_i, :1], 
                               traj_list[j][ind_j, :1],
                               p_ij, traj_list[i][ind_i, -1:]])
                pairs.append(p_ij)
            
    return pairs




def save_trajs_feather(trajs, filename):
    '''
    Saves a list of trajectory arrays (or a single concatenated array/DataFrame)
    to a Feather file for quick loading.
    
    Parameters:
    -----------
    trajs : list of numpy arrays, or numpy array, or pandas DataFrame
        The trajectory data to be saved. If it's a list of numpy arrays,
        each array is expected to have shape (N, 11) with columns:
        [traj_id, x, y, z, vx, vy, vz, ax, ay, az, time].
    filename : str
        Path to the output Feather file.
    '''
    if isinstance(trajs, list):
        if len(trajs) == 0:
            df = pd.DataFrame(columns=['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time'])
        else:
            all_data = np.vstack(trajs)
            df = pd.DataFrame(all_data, columns=['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time'])
    elif isinstance(trajs, np.ndarray):
        df = pd.DataFrame(trajs, columns=['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time'])
    elif isinstance(trajs, pd.DataFrame):
        df = trajs
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
    
    # Sort by traj_id and then by time to ensure correct chronological order
    df_sorted = df.sort_values(by=['traj_id', 'time'])
    values = df_sorted.values
    
    traj_ids = values[:, 0]
    split_indices = np.where(traj_ids[:-1] != traj_ids[1:])[0] + 1
    
    trajs = np.split(values, split_indices)
    return trajs





