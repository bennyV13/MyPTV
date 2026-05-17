"""
This script provides a function to overlay blob detection results onto a sequence of images and save the visualizations.
For each frame with detected blobs, it loads the corresponding image, draws the blobs (bounding boxes and orientation arrows),
and saves the resulting figure to a specified output directory.

How to use:
1. Call the `plot_and_save_blobs` function with the appropriate parameters.
2. `blobs_file`: Path to the CSV file containing blob detection results.
3. `images_dir`: Directory where the original image sequence is located.
4. `output_dir`: Directory where the generated overlay plots will be saved.
5. `image_ext`: (Optional) The extension of the image files (default is ".tif").
6. `scale`: (Optional) Scaling factor for the orientation arrows (default is 100.0).
7. An example call is provided within the `if __name__ == "__main__":` block.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.io import imread

def plot_and_save_blobs(blobs_file, images_dir, output_dir, image_ext=".tif", scale=100.0):
    """
    Overlay blob results (bounding boxes + orientation arrows) on images,
    save one figure per frame into output_dir.
    
    Parameters
    ----------
    blobs_file : str
        Path to blobs results file.
    images_dir : str
        Directory with image sequence.
    output_dir : str
        Directory to save the overlay figures.
    image_ext : str
        Image file extension (default: .tif).
    scale : float
        Arrow length scale in pixels.
    """
    # make sure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    # load blobs file
    cols = ["x", "y", "sx", "sy", "area", "frame", "dir_x", "dir_y"]
    blobs = pd.read_csv(blobs_file, delim_whitespace=True, names=cols)

    # get list of images sorted by name
    image_files = sorted(glob.glob(os.path.join(images_dir, f"*{image_ext}")))
    if not image_files:
        raise FileNotFoundError(f"No images with extension {image_ext} under {images_dir}")

    # loop through frames present in blobs file
    for frame_id in sorted(blobs["frame"].unique()):
        frame_blobs = blobs[blobs["frame"] == frame_id]

        if frame_id < 0 or frame_id >= len(image_files):
            print(f"⚠️ Skipping frame {frame_id}, no matching image")
            continue

        path_to_image = image_files[frame_id]
        img = imread(path_to_image)

        # robust display range (optional)
        lo = np.percentile(img, 1)
        hi = np.percentile(img, 99)

        plt.figure(figsize=(8, 8))
        plt.imshow(img, cmap="gray", vmin=lo, vmax=10)

        # plot all blobs in this frame
        for _, row in frame_blobs.iterrows():
            row_y = float(row["x"])  # actually row index
            col_x = float(row["y"])  # actually col index

            # convert direction properly
            dy = float(row["dir_x"]) * scale
            dx = float(row["dir_y"]) * scale

            cx = row["sy"]  # width
            cy = row["sx"]  # height

            # draw point
            plt.plot(col_x, row_y, "ro", markersize=1)

            # draw bounding box
            rect = plt.Rectangle((col_x - cx/2, row_y - cy/2), cx, cy,
                                 edgecolor="blue", facecolor="none", linewidth=1)
            plt.gca().add_patch(rect)

            # draw arrow
            plt.arrow(col_x, row_y, dx, dy, color="yellow",
                      head_width=3, length_includes_head=True)

        plt.title(f"Blobs overlay for frame {frame_id}\n{os.path.basename(path_to_image)}")
        plt.axis("off")
        plt.tight_layout()

        # save and close
        save_path = os.path.join(output_dir, f"frame_{frame_id:04d}.png")
        plt.savefig(save_path, dpi=150)
        plt.close()

        print(f"✅ Saved {save_path}")

if __name__ == "__main__":
    plot_and_save_blobs(
    blobs_file=r"try_blobs_cam4_directions",
    images_dir=r"D:\20251202\processed\20251202\Rec5\cam4",
    output_dir=r"D:/20251202/seg_results/20251202/Rec5/Cam4_overlays",
    image_ext=".tif",
    scale=100
)
