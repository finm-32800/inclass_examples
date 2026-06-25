"""Demo script showing paths work from the project root.

Run from the project root:
    python src/demo_script.py

The paths resolve correctly because settings.py anchors on __file__.
"""

from settings import config

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")

print("=" * 60)
print("settings.py Approach Demo")
print("=" * 60)
print()
print(f"Data directory:   {DATA_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Example paths:")
print(f"  DATA_DIR / 'raw' / 'prices.csv': {DATA_DIR / 'raw' / 'prices.csv'}")
print(f"  OUTPUT_DIR / 'charts' / 'fig.png': {OUTPUT_DIR / 'charts' / 'fig.png'}")
