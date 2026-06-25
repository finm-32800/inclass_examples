"""Demo script showing paths work from anywhere.

Run this script from any directory and the paths will resolve correctly:
    python src/demo_script.py
    cd src && python demo_script.py
    cd _data && python ../src/demo_script.py

All produce the same output because paths are anchored on the installed package.
"""

from myproj import project_root, data_dir, data_path, output_dir, output_path

print("=" * 60)
print("Package-Anchored Paths Demo")
print("=" * 60)
print()
print(f"Project root:    {project_root()}")
print(f"Data directory:  {data_dir()}")
print(f"Output directory:{output_dir()}")
print()
print("Example paths:")
print(f"  data_path('raw', 'prices.csv'): {data_path('raw', 'prices.csv')}")
print(f"  output_path('charts', 'fig.png'): {output_path('charts', 'fig.png')}")
print()
print("These paths work regardless of your current working directory!")
