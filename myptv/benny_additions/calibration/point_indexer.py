import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import os
import argparse

def filter_collinear_outliers(points, num_expected):
    """
    Uses SVD to find the direction vector of a group of points and 
    returns the indices of the 'num_expected' points that best fit the line.
    """
    if len(points) <= num_expected:
        return np.arange(len(points))
    
    # Center the points
    mean = np.mean(points, axis=0)
    centered = points - mean
    
    # SVD to find the principal component (direction vector)
    # centered = U * S * Vh
    _, _, vh = np.linalg.svd(centered)
    
    # The direction vector is the first row of vh (for the largest singular value)
    # The normal vector is the second row of vh
    normal_vector = vh[1]
    
    # Project points onto the normal vector to get perpendicular distances
    distances = np.abs(np.dot(centered, normal_vector))
    
    # Keep points with the smallest distances
    keep_indices = np.argsort(distances)[:num_expected]
    return np.sort(keep_indices)

def get_line_distance(points, line_mean, line_dir):
    """
    Calculates perpendicular distance of points from a line defined by a mean and direction vector.
    """
    centered = points - line_mean
    # Distance = |centered - (centered . dir) * dir|
    projections = np.outer(np.dot(centered, line_dir), line_dir)
    perpendicular_vecs = centered - projections
    return np.linalg.norm(perpendicular_vecs, axis=1)

def index_calibration_points(image_points_path, target_points_path, camera_id=0, 
                             origin='bl', swap_xy=False, x_dir=None, y_dir=None):
    """
    Indexes image points to real-world coordinates using a configurable spatial sorting approach.
    
    origin options (image space):
    - 'tl': Top-Left (min X, min Y)
    - 'tr': Top-Right (max X, min Y)
    - 'bl': Bottom-Left (min X, max Y)
    - 'br': Bottom-Right (max X, max Y)
    
    swap_xy: If True, Real X aligns with Image Y, and Real Y aligns with Image X.
    x_dir/y_dir: Explicit 'plus' or 'minus' to override origin-based directions.
    """
    # Load image points (px, py)
    try:
        image_pts = np.loadtxt(image_points_path)
    except Exception as e:
        print(f"Error loading image points: {e}")
        return None

    # Load target points (X, Y, Z)
    try:
        target_pts = np.loadtxt(target_points_path)
    except Exception as e:
        print(f"Error loading target points: {e}")
        return None

    # Determine pixel axes
    # Standard: Real X -> Image X (0), Real Y -> Image Y (1)
    # Swapped: Real X -> Image Y (1), Real Y -> Image X (0)
    p_idx = 1 if swap_xy else 0 # primary (the one we cluster to find 'columns')
    s_idx = 0 if swap_xy else 1 # secondary (the one we sort within clusters)
    
    # Determine cluster count from target file (unique Real X values)
    real_x_values = np.sort(np.unique(target_pts[:, 0]))
    num_clusters = len(real_x_values)

    # 1. Cluster image points into columns based on primary pixel axis
    kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)
    col_labels = kmeans.fit_predict(image_pts[:, p_idx].reshape(-1, 1))

    # 2. Iterative Refinement: Fit lines and reassign points based on proximity to lines
    print("Refining clusters iteratively...")
    for iter_idx in range(5):
        cluster_lines = []
        for i in range(num_clusters):
            pts = image_pts[col_labels == i]
            if len(pts) < 2:
                # Fallback if cluster becomes too small
                mean = image_pts[col_labels == i].mean(axis=0) if len(pts) > 0 else image_pts.mean(axis=0)
                cluster_lines.append((mean, np.array([0, 1] if not swap_xy else [1, 0])))
                continue
            
            mean = pts.mean(axis=0)
            centered = pts - mean
            _, _, vh = np.linalg.svd(centered)
            direction = vh[0] # Principal component (column direction)
            cluster_lines.append((mean, direction))
        
        # Reassign every point to the closest line
        new_labels = []
        for p in image_pts:
            dists = [get_line_distance(p.reshape(1, -1), m, d)[0] for m, d in cluster_lines]
            new_labels.append(np.argmin(dists))
        
        new_labels = np.array(new_labels)
        if np.array_equal(new_labels, col_labels):
            print(f"  Converged after {iter_idx+1} iterations.")
            break
        col_labels = new_labels

    # 3. Determine sorting directions
    # p_asc: Does Real X increase as primary pixel axis increases?
    # s_asc: Does Real Y increase as secondary pixel axis increases?
    
    if not swap_xy:
        # X is horizontal (px), Y is vertical (py)
        p_asc = origin in ['tl', 'bl']
        s_asc = origin in ['tl', 'tr']
    else:
        # X is vertical (py), Y is horizontal (px)
        p_asc = origin in ['tl', 'tr']
        s_asc = origin in ['tl', 'bl']

    # Explicit overrides
    if x_dir == 'plus': p_asc = True
    elif x_dir == 'minus': p_asc = False
    if y_dir == 'plus': s_asc = True
    elif y_dir == 'minus': s_asc = False

    # Sort cluster indices by their mean primary-pixel value
    col_means = [image_pts[col_labels == i, p_idx].mean() for i in range(num_clusters)]
    sorted_col_indices = np.argsort(col_means)
    if not p_asc:
        sorted_col_indices = sorted_col_indices[::-1]

    indexed_rows = []
    
    # Mapping for Plane indexing (required by OpenLPT)
    unique_z = sorted(np.unique(target_pts[:, 2]), reverse=True)
    z_to_plane = {z: i for i, z in enumerate(unique_z)}

    for i, col_idx in enumerate(sorted_col_indices):
        real_x = real_x_values[i]
        
        # Get image points for this column
        col_pts = image_pts[col_labels == col_idx]
        
        # Get target points for this real X
        target_col_mask = (target_pts[:, 0] == real_x)
        target_col_pts = target_pts[target_col_mask]
        num_target = len(target_col_pts)
        
        # Robust filtering: if we have extra blobs, keep those closest to the column line
        if len(col_pts) > num_target:
            best_indices = filter_collinear_outliers(col_pts, num_target)
            col_pts = col_pts[best_indices]

        # Sort by secondary pixel axis
        sorted_img_indices = np.argsort(col_pts[:, s_idx])
        if not s_asc:
            sorted_img_indices = sorted_img_indices[::-1]
        sorted_img_pts = col_pts[sorted_img_indices]
        
        # Target points for this real X already fetched, sort by Real Y
        target_col_pts = target_col_pts[np.argsort(target_col_pts[:, 1])]
        
        if len(sorted_img_pts) != num_target:
            print(f"Warning: Camera {camera_id+1}, Col {i} (X={real_x}): {len(sorted_img_pts)} image blobs vs {num_target} target points")

        # Match points one-by-one in the sorted Y-order
        for j in range(min(len(sorted_img_pts), len(target_col_pts))):
            img_p = sorted_img_pts[j]
            tgt_p = target_col_pts[j]
            
            plane_idx = z_to_plane[tgt_p[2]]
            
            # OpenLPT Format: CameraID, ImagePath, Plane, PixelX, PixelY, WorldX, WorldY, WorldZ
            indexed_rows.append([
                camera_id, "", plane_idx, img_p[0], img_p[1], tgt_p[0], tgt_p[1], tgt_p[2]
            ])

    return indexed_rows

