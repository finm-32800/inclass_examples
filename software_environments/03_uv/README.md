# 03 uv

[uv](https://docs.astral.sh/uv/) is a single, very fast Rust tool that
replaces `pip`, `venv`, `pip-tools`, and `pyenv`. One manifest
(`pyproject.toml`), one lockfile (`uv.lock`), one command to run.

## What You Learn

- That `uv run` bootstraps the *entire* environment automatically:
  downloads Python if needed, creates `.venv`, installs dependencies,
  then runs your script
- How dependencies live in a standard `pyproject.toml` `[project]` table
- That `uv.lock` pins exact versions for reproducibility

## Setup + Run (one step)

```bash
uv run analyze.py
```

The first run creates `.venv/` and `uv.lock`. Subsequent runs are instant.

Prefer an explicit two-step flow?

```bash
uv sync            # create/update the environment from pyproject.toml
uv run analyze.py  # run inside it
```

## Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

## Clean Up

```bash
rm -rf .venv uv.lock
```

## Handy Commands

| Command | Does |
|---------|------|
| `uv run analyze.py` | Sync env (if needed) and run the script |
| `uv sync` | Create/update `.venv` from `pyproject.toml` + lock |
| `uv add scipy` | Add a dependency (updates `pyproject.toml` + lock) |
| `uv lock` | Re-resolve and rewrite `uv.lock` |
| `uv run python` | Open the project's interpreter |

## Trade-offs

- **Pro:** Extremely fast, manages Python versions too, standards-based
  `pyproject.toml`, deterministic lockfile.
- **Con:** PyPI-only (no conda channels), so non-Python binaries that conda
  packages may not be available.

## Try It

- Run `uv add scipy` and watch `pyproject.toml` and `uv.lock` update
- Delete `.venv` and re-run — note how fast the rebuild is
