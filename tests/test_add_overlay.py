import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from myptv.segmentation_mod import particle_segmentation
from myptv.fibers.fiber_segmentation_mod import fiber_segmentation

# ponytail: simple check for add_overlay parameter in segmentation plot_blobs

def test_particle_plot_blobs_add_overlay():
    # 1. Create a dummy image with a few particle-like spots
    im = np.zeros((50, 50))
    im[10:13, 10:13] = 10
    im[30:33, 35:38] = 10
    
    # 2. Run particle segmentation
    ps = particle_segmentation(im, threshold=5, particle_size=3)
    ps.get_blobs()
    assert len(ps.blobs) > 0
    
    # Test with add_overlay=True (default)
    plt.close('all')
    ps.plot_blobs(add_overlay=True)
    fig = plt.gcf()
    ax = fig.gca()
    # errorbar adds lines/containers
    assert len(ax.lines) > 0
    
    # Test with add_overlay=False
    plt.close('all')
    ps.plot_blobs(add_overlay=False)
    fig = plt.gcf()
    ax = fig.gca()
    # when False, we only have the imshow image, no errorbar lines
    assert len(ax.lines) == 0


def test_fiber_plot_blobs_add_overlay():
    # 1. Create a dummy image
    im = np.zeros((50, 50))
    im[15:25, 15:25] = 10
    
    # 2. Run fiber segmentation
    fs = fiber_segmentation(im, threshold=5, particle_size=5)
    fs.get_blobs()
    assert len(fs.blobs) > 0
    
    # Test with add_overlay=True (default)
    plt.close('all')
    fs.plot_blobs(draw_fiber_features=True, add_overlay=True)
    fig = plt.gcf()
    ax = fig.gca()
    # It should have plotted circles (lines) or rectangle boxes (patches)
    assert len(ax.lines) > 0 or len(ax.patches) > 0
    
    # Test with add_overlay=False
    plt.close('all')
    fs.plot_blobs(draw_fiber_features=True, add_overlay=False)
    fig = plt.gcf()
    ax = fig.gca()
    # when False, there are no lines or patches drawn
    assert len(ax.lines) == 0
    assert len(ax.patches) == 0
