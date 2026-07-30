"""Minimal settings for the Databento in-class examples.

Mirrors the ``from settings import config`` pattern used across the course
repos, trimmed to what this example needs. ``DATABENTO_API_KEY`` is read from
the repo-root ``.env``; the output/data directories fall back to the repo-root
``_output``/``_data`` defaults (matching the master ``dodo.py``) so the
notebook runs without extra configuration.
"""

from pathlib import Path

from decouple import config as _config

_REPO_ROOT = Path(__file__).resolve().parents[1]

_DEFAULTS = {
    "OUTPUT_DIR": str(_REPO_ROOT / "_output"),
    "DATA_DIR": str(_REPO_ROOT / "_data"),
}


def config(key, default=None, **kwargs):
    """Look up a setting, supplying local defaults for the directory paths."""
    if default is None and key in _DEFAULTS:
        default = _DEFAULTS[key]
    if default is None:
        return _config(key, **kwargs)
    return _config(key, default=default, **kwargs)
