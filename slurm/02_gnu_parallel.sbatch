#!/bin/bash
#SBATCH --job-name=02-gnu-parallel
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --cpus-per-task=6
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%j.out

# Step 2: one job with six cores on one machine. GNU Parallel starts the six
# tasks at the same time, one per core. About 5 seconds.
# Compute nodes lack the C.UTF-8 locale that a Mac often sends over SSH.
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
module load parallel

parallel -j ${SLURM_CPUS_PER_TASK} bash slow_square.sh {} ::: 1 2 3 4 5 6
