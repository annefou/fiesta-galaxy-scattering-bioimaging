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
# # 04 — Figures
#
# The headline result: the input microscopy texture, the random starting noise,
# and the scattering-transform synthesis that matches the target's multi-scale
# statistics — a new field of nuclei that was never in the data, generated only
# from the scattering coefficients.

# %%
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CLEAN, FIGS = Path("../data/clean"), Path("../figures")
FIGS.mkdir(parents=True, exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")

target = np.load(CLEAN / "target.npy")
start = np.load(CLEAN / "start.npy")
synth = np.load(CLEAN / "synthesis.npy")
res = json.load(open(CLEAN / "synthesis_results.json"))

# %%
vmin, vmax = float(target.min()), float(target.max())
fig, ax = plt.subplots(1, 3, figsize=(11, 4))
panels = [
    (target, "Input microscopy texture\n(dividing nuclei)"),
    (start, "Random start"),
    (synth, f"Scattering synthesis\n({res['scat_improvement_pct']:.0f}% coefficient match)"),
]
for a, (im, title) in zip(ax, panels):
    a.imshow(im, cmap="gray", vmin=vmin, vmax=vmax)
    a.set_title(title, fontsize=10)
    a.set_xticks([])
    a.set_yticks([])
fig.suptitle(
    "Bioimaging scattering-transform texture synthesis "
    f"(FOSCAT, image_2d, {res['size']}px, {res['nsteps']} steps)",
    fontsize=11,
)
fig.savefig(FIGS / "main_result.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"wrote figures/main_result.png — {res['scat_improvement_pct']:.1f}% scattering-coefficient match")
