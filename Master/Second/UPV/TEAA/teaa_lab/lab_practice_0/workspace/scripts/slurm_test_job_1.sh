#!/bin/bash
#SBATCH -p docencia
#j#SBATCH --gres=gpu:0
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=test_job
#SBATCH --output=test_job_output_1.out
#SBATCH --time=00:01:00

echo "Hello, SLURM!"
date
sleep 10
date
echo "Bye! Bye!"
