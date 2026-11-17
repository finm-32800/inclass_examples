# SLURM: parallel jobs in six small steps

Tiny batch jobs for Midway3 that show two ways to run independent tasks at
the same time: GNU Parallel inside one job, and a SLURM job array. Each
runs in under a minute. The textbook page that walks through them is
[Parallel Jobs on a Cluster](https://finm-32800.github.io/Week8/parallel_jobs_on_a_cluster.html).

The "work" is `slow_square.sh`, which sleeps five seconds, squares a number,
and prints the machine it ran on.

| Script | What it shows |
|---|---|
| `01_serial.sbatch` | Six tasks one after another on one core: 30 seconds |
| `02_gnu_parallel.sbatch` | One job with six cores; GNU Parallel runs the six at once: 5 seconds |
| `03_array.sbatch` | A job array: six separate jobs, one per task |
| `04_gnu_parallel_srun.sbatch` | One job with six slots, possibly on several machines; `srun` places each task |
| `05_array_with_a_failure.sbatch` | Task 3 fails; rerun only it with `sbatch --array=3` |
| `06_gnu_parallel_with_a_failure.sbatch` | Task 3 fails; the job log and `--resume-failed` rerun only it |

## Run them

On Midway3:

```bash
git clone https://github.com/finm-32800/inclass_examples.git
cd inclass_examples/slurm

sbatch 01_serial.sbatch
squeue --me                 # watch it
cat 01-serial_*.out         # when it is done
```

After any of them:

```bash
sacct -X -j <job id> --format=JobID%16,JobName%18,State,Elapsed,NodeList,ExitCode
```

## The two failure examples

```bash
sbatch 05_array_with_a_failure.sbatch
sacct -X -j <job id> --format=JobID%16,State,ExitCode    # task 3 is FAILED
touch fixed                                              # "fix the bug"
sbatch --array=3 05_array_with_a_failure.sbatch          # rerun only task 3
rm fixed
```

```bash
sbatch 06_gnu_parallel_with_a_failure.sbatch
cat joblog.txt                                           # Exitval is 1 for task 3
touch fixed
sbatch 06_gnu_parallel_with_a_failure.sbatch             # reruns only task 3
rm fixed joblog.txt
```

## GNU Parallel at the prompt

```bash
module load parallel
parallel echo "Hello, {}" ::: Alice Bob Carol
parallel --dry-run -j 2 python clean_month.py {} ::: 2020-02 2020-03 2020-04
parallel echo {1} and {2} ::: a b ::: 1 2
```

The real version of all this, on corporate bond data, is in the `slurm`
folder of
[case_study_clean_trace](https://github.com/finm-32800/case_study_clean_trace).
