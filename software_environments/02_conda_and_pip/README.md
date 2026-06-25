# 02 Conda + Pip

Use conda for **just** the Python interpreter (isolation + Python version
control), then let `pip` install the project's packages from
`requirements.txt`. This is the hybrid workflow recommended in the course
textbook — and one many practitioners settle on.

## What You Learn

- Why you might split responsibilities: conda for the environment shell,
  pip for fast package installs
- That a blank conda env (just `python` + `pip`) keeps `environment.yml`
  tiny while `requirements.txt` carries the real dependency list
- Why keeping a `requirements.txt` is convenient (pip-only contributors,
  GitHub Actions)

## Setup

```bash
conda env create -f environment.yml
conda activate finm-env-conda-pip
pip install -r requirements.txt
```

## Run

```bash
python analyze.py
```

## Clean Up

```bash
conda deactivate
conda env remove --name finm-env-conda-pip
```

## Why This Pattern?

`conda` resolves a full environment (including the Python version and any
non-Python binaries) but can be slow. `pip` is fast at what it does. Using
a **blank** conda environment for isolation and `pip install -r
requirements.txt` for the packages gets you the best of both. The textbook
calls this out as the author's preferred approach.

You *can* inline the pip step inside `environment.yml` with a `- pip:`
block (commented out in that file), but a standalone `requirements.txt`
is friendlier to CI and pip-only users.

## Try It

- Move `matplotlib` from `requirements.txt` into the conda `dependencies:`
  and observe that both still work
- Run `pip freeze > requirements.txt` to see fully-pinned versions
