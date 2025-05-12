import dask.array as da
import imageio.v3 as iio
import matplotlib.pyplot as plt
import napari
import numpy as np
import os

import pandas as pd
import re
from aicsimageio import AICSImage
from pathlib import Path
from skimage import io, measure, morphology
from skimage.filters import threshold_otsu, threshold_li, threshold_local
from skimage.morphology import white_tophat, disk, square
from skimage import io, img_as_ubyte
print("#########################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 1")

# Input and output directories
fl_dir = Path("fl")
labels_dir = Path("largest_label")
output_dir = Path("measurement_output")

if not os.path.exists(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    
mask_fish = None
image_fl = None
mask_sack_li = None
mask_sack_otsu = None
mask_measure_li = None
mask_measure_otsu = None
print("#########################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 2")
rows = []
thrs = []
fracs = []
reg = r'fl.([A-Z,a-z]*)-'
# Process each label image
max_h = 0
max_w = 0
for file_fl in fl_dir.glob("*.tif"):
    image_fl = io.imread(file_fl)
    max_h = max(max_h, image_fl.shape[0])
    max_w = max(max_w, image_fl.shape[1])
print((max_h, max_w))
    
print("#########################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 3")


