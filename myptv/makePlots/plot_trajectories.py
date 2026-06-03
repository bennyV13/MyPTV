# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
Created on Fri May 31 15:01:48 2024

@author: ron
"""

from pandas import read_csv
from numpy import ptp, array, arange, amin, amax, percentile, gradient
import matplotlib.pyplot as plt

from moviepy.video.io.bindings import mplfig_to_npimage
import moviepy.editor as mpy






def plot_trajectories(fname, min_length, write_trajID=False, t0=0, te=-1):
    '''
    This function plots trajectories from a given file in 3D.
    
    inputs:
        
    fname - the path to the file that contains the trajectories; the file can 
            be either in trajectories format or in smoothed trajectories format
    
    min_lenth - only trajectories that have more samples than this number will
                be plotted
                
    write_trajID - If True this will desplay the trajectory ID on top of them
    
    t0 and te - used to delineate the time range for which we plot the data. 
                we only plot the samples in the time range starting at frame
                t0 and ending at frame te. Set t0=0 and te=-1 (default) to plot
                trajectories at all times available.
    '''
    import pandas as pd
    if isinstance(fname, str):
        fname = [fname]
        
    data_list = []
    for f_idx, f in enumerate(fname):
        d = read_csv(f, header=None, sep='\t')
        d[0] = d[0].apply(lambda x: f"{f_idx}_{x}" if x != -1 else x)
        data_list.append(d)
        
    data = pd.concat(data_list, ignore_index=True)
    trajectories = dict([(g, array(k.values)) 
                         for g,k in data.groupby(0) if g!=-1])
    
    xmax = amax(data[1])
    xmin = amin(data[1])
    ymax = amax(data[2])
    ymin = amin(data[2])
    zmax = amax(data[3])
    zmin = amin(data[3])
    
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    xm = []
    ym = []
    zm = []
    
    if te==-1:
        te = max(data[data.shape[1]-1])
    
    trajIDs = list(trajectories.keys())
    
    
    # estimate maximum velocity
    v_lst = [[],[],[]]
    used_ids = []
    for id_ in trajIDs:
        if len(trajectories[id_][:,1])<min_length: continue
        time = trajectories[id_][:,-1]
        inds = arange(len(trajectories[id_]))
        
        if time[0]>=te or time[-1]<=t0: 
            continue
    
        if time[0]>=t0: 
            i0 = 0
        else:
            i0 = inds[time==t0][0]
        
        if time[-1]<=te: 
            ie = -1
        else:
            ie = inds[time==te][0]    
            
        
        xs = trajectories[id_][i0:ie,1]
        ys = trajectories[id_][i0:ie,2]
        zs = trajectories[id_][i0:ie,3]
        if len(xs)<2: continue
        v_lst[0].append(abs(sum(gradient(xs))/len(xs)))
        v_lst[1].append(abs(sum(gradient(ys))/len(ys)))
        v_lst[2].append(abs(sum(gradient(zs))/len(zs)))
        used_ids.append(id_)
    
    V = amax(v_lst)
    
    count = 0
    for id_ in used_ids:
        time = trajectories[id_][:,-1]
        inds = arange(len(trajectories[id_]))
        
        if time[0]>=te or time[-1]<=t0: 
            continue
    
        if time[0]>=t0: 
            i0 = 0
        else:
            i0 = inds[time==t0][0]
        
        if time[-1]<=te: 
            ie = -1
        else:
            ie = inds[time==te][0]    
            
        
        xs = trajectories[id_][i0:ie,1]
        ys = trajectories[id_][i0:ie,2]
        zs = trajectories[id_][i0:ie,3]
        vx = sum(gradient(xs))/len(xs) / V
        vy = sum(gradient(ys))/len(ys) / V
        vz = sum(gradient(zs))/len(zs) / V
        #c = (1-(xs[0]-xmin)/(xmax-xmin)*0.97, 
        #     (ys[0]-ymin)/(ymax-ymin)*0.97, 
        #     (zs[0]-zmin)/(zmax-zmin)*0.97)
        c = [0.5-vx, 0.5+vy, 0.5+vz]
        c = [1*(ci>1) + ci*(ci<=1) for ci in c]
        c = [0*(ci<0) + ci*(ci>=0) for ci in c]
        l = ax.plot(xs, zs, ys, 'o-', ms=1, lw=0.5, color=c)
        
        xm.append(amin(xs)) ; xm.append(amax(xs))
        ym.append(amin(ys)) ; ym.append(amax(ys))
        zm.append(amin(zs)) ; zm.append(amax(zs))
        
        if write_trajID==True:
            color = l[0].get_color()
            ax.text(xs[0], zs[0], ys[0], str(id_),
                    fontdict={'fontsize': 12, 'color':color})
        
        count += 1
    
    ax.set_box_aspect((ptp(xm), ptp(zm), ptp(ym)))
    
    ax.set_xlabel('x')
    ax.set_zlabel('y')
    ax.set_ylabel('z')
    
    print('plotted %d trajectories'%(count))
    
    plt.show()









class animate_trajectories(object):
    
    def __init__(self, fname, min_length, f0=None, fe=None, fps=25,
                 tail_length=4, view_angles = (15,70), rotation_rate=0.1):
        
        
        
        data = read_csv(fname, header=None, sep='\t')
        
        self.trajectories = dict([(g, array(k.values)) 
                             for g,k in data.groupby(0) if g!=-1])
        
        self.longs = [k for k in self.trajectories.keys() 
                      if len(self.trajectories[k])>=min_length]
        
        x_lst, y_lst, z_lst = [], [], []
        for i in self.longs:
            x_lst += list(self.trajectories[i][:,1])
            y_lst += list(self.trajectories[i][:,2])
            z_lst += list(self.trajectories[i][:,3])
        
        self.xmax = amax(x_lst) ; self.xmin = amin(x_lst)
        self.ymax = amax(y_lst) ; self.ymin = amin(y_lst)
        self.zmax = amax(z_lst) ; self.zmin = amin(z_lst)
        
        if f0 is None:
            f0 = int(min(data[data.columns[-1]]))
            
        if fe is None:
            fe = int(max(data[data.columns[-1]]))
        
        self.fps = fps
        self.counter = 0
        self.frames = list(range(f0, fe+1))
        self.duration = (len(self.frames)-1)/self.fps
        self.tl = tail_length
        self.min_length = min_length
        self.angles = view_angles
        self.rotation = rotation_rate
        self.fig = None
        self.ax = None
        
        
    def setup_plot(self):
        v_lst = []
        for i in self.longs:
            tr = self.trajectories[i]
            dt = int(self.min_length/2)
            dx = sum([(tr[dt,j] - tr[0,j])**2 for j in [1,2,3]])**0.5
            v_lst.append(dx/dt)
            
        self.vscale = percentile(v_lst, 95)
        self.fig = plt.figure(figsize=(9,9))
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('z')
        self.ax.set_zlabel('y')
        self.ax.grid(False)


    def update(self, t):
        if self.ax is None:
            self.setup_plot()
            
        frame_index = int(t * self.fps)
        if frame_index >= len(self.frames):
            frame_index = len(self.frames) - 1
            
        frame = self.frames[frame_index]
        cmap = plt.get_cmap('jet')
        self.ax.clear()
        
        # Reset labels and grid after clear
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('z')
        self.ax.set_zlabel('y')
        self.ax.grid(False)

        for k in self.longs:
            tr = self.trajectories[k]
            # Fast lookup for current frame in this trajectory
            whr = tr[:,-1]==frame
            if any(whr):
                ind = arange(len(tr))[whr][0]
                # Extract tail
                tail_start = max(0, ind - self.tl)
                x = tr[tail_start:ind+1, 1]
                y = tr[tail_start:ind+1, 2]
                z = tr[tail_start:ind+1, 3]
                
                if len(x)==0: continue
                dx = ((x[-1]-x[0])**2 + (y[-1]-y[0])**2 + (z[-1]-z[0])**2)**0.5
                c = min([(dx/self.tl) / self.vscale, 1.0])
                self.ax.plot(x, z, y, '-', color = cmap(c*0.9))
        
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_zlim(self.ymin, self.ymax)
        self.ax.set_ylim(self.zmin, self.zmax)
        
        self.ax.view_init(elev=self.angles[0], 
                          azim=self.angles[1] + self.rotation*frame_index)
        
        self.ax.set_box_aspect((self.xmax-self.xmin, 
                                self.zmax-self.zmin, 
                                self.ymax-self.ymin))
        
        plt.tight_layout()
        
        # Custom fig to numpy conversion
        self.fig.canvas.draw()
        import numpy as np
        return np.array(self.fig.canvas.buffer_rgba())[:,:,:3] # RGB only

        

    def animate(self):
        '''
        will animate the particle's location, and save the animation
        '''
        self.setup_plot()
        animation = mpy.VideoClip(self.update, duration=self.duration)
        animation.write_videofile('animation.mp4', fps=self.fps)
        return animation
    








def getSamplesFromLongTrajectories(fname, min_len):
    '''
    Reads a trajectory file and returns an array with its samples that
    belong to "long" trajectories, whose length is >= than min_len.
    '''
    data = read_csv(fname, header=None, sep='\t')
    trajectories = dict([(g, array(k.values)) 
                         for g,k in data.groupby(0) if g!=-1])
    
    to_take = []
    for k in trajectories.keys():
        tr = trajectories[k]
        if len(tr)>=min_len:
            for i in range(len(tr)):
                to_take.append(tr[i])
            
    return array(to_take)




    
    

def PlotParticlePositionHistogram(fname):
    '''
    This function plots trajectories from a given file in 3D.
    '''
    data = read_csv(fname, header=None, sep='\t')
    
    fig, ax = plt.subplots(1,3)
    
    xm = list(data[0])
    ym = list(data[1])
    zm = list(data[2])
    
    ax[0].hist(xm, bins='auto')
    ax[1].hist(ym, bins='auto')
    ax[2].hist(zm, bins='auto')
    
    return None




import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as mcolors

def plot_fibers(trajectory_file, orientations_file, min_length, write_trajID=False, t0=0, te=-1, length_scale=10.0, mode='centered_rod', rod_segments=10):
    '''
    Plots fiber trajectories in 3D with orientation rods scaled by rotation rate.
    
    inputs:
        trajectory_file - path to the smoothed trajectories file (for center positions)
        orientations_file - path to the fiber orientations file
        min_length - only trajectories longer than this will be plotted
        write_trajID - whether to write the trajectory ID
        t0, te - time range in frames
        length_scale - scaling multiplier for the rod lengths
        mode - 'centered_rod', 'path_and_half_rod', or 'speed_colored_rod'
        rod_segments - number of segments to split the rod into (for speed_colored_rod mode)
    '''
    valid_modes = ['centered_rod', 'path_and_half_rod', 'speed_colored_rod']
    if mode not in valid_modes:
        raise ValueError(f"Unknown mode: {mode}. Must be one of {valid_modes}")

    if isinstance(trajectory_file, str):
        trajectory_file = [trajectory_file]
    if isinstance(orientations_file, str):
        orientations_file = [orientations_file]
        
    if len(trajectory_file) != len(orientations_file):
        raise ValueError("Number of trajectory files and orientations files must match")

    traj_data_list = []
    for f_idx, f in enumerate(trajectory_file):
        if not os.path.exists(f):
            raise FileNotFoundError(f"Trajectory file not found: {f}")
        d = pd.read_csv(f, header=None, sep='\t')
        d[0] = d[0].apply(lambda x: f"{f_idx}_{x}" if x != -1 else x)
        traj_data_list.append(d)
    traj_data = pd.concat(traj_data_list, ignore_index=True)

    ori_data_list = []
    for f_idx, f in enumerate(orientations_file):
        if not os.path.exists(f):
            raise FileNotFoundError(f"Orientations file not found: {f}")
        d = pd.read_csv(f, header=None, sep='\t')
        d[0] = d[0].apply(lambda x: f"{f_idx}_{x}" if x != -1 else x)
        ori_data_list.append(d)
    ori_data = pd.concat(ori_data_list, ignore_index=True)

    # Convert any values to floats and group by trajectory ID (column 0)
    trajs = dict([(k, np.array(g)) for k, g in traj_data.groupby(0) if k != -1])
    oris = dict([(k, np.array(g)) for k, g in ori_data.groupby(0) if k != -1])

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection='3d')
    cmap = plt.get_cmap('viridis')

    all_omega_dots = []
    plot_data = []

    # Gather data, align frames, and calculate gradients
    for tid in sorted(trajs.keys()):
        if tid not in oris:
            continue

        t_arr = trajs[tid]
        o_arr = oris[tid]

        t_df = pd.DataFrame(t_arr)
        o_df = pd.DataFrame(o_arr)

        # Assign explicit string column names for clarity and robustness
        # t_df has: 0: id, 1: x, 2: y, 3: z, 4: vx, 5: vy, 6: vz, 7: ax, 8: ay, 9: az, 10: frame
        t_df.columns = ['id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'frame']
        
        num_cols = len(o_df.columns)
        has_smoothed = False
        
        # Support both raw orientations (cams+6 cols) and smoothed orientations (cams+12 cols)
        # Determine based on column count (assuming at least 2 cameras).
        if num_cols >= 14:
            has_smoothed = True
            cams_count = num_cols - 12
            o_cols = ['id', 'px', 'py', 'pz', 'px_dot', 'py_dot', 'pz_dot', 'px_ddot', 'py_ddot', 'pz_ddot']
        else:
            cams_count = num_cols - 6
            o_cols = ['id', 'px', 'py', 'pz']
            
        for i in range(cams_count):
            o_cols.append(f'c{i+1}')
        o_cols.extend(['err', 'frame'])
        
        o_df.columns = o_cols

        # Merge on frame number
        merged = pd.merge(t_df, o_df, on='frame', suffixes=('_pos', '_ori'))
        if merged.empty:
            continue

        merged = merged.sort_values(by='frame')

        # Limit time
        te_lim = te if te != -1 else merged['frame'].max()
        merged = merged[(merged['frame'] >= t0) & (merged['frame'] <= te_lim)]

        if len(merged) < min_length:
            continue

        # Position (x, y, z)
        xs = merged['x'].values
        ys = merged['y'].values
        zs = merged['z'].values

        # Orientation (px, py, pz)
        px = merged['px'].values
        py = merged['py'].values
        pz = merged['pz'].values

        frames = merged['frame'].values
        vx = merged['vx'].values
        vy = merged['vy'].values
        vz = merged['vz'].values

        # Compute rotation rate (omega_dot)
        if has_smoothed and 'px_dot' in merged.columns:
            pdot_x = merged['px_dot'].values
            pdot_y = merged['py_dot'].values
            pdot_z = merged['pz_dot'].values
            omega_dots = np.sqrt(pdot_x**2 + pdot_y**2 + pdot_z**2)
        else:
            # Fallback to numerical gradient for raw orientations
            if len(frames) >= 2:
                pdot_x = np.gradient(px, frames)
                pdot_y = np.gradient(py, frames)
                pdot_z = np.gradient(pz, frames)
                omega_dots = np.sqrt(pdot_x**2 + pdot_y**2 + pdot_z**2)
            else:
                pdot_x = np.zeros(len(frames))
                pdot_y = np.zeros(len(frames))
                pdot_z = np.zeros(len(frames))
                omega_dots = np.zeros(len(frames))

        # Note: 'speed_colored_rod' colors segments by local speed (translation + rotation). 
        # Even with rod_segments=1, it is conceptually different from 'centered_rod':
        # - 'centered_rod' colors the entire rod based on its rotation rate (omega_dots) in rad/frame.
        # - 'speed_colored_rod' with 1 segment colors the entire rod based on its center of mass translational speed (v_cm) in pixels/frame.
        if mode == 'speed_colored_rod':
            L = length_scale
            s_mids = np.linspace(-0.5 * L, 0.5 * L, rod_segments + 1)
            s_mids = 0.5 * (s_mids[:-1] + s_mids[1:])
            segment_speeds = []
            for i in range(len(frames)):
                v_cm = np.array([vx[i], vy[i], vz[i]])
                pdot = np.array([pdot_x[i], pdot_y[i], pdot_z[i]])
                speeds = [np.linalg.norm(v_cm + s * pdot) for s in s_mids]
                segment_speeds.append(speeds)
            segment_speeds = np.array(segment_speeds)
            all_omega_dots.extend(segment_speeds.flatten())
            plot_data.append((tid, xs, ys, zs, px, py, pz, omega_dots, segment_speeds))
        else:
            all_omega_dots.extend(omega_dots)
            plot_data.append((tid, xs, ys, zs, px, py, pz, omega_dots, None))

    if not all_omega_dots:
        print("No trajectories met the criteria for plotting.")
        plt.show()
        return

    min_omega = min(all_omega_dots)
    max_omega = max(all_omega_dots)
    if max_omega == min_omega:
        max_omega = min_omega + 1e-5

    norm = mcolors.Normalize(vmin=min_omega, vmax=max_omega)

    # Initialize coordinates boundaries
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')
    z_min, z_max = float('inf'), float('-inf')

    # Plot
    for tid, xs, ys, zs, px, py, pz, omega_dots, segment_speeds in plot_data:
        x_min, x_max = min(x_min, xs.min()), max(x_max, xs.max())
        y_min, y_max = min(y_min, ys.min()), max(y_max, ys.max())
        z_min, z_max = min(z_min, zs.min()), max(z_max, zs.max())

        # Path connecting the centers is always a thin black line
        ax.plot(xs, zs, ys, '-', color='black', lw=0.7)

        # Plot sticks for each frame along the trajectory
        for i in range(len(xs)):
            cx, cy, cz = xs[i], ys[i], zs[i]
            ux, uy, uz = px[i], py[i], pz[i]
            omega = omega_dots[i]

            color = cmap(norm(omega))
            L = length_scale

            if mode == 'centered_rod':
                x_endpoints = [cx - 0.5 * L * ux, cx + 0.5 * L * ux]
                y_endpoints = [cy - 0.5 * L * uy, cy + 0.5 * L * uy]
                z_endpoints = [cz - 0.5 * L * uz, cz + 0.5 * L * uz]
                ax.plot(x_endpoints, z_endpoints, y_endpoints, '-', color=color, lw=1.5)
            elif mode == 'path_and_half_rod':
                x_endpoints = [cx, cx + 0.5 * L * ux]
                y_endpoints = [cy, cy + 0.5 * L * uy]
                z_endpoints = [cz, cz + 0.5 * L * uz]
                ax.plot(x_endpoints, z_endpoints, y_endpoints, '-', color=color, lw=1.5)
            elif mode == 'speed_colored_rod':
                s_nodes = np.linspace(-0.5 * L, 0.5 * L, rod_segments + 1)
                speeds = segment_speeds[i]
                for j in range(rod_segments):
                    s1 = s_nodes[j]
                    s2 = s_nodes[j+1]
                    x_endpts = [cx + s1 * ux, cx + s2 * ux]
                    y_endpts = [cy + s1 * uy, cy + s2 * uy]
                    z_endpts = [cz + s1 * uz, cz + s2 * uz]
                    c = cmap(norm(speeds[j]))
                    ax.plot(x_endpts, z_endpts, y_endpts, '-', color=c, lw=1.5)
            else:
                raise ValueError(f"Unknown mode: {mode}")

        if write_trajID and len(xs) > 0:
            ax.text(xs[0], zs[0], ys[0], str(tid), fontdict={'fontsize': 10, 'color': 'black'})


    ax.set_xlabel('x')
    ax.set_zlabel('y')
    ax.set_ylabel('z')

    # Coordinate boundaries aspect ratio
    from numpy import ptp
    ax.set_box_aspect((ptp([x_min, x_max]), ptp([z_min, z_max]), ptp([y_min, y_max])))

    # Colorbar
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array(all_omega_dots)
    cbar = fig.colorbar(mappable, ax=ax, pad=0.1, shrink=0.7)
    if mode == 'speed_colored_rod':
        cbar.set_label(r'Speed (pixels/frame)')
    else:
        cbar.set_label(r'$\dot{\omega}$ (rotation rate, rad/frame)')

    plt.title(f"Fiber Trajectories ({mode} mode)")
    print(f"plotted {len(plot_data)} fiber trajectories")
    plt.show()



