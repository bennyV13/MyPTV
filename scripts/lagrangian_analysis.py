# -*- coding: utf-8 -*-
"""
Lagrangian Trajectory Analysis Suite for MyPTV

This module provides tools for analyzing particle trajectories using Lagrangian 
statistics, following strictly peer-reviewed equations and protocols.

Equations implemented:
1. Mean Squared Displacement (MSD) - Taylor (1921)
2. Lagrangian Velocity Autocorrelation Function (LVACF)
3. Velocity and Acceleration PDFs and moments
4. Lagrangian Structure Functions (Kolmogorov 1941)

@author: Gemini CLI
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from myptv.data_analysis.analysis_tools import load_trajs_as_arrays
import os
import pickle


class LagrangianAnalysis:
    """
    Main class for Lagrangian trajectory analysis.
    """
    
    def __init__(self, traj_list=None):
        """
        Initialize with a list of trajectory arrays.
        Each array should have columns: [id, x, y, z, vx, vy, vz, ax, ay, az, frame]
        """
        self.trajs = traj_list if traj_list is not None else []
        self.results = {}

    def load_data(self, fname):
        """
        Load trajectories from a file.
        
        Parameters:
        fname (str): Path to the trajectory file (e.g., smoothed_trajectories).
        """
        print(f"Loading trajectories from {fname}...")
        self.trajs = load_trajs_as_arrays(fname)
        print(f"Loaded {len(self.trajs)} trajectories.")

    def calculate_msd(self, max_lag=None):
        r"""
        Calculate Mean Squared Displacement (MSD) according to Taylor (1921).
        
        Equation:
        \langle [X(t) - X(0)]^2 \rangle = 2 \langle v^2 \rangle \int_0^t (t-\tau) R_L(\tau) d\tau
        
        Parameters:
        max_lag (int): Maximum time lag to calculate.
        """
        if not self.trajs:
            raise ValueError("No trajectories loaded.")
            
        all_msd = []
        max_len = max(len(tr) for tr in self.trajs)
        if max_lag is None:
            max_lag = max_len // 2
            
        msd_sum = np.zeros(max_lag)
        msd_counts = np.zeros(max_lag)
        
        for tr in self.trajs:
            pos = tr[:, 1:4]
            n = len(pos)
            for lag in range(1, max_lag):
                if lag >= n:
                    continue
                diff = pos[lag:] - pos[:-lag]
                sq_dist = np.sum(diff**2, axis=1)
                msd_sum[lag] += np.sum(sq_dist)
                msd_counts[lag] += len(sq_dist)
                
        # Handle division by zero
        valid = msd_counts > 0
        msd = np.zeros(max_lag)
        msd[valid] = msd_sum[valid] / msd_counts[valid]
        
        self.results['msd'] = msd
        self.results['msd_lags'] = np.arange(max_lag)
        return msd

    def calculate_pdf(self, kind='vx', bins=100):
        """
        Calculate Probability Density Function (PDF) for velocity or acceleration.
        
        Parameters:
        kind (str): One of 'vx', 'vy', 'vz', 'ax', 'ay', 'az'.
        bins (int): Number of bins for the histogram.
        """
        col_map = {'vx': 4, 'vy': 5, 'vz': 6, 'ax': 7, 'ay': 8, 'az': 9}
        if kind not in col_map:
            raise ValueError(f"Invalid kind: {kind}")
            
        col_idx = col_map[kind]
        data = np.concatenate([tr[:, col_idx] for tr in self.trajs])
        
        hist, bin_edges = np.histogram(data, bins=bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        self.results[f'pdf_{kind}'] = (bin_centers, hist)
        return bin_centers, hist

    def calculate_lvacf(self, kind='vx', max_lag=None):
        r"""
        Calculate Lagrangian Velocity Autocorrelation Function (LVACF).
        
        Equation:
        R_{ij}(\tau) = \frac{\langle v_i'(t) v_j'(t + \tau) \rangle}{\sigma_{v_i} \sigma_{v_j}}
        
        Parameters:
        kind (str): Velocity component 'vx', 'vy', or 'vz'.
        max_lag (int): Maximum time lag.
        """
        col_map = {'vx': 4, 'vy': 5, 'vz': 6}
        if kind not in col_map:
            raise ValueError(f"Invalid velocity kind: {kind}")
            
        col_idx = col_map[kind]
        
        # Get all velocities for mean/std calculation
        all_v = np.concatenate([tr[:, col_idx] for tr in self.trajs])
        v_mean = np.mean(all_v)
        v_std = np.std(all_v)
        
        if max_lag is None:
            max_len = max(len(tr) for tr in self.trajs)
            max_lag = max_len // 2
            
        corr_sum = np.zeros(max_lag)
        corr_counts = np.zeros(max_lag)
        
        for tr in self.trajs:
            v_prime = tr[:, col_idx] - v_mean
            n = len(v_prime)
            for lag in range(max_lag):
                if lag >= n:
                    continue
                if lag == 0:
                    corr_sum[lag] += np.sum(v_prime * v_prime)
                    corr_counts[lag] += n
                else:
                    corr_sum[lag] += np.sum(v_prime[lag:] * v_prime[:-lag])
                    corr_counts[lag] += (n - lag)
                    
        valid = corr_counts > 0
        lvacf = np.zeros(max_lag)
        lvacf[valid] = corr_sum[valid] / (corr_counts[valid] * v_std**2)
        
        self.results[f'lvacf_{kind}'] = lvacf
        self.results[f'lvacf_lags_{kind}'] = np.arange(max_lag)
        return lvacf

    def calculate_structure_function(self, kind='vx', order=2, max_lag=None):
        r"""
        Calculate Lagrangian Velocity Structure Functions.
        
        Equation:
        D_n(\tau) = \langle |v(t + \tau) - v(t)|^n \rangle
        
        Parameters:
        kind (str): Velocity component 'vx', 'vy', or 'vz'.
        order (int): Order of the structure function (e.g., 2).
        max_lag (int): Maximum time lag.
        """
        col_map = {'vx': 4, 'vy': 5, 'vz': 6}
        if kind not in col_map:
            raise ValueError(f"Invalid velocity kind: {kind}")
            
        col_idx = col_map[kind]
        
        if max_lag is None:
            max_len = max(len(tr) for tr in self.trajs)
            max_lag = max_len // 2
            
        sf_sum = np.zeros(max_lag)
        sf_counts = np.zeros(max_lag)
        
        for tr in self.trajs:
            v = tr[:, col_idx]
            n = len(v)
            for lag in range(1, max_lag):
                if lag >= n:
                    continue
                dv = np.abs(v[lag:] - v[:-lag])**order
                sf_sum[lag] += np.sum(dv)
                sf_counts[lag] += len(dv)
                
        valid = sf_counts > 0
        sf = np.zeros(max_lag)
        sf[valid] = sf_sum[valid] / sf_counts[valid]
        
        self.results[f'sf{order}_{kind}'] = sf
        self.results[f'sf_lags_{kind}'] = np.arange(max_lag)
        return sf

    def save_results(self, fname):
        """Save analysis results to a pickle file."""
        with open(fname, 'wb') as f:
            pickle.dump(self.results, f)
        print(f"Results saved to {fname}")

    def load_results(self, fname):
        """Load analysis results from a pickle file."""
        with open(fname, 'rb') as f:
            self.results = pickle.load(f)
        print(f"Results loaded from {fname}")

    def plot_msd(self, save_path=None):
        """Plot the calculated MSD."""
        if 'msd' not in self.results:
            print("MSD not calculated.")
            return
            
        plt.figure(figsize=(8, 6))
        plt.loglog(self.results['msd_lags'], self.results['msd'], 'o-', label='Data')
        # Add Taylor regimes fits if enough data?
        # ballistic: ~ t^2
        # diffusive: ~ t
        plt.xlabel('Time lag [frames]')
        plt.ylabel('MSD [length units^2]')
        plt.title('Mean Squared Displacement (Taylor 1921)')
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
            print(f"MSD plot saved to {save_path}")
        plt.show()

    def plot_pdf(self, kind='vx', save_path=None):
        """Plot the calculated PDF."""
        key = f'pdf_{kind}'
        if key not in self.results:
            print(f"PDF for {kind} not calculated.")
            return
            
        centers, hist = self.results[key]
        plt.figure(figsize=(8, 6))
        plt.semilogy(centers, hist, 'o-', label=f'Data {kind}')
        plt.xlabel(f'{kind} [units]')
        plt.ylabel('PDF')
        plt.title(f'Probability Density Function: {kind}')
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
            print(f"PDF plot saved to {save_path}")
        plt.show()

    def plot_lvacf(self, kind='vx', save_path=None):
        """Plot the calculated LVACF."""
        key = f'lvacf_{kind}'
        if key not in self.results:
            print(f"LVACF for {kind} not calculated.")
            return
            
        lvacf = self.results[key]
        lags = self.results[f'lvacf_lags_{kind}']
        
        plt.figure(figsize=(8, 6))
        plt.plot(lags, lvacf, 'o-', label=f'Data {kind}')
        plt.axhline(0, color='k', linestyle='--', alpha=0.3)
        plt.xlabel('Time lag [frames]')
        plt.ylabel('$R_L(\\tau)$')
        plt.title(f'Lagrangian Velocity Autocorrelation Function: {kind}')
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
            print(f"LVACF plot saved to {save_path}")
        plt.show()

    def generate_html_report(self, fname="report.html"):
        """Generate an interactive HTML report using Plotly."""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            print("Plotly not installed. HTML report skipped.")
            return

        fig = make_subplots(rows=2, cols=2, 
                           subplot_titles=("MSD", "Velocity PDF (vx)", "LVACF (vx)", "Structure Function (D2, vx)"))

        # MSD
        if 'msd' in self.results:
            fig.add_trace(go.Scatter(x=self.results['msd_lags'], y=self.results['msd'], mode='lines+markers', name='MSD'),
                          row=1, col=1)
            fig.update_xaxes(type="log", row=1, col=1)
            fig.update_yaxes(type="log", row=1, col=1)

        # PDF vx
        if 'pdf_vx' in self.results:
            centers, hist = self.results['pdf_vx']
            fig.add_trace(go.Scatter(x=centers, y=hist, mode='lines+markers', name='PDF vx'),
                          row=1, col=2)
            fig.update_yaxes(type="log", row=1, col=2)

        # LVACF vx
        if 'lvacf_vx' in self.results:
            fig.add_trace(go.Scatter(x=self.results['lvacf_lags_vx'], y=self.results['lvacf_vx'], mode='lines+markers', name='LVACF vx'),
                          row=2, col=1)

        # SF2 vx
        if 'sf2_vx' in self.results:
            fig.add_trace(go.Scatter(x=self.results['sf_lags_vx'], y=self.results['sf2_vx'], mode='lines+markers', name='SF2 vx'),
                          row=2, col=2)

        fig.update_layout(height=800, width=1000, title_text="Lagrangian Trajectory Analysis Report")
        fig.write_html(fname)
        print(f"HTML report saved to {fname}")

    def apply_smoothing(self, window_size=7, poly_order=3, dt=1.0):
        r"""
        Apply Savitzky-Golay smoothing and differentiation to raw trajectories.
        Updates the trajectories in place with calculated v and a.
        
        Parameters:
        window_size (int): Length of the filter window.
        poly_order (int): Order of the polynomial used to fit the samples.
        dt (float): Time step between frames.
        """
        from scipy.signal import savgol_filter
        print(f"Applying Savitzky-Golay smoothing (window={window_size}, order={poly_order})...")
        
        new_trajs = []
        for tr in self.trajs:
            # Assuming tr columns: [id, x, y, z, ..., frame]
            # We want to fill columns 4-6 (v) and 7-9 (a)
            n = len(tr)
            if n <= window_size:
                continue
                
            pos = tr[:, 1:4]
            # Smooth positions and get derivatives
            # velocity (1st derivative)
            v = savgol_filter(pos, window_size, poly_order, deriv=1, delta=dt, axis=0)
            # acceleration (2nd derivative)
            a = savgol_filter(pos, window_size, poly_order, deriv=2, delta=dt, axis=0)
            
            # Update trajectory array
            tr_new = tr.copy()
            tr_new[:, 4:7] = v
            tr_new[:, 7:10] = a
            new_trajs.append(tr_new)
            
        self.trajs = new_trajs
        print(f"Smoothing complete. {len(self.trajs)} trajectories processed.")

    def calculate_all(self, max_lag=None):
        """Run all standard Lagrangian analyses."""
        print("Calculating MSD...")
        self.calculate_msd(max_lag=max_lag)
        
        print("Calculating PDFs...")
        for k in ['vx', 'vy', 'vz', 'ax', 'ay', 'az']:
            self.calculate_pdf(kind=k)
            
        print("Calculating LVACF...")
        for k in ['vx', 'vy', 'vz']:
            self.calculate_lvacf(kind=k, max_lag=max_lag)
            
        print("Calculating Structure Functions...")
        for k in ['vx', 'vy', 'vz']:
            self.calculate_structure_function(kind=k, order=2, max_lag=max_lag)
        
        print("All calculations complete.")

if __name__ == "__main__":
    # Example usage
    analysis = LagrangianAnalysis()
    # Path to actual data
    data_path = "Data_and_analysis/20260315_frames/smoothed_trajectories"
    if os.path.exists(data_path):
        analysis.load_data(data_path)
        # analysis.calculate_msd()
        # analysis.plot_msd()
    else:
        print(f"Data file not found at {data_path}")