def save_and_plot(indexed_rows, output_csv, output_plot, camera_name, create_plot=True):
    """
    Saves the indexed points to a CSV and optionally generates a validation plot.
    """
    headers = ["CameraID", "ImagePath", "Plane", "PixelX", "PixelY", "WorldX", "WorldY", "WorldZ"]
    df = pd.DataFrame(indexed_rows, columns=headers)
    df.to_csv(output_csv, index=False)
    
    if not create_plot:
        print(f"Successfully processed {camera_name}. (Plot skipped)")
        return

    import matplotlib.pyplot as plt
    
    # Plotting for Human Approval
    plt.figure(figsize=(10, 8))
    unique_x = df['WorldX'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_x)))
    
    for i, x in enumerate(unique_x):
        mask = df['WorldX'] == x
        plt.scatter(df.loc[mask, 'PixelX'], df.loc[mask, 'PixelY'], color=colors[i], label=f'X={x}', s=15)
        
        # Label first and last points of each column
        sub_df = df[mask].reset_index()
        if not sub_df.empty:
            indices_to_label = [0, len(sub_df)-1]
            for idx in indices_to_label:
                row = sub_df.iloc[idx]
                plt.text(row['PixelX'], row['PixelY'], f"({int(row['WorldX'])},{int(row['WorldY'])})", 
                         fontsize=8, fontweight='bold', alpha=0.9)

    plt.title(f"Point Indexing Validation - {camera_name}")
    plt.xlabel("Image X (px)")
    plt.ylabel("Image Y (px)")
    plt.gca().invert_yaxis() 
    plt.legend(title="Target X-Columns", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_plot, dpi=150)
    plt.close()
    print(f"Successfully processed {camera_name}. Validation plot: {output_plot}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index calibration points to real-world coordinates.")
    
    # File arguments
    parser.add_argument("--image_points", help="Path to image points file (e.g., blobs.txt)")
    parser.add_argument("--target_points", help="Path to target points file (e.g., cal_points)")
    parser.add_argument("--output", help="Output CSV path")
    parser.add_argument("--camera_id", type=int, default=0, help="Camera ID (default 0)")
    parser.add_argument("--plot", help="Path to save validation plot")
    parser.add_argument("--create_png", action="store_true", help="Enable generating the validation plot (PNG)")
    parser.add_argument("--cal_image", help="Path to the background calibration image (e.g. image.png)")

    # Mapping arguments
    parser.add_argument("--origin", choices=['tl', 'tr', 'bl', 'br'], default='bl',
                        help="Origin corner in image space: tl (top-left), tr (top-right), bl (bottom-left), br (bottom-right)")
    parser.add_argument("--swap_xy", action="store_true", help="Swap Real X and Real Y axes (for vertical grids)")
    
    # Direction aliases/overrides
    parser.add_argument("--top_left", action="store_true", help="Set origin to Top-Left")
    parser.add_argument("--top_right", action="store_true", help="Set origin to Top-Right")
    parser.add_argument("--bottom_left", action="store_true", help="Set origin to Bottom-Left")
    parser.add_argument("--bottom_right", action="store_true", help="Set origin to Bottom-Right")
    parser.add_argument("--lower_right", action="store_true", help="Alias for --bottom_right")
    
    parser.add_argument("--plus_x", action="store_true", help="Real X increases with Pixel X (or Y if swapped)")
    parser.add_argument("--minus_x", action="store_true", help="Real X decreases with Pixel X (or Y if swapped)")
    parser.add_argument("--plus_y", action="store_true", help="Real Y increases with Pixel Y (or X if swapped)")
    parser.add_argument("--minus_y", action="store_true", help="Real Y decreases with Pixel Y (or X if swapped)")

    args = parser.parse_args()

    # Determine origin from flags
    origin = args.origin
    if args.top_left: origin = 'tl'
    elif args.top_right: origin = 'tr'
    elif args.bottom_left: origin = 'bl'
    elif args.bottom_right or args.lower_right: origin = 'br'

    # Determine explicit directions
    x_dir = None
    if args.plus_x: x_dir = 'plus'
    elif args.minus_x: x_dir = 'minus'
    
    y_dir = None
    if args.plus_y: y_dir = 'plus'
    elif args.minus_y: y_dir = 'minus'

    # Validate arguments
    if args.cal_image:
        if not (args.image_points and args.target_points):
            parser.error("Error: --cal_image can only be used in single-camera mode. "
                         "Please provide both --image_points and --target_points.")

    if args.image_points and args.target_points:
        # Process single camera
        output_csv = args.output if args.output else "indexed_points.csv"
        output_plot = args.plot if args.plot else "indexing_validation.png"
        
        # Plotting is enabled if --create_png is True OR if --plot was explicitly provided
        # For backward compatibility, we'll keep it True if neither is provided but we want to 
        # allow the user to control it.
        # Actually, if they ask for --create_png, it's cleaner to make it explicit.
        # But let's check if the user wants to DISABLE it.
        # If I make it False by default, I break the existing Cam 1 command if it didn't use --plot.
        # But it DID use --plot.
        
        create_plot = args.create_png or (args.plot is not None)
        
        rows = index_calibration_points(args.image_points, args.target_points, camera_id=args.camera_id,
                                        origin=origin, swap_xy=args.swap_xy, x_dir=x_dir, y_dir=y_dir)
        if rows:
            save_and_plot(rows, output_csv, output_plot, f"Cam {args.camera_id}", create_plot=create_plot)
    else:
        # Default execution for the 4 cameras in synthetic_data
        print("No input files specified. Running default batch for synthetic_data...")
        base_dir = "synthetic_data"
        target_file = os.path.join(base_dir, "calibration/cal_points")
        
        for cam_id in range(1, 5):
            img_file = os.path.join(base_dir, f"calibration/blobs_cam{cam_id}_cal_im.txt")
            out_csv = os.path.join(base_dir, f"calibration/cam{cam_id}_indexed.csv")
            out_plot = os.path.join(base_dir, f"calibration/cam{cam_id}_validation.png")
            
            if os.path.exists(img_file):
                rows = index_calibration_points(img_file, target_file, camera_id=cam_id-1,
                                                origin=origin, swap_xy=args.swap_xy, x_dir=x_dir, y_dir=y_dir)
                if rows:
                    save_and_plot(rows, out_csv, out_plot, f"Cam {cam_id}", create_plot=args.create_png or True)
            else:
                print(f"Skipping Camera {cam_id}: {img_file} not found.")
