# Snakefile — orchestrates the bioimaging scattering-transform pipeline.
#
# One rule per pipeline stage; each rule wraps a jupytext notebook (the
# notebook stays the source of truth, the Snakefile just sequences them).
#
# Usage:
#   snakemake --cores 1                  # run everything
#   snakemake --cores 1 -n               # dry run

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


rule all:
    input:
        f"{FIGURES}/main_result.png",


# ---------- 01: Data download ----------
# Self-contained: the microscopy image is downloaded by the notebook, never
# assumed to exist locally. See CLAUDE.md § Self-contained data.
rule data_download:
    output:
        f"{DATA}/raw/microscopy.png",
        f"{DATA}/raw/sources.json",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 01_data_download.py 2>&1 | tee ../{{log}}"


# ---------- 02: Data clean ----------
rule data_clean:
    input:
        f"{DATA}/raw/microscopy.png",
    output:
        f"{DATA}/clean/target.npy",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 02_data_clean.py"


# ---------- 03: Analysis (scattering synthesis) ----------
rule analysis:
    input:
        f"{DATA}/clean/target.npy",
    output:
        f"{DATA}/clean/synthesis.npy",
        f"{DATA}/clean/synthesis_results.json",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 03_analysis.py"


# ---------- 04: Figures ----------
rule figures:
    input:
        f"{DATA}/clean/synthesis.npy",
    output:
        f"{FIGURES}/main_result.png",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 04_figures.py"
