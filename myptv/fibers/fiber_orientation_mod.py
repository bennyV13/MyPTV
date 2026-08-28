# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:59:35 2022

@author: Eric Aschari

"""

import numpy as np
import math
from scipy import linalg
from myptv.traj_smoothing_mod import smooth_traj_poly
from tqdm import tqdm


class FiberOrientation(object):
    '''A class to obtain the 3D fiber orientation from two fiber 
    points on every segmented image'''
    
    def __init__(self, X: np.ndarray,
                 B: np.ndarray):
        self.X = X # Center of fiber
        self.B = B # Endpoints of fiber
 

    def image2fiber(self, cams):
        '''
        input:
            cams: array of cameras
        output:
            cAvg: point on 3D line passing through fiber
            uAvg: 3D orientation of fiber
        '''
        
        cs = self.X
        bs = self.B
        # alphas = self.get_alphas()
        s = np.shape(cams)[0]
        c = np.zeros((3, math.comb(s,2)));
        u = np.zeros((3, math.comb(s,2)));
        r = 0 # non-nan result counter
        
        # for all camera pairs calculate the intersecting line
        for i in range(0,s-1):
            for j in range((i + 1),s):
                # get_r_ori???
                p1_n, p1_m = self.getPlane(np.transpose(np.array([cams[i].O])),
                              cams[i].get_r_ori(cs[i]),
                              cams[i].get_r_ori(bs[i]))
                p2_n, p2_m = self.getPlane(np.transpose(np.array([cams[j].O])),
                              cams[j].get_r_ori(cs[j]),
                              cams[j].get_r_ori(bs[j]))
                ctemp,utemp = self.intersectPlanes(p1_n,p1_m,p2_n,p2_m)
                
                if type(utemp) != str:
                    if type(utemp[0]) != 'NaN' and type(utemp[1]) != 'NaN' and type(utemp[2]) != 'NaN':
                        c[:,[r]] = ctemp
                        u[:,[r]] = utemp
                        r += 1
        
        cAvg,uAvg = self.averageLine(c,u)
        
        ori = self.get_ori(uAvg)
        
        return cAvg,uAvg,ori
    
    
    ### helper functions
    
    def solve_svd(self, A, b):
        '''
        input:
            A: matrix
            b: column vector
        output:
            x: vector so that A*x = b
        '''
        # compute svd of A
        U,s,Vh = linalg.svd(A)
        # U diag(s) Vh x = b <=> diag(s) Vh x = U.T b = c
        c = np.dot(U.T,b)
        # diag(s) Vh x = c <=> Vh x = diag(1/s) c = w (trivial inversion of a diagonal matrix)
        w = np.dot(np.diag(1/s),c)
        # Vh x = w <=> x = Vh.H w (where .H stands for hermitian = conjugate transpose)
        x = np.dot(Vh.conj().T,w)
        return x
    

    def getPlane(self, P1, P2, P3): 
        '''
        input:
            P123: three 3D points
        output:
            p_n: normal vector to plane spun by P123
            p_m: ax + by + cz = *m*
        '''
        A = np.array([[P1[0,0], P1[1,0], -1.0],
                      [P2[0,0], P2[1,0], -1.0],
                      [P3[0,0], P3[1,0], -1.0]])
        z = np.array([[-P1[2,0]], [-P2[2,0]], [-P3[2,0]]])
        # b = np.linalg.solve(A,z)
        # print('A___',A)
        # print('z___',z)
        b = self.solve_svd(A,z)
        
        p_n = np.array([[b[0,0]], [b[1,0]], [1]])
        p_m = b[2] / np.linalg.norm(p_n)
        p_n = p_n / np.linalg.norm(p_n)
        return p_n, p_m[0]


    def intersectPlanes(self, p1_n, p1_m, p2_n, p2_m): 
        '''
        input:
            p12_n: normal vectors of two planes
            p12_m: plane constant
        output:
            c,u: f(k) = c + k * u 
        '''
        n = np.concatenate([np.transpose(p1_n),np.transpose(p2_n)])
        if np.dot(np.transpose(p1_n),p2_n) > 0.9999:  #small angle between planes
            c = 'NaN'
            u = 'NaN'
            return c,u

        c = np.linalg.lstsq(n,np.array([[p1_m],[p2_m]]),rcond=-1)[0]
        u = linalg.null_space(n)
        return c,u
    

    def averageLine(self, c, u): 
        '''
        input:
            c,u: f(k) = c + k * u 
        output:
            cAvg: average of c
            uAvg: average of u
        '''
        A = np.zeros(np.shape(u))
        for i in range(0,np.shape(A)[1]):
            A[:,i] = u[:,0]
        
        s = np.sign(np.dot(np.transpose(A),u))[0]
        u = np.multiply(s,u)
        uAvg = np.mean(u,1)
        cAvg = np.mean(c,1)
        return cAvg,uAvg
    

    def get_alphas(self):
        '''
        input:
            self: centers and endpoints of fibers
        output:
            alphas: array of angles on camera planes
        '''
        alpha1 = np.arctan2((self.B[0,1] - self.X[0,1]), (self.B[0,0] - self.X[0,0]))[0]
        alpha2 = np.arctan2((self.B[1,1] - self.X[1,1]), (self.B[1,0] - self.X[1,0]))[0]
        # alpha3 = np.arctan2((self.B[2,1] - self.X[2,1]), (self.B[2,0] - self.X[2,0]))[0]
        # alpha4 = np.arctan2((self.B[3,1] - self.X[3,1]), (self.B[3,0] - self.X[3,0]))[0]
        
        # alphas = np.array([alpha1, alpha2, alpha3, alpha4])
        alphas = np.array([alpha1, alpha2])

        return alphas
    
    
    def get_ori(self,u):
        '''
        input:
            u: direction vector
        output:
            ori: angle array []
        '''
        xy_ori = np.arctan2(u[1],u[0])
        xz_ori = np.arctan2(u[2],u[0])
        ori = np.array([xy_ori,xz_ori])
        
        return ori
    
    
    
    
    

# ===============================================================
#      Fiber orientations from minimized projection err (Ron)
#         
#         (2 classes for the minimized projection method)
#
# Use fiber_traj_orientation to calculate fiber orientations and
# save the results on the disk. The fiber_ori_projection_method
# minimizes projection for single blobs. 
# ===============================================================


import numpy as np
from scipy.optimize import differential_evolution
import pandas as pd
from tqdm import tqdm


class fiber_ori_projection_method(object):
    '''
    A class for finding the orientation of a fiber by minimizing the
    discrepancy with respect to the orientation of the blob.
    '''

    def __init__(self, cams, imageOrients, pos, ori0=None,
                 fiber_length=None, imageProjLengths=None):
        '''
        cams - a list of Nc calibrated objects that can project lab-space
               positions to image space positions.

        imageOrients - a list of Nc 2D unit vectors representing the
                       orientation of the fiber long axis in image space of
                       each camra. to compare the results during minimization
                       we make sure that the first vector component is always
                       positive.

        pos - the lab space, 3D, position of the fiber center.

        ori0 - an optional initial guess for the orientation.

        fiber_length - the physical length of the fiber in lab-space units
                       (mm). Used for projected-length matching to prevent
                       optical-axis bias. If None, falls back to direction-only
                       matching (original behavior).

        imageProjLengths - a list of Nc floats giving the observed projected
                          length (major axis in pixels) of the fiber in each
                          camera. If provided alongside fiber_length, enables
                          projected-length consistency in the cost function.
        '''

        self.cams = cams
        self.imgOri_lst = imageOrients

        for i in range(len(self.imgOri_lst)):

            # ensuring the format is right (first component positive)
            if len(self.imgOri_lst[i]) == 0:
                raise ValueError("One of the image orientation vectors is empty. "
                                 "Check that the input blob files contain orientation data.")

            if self.imgOri_lst[i][0]<0:
                self.imgOri_lst[i] = self.imgOri_lst[i] * -1

            # ensuring norm is 1
            self.imgOri_lst[i] = self.imgOri_lst[i] / np.linalg.norm(self.imgOri_lst[i])


        self.pos = pos
        self.fiber_length = fiber_length
        self.imageProjLengths = imageProjLengths

        if ori0 is None:
            self.ori0 = np.array([1,1,1])/3**0.5
            self.smartIG = 0 # index whether an initial guess was given

        else:
            self.ori0 = ori0
            self.smartIG = 1


    def OriToImageOri(self, ori):
        '''
        Given a vector, this function estimates and returns its
        image space orientations in each camera, assuming it is centered
        at self.pos.
        '''
        ori = ori/np.linalg.norm(ori)
        ds = 1e-6
        p1 = self.pos + ori*ds/2
        p2 = self.pos - ori*ds/2

        imgOri_lst = []
        for e, cam in enumerate(self.cams):
            c1 = np.array(cam.projection(p1))[::-1]
            c2 = np.array(cam.projection(p2))[::-1]
            imgOri = (c1-c2) / np.linalg.norm(c1-c2)
            if imgOri[0]<0:
                imgOri = -1*imgOri
            imgOri_lst.append(imgOri)

        return imgOri_lst


    def _project_fiber(self, ori):
        '''
        Projects fiber endpoints through each camera. Returns per-camera
        projected direction vectors and their lengths in pixels.
        Uses the actual fiber half-length for physically meaningful results.
        '''
        ori = ori / np.linalg.norm(ori)
        half_L = self.fiber_length / 2.0
        p1 = self.pos + ori * half_L
        p2 = self.pos - ori * half_L

        directions = []
        lengths = []
        for cam in self.cams:
            c1 = np.array(cam.projection(p1))[::-1]
            c2 = np.array(cam.projection(p2))[::-1]
            diff = c1 - c2
            proj_len = np.linalg.norm(diff)
            lengths.append(proj_len)

            if proj_len > 1e-8:
                d = diff / proj_len
            else:
                d = np.array([1.0, 0.0])

            if d[0] < 0:
                d = -d
            directions.append(d)

        return directions, np.array(lengths)


    def Minimize_Ori(self):
        '''
        Searches for a vector that minimizes the difference in orientation
        between its projection on image-space and segmented orientation of the
        blobs.

        When fiber_length is provided, uses a combined angular + projected-length
        cost that prevents the optimizer from collapsing into the degenerate
        optical-axis zone.

        returns

        ori - predicted orientation that minimizes projection vs. segmentation
              error.

        MSE - mean squared orientation error.
        '''

        if self.fiber_length is not None:
            return self._minimize_ori_robust()

        # Original behavior when no fiber_length is given
        def ori_MSE(ori):
            res = np.array(self.OriToImageOri(ori)) - np.array(self.imgOri_lst)
            MSE = np.mean(np.sum(res**2, axis=0))
            return MSE

        popsize = 15

        res_de = differential_evolution(ori_MSE, bounds=[(0,1),(-1,1),(-1,1)],
                                        popsize=popsize, x0=self.ori0)
        ori = res_de.x / np.linalg.norm(res_de.x)

        MSE = res_de.fun

        return ori, MSE


    def _minimize_ori_robust(self):
        '''
        Robust orientation minimization using angular distance + projected-length
        consistency. Prevents spurious polarization toward the optical axis.
        '''
        have_obs_lengths = (self.imageProjLengths is not None
                           and len(self.imageProjLengths) == len(self.cams))

        if have_obs_lengths:
            obs_lengths = np.array(self.imageProjLengths, dtype=float)
            ref_len = np.mean(obs_lengths)

        Nc = len(self.cams)

        def cost(ori):
            directions, pred_lengths = self._project_fiber(ori)

            # Term 1: Angular cost (apolar distance: 1 - |cos(angle)|)
            ang_cost = 0.0
            for i in range(Nc):
                dot = np.dot(directions[i], self.imgOri_lst[i])
                ang_cost += 1.0 - abs(dot)
            ang_cost /= Nc

            # Term 2: Projected-length matching
            if have_obs_lengths:
                # Normalized length discrepancy: penalizes when predicted length
                # doesn't match observed length. Catches the case where optimizer
                # claims "vertical" but camera sees a long rod.
                len_cost = np.mean(((pred_lengths - obs_lengths) / (ref_len + 1.0))**2)
            else:
                # Fallback: mild observability regularization. Only activates
                # strongly for sub-pixel projections (truly degenerate zone).
                # Conservative to avoid biasing truly vertical fibers.
                min_observable = 1.0  # pixels
                mean_pred = np.mean(pred_lengths)
                len_cost = (min_observable / (mean_pred + min_observable))**2

            # Weight: angular term dominates, length term breaks degeneracy.
            # With observed lengths the signal is reliable so weight is higher.
            alpha = 0.3 if have_obs_lengths else 0.03
            return ang_cost + alpha * len_cost

        popsize = 15

        res_de = differential_evolution(cost, bounds=[(0,1),(-1,1),(-1,1)],
                                        popsize=popsize, x0=self.ori0)
        ori = res_de.x / np.linalg.norm(res_de.x)
        MSE = res_de.fun

        return ori, MSE
    
    
    



class fiber_traj_orientation(object):
    '''
    Given a trajectory file, a list of files with segmented
    fiber directions, and a list of cameras, this class is
    used to determine the orientations of the fiber using
    the projection method.
    '''

    def __init__(self, traj_filename, blobs_ori_filename, cams,
                 fiber_length=None, blob_format='bbox'):
        '''
        fiber_length - the physical fiber length in mm. Can be:
            - None: uses original direction-only method (no p_z correction)
            - float: uses this fixed length for all trajectories
            - 'auto': estimates length from the population of max-projection
              blob lengths (90th percentile). Recommended when fiber length
              is unknown.

        blob_format - format of columns 2,3 in the blob files:
            - 'bbox': bounding box dimensions [maxr-minr, maxc-minc]
              (old format, before 2026-08-20 fix)
            - 'ellipse': fitted ellipse [major_axis_length, minor_axis_length]
              (new format)
        '''

        self.cams = cams
        self.fiber_length = fiber_length
        self.blob_format = blob_format

        self.blobs_ori = []
        for bfn in blobs_ori_filename:
            data = pd.read_csv(bfn, sep='\t', header=None)
            if data.shape[1] < 8:
                raise ValueError(f"Blob file {bfn} only has {data.shape[1]} columns. "
                                 "Expected at least 8 columns for fiber orientation analysis. "
                                 "Please use the '_directions' files generated during segmentation.")
            self.blobs_ori.append(dict([(k,np.array(g)) for k,g in data.groupby(5)]))

        data = pd.read_csv(traj_filename, sep='\t', header=None)
        self.trajs = dict([(k,np.array(g)) for k, g in data.groupby(0)])


    def _blob_projected_length(self, blob_row):
        '''
        Extracts the projected fiber length (in pixels) from a blob data row.
        Handles both bbox and ellipse blob formats.
        '''
        if self.blob_format == 'ellipse':
            return float(blob_row[2])

        # bbox format: col2=height (maxr-minr), col3=width (maxc-minc)
        # col6=cos(ori), col7=sin(ori)
        H = float(blob_row[2])
        W = float(blob_row[3])
        cos_th = float(blob_row[6])
        sin_th = float(blob_row[7])

        u_y = abs(cos_th)
        u_x = abs(sin_th)
        norm = np.hypot(u_x, u_y)
        if norm > 1e-6:
            u_x /= norm
            u_y /= norm
        else:
            u_x, u_y = 1.0, 0.0

        l_raw = W * u_x + H * u_y
        return max(l_raw, max(W, H), 1.0)


    def _estimate_traj_length(self, traj):
        '''
        Estimates the physical fiber length for a trajectory from the observed
        projected blob lengths, then converting to mm using local magnification.

        Uses the 85th percentile of per-frame max projected lengths (across
        cameras) to be robust against outlier blobs from agglomerations or
        segmentation artifacts.
        '''
        blob_indexes = list(traj[:, 4:-2])
        frames = list(traj[:, -1])

        # Collect per-frame maximum projected length (across cameras)
        frame_max_lens = []
        frame_cam_idx = []
        frame_positions = []

        for e, frm in enumerate(frames):
            pos = traj[e, 1:4]
            frame_best = 0.0
            frame_best_cam = 0
            for i in range(len(self.cams)):
                ind_ie = int(blob_indexes[e][i])
                if ind_ie == -1:
                    continue
                try:
                    blobs_in_frame = self.blobs_ori[i][int(frm)]
                except KeyError:
                    continue
                if ind_ie >= len(blobs_in_frame):
                    continue

                proj_len = self._blob_projected_length(blobs_in_frame[ind_ie])
                if proj_len > frame_best:
                    frame_best = proj_len
                    frame_best_cam = i

            if frame_best > 1.0:
                frame_max_lens.append(frame_best)
                frame_cam_idx.append(frame_best_cam)
                frame_positions.append(pos)

        if len(frame_max_lens) < 2:
            return None

        # Use 85th percentile: robust to outlier blobs while capturing
        # the fiber at near-horizontal orientation
        pctile_idx = int(0.85 * len(frame_max_lens))
        sorted_indices = np.argsort(frame_max_lens)
        best_idx = sorted_indices[min(pctile_idx, len(sorted_indices) - 1)]

        best_proj_len = frame_max_lens[best_idx]
        best_cam_idx = frame_cam_idx[best_idx]
        best_pos = frame_positions[best_idx]

        # Convert pixels to mm using local magnification
        cam = self.cams[best_cam_idx]
        c0 = np.array(cam.projection(best_pos))
        cx = np.array(cam.projection(best_pos + np.array([1.0, 0.0, 0.0])))
        cy = np.array(cam.projection(best_pos + np.array([0.0, 1.0, 0.0])))
        scale_px_per_mm = 0.5 * (np.linalg.norm(cx - c0) + np.linalg.norm(cy - c0))

        if scale_px_per_mm < 1e-6:
            return None

        return best_proj_len / scale_px_per_mm
    
        
    def get_traj_orientation(self, traj, fiber_length_override=None):
        '''
        Finds the orientations of a given fiber by minimizing the
        error of its image projections

        traj - an array representing the trajectory

        fiber_length_override - if provided, uses this length (in mm) instead
                                of self.fiber_length for this trajectory.
        '''
        # Determine effective fiber length for this trajectory
        fl = fiber_length_override
        if fl is None:
            if self.fiber_length == 'auto':
                fl = self._estimate_traj_length(traj)
            elif self.fiber_length is not None:
                fl = self.fiber_length

        blob_indexes = list(traj[:,4:-2])
        frames = list(traj[:,-1])
        traj_ori = []

        for e, frm in enumerate(frames):
            # get the image space orientation at frame e
            imageOrients = []
            imageProjLens = []
            used_cams = []
            for i in range(len(self.cams)):
                ind_ie = int(blob_indexes[e][i])

                # Skip cameras that didn't see the fiber
                if ind_ie == -1:
                    continue

                # Use the frame number 'frm' as the key
                try:
                    blobs_in_frame = self.blobs_ori[i][int(frm)]
                except KeyError:
                    # This shouldn't happen if the trajectory is consistent
                    continue

                # Check if the blob index is valid
                if ind_ie >= len(blobs_in_frame):
                    continue

                imageOrients.append(blobs_in_frame[ind_ie,6:8])
                imageProjLens.append(self._blob_projected_length(blobs_in_frame[ind_ie]))
                used_cams.append(self.cams[i])

            # set up an fiberOrientations instance
            pos = traj[e,1:4]
            if len(traj_ori)>0: ori0=traj_ori[-1]
            else: ori0=None

            # We need at least 2 cameras to find a unique 3D orientation
            if len(imageOrients) < 2:
                if len(traj_ori) > 0:
                    traj_ori.append(traj_ori[-1])
                else:
                    traj_ori.append((np.array([0,0,0]), 1.0))
                continue

            FO = fiber_ori_projection_method(
                used_cams, imageOrients, pos, ori0=ori0,
                fiber_length=fl,
                imageProjLengths=imageProjLens if fl else None
            )

            # Minimize for the fiber orientation
            traj_ori.append(FO.Minimize_Ori())

        return traj_ori
    
    
    def get_ori_lst(self):
        '''
        Iterates over the trajectories and obtains the orientation
        of each of them. The results are stored in self.ori_lst.

        When fiber_length='auto', estimates fiber length per-trajectory
        from the maximum observed projected blob length. This handles
        polydisperse populations correctly (each fiber gets its own
        length estimate).
        '''
        print('','Getting trajectory orientations...','')
        self.ori_lst = []
        self.traj_lengths = {}

        # Pre-pass: estimate per-trajectory fiber lengths
        if self.fiber_length == 'auto':
            print(' Estimating per-trajectory fiber lengths...')
            for k in self.trajs.keys():
                traj = self.trajs[k]
                est = self._estimate_traj_length(traj)
                if est is not None:
                    self.traj_lengths[k] = est

            if self.traj_lengths:
                lengths = list(self.traj_lengths.values())
                print(f' Estimated lengths for {len(lengths)} trajectories: '
                      f'median={np.median(lengths):.2f} mm, '
                      f'range=[{np.min(lengths):.2f}, {np.max(lengths):.2f}] mm')
            else:
                print(' WARNING: could not estimate fiber lengths, '
                      'falling back to direction-only method')

        for k in tqdm(self.trajs.keys()):
            traj = self.trajs[k]

            if self.fiber_length == 'auto':
                fl_override = self.traj_lengths.get(k, None)
            else:
                fl_override = None

            ori = self.get_traj_orientation(traj, fiber_length_override=fl_override)
            for i in range(len(traj)):
                ln = traj[i].copy()
                ln[1:4] = ori[i][0]
                self.ori_lst.append(ln)
                
    
    def save_orientations(self, savename):
        '''
        Saves the results of self.get_ori_lst() as a tab separated 
        file with the same format as trajectories files.
        '''
        fmt = ['%d', '%.4f', '%.4f', '%.4f']
        for i in range(len(self.ori_lst[0])-6):
            fmt.append('%d')
        fmt += ['%.3f', '%.3f']
        np.savetxt(savename , self.ori_lst,
                delimiter='\t', fmt=fmt)
                
    
    
    
    
    
    
    
    

class smooth_orientations(object):
    '''
    A class used to smooth fiber orientations in a list. 
    During smoothing, we also calculate the angular velocity (px_dot, py_dot, pz_dot)
    and angular acceleration (px_ddot, py_ddot, pz_ddot) of the orientations.
    The output has 12 + C columns: id, px, py, pz, px_dot, py_dot, pz_dot, px_ddot, py_ddot, pz_ddot, c1..cC, err, frame
    '''
    
    def __init__(self, ori_list, window, polyorder, repetitions=1, min_traj_length=4):
        self.ori_list = ori_list
        self.window = window
        self.polyorder = polyorder
        self.repetitions = repetitions
        
        if min_traj_length <= polyorder:
            raise ValueError('min_traj_length must be larger than polyorder')
            
        self.min_traj_length = min_traj_length
        self.smoothed_oris = []
        
    def smooth(self):
        '''
        Performs the smoothing and returns the results. 
        '''
        # organizing trajectories in a dictionary:
        traj_dic = {}
        zero_length_trajs = []
        for i in range(len(self.ori_list)):
            tr = self.ori_list[i]
            
            # for unconnected samples, put zero velocity and acceleration:
            if tr[0] == -1: 
                new_tr = [tr[0], tr[1], tr[2], tr[3], 
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0] + list(tr[4:])
                zero_length_trajs.append(new_tr)
            
            # from the connected samples, make a trajectory dictionary
            else:
                if tr[0] in traj_dic.keys():
                    traj_dic[tr[0]].append(tr)
                else:
                    traj_dic[tr[0]] = [tr]
        
        short_trajs = []
        smoothed_traj_list = []
        count = 0
        total = 0
        for tr_num in tqdm(traj_dic.keys()):
            
            total += 1
            
            tr_len = len(traj_dic[tr_num])
            
            if tr_len < self.min_traj_length:
                for i in range(len(traj_dic[tr_num])):
                    tr = traj_dic[tr_num][i]
                    new_tr = [tr[0], tr[1], tr[2], tr[3], 
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0] + list(tr[4:])
                    short_trajs.append(new_tr)
                continue
            
            elif tr_len < self.window:
                W = tr_len - 1*(tr_len%2==0)
            
            else:
                W = self.window
            
            # sort samples according to time:
            traj = sorted(traj_dic[tr_num], key=lambda s: s[-1])
            traj_arr = np.array(traj)
            
            # Enforce sign continuity on the raw orientations
            # so that the numerical derivatives and smoothing do not
            # encounter sudden jumps between p and -p.
            for i in range(1, len(traj_arr)):
                dot_prod = traj_arr[i, 1]*traj_arr[i-1, 1] + traj_arr[i, 2]*traj_arr[i-1, 2] + traj_arr[i, 3]*traj_arr[i-1, 3]
                if dot_prod < 0:
                    traj_arr[i, 1:4] = -traj_arr[i, 1:4]
            
            # smoothing orientations
            p, v, a = smooth_traj_poly(traj_arr.T[1:4,:], 
                                       W, 
                                       self.polyorder,
                                       repetitions=self.repetitions)
            
            # Normalizing the smoothed position vectors to have a magnitude of 1
            for i in range(len(p[0])):
                mag = math.sqrt(p[0][i]**2 + p[1][i]**2 + p[2][i]**2)
                if mag > 0:
                    p[0][i] /= mag
                    p[1][i] /= mag
                    p[2][i] /= mag
            
            # setting a new trajectories
            new_traj = []
            N = int(self.window/2)+1
            for i in range(N, len(traj_dic[tr_num]) - N):
                new_traj.append([])
                new_traj[-1].append(traj[i][0])
                new_traj[-1].append(p[0][i])
                new_traj[-1].append(p[1][i])
                new_traj[-1].append(p[2][i])
                new_traj[-1].append(v[0][i])
                new_traj[-1].append(v[1][i])
                new_traj[-1].append(v[2][i])
                new_traj[-1].append(a[0][i])
                new_traj[-1].append(a[1][i])
                new_traj[-1].append(a[2][i])
                # Append camera indices, error, and frame
                new_traj[-1].extend(traj[i][4:])
                
            smoothed_traj_list += new_traj
            count+=1
            
        print('')
        print('smoothed samples: %d'%(len(smoothed_traj_list)))
        print('too short to smooth: %d'%(len(short_trajs)))
        print('single samples: %d'%(len(zero_length_trajs)))
        
        smoothed_traj_list += short_trajs    
        smoothed_traj_list += zero_length_trajs
        self.smoothed_oris = smoothed_traj_list
        
        
    def save_results(self, fname):
        '''
        Will save the smoothed orientations in a text file.
        '''
        if len(self.smoothed_oris) == 0:
            print("No smoothed orientations to save.")
            return

        fmt = ['%d', '%.4f', '%.4f', '%.4f', '%.6f', '%.6f', '%.6f', '%.9f', '%.9f', '%.9f']
        # Add a %d for each camera column. The last 2 are error and frame.
        for i in range(len(self.smoothed_oris[0]) - 12):
            fmt.append('%d')
        fmt += ['%.3f', '%.3f']
        
        np.savetxt(fname, self.smoothed_oris, fmt=fmt, delimiter='\t')