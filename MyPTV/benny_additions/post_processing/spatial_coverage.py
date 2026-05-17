import numpy as np
import argparse
import os
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
from pyevtk.hl import gridToVTK
import plotly.graph_objects as go
from PIL import Image
import tifffile as tiff

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_unique_filename(base_name, extension):
    if not os.path.exists(f"{base_name}{extension}"):
        return f"{base_name}{extension}"
    counter = 1
    while os.path.exists(f"{base_name}_{counter}{extension}"):
        counter += 1
    return f"{base_name}_{counter}{extension}"

def load_data(file_path, cols=(1, 2, 3)):
    try:
        data = np.loadtxt(file_path, usecols=cols)
        return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        raise

def load_mask(mask_path):
    try:
        img = Image.open(mask_path)
        mask_array = np.array(img) > 0
        print(f"Loaded mask from {mask_path} (Size: {img.size}, Shape: {mask_array.shape})")
        return mask_array
    except Exception as e:
        print(f"Error loading mask from {mask_path}: {e}")
        return None

def generate_grid(ranges, resolution=1.0):
    coords = [np.arange(r[0], r[1] + resolution, resolution) for r in ranges]
    mesh = np.meshgrid(*coords, indexing='ij')
    grid_points = np.vstack([m.ravel() for m in mesh]).T
    grid_shape = tuple(len(c) for c in coords)
    return grid_points, grid_shape, coords

