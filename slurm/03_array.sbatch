#!/bin/bash
#SBATCH --job-name=03-array
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --array=1-6
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%A_%a.out

# Step 3: a job array. SLURM runs this script six times, as six separate
# jobs, and tells each copy which one it is in SLURM_ARRAY_TASK_ID.
# %A in the output name is the array's job ID and %a is the task's number,
# so each task writes its own file.
bash slow_square.sh ${SLURM_ARRAY_TASK_ID}
