import os
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from skimage import draw, io, measure

def load_blobs(fname):
    '''
    Loads blob coordinates from a text file.
    Supports both 2-column (x, y) and multi-column (x, y, ...) files.
    Always returns the first two columns, assuming they are the image coordinates.
    '''
    try:
        data = np.loadtxt(fname)
    except Exception as e:
        print(f"Error loading file {fname}: {e}")
        raise
        
    if data.ndim == 1:
        data = data.reshape(1, -1)
        
    return data[:, :2] # Columns 0=x, 1=y

def get_padded_hull(vertices, padding):
    '''
    Given a set of vertices in order, returns a new set of vertices
    expanded outward by 'padding' distance.
    '''
    new_vertices = []
    n = len(vertices)
    for i in range(n):
        v_prev = vertices[(i - 1) % n]
        v_curr = vertices[i]
        v_next = vertices[(i + 1) % n]
        
        # Edge vectors
        e1 = v_curr - v_prev
        e2 = v_next - v_curr
        
        # Unit normal vectors (outward for CW in image coords: [dx, -dy])
        # Note: v[0] is x, v[1] is y. So e[0] is dx, e[1] is dy.
        # Normal to e1: [e1[1], -e1[0]] -> [dy, -dx]
        n1 = np.array([e1[1], -e1[0]]) / (np.linalg.norm(e1) + 1e-10)
        n2 = np.array([e2[1], -e2[0]]) / (np.linalg.norm(e2) + 1e-10)
        
        # Average normal (bisector)
        m_curr = (n1 + n2)
        norm_m = np.linalg.norm(m_curr)
        if norm_m < 1e-10:
            # Parallel edges - use normal of either edge
            m_curr = n1
        else:
            m_curr /= norm_m
        
        # Scaling to maintain 'padding' distance from edges
        # cos(theta) is the projection of the bisector onto the normal
        cos_theta = np.dot(n1, m_curr)
        
        # Move along bisector
        new_vertices.append(v_curr + m_curr * (padding / (max(cos_theta, 1e-10))))
        
    return np.array(new_vertices)

def alpha_shape(points, alpha):
    '''
    Compute the alpha shape (concave hull) of a set of points.
    'alpha' is the influence radius. Smaller alpha = tighter fit.
    '''
    if len(points) < 4:
        # Need at least 4 points for a concave hull to be different from convex
        hull = ConvexHull(points)
        return points[hull.vertices]
    
    from scipy.spatial import Delaunay
    tri = Delaunay(points)
    edges = set()
    
    # Loop over triangles
    for ia, ib, ic in tri.simplices:
        pa = points[ia]
        pb = points[ib]
        pc = points[ic]
        
        # Side lengths
        a = np.linalg.norm(pa - pb)
        b = np.linalg.norm(pb - pc)
        c = np.linalg.norm(pc - pa)
        
        # Area (Heron's formula)
        s = (a + b + c) / 2.0
        area = np.sqrt(max(0, s * (s - a) * (s - b) * (s - c)))
        
        # Circumradius
        if area > 0:
            r = a * b * c / (4.0 * area)
            if r < alpha:
                for i, j in [(ia, ib), (ib, ic), (ic, ia)]:
                    if (j, i) in edges:
                        edges.remove((j, i))
                    else:
                        edges.add((i, j))
        
    if not edges:
        hull = ConvexHull(points)
        return points[hull.vertices]
        
    # Order the edges into a polygon
    import networkx as nx
    G = nx.Graph()
    G.add_edges_from(edges)
    
    # Take the largest connected component
    if not nx.is_connected(G):
        main_nodes = max(nx.connected_components(G), key=len)
        G = G.subgraph(main_nodes).copy()
        
    # Find the cycle
    try:
        path = nx.find_cycle(G)
        vertices = [points[u] for u, v in path]
        return np.array(vertices)
    except:
        hull = ConvexHull(points)
        return points[hull.vertices]

def generate_blob_polygon_mask(blob_file, reference_image, padding, output_bit_depth, save_name, max_sides=None, alpha=None):
    points = load_blobs(blob_file)
    
    # Load reference image to get resolution
    ref_im = io.imread(reference_image)
    resolution = [ref_im.shape[1], ref_im.shape[0]] # [width, height]
    print(f"Image resolution: {resolution}")
    
    # Get initial hull (Convex or Alpha)
    if alpha is not None:
        print(f"Computing alpha shape with alpha={alpha}")
        vertices = alpha_shape(points, float(alpha))
    else:
        print("Computing convex hull")
        hull = ConvexHull(points)
        vertices = points[hull.vertices]
    print(f"Initial vertices count: {len(vertices)}")
    
    # Optional: Simplify the hull to a maximum number of sides
    if max_sides is not None and len(vertices) > max_sides:
        # Iteratively increase tolerance until we reach target side count
        tol = 1.0
        simplified = vertices
        # approximate_polygon needs a closed loop
        vertices_closed = np.append(vertices, [vertices[0]], axis=0)
        
        while len(simplified) > max_sides and tol < 500:
            simplified = measure.approximate_polygon(vertices_closed, tolerance=tol)[:-1]
            tol *= 1.2
        vertices = simplified
    
    padded_hull = get_padded_hull(vertices, padding)
    
    # Clip padded hull to resolution [width, height]
    # Note: resolution is [width, height], so resolution[0] is X_max, resolution[1] is Y_max
    # padded_hull[:, 0] is X, padded_hull[:, 1] is Y
    padded_hull[:, 0] = np.clip(padded_hull[:, 0], 0, resolution[0]-1) # X
    padded_hull[:, 1] = np.clip(padded_hull[:, 1], 0, resolution[1]-1) # Y
    
    fig, ax = plt.subplots()
    if len(ref_im.shape) == 2:
        ax.imshow(ref_im, cmap='gray')
    else:
        ax.imshow(ref_im)
        
    ax.scatter(points[:, 0], points[:, 1], c='blue', label='Blobs', s=5, alpha=0.5)
    
    # Plot the polygon line
    poly_line = np.append(padded_hull, [padded_hull[0]], axis=0)
    ax.plot(poly_line[:, 0], poly_line[:, 1], 'r-', lw=2, label='Padded Hull')
    
    # Red dots at the vertices to show the "sides" clearly
    ax.scatter(padded_hull[:, 0], padded_hull[:, 1], c='red', s=40, edgecolors='white', label='Vertices', zorder=5)
    
    ax.set_xlim(0, resolution[0])
    ax.set_ylim(resolution[1], 0) # Flip Y for image coords
    ax.legend(loc='center')
    ax.set_title(f"Sides: {len(padded_hull)} | Padding: {padding}px\nClose to save, Ctrl+C to abort.")
    plt.show()

    # Rasterize
    mask = np.zeros((resolution[1], resolution[0]), dtype=np.uint8 if output_bit_depth == 8 else np.uint16)
    # draw.polygon expects (r, c) which is (Y, X)
    rr, cc = draw.polygon(padded_hull[:, 1], padded_hull[:, 0], mask.shape)
    
    val = 255 if output_bit_depth == 8 else 65535
    mask[rr, cc] = val
    
    # Ensure directory exists
    dir_name = os.path.dirname(save_name)
    if dir_name != '' and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    io.imsave(save_name, mask, check_contrast=False)
    print(f"Mask saved to {save_name} with {len(padded_hull)} sides.")
    
    # Save vertices to a text file
    vertices_save_name = os.path.splitext(save_name)[0] + "_vertices.txt"
    np.savetxt(vertices_save_name, padded_hull, fmt='%.3f', header='x\ty')
    print(f"Vertices saved to {vertices_save_name}")
