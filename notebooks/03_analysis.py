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
# # 03 — Analysis: scattering-transform texture synthesis
#
# Starting from random noise, we synthesise a new image whose **scattering
# coefficients** match those of the microscopy target. This is the classic
# scattering-transform texture synthesis (Bruna & Mallat) — the model captures
# the non-Gaussian, multi-scale statistics of the texture and regenerates a new
# realisation with the same statistics.
#
# This notebook is the **local / same-algorithm path**. It uses exactly the
# FOSCAT calls (`foscat.scat_cov` with `use_2D=True` → `foscat.Synthesis`) that
# the Galaxy **`foscat-synthesis`** tool runs (`domain=image_2d`). On Galaxy the
# identical computation runs as a workflow on the `target.npy` produced by
# notebook 02; here it runs in-process so CI and the Jupyter Book build
# hermetically. The sibling FIESTA repositories apply the *same* tool to a
# HEALPix cosmological map (synthesis) and to SST fields (gap-filling).

# %%
import json
import os
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "4")

CLEAN = Path("../data/clean")

NORIENT, KERNELSZ, SEED = 4, 3, 1234
NSTEPS = 60 if os.environ.get("CI") else 120

# %% [markdown]
# ## Load the target and build a random start

# %%
target2d = np.load(CLEAN / "target.npy").astype(np.float32)
target = target2d.reshape(1, *target2d.shape)
rng = np.random.default_rng(SEED)
start = (rng.standard_normal(size=target.shape).astype(np.float32)
         * float(target.std()) + float(target.mean()))
print(f"target {target.shape}  mean {target.mean():.4f} std {target.std():.4f}")

# %% [markdown]
# ## FOSCAT scattering operator (2D) — same configuration as the Galaxy tool

# %%
import foscat.scat_cov as sc
import foscat.Synthesis as synthe

scat = sc.funct(NORIENT=NORIENT, KERNELSZ=KERNELSZ, all_type="float32",
                silent=True, use_2D=True)
print("FOSCAT device:", scat.backend.device)

ref, sref = scat.eval(target, calc_var=True)


def the_loss(x, scat_operator, args):
    ref_a, _mask, sref_a = args[0], args[1], args[2]
    learn = scat_operator.eval(x)
    diff = (ref_a - learn) / sref_a
    return scat_operator.reduce_mean(scat_operator.square(diff))


loss = synthe.Loss(the_loss, scat, ref, None, sref)
sy = synthe.Synthesis([loss])

# %% [markdown]
# ## Run the synthesis

# %%
print(f"running synthesis: {NSTEPS} L-BFGS steps...")
t0 = time.time()
omap = sy.run(scat.backend.bk_cast(start),
              EVAL_FREQUENCY=max(NSTEPS // 10, 1), NUM_EPOCHS=NSTEPS, do_lbfgs=True)
omap_np = np.array(omap) if not hasattr(omap, "numpy") else omap.numpy()
elapsed = time.time() - t0
np.save(CLEAN / "synthesis.npy", omap_np.reshape(target2d.shape))
np.save(CLEAN / "start.npy", start.reshape(target2d.shape))

# %% [markdown]
# ## Validation — how close are the scattering coefficients?

# %%
ref_s1 = scat.backend.to_numpy(ref.S1)
out_s1 = scat.backend.to_numpy(scat.eval(omap_np).S1)
start_s1 = scat.backend.to_numpy(scat.eval(start).S1)
err_start = float(np.mean((ref_s1 - start_s1) ** 2))
err_out = float(np.mean((ref_s1 - out_s1) ** 2))
improvement = (1.0 - err_out / err_start) * 100.0 if err_start > 0 else 0.0

results = {
    "domain": "image_2d", "size": int(target2d.shape[0]),
    "norient": NORIENT, "kernelsz": KERNELSZ, "nsteps": NSTEPS,
    "device": str(scat.backend.device), "elapsed_s": round(elapsed, 2),
    "scat_err_start": err_start, "scat_err_synth": err_out,
    "scat_improvement_pct": round(improvement, 2),
    "target_mean": float(target.mean()), "target_std": float(target.std()),
    "synth_mean": float(omap_np.mean()), "synth_std": float(omap_np.std()),
}
with open(CLEAN / "synthesis_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"synthesis done in {elapsed:.1f}s | scattering-coefficient error "
      f"{err_start:.4f} -> {err_out:.4f}  ({improvement:.1f}% closer to the target)")
