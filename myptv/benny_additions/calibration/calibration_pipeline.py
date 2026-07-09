#!/usr/bin/env python3
"""
calibration_pipeline.py — Unified MyPTV Calibration Pipeline
=============================================================

Chains together all calibration steps for a 4-camera setup:

  Step 1 — Point Indexing   : Maps raw per-camera blob detections to their
                               known 3D world coordinates using KMeans + SVD.
  Step 2 — Reformat         : Converts indexed CSVs to MyPTV's tab-separated
                               5-column cal_points format.
  Step 3 — 2-Step Calibrate : Runs the automated two-step calibration
                               (sparse auto-subset → full-grid refinement).

Usage
-----
    python calibration_pipeline.py config.yml
    python calibration_pipeline.py --help        # show YAML format docs

YAML Config Format
------------------
    cal_dir: /path/to/cal_directory      # root for all outputs
    target_points: /path/to/cal_points   # 3-column (X, Y, Z) world target file

    calibration:
      alpha: 0.001                       # regularisation (default 0.001)
      step1_quadratic: false             # Step 1 solver order (default cubic)
      step2_quadratic: false             # Step 2 solver order (default cubic)

    cameras:
      - name: Cam1
        camera_id: 0
        blobs_file: /path/to/Cam1_blobs.txt   # 2-column PixelX, PixelY file
        origin: bl                            # tl | tr | bl | br
        swap_xy: false                        # swap Real X↔Y axes
        x_dir: null                           # plus | minus | null
        y_dir: null                           # plus | minus | null
        cal_image: /path/to/BG_Cam1.tif      # optional, overlaid on validation plot

      - name: Cam2
        camera_id: 1
        blobs_file: /path/to/Cam2_blobs.txt
        origin: bl
        swap_xy: false
        x_dir: null
        y_dir: null
        cal_image: null

      # ... repeat for Cam3, Cam4

Output Structure
----------------
    cal_dir/
      indexed/          # raw indexed CSVs  (camN_indexed.csv)
      cal_points/       # reformatted files  (camN_cal_points)   + .cam files
      plots/            # validation PNGs    (camN_validation.png)
"""

import os
import sys
import argparse

