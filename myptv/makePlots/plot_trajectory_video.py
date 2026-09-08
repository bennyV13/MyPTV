# -*- coding: utf-8 -*-
"""
plot_trajectory_video.py

Generates synchronized multi-camera MP4 videos (and GIF previews) following
individual particle or fiber trajectories.

Supports:
- Both 'particles' (spheres/points) and 'fibers' (rods/ellipsoids).
- Both 'old' (raw blob width/height) and 'smart' (size_measure decomposed) bounding box styles.
- Reading configuration directly from MyPTV YAML parameter files.
- Integration as a workflow action in workflow.py ('trajectory_video' or 'make_trajectory_video').
- Standalone CLI execution.
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
import imageio


def resolve_filepath(path, base_dirs=None):
    """
    Helper to resolve relative paths against candidate base directories.
    """
    if path is None:
        return None
    if os.path.isabs(path) and os.path.exists(path):
        return path
        
    candidates = []
    if os.path.isabs(path):
        candidates.append(path)
    else:
        candidates.append(os.path.abspath(path))
        if base_dirs:
            for b in base_dirs:
                if b and os.path.exists(b):
                    candidates.append(os.path.abspath(os.path.join(b, path)))
                    
        # Common research root fallbacks
        for root in ["/Users/user/Desktop/Research",
                     "/Users/user/Desktop/Research/Data_Analysis/MyPTV_analysis"]:
            candidates.append(os.path.abspath(os.path.join(root, path)))

    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return candidates[0] if candidates else path


def load_frame_image(img_path):
    """
    Loads an image from disk, supporting raw (.dng) and standard (.tif, .png, etc.) formats.
    """
    ext = os.path.splitext(img_path)[1].lower()
    if ext == ".dng":
        import rawpy
        with rawpy.imread(img_path) as raw:
            return raw.raw_image.copy().astype(float)
    else:
        import imageio.v2 as iio
        img = iio.imread(img_path)
        if img.ndim == 3:
            # Convert RGB to grayscale
            img = 0.2989 * img[:, :, 0] + 0.5870 * img[:, :, 1] + 0.1140 * img[:, :, 2]
        return img.astype(float)


def load_cameras(camera_names, base_dirs=None):
    """
    Loads camera objects using camera_wrapper.
    camera_names can be a list or comma-separated string.
    """
    from myptv.imaging_mod import camera_wrapper

    if isinstance(camera_names, str):
        c_list = [c.strip() for c in camera_names.split(",") if c.strip()]
    else:
        c_list = list(camera_names)

    cams = []
    for cn in c_list:
        resolved = resolve_filepath(cn, base_dirs)
        if os.path.isdir(resolved):
            # If a directory like cal_v1 is passed, try Cam1..Cam4
            dir_path = resolved
            file_name = os.path.basename(cn) if os.path.basename(cn) != os.path.basename(resolved) else "Cam1"
        else:
            dir_path, file_name = os.path.split(resolved)
            
        cam = camera_wrapper(file_name, dir_path)
        cam.load()
        cams.append(cam)
    return cams


def find_camera_image_files(images_folder, num_cams=4, ext=".dng", base_dirs=None):
    """
    Locates image files for each camera folder (e.g. Cam1..Cam4 or cam1..cam4).
    Returns a dict {cam_idx: [sorted_image_filenames]}, and the base directory.
    """
    resolved_folder = resolve_filepath(images_folder, base_dirs)
    if not os.path.exists(resolved_folder):
        raise FileNotFoundError(f"Images folder not found: {images_folder} (resolved: {resolved_folder})")

    # Check if images_folder points to a single camera like .../Rec13/Cam1
    base_folder = resolved_folder
    last_elem = os.path.basename(os.path.normpath(resolved_folder))
    if last_elem.lower().startswith("cam"):
        parent = os.path.dirname(os.path.normpath(resolved_folder))
        if os.path.exists(parent):
            base_folder = parent

    cam_files = {}
    cam_dirs = {}
    for i in range(num_cams):
        # Look for Cam{i+1}, cam{i+1}, Camera_{i+1}, etc.
        candidate_names = [f"Cam{i+1}", f"cam{i+1}", f"Camera_{i+1}", f"camera_{i+1}", f"Cam_{i+1}"]
        found_dir = None
        for cname in candidate_names:
            p = os.path.join(base_folder, cname)
            if os.path.isdir(p):
                found_dir = p
                break

        if found_dir is None:
            # Fallback: check if base_folder itself contains images and num_cams == 1
            if num_cams == 1:
                found_dir = base_folder
            else:
                raise FileNotFoundError(
                    f"Could not find camera folder for Camera {i+1} in {base_folder}. "
                    f"Checked candidates: {candidate_names}"
                )

        cam_dirs[i] = found_dir
        flist = sorted([
            f for f in os.listdir(found_dir)
            if f.lower().endswith(ext.lower()) and not f.startswith("._")
        ])
        if len(flist) == 0:
            raise FileNotFoundError(f"No {ext} images found in {found_dir}")
        cam_files[i] = flist

    return cam_files, cam_dirs


def load_blob_tables(blob_files, num_cams=4, base_dirs=None):
    """
    Loads 2D blob tables for all cameras into a dictionary of DataFrames.
    """
    if isinstance(blob_files, str):
        b_list = [b.strip() for b in blob_files.split(",") if b.strip()]
    else:
        b_list = list(blob_files)

    blob_dfs = {}
    for i in range(num_cams):
        if i < len(b_list):
            bf = resolve_filepath(b_list[i], base_dirs)
            if os.path.exists(bf):
                blob_dfs[i] = pd.read_csv(bf, sep=r"\s+", header=None)
                continue

        # Fallback: attempt to find blobs_Cam{i+1} or blobs_cam{i+1}
        search_dirs = base_dirs or [os.getcwd()]
        found = False
        for sdir in search_dirs:
            for pat in [f"blobs_Cam{i+1}_directions", f"blobs_cam{i+1}_directions",
                        f"blobs_Cam{i+1}", f"blobs_cam{i+1}"]:
                cand = os.path.join(sdir, pat)
                if os.path.exists(cand):
                    blob_dfs[i] = pd.read_csv(cand, sep=r"\s+", header=None)
                    found = True
                    break
            if found:
                break

        if not found:
            # If no blob file, store empty dataframe
            blob_dfs[i] = pd.DataFrame()

    return blob_dfs


def extract_trajectory_data(traj_file, traj_id=None, orientations_file=None, base_dirs=None):
    """
    Loads trajectory rows for a given traj_id from text file or .npz.
    Returns:
      traj_rows: DataFrame or ndarray of trajectory records
      traj_id_used: the selected trajectory ID
      orientations_map: dict {(traj_id, frame): [px, py, pz]} (if available)
    """
    resolved_traj = resolve_filepath(traj_file, base_dirs)
    if not os.path.exists(resolved_traj):
        raise FileNotFoundError(f"Trajectory file not found: {traj_file} (resolved: {resolved_traj})")

    orientations_map = {}
    if orientations_file:
        res_ori = resolve_filepath(orientations_file, base_dirs)
        if os.path.exists(res_ori):
            odf = pd.read_csv(res_ori, sep=r"\s+", header=None)
            # col 0: traj_id, cols 1..3: px, py, pz, col -1: frame
            f_col = odf.columns[-1]
            for _, r in odf.iterrows():
                tid = int(r[0])
                frm = int(round(r[f_col]))
                orientations_map[(tid, frm)] = np.array([float(r[1]), float(r[2]), float(r[3])])

    if resolved_traj.endswith(".npz"):
        npz_data = np.load(resolved_traj, allow_pickle=True)["data"]
        # If traj_id is None, pick first non-empty or longest
        if traj_id is None:
            lengths = [len(tr) if tr is not None else 0 for tr in npz_data]
            traj_id = int(np.argmax(lengths))
        tr = npz_data[traj_id]
        return tr, traj_id, orientations_map

    # Text trajectory file (e.g. trajectories or smoothed_trajectories)
    tdf = pd.read_csv(resolved_traj, sep=r"\s+", header=None)
    
    # Identify available trajectory IDs (excluding noise ID -1)
    valid_ids = [tid for tid in tdf[0].unique() if tid > 0]
    if not valid_ids:
        valid_ids = list(tdf[0].unique())
    if not valid_ids:
        raise ValueError(f"No trajectory records found in {resolved_traj}")

    if traj_id is None or traj_id == "longest":
        # Pick trajectory with highest count of frames
        id_counts = tdf[tdf[0].isin(valid_ids)][0].value_counts()
        traj_id = int(id_counts.index[0])
    else:
        traj_id = int(traj_id)

    frame_col = tdf.columns[-1]
    sub_tr = tdf[tdf[0] == traj_id].sort_values(by=frame_col).copy()
    if len(sub_tr) == 0:
        raise ValueError(f"Trajectory ID {traj_id} not found in {resolved_traj}")
    sub_tr["frame_number"] = np.round(sub_tr[frame_col].values).astype(int)

    # Check if this is a smoothed trajectory file (11 cols) and see if raw trajectories file exists
    # to provide exact camera blob indices
    if len(tdf.columns) == 11 and "smoothed" in os.path.basename(resolved_traj):
        raw_name = os.path.basename(resolved_traj).replace("smoothed_", "")
        raw_path = os.path.join(os.path.dirname(resolved_traj), raw_name)
        if os.path.exists(raw_path):
            try:
                raw_df = pd.read_csv(raw_path, sep=r"\s+", header=None)
                raw_sub = raw_df[raw_df[0] == traj_id]
                raw_f_col = raw_df.columns[-1]
                cam_cols = [c for c in range(4, min(8, len(raw_df.columns) - 2))]
                merged = pd.merge(
                    sub_tr,
                    raw_sub[[raw_f_col] + cam_cols],
                    left_on="frame_number",
                    right_on=raw_f_col,
                    how="left",
                    suffixes=("", "_raw")
                )
                sub_tr = merged
            except Exception:
                pass

    return sub_tr, traj_id, orientations_map


def render_trajectory_video(
    traj_data,
    traj_id,
    cams,
    cam_files,
    cam_dirs,
    blob_dfs,
    shape="particles",
    bbox_style="old",
    orientations_map=None,
    pad=40,
    fps_mp4=250,
    fps_gif=10,
    save_mp4=True,
    save_gif=True,
    out_mp4=None,
    out_gif=None,
    frame_start=None,
    frame_end=None,
    rec_name=None,
):
    """
    Renders synchronized video frames for a trajectory across all cameras.
    """
    shape = str(shape).lower().strip()
    bbox_style = str(bbox_style).lower().strip()
    num_cams = len(cams)

    # Convert traj_data to standard row access
    if isinstance(traj_data, np.ndarray):
        # NPZ format (e.g. Analysis_f format)
        is_npz = True
        n_rows = len(traj_data)
        raw_frames = np.round(traj_data[:, 24] * 250.0).astype(int) if traj_data.shape[1] > 24 else np.arange(n_rows)
        frames = raw_frames % 1000000
    else:
        is_npz = False
        n_rows = len(traj_data)
        f_col = "frame_number" if "frame_number" in traj_data.columns else traj_data.columns[-1]
        frames = np.round(traj_data[f_col].values).astype(int)

    # Filter frame range if specified
    indices = []
    for idx in range(n_rows):
        frm = frames[idx]
        if frame_start is not None and frm < frame_start:
            continue
        if frame_end is not None and frm > frame_end:
            continue
        indices.append(idx)

    if not indices:
        raise ValueError(f"No frames to render for Trajectory {traj_id} in range [{frame_start}, {frame_end}]")

    start_frame = int(frames[indices[0]])
    end_frame = int(frames[indices[-1]])
    display_rec = rec_name or f"Traj {traj_id}"

    # Try importing smart bbox decomposition if requested and shape is fibers
    use_smart = (bbox_style == "smart" and shape == "fibers")
    decompose_blob_bbox = None
    compute_local_scale = None
    if use_smart:
        try:
            from geometry import decompose_blob_bbox as _decomp, compute_local_scale as _scale
            decompose_blob_bbox = _decomp
            compute_local_scale = _scale
        except ImportError:
            print("Notice: size_measure.geometry module not found; falling back to old bbox style.")
            use_smart = False
            bbox_style = "old"

    print(f"--> Rendering Trajectory {traj_id} ({shape.upper()}, {bbox_style.upper()} BBox, "
          f"Frames {start_frame}..{end_frame}, {len(indices)} frames)...")

    video_frames = []

    # Grid layout: 2x2 for 4 cams, 1x2 for 2 cams, 1x3 for 3 cams
    if num_cams == 4:
        nrows, ncols = 2, 2
        figsize = (8.5, 8.5)
    elif num_cams == 2:
        nrows, ncols = 1, 2
        figsize = (9.0, 4.5)
    elif num_cams == 3:
        nrows, ncols = 1, 3
        figsize = (12.0, 4.2)
    else:
        nrows = int(np.ceil(num_cams / 2))
        ncols = 2
        figsize = (8.5, 4.2 * nrows)

    for row_idx in indices:
        f_idx = int(frames[row_idx])

        # Extract 3D position and orientation
        if is_npz:
            pos_3d = traj_data[row_idx, 1:4]
            if traj_data.shape[1] > 12:
                px, py, pz = traj_data[row_idx, 10:13]
            else:
                px, py, pz = None, None, None
            blob_indices = [int(traj_data[row_idx, 19 + c_i]) if traj_data.shape[1] > 19 + c_i else -1
                            for c_i in range(num_cams)]
        else:
            row_vals = traj_data.iloc[row_idx].values
            pos_3d = np.array([float(row_vals[1]), float(row_vals[2]), float(row_vals[3])])
            
            # Check orientations_map or orientation columns
            if orientations_map and (traj_id, f_idx) in orientations_map:
                px, py, pz = orientations_map[(traj_id, f_idx)]
            elif shape == "fibers" and len(row_vals) > 12:
                px, py, pz = float(row_vals[10]), float(row_vals[11]), float(row_vals[12])
            else:
                px, py, pz = None, None, None

            # Check blob indices
            # If merged raw columns are present (4_raw, 5_raw, etc.), use them, otherwise check cols 4..4+num_cams
            blob_indices = []
            for c_i in range(num_cams):
                b_val = -1
                if f"{4 + c_i}_raw" in traj_data.columns:
                    b_val = traj_data.iloc[row_idx][f"{4 + c_i}_raw"]
                elif len(row_vals) >= 4 + num_cams and len(row_vals) != 11:
                    # In standard 10-col tracking file, cols 4..7 are blob indices
                    b_val = row_vals[4 + c_i]
                blob_indices.append(int(b_val) if not np.isnan(b_val) else -1)

        # Telemetry calculations for title
        has_ori = (px is not None and not np.isnan(px) and shape == "fibers")
        if has_ori:
            phi_deg = np.degrees(np.arccos(np.clip(pz, -1.0, 1.0)))
            safe_px = px if abs(px) > 1e-12 else 1e-12
            theta_deg = np.degrees(np.arctan(py / safe_px))
        else:
            phi_deg, theta_deg = 0.0, 0.0

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=100)
        fig.patch.set_facecolor("#1a1a1a")
        axes_flat = axes.flat if hasattr(axes, "flat") else [axes]

        for c_i in range(num_cams):
            ax = axes_flat[c_i]
            ax.set_facecolor("#0a0a0a")

            # Resolve image filename for this frame
            flist = cam_files[c_i]
            img_file = None
            if 0 <= f_idx < len(flist):
                img_file = flist[f_idx]
            else:
                # Try finding file matching frame index numerically
                for f in flist:
                    base_num = "".join(filter(str.isdigit, os.path.splitext(f)[0]))
                    if base_num and int(base_num) == f_idx:
                        img_file = f
                        break

            if img_file is None:
                # Fallback to closest frame
                img_file = flist[min(max(0, f_idx), len(flist) - 1)]

            img_path = os.path.join(cam_dirs[c_i], img_file)
            gray = load_frame_image(img_path)

            b_idx = blob_indices[c_i] if c_i < len(blob_indices) else -1
            matched = False
            c_row, c_col = None, None
            bw, bh = 6.0, 6.0
            mass = 0.0
            cos_th, sin_th = 1.0, 0.0

            df_blobs = blob_dfs.get(c_i, pd.DataFrame())
            if not df_blobs.empty:
                # Filter blobs for current frame (col 5 is frame)
                frame_blobs = df_blobs[df_blobs[5] == f_idx]
                if b_idx >= 0 and b_idx < len(frame_blobs):
                    b_row = frame_blobs.iloc[b_idx]
                    c_row, c_col = float(b_row[0]), float(b_row[1])
                    bw, bh = float(b_row[2]), float(b_row[3])
                    mass = float(b_row[4])
                    if len(b_row) > 6:
                        cos_th = float(b_row[6])
                        sin_th = float(b_row[7])
                    matched = True
                elif b_idx < 0 and not frame_blobs.empty:
                    # Trajectory didn't record blob index (e.g. smoothed file) -> reproject and search nearest
                    proj = cams[c_i].projection(pos_3d)
                    p_col, p_row = float(proj[0]), float(proj[1])
                    dists = np.hypot(frame_blobs[1].values - p_col, frame_blobs[0].values - p_row)
                    min_idx = np.argmin(dists)
                    if dists[min_idx] <= 6.0:  # within 6 px
                        b_row = frame_blobs.iloc[min_idx]
                        b_idx = min_idx
                        c_row, c_col = float(b_row[0]), float(b_row[1])
                        bw, bh = float(b_row[2]), float(b_row[3])
                        mass = float(b_row[4])
                        if len(b_row) > 6:
                            cos_th = float(b_row[6])
                            sin_th = float(b_row[7])
                        matched = True

            if not matched:
                # Use 3D projection coordinates
                proj = cams[c_i].projection(pos_3d)
                c_col, c_row = float(proj[0]), float(proj[1])

            # Crop around centroid
            y_min = max(0, int(round(c_row - pad)))
            y_max = min(gray.shape[0], int(round(c_row + pad)))
            x_min = max(0, int(round(c_col - pad)))
            x_max = min(gray.shape[1], int(round(c_col + pad)))

            crop = gray[y_min:y_max, x_min:x_max]

            if crop.size > 0:
                vmin, vmax = np.percentile(crop, [2, 99.8])
                crop_norm = np.clip((crop - vmin) / (vmax - vmin + 1e-5), 0, 1)
                ax.imshow(crop_norm, cmap="inferno", origin="upper")

            cx_loc = c_col - x_min
            cy_loc = c_row - y_min

            # Draw overlays
            if matched:
                if shape == "fibers":
                    u = np.array([sin_th, cos_th])
                    norm_u = np.linalg.norm(u)
                    u = u / norm_u if norm_u > 1e-6 else np.array([1.0, 0.0])
                    v = np.array([-u[1], u[0]])

                    if use_smart and decompose_blob_bbox is not None:
                        l_px, d_px = decompose_blob_bbox(bw, bh, cos_th, sin_th)
                        _, mm_per_px = compute_local_scale(cams[c_i], pos_3d)
                        l_mm = l_px * mm_per_px * 0.90
                        hL = (l_px * 0.90) / 2.0
                        hD = d_px / 2.0
                        status_str = f"Cam {c_i+1} | L={l_px:.1f}px ({l_mm:.2f}mm)"
                    else:
                        # Old BBox method: simple max/min
                        hL = max(bw, bh) / 2.0
                        hD = min(bw, bh) / 2.0
                        status_str = f"Cam {c_i+1} | Blob #{b_idx}"

                    c1 = np.array([cx_loc, cy_loc]) + hL * u + hD * v
                    c2 = np.array([cx_loc, cy_loc]) + hL * u - hD * v
                    c3 = np.array([cx_loc, cy_loc]) - hL * u - hD * v
                    c4 = np.array([cx_loc, cy_loc]) - hL * u + hD * v

                    poly = Polygon([c1, c2, c3, c4], closed=True, edgecolor="cyan", facecolor="none", linewidth=1.8)
                    ax.add_patch(poly)
                    ax.plot(cx_loc, cy_loc, "c+", markersize=6)
                    status_sub = f"Mass: {int(mass):,}"
                    status_color = "#00ffcc"

                else:
                    # Shape == particles: bounding box around spherical particle
                    h_w = max(bw / 2.0, 2.0)
                    h_h = max(bh / 2.0, 2.0)
                    p_corners = [
                        [cx_loc - h_w, cy_loc - h_h],
                        [cx_loc + h_w, cy_loc - h_h],
                        [cx_loc + h_w, cy_loc + h_h],
                        [cx_loc - h_w, cy_loc + h_h]
                    ]
                    poly = Polygon(p_corners, closed=True, edgecolor="cyan", facecolor="none", linewidth=1.8)
                    ax.add_patch(poly)
                    ax.plot(cx_loc, cy_loc, "c+", markersize=6)
                    status_str = f"Cam {c_i+1} | Blob #{b_idx}"
                    status_sub = f"Mass: {int(mass):,} | {bw:.0f}x{bh:.0f}px"
                    status_color = "#00ffcc"

            else:
                # Unmatched: Reprojection dashed circle
                circle = Circle((cx_loc, cy_loc), 5, edgecolor="#ff4444", facecolor="none", linestyle="--", linewidth=1.5)
                ax.add_patch(circle)
                status_str = f"Cam {c_i+1} | No Match"
                status_sub = "3D Reproject"
                status_color = "#ff6666"

            ax.set_xlim(0, 2 * pad)
            ax.set_ylim(2 * pad, 0)
            ax.axis("off")
            ax.set_title(f"{status_str}\n{status_sub}", color=status_color, fontsize=9, pad=3)

        # Turn off any extra unused subplots
        for extra_ax in axes_flat[num_cams:]:
            extra_ax.axis("off")

        # Global Header
        bbox_label = f"({bbox_style.upper()} BBox)" if shape == "fibers" else "(Particles)"
        header1 = f"{display_rec} | Trajectory {traj_id} {bbox_label} | Frame {f_idx:03d} / {end_frame}"
        if has_ori:
            header2 = (f"3D: [{pos_3d[0]:.1f}, {pos_3d[1]:.1f}, {pos_3d[2]:.1f}] mm  |  "
                       f"p: [{px:+.2f}, {py:+.2f}, {pz:+.2f}]  |  θ: {theta_deg:+.1f}°, φ: {phi_deg:.1f}°")
        else:
            header2 = f"3D: [{pos_3d[0]:.2f}, {pos_3d[1]:.2f}, {pos_3d[2]:.2f}] mm"

        fig.suptitle(f"{header1}\n{header2}", color="white", fontsize=11, weight="bold", y=0.98)
        plt.subplots_adjust(left=0.03, right=0.97, top=0.88, bottom=0.03, wspace=0.06, hspace=0.15)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        video_frames.append(rgba)
        plt.close(fig)

    # Save outputs
    if save_mp4 and out_mp4:
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
        print(f"Saving MP4 video at {fps_mp4} fps to {out_mp4}...")
        imageio.mimwrite(out_mp4, video_frames, fps=fps_mp4, codec="libx264", macro_block_size=None)
        print(f"Video saved: {out_mp4}")

    if save_gif and out_gif:
        os.makedirs(os.path.dirname(os.path.abspath(out_gif)), exist_ok=True)
        print(f"Saving preview GIF at {fps_gif} fps to {out_gif}...")
        imageio.mimwrite(out_gif, video_frames, fps=fps_gif, loop=0)
        print(f"GIF saved:   {out_gif}")

    return out_mp4, out_gif


def render_trajectory_video_from_params(params_file, **overrides):
    """
    Parses a MyPTV YAML parameters file, extracts parameters with intelligent fallbacks,
    and runs render_trajectory_video.
    """
    from yaml import safe_load

    params_path = os.path.abspath(params_file)
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"Parameters file not found: {params_file}")

    with open(params_path, "r") as f:
        yaml_data = safe_load(f)

    # Collect sections into a dictionary
    sections = {}
    if isinstance(yaml_data, list):
        for entry in yaml_data:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    sections[k] = v if v is not None else {}
    elif isinstance(yaml_data, dict):
        sections = yaml_data

    # Check dedicated trajectory_video or make_trajectory_video block
    vid_block = sections.get("trajectory_video") or sections.get("make_trajectory_video") or {}

    # Merge overrides from kwargs
    cfg = {**vid_block, **{k: v for k, v in overrides.items() if v is not None}}

    params_dir = os.path.dirname(params_path)
    base_dirs = [params_dir, os.getcwd(), os.path.dirname(params_dir)]

    # 1. Determine shape ('particles' or 'fibers')
    shape = cfg.get("shape")
    if not shape:
        seg_block = sections.get("segmentation", {})
        shape = seg_block.get("shape", "particles")
    shape = str(shape).lower().strip()

    # 2. Determine bbox_style ('old' or 'smart')
    bbox_style = cfg.get("bbox_style", "old")

    # 3. Determine camera calibration
    camera_names = cfg.get("camera_names")
    if not camera_names:
        matching_block = sections.get("matching", {})
        camera_names = matching_block.get("camera_names")
    if not camera_names:
        cal_err_block = sections.get("analyze_calibration_error", {})
        camera_names = cal_err_block.get("camera_names")
    if not camera_names:
        ori_block = sections.get("fiber_orientations", {})
        camera_names = ori_block.get("camera_names")
    if not camera_names:
        cal_block = sections.get("calibration", {})
        camera_names = cal_block.get("camera_name")
    if not camera_names:
        raise ValueError("No camera calibration (camera_names) found in parameters file or arguments.")

    cams = load_cameras(camera_names, base_dirs=base_dirs)

    # 4. Determine images folder and extension
    images_folder = cfg.get("images_folder")
    if not images_folder:
        seg_block = sections.get("segmentation", {})
        images_folder = seg_block.get("images_folder") or seg_block.get("images_folder1")
    if not images_folder:
        raise ValueError("No images_folder found in parameters file or arguments.")

    seg_block = sections.get("segmentation", {})
    image_ext = cfg.get("image_extension") or seg_block.get("image_extension", ".dng")

    cam_files, cam_dirs = find_camera_image_files(
        images_folder, num_cams=len(cams), ext=image_ext, base_dirs=base_dirs
    )

    # 5. Determine trajectory file
    traj_file = cfg.get("trajectory_file")
    if not traj_file:
        smooth_block = sections.get("smoothing", {})
        traj_file = smooth_block.get("save_name") or smooth_block.get("trajectory_file")
    if not traj_file:
        track_block = sections.get("tracking", {})
        traj_file = track_block.get("save_name")
    if not traj_file:
        stitch_block = sections.get("stitching", {})
        traj_file = stitch_block.get("save_name")
    if not traj_file:
        raise ValueError("No trajectory file found in parameters file or arguments.")

    # 6. Determine blob files
    blob_files = cfg.get("blob_files")
    if not blob_files:
        if shape == "fibers":
            ori_block = sections.get("fiber_orientations", {})
            blob_files = ori_block.get("blob_files")
        if not blob_files:
            matching_block = sections.get("matching", {})
            blob_files = matching_block.get("blob_files")

    blob_dfs = load_blob_tables(blob_files, num_cams=len(cams), base_dirs=base_dirs)

    # 7. Determine orientations file (for fibers)
    orientations_file = cfg.get("orientations_file")
    if not orientations_file and shape == "fibers":
        so_block = sections.get("smoothed_orientations", {})
        orientations_file = so_block.get("save_name") or so_block.get("orientations_file")
        if not orientations_file:
            fo_block = sections.get("fiber_orientations", {})
            orientations_file = fo_block.get("save_name")

    # 8. Load trajectory data and determine traj_id
    traj_id_req = cfg.get("traj_id") or cfg.get("traj_idx") or cfg.get("particle_id")
    traj_data, traj_id_used, ori_map = extract_trajectory_data(
        traj_file, traj_id=traj_id_req, orientations_file=orientations_file, base_dirs=base_dirs
    )

    # 9. Output directory and filenames
    save_dir = cfg.get("save_dir") or cfg.get("out_dir") or params_dir
    save_name = cfg.get("save_name")
    rec_name = cfg.get("rec_name")
    if not rec_name:
        # Try inferring from trajectory path or images_folder (e.g. Rec13, Rec15)
        for part in traj_file.replace("/", "_").split("_"):
            if part.lower().startswith("rec") and any(c.isdigit() for c in part):
                rec_name = part.capitalize()
                break
        if not rec_name:
            for part in images_folder.replace("/", "_").split("_"):
                if part.lower().startswith("rec") and any(c.isdigit() for c in part):
                    rec_name = part.capitalize()
                    break

    tag = f"_{rec_name.lower()}" if rec_name else ""
    default_prefix = f"traj{traj_id_used:04d}{tag}_{shape}_{bbox_style}_bbox"
    if save_name:
        if save_name.endswith(".mp4") or save_name.endswith(".gif"):
            base_out = os.path.splitext(save_name)[0]
        else:
            base_out = os.path.join(save_dir, save_name)
    else:
        base_out = os.path.join(save_dir, default_prefix)

    out_mp4 = f"{base_out}.mp4"
    out_gif = f"{base_out}.gif"

    pad = int(cfg.get("pad", 40))
    fps_mp4 = int(cfg.get("fps", cfg.get("fps_mp4", 250)))
    fps_gif = int(cfg.get("fps_gif", 10))
    save_mp4 = bool(cfg.get("save_mp4", True))
    save_gif = bool(cfg.get("save_gif", True))
    frame_start = cfg.get("frame_start")
    frame_end = cfg.get("frame_end")
    if frame_start is not None:
        frame_start = int(frame_start)
    if frame_end is not None:
        frame_end = int(frame_end)

    return render_trajectory_video(
        traj_data=traj_data,
        traj_id=traj_id_used,
        cams=cams,
        cam_files=cam_files,
        cam_dirs=cam_dirs,
        blob_dfs=blob_dfs,
        shape=shape,
        bbox_style=bbox_style,
        orientations_map=ori_map,
        pad=pad,
        fps_mp4=fps_mp4,
        fps_gif=fps_gif,
        save_mp4=save_mp4,
        save_gif=save_gif,
        out_mp4=out_mp4,
        out_gif=out_gif,
        frame_start=frame_start,
        frame_end=frame_end,
        rec_name=rec_name,
    )


def cli_main():
    """
    Command-line interface for standalone execution.
    """
    parser = argparse.ArgumentParser(
        description="Create synchronized multi-camera MP4 video & GIF for particle or fiber trajectory."
    )
    parser.add_argument("params_file", help="Path to MyPTV parameters YAML file")
    parser.add_argument("--traj", "--traj-id", dest="traj_id", default=None, help="Trajectory ID to render (or 'longest')")
    parser.add_argument("--shape", choices=["particles", "fibers"], default=None, help="Target shape ('particles' or 'fibers')")
    parser.add_argument("--bbox", "--bbox-style", dest="bbox_style", choices=["old", "smart"], default=None, help="Bounding box style")
    parser.add_argument("--pad", type=int, default=None, help="Crop region half-size in pixels (default: 40)")
    parser.add_argument("--fps", type=int, default=None, help="MP4 framerate (default: 250)")
    parser.add_argument("--fps-gif", type=int, default=None, help="GIF framerate (default: 10)")
    parser.add_argument("--no-gif", action="store_true", help="Disable GIF preview export")
    parser.add_argument("--images-folder", default=None, help="Path to images directory (overrides params file)")
    parser.add_argument("--out-dir", default=None, help="Output directory for MP4 and GIF")
    parser.add_argument("--save-name", default=None, help="Custom output filename prefix")
    parser.add_argument("--f-start", type=int, default=None, help="Starting frame number")
    parser.add_argument("--f-end", type=int, default=None, help="Ending frame number")

    args = parser.parse_args()

    render_trajectory_video_from_params(
        args.params_file,
        traj_id=args.traj_id,
        shape=args.shape,
        bbox_style=args.bbox_style,
        pad=args.pad,
        images_folder=args.images_folder,
        fps=args.fps,
        fps_gif=args.fps_gif,
        save_gif=(not args.no_gif),
        save_dir=args.out_dir,
        save_name=args.save_name,
        frame_start=args.f_start,
        frame_end=args.f_end,
    )


if __name__ == "__main__":
    cli_main()
