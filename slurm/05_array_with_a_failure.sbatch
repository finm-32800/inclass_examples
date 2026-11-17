#!/bin/bash
#SBATCH --job-name=05-array-fail
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --array=1-6
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%A_%a.out

# Step 5: task 3 fails. SLURM does not rerun it and does not remember it.
#
#   sbatch 05_array_with_a_failure.sbatch
#   sacct -j <job id> --format=JobID,State,ExitCode    # 3 is FAILED
#   touch fixed                                        # "fix the bug"
#   sbatch --array=3 05_array_with_a_failure.sbatch    # rerun only task 3
bash flaky_square.sh ${SLURM_ARRAY_TASK_ID}
