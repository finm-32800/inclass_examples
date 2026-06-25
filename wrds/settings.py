"""Minimal settings for the WRDS in-class example.

Mirrors the ``from settings import config`` pattern used across the course
repos, trimmed to what this example needs. ``WRDS_USERNAME`` is read from the
repo-root ``.env``; the output/data directories fall back to local defaults so
the notebook runs without extra configuration.
"""

from pathlib import Path

from decouple import config as _config

_HERE = Path(__file__).resolve().parent

_DEFAULTS = {
    "OUTPUT_DIR": str(_HERE / "_output"),
    "DATA_DIR": str(_HERE / "_data"),
}


def config(key, default=None, **kwargs):
    """Look up a setting, supplying local defaults for the directory paths."""
    if default is None and key in _DEFAULTS:
        default = _DEFAULTS[key]
    if default is None:
        return _config(key, **kwargs)
    return _config(key, default=default, **kwargs)
