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
# # 02 — Data clean
#
# Turns the raw microscopy image into the **2D target array** that the
# scattering-transform synthesis ingests — the exact same `.npy` interface the
# Galaxy `foscat-synthesis` tool expects (`domain=image_2d`, a single 2D
# `float32` array).
#
# Steps: load the grayscale field of nuclei, resize to a square `SIZE x SIZE`
# texture (keeping the whole field), and cast to `float32`. We deliberately
# keep the natural intensity texture (bright nuclei on a dark background) — that
# is the non-Gaussian structure the scattering transform captures and
# regenerates.

# %%
import os
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from skimage import img_as_float, transform

RAW, CLEAN = Path("../data/raw"), Path("../data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)

# Smaller field in CI keeps the hermetic synthesis fast; full size locally.
SIZE = 128 if os.environ.get("CI") else 256

# %%
img = img_as_float(iio.imread(RAW / "microscopy.png").astype(np.float32))
if img.ndim == 3:
    img = img.mean(axis=2)
target = transform.resize(img, (SIZE, SIZE), anti_aliasing=True).astype(np.float32)

np.save(CLEAN / "target.npy", target)
iio.imwrite(CLEAN / "target_preview.png",
            (255 * (target - target.min()) / (np.ptp(target) + 1e-9)).astype(np.uint8))

print(f"wrote data/clean/target.npy — shape {target.shape}, "
      f"range [{target.min():.4f}, {target.max():.4f}], "
      f"mean {target.mean():.4f}, std {target.std():.4f}")
