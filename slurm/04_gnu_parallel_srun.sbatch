#!/bin/bash
#SBATCH --job-name=04-parallel-srun
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --ntasks=6
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%j.out

# Step 4: one job that asks for six slots, which SLURM may place on more than
# one machine. GNU Parallel decides which task runs next; `srun` places each
# one on a free slot of the job's allocation. Look at the host names in the
# output.
# Compute nodes lack the C.UTF-8 locale that a Mac often sends over SSH.
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
module load parallel

parallel -j ${SLURM_NTASKS} \
    srun --exclusive -N1 -n1 bash slow_square.sh {} ::: 1 2 3 4 5 6
