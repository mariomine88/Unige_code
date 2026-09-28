#!/bin/bash

# Launch in local via SLURM for a range of workers
for n_workers in 1 2 4 8 16 24 32 64
do
    for n_files in 10 100
    do
        sbatch  --cpus-per-task=${n_workers} \
                --output=output_wordcount_example_for_${n_files}_files_with_${n_workers}_workers.out \
                scripts/slurm_run_wordcount_example.sh ${n_files} ${n_workers}
    done
done

for n_workers in 32 64
do
    for n_files in 0
    do
        sbatch  --cpus-per-task=${n_workers} \
                --output=output_wordcount_example_for_${n_files}_files_with_${n_workers}_workers.out \
                scripts/slurm_run_wordcount_example.sh ${n_files} ${n_workers}
    done
done