import numpy as np
import pandas as pd
from yaml import safe_load

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs(cal_dir):
    dirs = {
        "indexed":    os.path.join(cal_dir, "indexed"),
        "cal_points": os.path.join(cal_dir, "cal_points"),
        "plots":      os.path.join(cal_dir, "plots"),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs


def _load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = safe_load(f)

    # Validate required top-level keys
    for key in ("cal_dir", "target_points", "cameras"):
        if key not in cfg:
            raise ValueError(f"Missing required config key: '{key}'")

    if not os.path.isdir(cfg["cal_dir"]):
        os.makedirs(cfg["cal_dir"], exist_ok=True)

    if not os.path.exists(cfg["target_points"]):
        raise FileNotFoundError(f"target_points not found: {cfg['target_points']}")

    # Defaults for calibration block
    cal_cfg = cfg.get("calibration", {}) or {}
    cfg["calibration"] = {
        "alpha":           cal_cfg.get("alpha",           0.001),
        "step1_quadratic": cal_cfg.get("step1_quadratic", False),
        "step2_quadratic": cal_cfg.get("step2_quadratic", False),
    }

    # Defaults for each camera
    for cam in cfg["cameras"]:
        cam.setdefault("origin",    "bl")
        cam.setdefault("swap_xy",   False)
        cam.setdefault("x_dir",     None)
        cam.setdefault("y_dir",     None)
        cam.setdefault("cal_image", None)
        if not cam.get("blobs_file"):
            raise ValueError(f"Camera '{cam.get('name')}' is missing 'blobs_file'")
        if not os.path.exists(cam["blobs_file"]):
            raise FileNotFoundError(f"blobs_file not found for {cam['name']}: {cam['blobs_file']}")

    return cfg


# ---------------------------------------------------------------------------
# Stage 1 — Indexing  (point_indexer logic)
# ---------------------------------------------------------------------------

def _filter_collinear_outliers(points, num_expected):
    if len(points) <= num_expected:
        return np.arange(len(points))
    mean = np.mean(points, axis=0)
    centered = points - mean
    _, _, vh = np.linalg.svd(centered)
    normal_vector = vh[1]
    distances = np.abs(np.dot(centered, normal_vector))
    return np.sort(np.argsort(distances)[:num_expected])


def _get_line_distance(points, line_mean, line_dir):
    centered = points - line_mean
    projections = np.outer(np.dot(centered, line_dir), line_dir)
    return np.linalg.norm(centered - projections, axis=1)


def _index_camera(cam_cfg, target_pts):
    from sklearn.cluster import KMeans

    blobs_path  = cam_cfg["blobs_file"]
    camera_id   = cam_cfg.get("camera_id", 0)
    origin      = cam_cfg["origin"]
    swap_xy     = cam_cfg["swap_xy"]
    x_dir       = cam_cfg["x_dir"] or None
    y_dir       = cam_cfg["y_dir"] or None

    image_pts = np.loadtxt(blobs_path)

    p_idx = 1 if swap_xy else 0   # primary axis used for clustering
    s_idx = 0 if swap_xy else 1   # secondary axis used for within-cluster sorting

    real_x_values = np.sort(np.unique(target_pts[:, 0]))
    num_clusters  = len(real_x_values)

    # Initial KMeans clustering
    kmeans    = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)
    col_labels = kmeans.fit_predict(image_pts[:, p_idx].reshape(-1, 1))

    # Iterative line-based refinement
    print(f"  [{cam_cfg['name']}] Refining clusters iteratively...")
    for iter_idx in range(5):
        cluster_lines = []
        for i in range(num_clusters):
            pts = image_pts[col_labels == i]
            if len(pts) < 2:
                mean = pts.mean(axis=0) if len(pts) > 0 else image_pts.mean(axis=0)
                cluster_lines.append((mean, np.array([0, 1] if not swap_xy else [1, 0])))
                continue
            mean = pts.mean(axis=0)
            _, _, vh = np.linalg.svd(pts - mean)
            cluster_lines.append((mean, vh[0]))

        new_labels = np.array([
            np.argmin([_get_line_distance(p.reshape(1, -1), m, d)[0] for m, d in cluster_lines])
            for p in image_pts
        ])

        if np.array_equal(new_labels, col_labels):
            print(f"  [{cam_cfg['name']}] Converged after {iter_idx + 1} iteration(s).")
            break
        col_labels = new_labels

    # Sorting directions
    if not swap_xy:
        p_asc = origin in ["tl", "bl"]
        s_asc = origin in ["tl", "tr"]
    else:
        p_asc = origin in ["tl", "tr"]
        s_asc = origin in ["tl", "bl"]

    if x_dir == "plus":  p_asc = True
    elif x_dir == "minus": p_asc = False
    if y_dir == "plus":  s_asc = True
    elif y_dir == "minus": s_asc = False

    col_means = [image_pts[col_labels == i, p_idx].mean() for i in range(num_clusters)]
    sorted_col_indices = np.argsort(col_means)
    if not p_asc:
        sorted_col_indices = sorted_col_indices[::-1]

    unique_z  = sorted(np.unique(target_pts[:, 2]), reverse=True)
    z_to_plane = {z: i for i, z in enumerate(unique_z)}

    indexed_rows = []
    for i, col_idx in enumerate(sorted_col_indices):
        real_x     = real_x_values[i]
        col_pts    = image_pts[col_labels == col_idx]
        tgt_mask   = target_pts[:, 0] == real_x
        tgt_col    = target_pts[tgt_mask]
        num_target = len(tgt_col)

        if len(col_pts) > num_target:
            col_pts = col_pts[_filter_collinear_outliers(col_pts, num_target)]

        sorted_img = col_pts[np.argsort(col_pts[:, s_idx])]
        if not s_asc:
            sorted_img = sorted_img[::-1]

        tgt_col = tgt_col[np.argsort(tgt_col[:, 1])]

        if len(sorted_img) != num_target:
            print(f"  [{cam_cfg['name']}] Warning: Col {i} (X={real_x}): "
                  f"{len(sorted_img)} blobs vs {num_target} targets")

        for j in range(min(len(sorted_img), len(tgt_col))):
            img_p = sorted_img[j]
            tgt_p = tgt_col[j]
            indexed_rows.append([
                camera_id, "", z_to_plane[tgt_p[2]],
                img_p[0], img_p[1],
                tgt_p[0], tgt_p[1], tgt_p[2]
            ])

    return indexed_rows


