"""Demo script showing paths work using chartbook.env.

Run from the project root:
    python src/demo_script.py

The paths resolve correctly because chartbook.env.get_project_root()
searches upward for marker files like .git, pyproject.toml, or .env.
"""

from settings import config

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")

print("=" * 60)
print("chartbook.env Approach Demo")
print("=" * 60)
print()
print(f"Data directory:   {DATA_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Example paths:")
print(f"  DATA_DIR / 'raw' / 'prices.csv': {DATA_DIR / 'raw' / 'prices.csv'}")
print(f"  OUTPUT_DIR / 'charts' / 'fig.png': {OUTPUT_DIR / 'charts' / 'fig.png'}")
