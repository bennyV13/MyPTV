#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 2026

@author: Antigravity

Image Multiplication Script:
This script loads a TIFF or RAW image, multiplies its pixel values by a factor (default 2.0),
and saves the result at the original location with 'x2' at the end of the name.
It integrates with existing image loading functions from the MyPTV package.
"""

import os
import sys
import argparse
import numpy as np
from skimage import io

# Attempt to import MyPTV functions using jcodemunch context
try:
    from myptv.segmentation_mod import get_imread_func
except ImportError:
    # Fallback to local definition if MyPTV is not in python path
    def get_imread_func(raw_format=False):
        if not raw_format:
            return lambda x: io.imread(x)
        else:
            def read_raw(x):
                import rawpy
                with rawpy.imread(x) as raw:
                    return raw.raw_image.copy()
            return read_raw


def multiply_image(image_path, factor=2.0, output_path=None, force_raw=False):
    """
    Loads an image, multiplies its pixel values by `factor`,
    and saves the output.
    """
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Determine file extension and whether it's a RAW image
    base, ext = os.path.splitext(image_path)
    raw_extensions = {'.dng', '.nef', '.cr2', '.cr3', '.arw', '.raw', '.pef', '.orf', '.raf'}
    is_raw = force_raw or (ext.lower() in raw_extensions)

    print(f"Loading image: {image_path} (Format: {'RAW' if is_raw else 'TIFF/Standard'})")
    
    # Use existing MyPTV function to read the image
    try:
        imread_func = get_imread_func(raw_format=is_raw)
        img_data = imread_func(image_path)
    except Exception as e:
        print(f"Error reading image: {e}", file=sys.stderr)
        sys.exit(1)

    original_dtype = img_data.dtype
    print(f"Original image shape: {img_data.shape}, dtype: {original_dtype}")

    # Perform multiplication with datatype boundaries safety to prevent overflow
    if np.issubdtype(original_dtype, np.integer):
        info = np.iinfo(original_dtype)
        min_val, max_val = info.min, info.max
        # Convert to float64 to perform multiplication safely
        multiplied = img_data.astype(np.float64) * factor
        # Clip to the original datatype bounds and cast back
        processed_img = np.clip(multiplied, min_val, max_val).astype(original_dtype)
    else:
        # Floating point datatype
        processed_img = img_data * factor

    # Determine default output path if not specified
    if not output_path:
        output_path = f"{base}x2{ext}"

    print(f"Saving multiplied image to: {output_path}")

    # Save the processed image using scikit-image's imsave
    try:
        # skimage.io.imsave is also used in MyPTV to save TIFF/processed images
        io.imsave(output_path, processed_img, check_contrast=False)
        print("Success!")
    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Multiply image values and save at the original location with 'x2' appended to the filename."
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the input image file (TIFF or RAW)."
    )
    parser.add_argument(
        "-f", "--factor",
        type=float,
        default=2.0,
        help="Multiplication factor (default: 2.0)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom output file path. Defaults to input path with 'x2' appended."
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Force loading the image as RAW format."
    )
    
    args = parser.parse_args()
    multiply_image(
        image_path=args.image_path,
        factor=args.factor,
        output_path=args.output,
        force_raw=args.raw
    )
