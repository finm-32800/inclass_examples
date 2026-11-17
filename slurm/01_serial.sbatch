#!/bin/bash
#SBATCH --job-name=01-serial
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%j.out

# Step 1: one job, one core, six tasks one after another. About 30 seconds.
for N in 1 2 3 4 5 6; do
    bash slow_square.sh ${N}
done
