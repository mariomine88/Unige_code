#!/bin/bash

# Launch in local via SLURM for a range of workers
for n_workers in 1 2 4 8 16 24 32 64
do
    sbatch  --cpus-per-task=${n_workers} \
            --output=output_pi_example_with_${n_workers}_workers.out \
            scripts/slurm_run_pi_example.sh ${n_workers}
done
