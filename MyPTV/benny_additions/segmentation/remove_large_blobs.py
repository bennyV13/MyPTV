import os
import matplotlib.pyplot as plt

"""
   1. center_x (float): The X-coordinate (horizontal) of the particle centroid in pixels.
   2. center_y (float): The Y-coordinate (vertical) of the particle centroid in pixels.
   3. size_x (int): The width of the particle's bounding box in pixels.
   4. size_y (int): The height of the particle's bounding box in pixels.
   5. area/mass (int): The total integrated intensity (brightness) of the detected particle.
   6. frame_number (int): The index of the frame where the particle was found.
"""

def plot_blob_size_histogram(blob_file, column_index=2):
    """
    Plots a histogram of blob sizes from a MyPTV blobs file.
    """
    if not os.path.exists(blob_file):
        print(f"Error: File {os.path.abspath(blob_file)} not found.")
        return

    sizes = []
    # Iterate through the file line by line to handle large files efficiently
    with open(blob_file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) > column_index:
                try:
                    # Extract the size value from the specified column
                    val = float(parts[column_index])
                    sizes.append(val)
                except ValueError:
                    # Skip lines that don't have a valid number in the size column
                    continue

    print(f"Read {len(sizes)} blobs from {blob_file}.")
    if sizes:
        max_size = max(sizes)
        min_size = min(sizes)
        print(f"Min size: {min_size:.2f}, Max size: {max_size:.2f}")

        # Create the histogram
        plt.figure(figsize=(10, 6))
        plt.hist(sizes, bins=100, color='skyblue', edgecolor='black', alpha=0.7)
        
        plt.title(f'Histogram of Blob Sizes (Column {column_index})\n{blob_file}')
        plt.xlabel('Size')
        plt.ylabel('Frequency')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Explicitly set the x-axis range to ensure it covers 0 to max
        plt.xlim(left=0, right=max_size)
        
        plt.show()
    else:
        print("No valid size data found to plot.")

if __name__ == "__main__":
    # --- Configuration ---
    # Note: The notebook is in Data_Analysis/MyPTV_analysis/20260506_analysis/
    # Use relative paths from that directory.
    blob_file = 'ptv_results/Rec26_data/particles_all/blobs_Cam1'
    column_index = 2  # Index 2 is height, 3 is width in typical MyPTV blobs files
    plot_blob_size_histogram(blob_file, column_index)