import numpy as np
from scipy.spatial import ConvexHull

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