def calculate_gio(particles, grid_points, sigma=3.0):
    print(f"Building KDTree for {len(particles)} particles...")
    particle_tree = KDTree(particles)
    cutoff = 3.0 * sigma
    print(f"Querying KDTree with {len(grid_points)} grid points (cutoff={cutoff})...")
    
    occupancy = np.zeros(len(grid_points))
    inv_2sigma2 = 1.0 / (2.0 * sigma**2)
    
    # Process in chunks to save memory
    chunk_size = 1000
    for start_idx in range(0, len(grid_points), chunk_size):
        end_idx = min(start_idx + chunk_size, len(grid_points))
        chunk_points = grid_points[start_idx:end_idx]
        
        indices = particle_tree.query_ball_point(chunk_points, cutoff)
        
        for i, idx_list in enumerate(indices):
            if idx_list:
                diff = particles[idx_list] - chunk_points[i]
                d2 = np.sum(diff**2, axis=1)
                occupancy[start_idx + i] = np.sum(np.exp(-d2 * inv_2sigma2))
                
        if (start_idx // chunk_size) % 10 == 0:
            print(f"Progress: {end_idx}/{len(grid_points)} points processed...")
            
    return occupancy

def export_to_vtk(filename_base, occupancy, grid_shape, grid_coords, valid_mask=None):
    filename = get_unique_filename(filename_base, "")
    if len(grid_coords) == 2:
        x, y = grid_coords
        z = np.array([0.0])
        grid_shape_3d = (grid_shape[0], grid_shape[1], 1)
    else:
        x, y, z = grid_coords
        grid_shape_3d = grid_shape
    occupancy_3d = occupancy.reshape(grid_shape_3d)
    point_data = {"Occupancy": occupancy_3d}
    if valid_mask is not None:
        point_data["Mask"] = valid_mask.reshape(grid_shape_3d).astype(np.float32)
    gridToVTK(filename, x, y, z, pointData=point_data)
    return f"{filename}.vtr"

def generate_heatmaps(filename, occupancy, grid_shape, grid_coords, info, z_levels=None, valid_mask=None):
    if len(grid_shape) == 2:
        x, y = grid_coords
        occupancy_2d = occupancy.reshape(grid_shape)
        if valid_mask is not None:
            plot_data = np.ma.masked_array(occupancy_2d, mask=~valid_mask.reshape(grid_shape)).T
        else:
            plot_data = occupancy_2d.T
        
        # Rotate 90 deg CW
        plot_data = np.rot90(plot_data, k=3)
        plot_data = np.rot90(plot_data, k=3)
        plot_data = np.rot90(plot_data, k=3)
        plt.figure(figsize=(8, 10))
        im = plt.imshow(plot_data, extent=[y[0], y[-1], x[0], x[-1]], origin='lower', cmap='viridis', 
                        norm=plt.matplotlib.colors.LogNorm(vmin=1e-2, vmax=max(1.0, occupancy.max())))
        plt.title(f"2D Spatial Coverage: {info['input_file']}")
        plt.xlabel("Y (px)"); plt.ylabel("X (px)"); plt.colorbar(im, label='Occupancy Score (S)')
        summary_text = f"Sigma: {info['sigma']} | Resolution: {info['resolution']}"
        if valid_mask is not None: summary_text += " | Masked"
        plt.figtext(0.5, 0.01, summary_text, ha="center", fontsize=10)
    else:
        x, y, z = grid_coords
        occupancy_3d = occupancy.reshape(grid_shape)
        if z_levels is None: z_levels = [z[len(z)//4], z[len(z)//2], z[3*len(z)//4]]
        n_slices = len(z_levels); fig, axes = plt.subplots(1, n_slices, figsize=(5 * n_slices, 8), sharey=True)
        if n_slices == 1: axes = [axes]
        for i, z_val in enumerate(z_levels):
            z_idx = np.abs(z - z_val).argmin(); actual_z = z[z_idx]; slice_data = occupancy_3d[:, :, z_idx].T
            
            # Rotate 90 deg CW
            slice_data = np.rot90(slice_data, k=3)
            
            im = axes[i].imshow(slice_data, extent=[y[0], y[-1], x[0], x[-1]], origin='lower', cmap='viridis', 
                                norm=plt.matplotlib.colors.LogNorm(vmin=1e-2, vmax=max(1.0, occupancy.max())))
            axes[i].set_title(f"Z = {actual_z:.1f}"); axes[i].set_xlabel("Y")
            if i == 0: axes[i].set_ylabel("X")
        summary_text = f"File: {info['input_file']} | Sigma: {info['sigma']} | Resolution: {info['resolution']}"
        fig.suptitle(summary_text, fontsize=14, y=1.05)
        fig.subplots_adjust(right=0.9, top=0.85); cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        fig.colorbar(im, cax=cbar_ax, label='Occupancy Score (S)')
    plt.savefig(filename, bbox_inches='tight'); plt.close()

def generate_html_report(filename, occupancy, grid_shape, grid_coords, stats, info, valid_mask=None):
    if len(grid_shape) == 3:
        x, y, z = grid_coords
        xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
        fig = go.Figure(data=go.Isosurface(
            x=xx.flatten(), y=yy.flatten(), z=zz.flatten(), value=occupancy.flatten(),
            isomin=0.01, isomax=occupancy.max(), surface_count=5, colorbar_title='Occupancy (S)',
            caps=dict(x_show=False, y_show=False), colorscale='Viridis', opacity=0.6
        ))
        report_title = f"3D Spatial Coverage: {info['input_file']}"
        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z', aspectmode='data'))
    else:
        x, y = grid_coords
        occupancy_2d = occupancy.reshape(grid_shape)
        if valid_mask is not None:
            plot_z = occupancy_2d.astype(float); plot_z[~valid_mask.reshape(grid_shape)] = np.nan; plot_z = plot_z.T
        else:
            plot_z = occupancy_2d.T
        fig = go.Figure(data=go.Heatmap(
            z=plot_z, x=x, y=y, colorscale='Viridis', colorbar_title='Occupancy (S)',
            zmin=0.01, zmax=max(1.0, occupancy.max())
        ))
        report_title = f"2D Spatial Coverage: {info['input_file']}"
        fig.update_layout(xaxis_title='X', yaxis_title='Y')
    fig.update_layout(title=dict(text=report_title, x=0.5, y=0.98), margin=dict(l=0, r=0, b=0, t=50))
    dim_str = f"{len(grid_shape)}D"
    if valid_mask is not None: dim_str += " (Masked)"
    info_text = (f"<b>Source File:</b> {info['input_file']}<br><b>Dimensions:</b> {dim_str}<br>"
                 f"<b>Sigma:</b> {info['sigma']}<br><b>Resolution:</b> {info['resolution']}<br>"
                 f"<b>Total Points:</b> {stats['points']}<br><b>Active Area Coverage:</b> {stats['coverage']:.2f}%<br>"
                 f"<b>Max Score:</b> {stats['max']:.2f}")
    fig.add_annotation(text=info_text, align='left', showarrow=False, xref='paper', yref='paper', x=0.02, y=0.98,
                       bgcolor="white", opacity=0.8, bordercolor="black", borderwidth=1)
    fig.write_html(filename)

def generate_tif(filename, occupancy, grid_shape, target_size=(2176, 2172)):
    if len(grid_shape) != 2:
        print("Warning: TIF export only supported for 2D data.")
        return
    
    occupancy_2d = occupancy.reshape(grid_shape)
    
    # Normalize to [0, 1] for EQ map standard
    max_val = occupancy_2d.max()
    if max_val > 0:
        tif_data = (occupancy_2d / max_val).astype(np.float32)
    else:
        tif_data = occupancy_2d.astype(np.float32)
        
    # Standard EQ maps in MyPTV are often (Rows, Cols) which maps to (Y, X)
    # Our grid is (X, Y) indexing='ij', so we transpose to (Y, X)
    tif_data = tif_data.T
    
    # If the grid resolution is not 1, we need to upscale to target_size
    if tif_data.shape != target_size[::-1]: # Note: target_size is (W, H), shape is (H, W)
        print(f"Resizing TIF from {tif_data.shape} to {target_size[::-1]}")
        from scipy.ndimage import zoom
        zoom_factors = (target_size[1] / tif_data.shape[0], target_size[0] / tif_data.shape[1])
        tif_data = zoom(tif_data, zoom_factors, order=1)
    
    tiff.imwrite(filename, tif_data)
    return filename

def main():
    parser = argparse.ArgumentParser(description="Calculate N-D spatial occupancy and coverage.")
    parser.add_argument("input", help="Path to data file")
    parser.add_argument("--cols", type=int, nargs='+', default=[1, 2, 3], help="Columns for coordinates")
    parser.add_argument("--sigma", type=float, default=3.0, help="Influence radius")
    parser.add_argument("--res", type=float, default=1.0, help="Grid resolution")
    parser.add_argument("--autorange", action="store_true", help="Auto detect range")
    parser.add_argument("--mask", help="Path to TIFF mask file")
    
    # HARDCODED DEFAULTS for 90-degree CCW shift:
    parser.add_argument("--mask-swap", type=str2bool, default=True, help="Swap X/Y for mask mapping")
    parser.add_argument("--mask-flip-y", type=str2bool, default=False, help="Flip Y for mask mapping")
    parser.add_argument("--mask-flip-x", type=str2bool, default=True, help="Flip X for mask mapping")
    
    parser.add_argument("--xrange", type=float, nargs=2, help="X range: min max")
    parser.add_argument("--yrange", type=float, nargs=2, help="Y range: min max")
    parser.add_argument("--zrange", type=float, nargs=2, help="Z range: min max")
    parser.add_argument("--html", action="store_true", help="Generate interactive HTML report")
    parser.add_argument("--vtr", action="store_true", help="Export to VTK (.vtr) format")
    parser.add_argument("--tif", action="store_true", help="Export to TIFF (.tif) for EQ mapping")
    
    args = parser.parse_args()
    if not os.path.exists(args.input): print(f"Error: File {args.input} not found."); return
    
    info = {'input_file': os.path.basename(args.input), 'sigma': args.sigma, 'resolution': args.res}
    print(f"--- Spatial Occupancy Analysis ---")
    particles = load_data(args.input, cols=args.cols)

    # Swap X and Y coordinates (e.g. Row/Col or Y/X datasets)
    if particles.shape[1] >= 2:
        particles[:, [0, 1]] = particles[:, [1, 0]]

    print(f"Total points loaded: {len(particles)}")

    
    ranges = []
    if args.autorange:
        for d in range(particles.shape[1]):
            p_min, p_max = np.min(particles[:, d]), np.max(particles[:, d])
            ranges.append((p_min - args.sigma, p_max + args.sigma))
    else:
        x_r, y_r, z_r = (args.xrange or (0, 100)), (args.yrange or (0, 100)), (args.zrange or (-50, 0))
        ranges = [x_r, y_r, z_r] if len(args.cols) == 3 else [x_r, y_r]

    print(f"Generating grid (Resolution: {args.res})...")
    grid_points, grid_shape, grid_coords = generate_grid(ranges, args.res)
    
    valid_mask = None
    if args.mask and len(grid_shape) == 2:
        mask_data = load_mask(args.mask)
        if mask_data is not None:
            mask_h, mask_w = mask_data.shape
            px, py = grid_points[:, 0], grid_points[:, 1]
            
            # Map Cartesian (X,Y) to Image (Row, Col)
            if args.mask_swap:
                # Rotated setup (default True): Cartesian X -> Row, Cartesian Y -> Col
                row_indices, col_indices = px.copy(), py.copy()
            else:
                # Standard setup: Cartesian Y -> Row, Cartesian X -> Col
                row_indices, col_indices = py.copy(), px.copy()
            
            # Application of flips
            if args.mask_flip_y: row_indices = (mask_h - 1) - row_indices
            if args.mask_flip_x: col_indices = (mask_w - 1) - col_indices
            
            row_indices = np.clip(row_indices.astype(int), 0, mask_h - 1)
            col_indices = np.clip(col_indices.astype(int), 0, mask_w - 1)
            valid_mask = mask_data[row_indices, col_indices]
            print(f"Mask filtering active: {np.sum(valid_mask)}/{len(valid_mask)} points valid.")
    
    print(f"Calculating GIO (Sigma: {args.sigma})...")
    occupancy = calculate_gio(particles, grid_points, sigma=args.sigma)
    
    if valid_mask is not None:
        total_valid = np.sum(valid_mask)
        occupied_valid = np.sum((occupancy > 0.01) & valid_mask)
        coverage_pct = (occupied_valid / total_valid) * 100 if total_valid > 0 else 0
    else:
        total_voxels = len(occupancy)
        occupied_voxels = np.sum(occupancy > 0.01)
        coverage_pct = (occupied_voxels / total_voxels) * 100

    stats = {'coverage': coverage_pct, 'points': len(particles), 'max': occupancy.max(), 'min': occupancy.min()}
    print(f"\n--- Statistics ---\nSpatial Coverage %: {coverage_pct:.2f}%")
    
    print(f"\n--- Exporting Results ---")
    base_prefix = os.path.splitext(info['input_file'])[0]
    
    if args.vtr:
        vtk_file = export_to_vtk(f"{base_prefix}_occupancy", occupancy, grid_shape, grid_coords, valid_mask=valid_mask)
        print(f"VTK Map: {vtk_file}")
    
    png_file = get_unique_filename(f"{base_prefix}_heatmap", ".png")
    print(f"Heatmap: {png_file}")
    z_levels = [-45, -35, -25, -15, -5] if len(grid_shape) == 3 and not args.autorange else None
    generate_heatmaps(png_file, occupancy, grid_shape, grid_coords, info, z_levels=z_levels, valid_mask=valid_mask)
    
    if args.tif:
        tif_file = get_unique_filename(f"{base_prefix}_EQmap", ".tif")
        generate_tif(tif_file, occupancy, grid_shape)
        print(f"EQ TIF Map: {tif_file}")
    
    if args.html:
        html_file = get_unique_filename(f"{base_prefix}_report", ".html")
        print(f"Interactive Report: {html_file}")
        generate_html_report(html_file, occupancy, grid_shape, grid_coords, stats, info, valid_mask=valid_mask)
    
    print(f"\nAnalysis complete.")

if __name__ == "__main__":
    main()
