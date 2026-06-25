# 04 pixi

[pixi](https://pixi.sh/) gives you a uv-style workflow (one manifest, one
lockfile, automatic per-project environments) but resolves packages from
the **conda** ecosystem (`conda-forge`) — so you get conda's non-Python
binaries with modern speed and ergonomics. It can also pull from PyPI.

## What You Learn

- That pixi reads `pixi.toml`, builds a per-project environment under
  `.pixi/`, and writes `pixi.lock` automatically
- How `[tasks]` let you define named commands (`pixi run start`)
- That pixi uses conda channels, unlike uv (PyPI-only)

## Setup + Run (one step)

```bash
pixi run start
```

`start` is defined in `pixi.toml` as `python analyze.py`. On first run,
pixi resolves the environment, installs it under `.pixi/`, and writes
`pixi.lock`. You can also run arbitrary commands:

```bash
pixi run python analyze.py
pixi shell          # activate an interactive shell in the environment
```

## Install pixi

```bash
# macOS / Linux
curl -fsSL https://pixi.sh/install.sh | bash
```

## Clean Up

```bash
rm -rf .pixi pixi.lock
```

## Handy Commands

| Command | Does |
|---------|------|
| `pixi run start` | Run the `start` task (`python analyze.py`) |
| `pixi run <cmd>` | Run any command inside the environment |
| `pixi shell` | Activate an interactive shell |
| `pixi add scipy` | Add a conda dependency (updates manifest + lock) |
| `pixi add --pypi some-pkg` | Add a PyPI dependency |

## Trade-offs

- **Pro:** Conda packages (non-Python binaries) + fast resolution + a
  clean per-project workflow and lockfile. Cross-platform `platforms` list.
- **Con:** Newer tool; smaller ecosystem of examples than conda or pip.

## Try It

- Run `pixi add scipy` and watch `pixi.toml` and `pixi.lock` update
- Add a second task, e.g. `lint = "python -m compileall analyze.py"`, then
  `pixi run lint`
