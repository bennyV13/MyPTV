import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from skimage import draw, io

def load_blobs(fname):
    data = np.loadtxt(fname)
    return data[:, :2] # Columns 0=y, 1=x

def get_padded_hull(points, padding):
    if len(points) < 3:
        raise ValueError("Need at least 3 points for a convex hull.")
    hull = ConvexHull(points)
    vertices = points[hull.vertices]
    
    # Simple expansion: move each vertex along the bisector of its adjacent edges
    new_vertices = []
    n = len(vertices)
    for i in range(n):
        v_prev = vertices[(i - 1) % n]
        v_curr = vertices[i]
        v_next = vertices[(i + 1) % n]
        
        # Edge vectors
        e1 = v_curr - v_prev
        e2 = v_next - v_curr
        
        # Unit normal vectors (outward for CW in image coords: (dy, -dx))
        n1 = np.array([e1[1], -e1[0]]) / np.linalg.norm(e1)
        n2 = np.array([e2[1], -e2[0]]) / np.linalg.norm(e2)
        
        # Average normal (bisector)
        m_curr = (n1 + n2)
        m_curr /= np.linalg.norm(m_curr)
        
        # Scaling to maintain 'padding' distance from edges
        # cos(theta) = n1 . m_curr
        cos_theta = np.dot(n1, m_curr)
        
        # Move along bisector
        new_vertices.append(v_curr + m_curr * (padding / cos_theta))
        
    return np.array(new_vertices)

def generate_blob_polygon_mask(blob_file, resolution, padding, output_bit_depth, save_name):
    points = load_blobs(blob_file)
    padded_hull = get_padded_hull(points, padding)
    
    # Clip padded hull to resolution [width, height]
    # Note: resolution param is [width, height]
    padded_hull[:, 0] = np.clip(padded_hull[:, 0], 0, resolution[1]-1) # Y
    padded_hull[:, 1] = np.clip(padded_hull[:, 1], 0, resolution[0]-1) # X
    
    fig, ax = plt.subplots()
    ax.scatter(points[:, 1], points[:, 0], c='blue', label='Blobs', s=5)
    ax.plot(np.append(padded_hull[:, 1], padded_hull[0, 1]), 
            np.append(padded_hull[:, 0], padded_hull[0, 0]), 'r-', label='Padded Hull')
    ax.set_xlim(0, resolution[0])
    ax.set_ylim(resolution[1], 0) # Flip Y for image coords
    ax.legend()
    ax.set_title("Approve Polygon Mask? Close to save, Ctrl+C in terminal to abort.")
    plt.show()
    
    # Rasterize
    mask = np.zeros((resolution[1], resolution[0]), dtype=np.uint8 if output_bit_depth == 8 else np.uint16)
    rr, cc = draw.polygon(padded_hull[:, 0], padded_hull[:, 1], mask.shape)
    
    val = 255 if output_bit_depth == 8 else 65535
    mask[rr, cc] = val
    
    io.imsave(save_name, mask, check_contrast=False)
    print(f"Mask saved to {save_name}")
