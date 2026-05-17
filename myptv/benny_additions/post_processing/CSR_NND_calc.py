from scipy.spatial import KDTree
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def rand_data(n,x,y,z):


    # Generate random 3D particle positions
    np.random.rand()
    num_particles = n
    particles = np.random.rand(num_particles, 3)  # 3D coordinates (x, y, z)
    particles[:,0]*=x
    particles[:,1]*=y
    particles[:,2]*=z

    # Build KDTree
    kdtree = KDTree(particles)

    # Query for the nearest neighbor for each particle
    # k=2 because the closest point is the particle itself
    distances, indices = kdtree.query(particles, k=2)

    # Extract the nearest neighbor distances (skip the first which is distance to self)
    nearest_distances = distances[:, 1]
    nearest_indices = indices[:, 1]

    # Prepare the result dataframe
    # result_df = pd.DataFrame({
    #     'Particle_Index': range(num_particles),
    #     'Nearest_Neighbor_Index': nearest_indices,
    #     'Nearest_Neighbor_Distance': nearest_distances
    # })
    return nearest_distances

    # # Calculate PDF
    # kde = gaussian_kde(data)
    # x_vals = np.linspace(min(data), max(data), 1000)
    # pdf = kde(x_vals)

    # # Plot PDF
    # plt.plot(x_vals, pdf, label='PDF')
    # plt.fill_between(x_vals, pdf, alpha=0.3)
    # plt.title('PDF using SciPy gaussian_kde')
    # plt.xlabel('Nearest distances [mm]')
    # plt.ylabel('Density')
    # plt.legend()
    # plt.show()