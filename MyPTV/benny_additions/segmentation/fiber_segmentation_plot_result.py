"""
This script loads blob detection results from a specified CSV file and overlays them onto a single image frame.
It visualizes the detected blobs as red points, their bounding boxes as blue rectangles, and their
orientation as yellow arrows on the corresponding image. The script then displays the image with these overlays.

How to use:
1. Update the `blobs_file` variable with the path to your blob detection results CSV.
2. Set `images_dir` to the directory containing the image sequence.
3. Specify `image_ext` with the correct image file extension (e.g., ".tif", ".png").
4. Adjust `frame_id` to the 0-based index of the frame you wish to visualize.
5. Run the script to display the plot.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.io import imread

# --- your paths (make them absolute or run from the project root) ---
blobs_file = r"try_blobs_cam4_directions" #
images_dir = r"D:\20251202\processed\20251202\Rec5\Cam4"
image_ext  = ".tif"
frame_id = 11  # this is the index saved in the blobs file (0-based)

# --- load blobs file ---
cols = ["x", "y", "sx", "sy", "area", "frame", "dir_x", "dir_y"]
blobs = pd.read_csv(blobs_file, delim_whitespace=True, names=cols)

# select blobs for this frame
frame_blobs = blobs[blobs["frame"] == frame_id]

# --- resolve the actual image by INDEX, not by formatted number ---
image_files = sorted(glob.glob(os.path.join(images_dir, f"*{image_ext}")))
if not image_files:
    raise FileNotFoundError(f"No images with extension {image_ext} under {images_dir}")

if frame_id < 0 or frame_id >= len(image_files):
    raise IndexError(f"frame_id {frame_id} is out of range 0..{len(image_files)-1}")

path_to_image = image_files[frame_id]
img = imread(path_to_image)

# robust display range
lo = np.percentile(img, 1)
hi = np.percentile(img, 99)

plt.figure(figsize=(8, 8))
plt.imshow(img, cmap="gray", vmin=3, vmax=11)

# IMPORTANT: swap (x,y) -> (col,row) == (y,x) for plotting
# Optionally draw orientation arrows. If the arrow seems flipped vertically,
# change dy to -dy (see note below).
scale = 100.0  # arrow length scale in pixels

for _, row in frame_blobs.iterrows():
    row_y = float(row["x"])  # this is actually row index
    col_x = float(row["y"])  # this is actually column index

    dy = float(row["dir_x"]) * scale
    dx = float(row["dir_y"]) * scale   # if upside-down, set dy = -float(row["dir_y"]) * scale

    
    cx=row["sy"]
    cy=row["sx"]
    

    # plot point at (col,row)
    plt.plot(col_x, row_y, "ro", markersize=1)
    
    # plot box around blob
    rect = plt.Rectangle((col_x - cx/2, row_y - cy/2), cx, cy,
                         edgecolor='blue', facecolor='none', linewidth=3)
    plt.gca().add_patch(rect)

    # plot arrow from (col,row)
    plt.arrow(col_x, row_y, dx, dy, color="yellow",
              head_width=3, length_includes_head=True)

plt.title(f"Blobs overlay for frame {frame_id}\n{os.path.basename(path_to_image)}")
plt.axis("off")
plt.tight_layout()
plt.show()