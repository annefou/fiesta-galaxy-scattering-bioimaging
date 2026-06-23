# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 01 — Data download
#
# Fetches the input image for the bioimaging scattering-transform texture
# synthesis: a **public-domain fluorescence-microscopy field of dividing cell
# nuclei** (the `human_mitosis` sample distributed with scikit-image, sourced
# from the Broad Bioimage Benchmark Collection). It is a textured field of
# bright nuclei on a dark background — the bioimaging analogue of the
# astrophysical and Earth-observation fields the same FOSCAT scattering
# transform is applied to in the sibling FIESTA repositories.
#
# **Self-contained:** the repo ships without input data; this notebook is the
# only path that brings data into `data/raw/`. scikit-image downloads the image
# from its pinned data registry (a fixed content hash) via `pooch`, so the
# fetch is reproducible.

# %%
import json
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from skimage import data

RAW = Path("../data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Download the microscopy image

# %%
# Public-domain (BBBC) fluorescence microscopy of dividing nuclei, 512x512.
img = np.asarray(data.human_mitosis(), dtype=np.uint8)
iio.imwrite(RAW / "microscopy.png", img)
print(f"wrote data/raw/microscopy.png — shape {img.shape}, dtype {img.dtype}, "
      f"range [{img.min()}, {img.max()}]")

# %% [markdown]
# ## Record the data source

# %%
sources = {
    "microscopy.png": {
        "title": "human_mitosis — fluorescence microscopy of dividing nuclei",
        "source": "scikit-image sample data (data.human_mitosis)",
        "origin": "Broad Bioimage Benchmark Collection (BBBC)",
        "license": "public domain",
        "url": "https://scikit-image.org/docs/stable/api/skimage.data.html#skimage.data.human_mitosis",
        "shape": list(img.shape),
    }
}
with open(RAW / "sources.json", "w") as f:
    json.dump(sources, f, indent=2)
print("wrote data/raw/sources.json")