def _save_indexed_and_plot(indexed_rows, out_csv, out_plot, cam_cfg):
    headers = ["CameraID", "ImagePath", "Plane", "PixelX", "PixelY", "WorldX", "WorldY", "WorldZ"]
    df = pd.DataFrame(indexed_rows, columns=headers)
    df.to_csv(out_csv, index=False)

    import matplotlib
    matplotlib.use("Agg")   # non-interactive backend
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))

    cal_image = cam_cfg.get("cal_image")
    if cal_image and os.path.exists(cal_image):
        try:
            img = plt.imread(cal_image)
            cmap = "gray" if img.ndim == 2 else None
            ax.imshow(img, cmap=cmap, alpha=0.6)
        except Exception as e:
            print(f"  [{cam_cfg['name']}] Warning: could not load cal_image: {e}")

    unique_x = df["WorldX"].unique()
    colors   = plt.cm.tab10(np.linspace(0, 1, len(unique_x)))

    for i, x in enumerate(unique_x):
        mask   = df["WorldX"] == x
        sub_df = df[mask].reset_index()
        ax.scatter(sub_df["PixelX"], sub_df["PixelY"], color=colors[i], label=f"X={x}", s=15)
        for idx in [0, len(sub_df) - 1]:
            row = sub_df.iloc[idx]
            ax.text(row["PixelX"], row["PixelY"],
                    f"({int(row['WorldX'])},{int(row['WorldY'])})",
                    fontsize=7, fontweight="bold", alpha=0.85)

    ax.set_title(f"Indexing Validation — {cam_cfg['name']}")
    ax.set_xlabel("Image X (px)")
    ax.set_ylabel("Image Y (px)")
    if not ax.yaxis_inverted():
        ax.invert_yaxis()
    ax.legend(title="World X-columns", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_plot, dpi=150)
    plt.close(fig)
    print(f"  [{cam_cfg['name']}] Validation plot saved → {out_plot}")


# ---------------------------------------------------------------------------
# Stage 2 — Reformat CSV → cal_points  (reformat_cal_csv logic)
# ---------------------------------------------------------------------------

def _reformat_to_cal_points(indexed_csv, out_cal_points):
    df = pd.read_csv(indexed_csv)
    if "PixelX" in df.columns:
        out = df[["PixelX", "PixelY", "WorldX", "WorldY", "WorldZ"]]
    else:
        raise ValueError(f"Unexpected CSV format in {indexed_csv}")
    out.to_csv(out_cal_points, sep="\t", header=False, index=False)
    print(f"  Reformatted → {out_cal_points}")


# ---------------------------------------------------------------------------
# Stage 3 — 2-Step Calibration  (calibrate_2Step logic)
# ---------------------------------------------------------------------------

