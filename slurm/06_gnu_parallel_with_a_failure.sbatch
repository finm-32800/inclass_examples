#!/bin/bash
#SBATCH --job-name=06-parallel-fail
#SBATCH --account=finm32800
#SBATCH --partition=caslake
#SBATCH --cpus-per-task=6
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=%x_%j.out

# Step 6: the same failure under GNU Parallel. The job log has one line per
# task with its exit code. Submitted a second time, --resume-failed reads the
# log and reruns only the tasks that failed.
#
#   sbatch 06_gnu_parallel_with_a_failure.sbatch
#   cat joblog.txt                                     # Exitval is 1 for task 3
#   touch fixed                                        # "fix the bug"
#   sbatch 06_gnu_parallel_with_a_failure.sbatch       # reruns only task 3
# Compute nodes lack the C.UTF-8 locale that a Mac often sends over SSH.
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
module load parallel

parallel -j ${SLURM_CPUS_PER_TASK} --joblog joblog.txt --resume-failed \
    bash flaky_square.sh {} ::: 1 2 3 4 5 6