def _discover_initial_points(data):
    ix, iy, iz = (2, 3, 4) if data.shape[1] == 5 else (0, 1, 2)
    xz_coords    = data[:, [ix, iz]]
    unique_cols  = np.unique(xz_coords, axis=0)

    corners = [
        np.argmin(data[:, ix] + data[:, iy]),
        np.argmax(data[:, ix] + data[:, iy]),
        np.argmin(data[:, ix] - data[:, iy]),
        np.argmax(data[:, ix] - data[:, iy]),
    ]
    selected = list(corners)

    current_shift = 0
    for i, col in enumerate(unique_cols):
        col_mask  = (data[:, ix] == col[0]) & (data[:, iz] == col[1])
        col_idx   = np.where(col_mask)[0]
        sorted_idx = col_idx[np.argsort(data[col_idx, iy])]
        n = len(sorted_idx)

        if n < 3:
            selected.extend(sorted_idx)
            continue

        increment     = (2 + (i - 1)) if i > 0 else 0
        current_shift = (current_shift + increment) % n
        gap           = n // 3

        selected.append(sorted_idx[current_shift % n])
        selected.append(sorted_idx[(current_shift + gap) % n])
        selected.append(sorted_idx[(current_shift + 2 * gap) % n])

    unique_sel = np.unique(selected)
    target_count = 25
    if len(unique_sel) > target_count:
        corner_arr = np.array(corners)
        others     = np.array([idx for idx in unique_sel if idx not in corner_arr])
        num_needed = target_count - len(corner_arr)
        if num_needed > 0:
            step     = len(others) / float(num_needed)
            subsampled = [others[int(k * step)] for k in range(num_needed)]
            unique_sel = np.sort(np.concatenate([corner_arr, subsampled]))
        else:
            unique_sel = np.sort(corner_arr)

    return unique_sel


def _calibrate_camera_2step(cam_name, cal_points_file, output_dir, alpha, step1_quadratic, step2_quadratic):
    from myptv.extendedZolof.camera    import camera_extendedZolof
    from myptv.extendedZolof.calibrate import calibrate_extendedZolof

    full_data = np.loadtxt(cal_points_file)

    # --- Step 1: auto-subset initial solve ---
    print(f"\n  [{cam_name}] Step 1: Auto-subset initial solve")
    indices = _discover_initial_points(full_data)
    subset  = full_data[indices]

    tmp_file = os.path.join(output_dir, f"{cam_name.lower()}_temp_subset")
    np.savetxt(tmp_file, subset, fmt="%.3f", delimiter="\t")
    try:
        cam1 = camera_extendedZolof(cam_name, cal_points_fname=tmp_file)
        cal1 = calibrate_extendedZolof(cam1, cam1.image_points, cam1.lab_points,
                                       quadratic=step1_quadratic, alpha=alpha)
        order = "Quadratic" if step1_quadratic else "3rd-order"
        print(f"  [{cam_name}] Solving with {len(subset)} points ({order}, α={alpha})...")
        cal1.calibrate()
        print(f"  [{cam_name}] Step 1 RMS: {cal1.mean_squared_err():.6f} px")
        cam1.save(output_dir)
    except Exception as e:
        print(f"  [{cam_name}] ERROR in Step 1: {e}")
        return False
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    # --- Step 2: full-grid refinement ---
    print(f"  [{cam_name}] Step 2: Full-grid refinement ({len(full_data)} points)")
    try:
        cam2 = camera_extendedZolof(cam_name, cal_points_fname=cal_points_file)
        cam2.load(output_dir)
        cal2 = calibrate_extendedZolof(cam2, cam2.image_points, cam2.lab_points,
                                       quadratic=step2_quadratic, alpha=alpha)
        order = "Quadratic" if step2_quadratic else "3rd-order"
        print(f"  [{cam_name}] Refining ({order}, α={alpha})...")
        cal2.calibrate()
        print(f"  [{cam_name}] Step 2 RMS: {cal2.mean_squared_err():.6f} px")
        cam2.save(output_dir)
        print(f"  [{cam_name}] .cam file saved → {output_dir}")
    except Exception as e:
        print(f"  [{cam_name}] ERROR in Step 2: {e}")
        return False

    return True


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(config_path):
    cfg     = _load_config(config_path)
    cal_dir = cfg["cal_dir"]
    target_pts_path = cfg["target_points"]
    cal_cfg = cfg["calibration"]

    dirs = _ensure_dirs(cal_dir)

    target_pts = np.loadtxt(target_pts_path)
    if target_pts.shape[1] != 3:
        raise ValueError(f"target_points must be 3 columns (X,Y,Z), got {target_pts.shape[1]}")

    cameras = cfg["cameras"]
    n = len(cameras)

    header  = "=" * 65
    print(f"\n{header}")
    print(f"  MyPTV Calibration Pipeline  |  {n} camera(s)")
    print(f"  cal_dir      : {cal_dir}")
    print(f"  target_points: {target_pts_path}")
    print(f"  alpha={cal_cfg['alpha']}  step1_quad={cal_cfg['step1_quadratic']}  step2_quad={cal_cfg['step2_quadratic']}")
    print(header)

    results = {}

    for cam_cfg in cameras:
        cam_name = cam_cfg["name"]
        cam_id   = cam_cfg.get("camera_id", cameras.index(cam_cfg))

        print(f"\n{'─'*65}")
        print(f"  CAMERA: {cam_name}  (id={cam_id})")
        print(f"{'─'*65}")

        # ── Stage 1: Indexing ─────────────────────────────────────────────
        print(f"\n[1/3] Indexing blobs → world coordinates")
        out_csv  = os.path.join(dirs["indexed"],    f"{cam_name.lower()}_indexed.csv")
        out_plot = os.path.join(dirs["plots"],      f"{cam_name.lower()}_validation.png")

        try:
            indexed_rows = _index_camera(cam_cfg, target_pts)
            _save_indexed_and_plot(indexed_rows, out_csv, out_plot, cam_cfg)
        except Exception as e:
            print(f"  [{cam_name}] ERROR in indexing: {e}")
            results[cam_name] = "FAILED (indexing)"
            continue

        # ── Stage 2: Reformat ─────────────────────────────────────────────
        print(f"\n[2/3] Reformatting indexed CSV → cal_points")
        out_cal = os.path.join(dirs["cal_points"], f"{cam_name.lower()}_cal_points")

        try:
            _reformat_to_cal_points(out_csv, out_cal)
        except Exception as e:
            print(f"  [{cam_name}] ERROR in reformat: {e}")
            results[cam_name] = "FAILED (reformat)"
            continue

        # ── Stage 3: 2-Step Calibration ───────────────────────────────────
        print(f"\n[3/3] Running 2-step calibration")
        ok = _calibrate_camera_2step(
            cam_name, out_cal, dirs["cal_points"],
            alpha           = cal_cfg["alpha"],
            step1_quadratic = cal_cfg["step1_quadratic"],
            step2_quadratic = cal_cfg["step2_quadratic"],
        )
        results[cam_name] = "OK" if ok else "FAILED (calibration)"

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{header}")
    print("  PIPELINE SUMMARY")
    print(header)
    for cam_name, status in results.items():
        icon = "✓" if status == "OK" else "✗"
        print(f"  {icon}  {cam_name:10s}  {status}")
    print(header)
    print(f"\n  Outputs written to:")
    print(f"    Indexed CSVs  : {dirs['indexed']}")
    print(f"    Cal points    : {dirs['cal_points']}")
    print(f"    Plots         : {dirs['plots']}")
    print(f"    .cam files    : {dirs['cal_points']}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="calibration_pipeline.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "config",
        nargs="?",
        help="Path to the YAML configuration file.",
    )
    args = parser.parse_args()

    if not args.config:
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(args.config):
        print(f"Error: config file not found: {args.config}")
        sys.exit(1)

    run_pipeline(args.config)


if __name__ == "__main__":
    main()
