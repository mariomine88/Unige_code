#!/bin/bash
#SBATCH -p docencia
#SBATCH --gres=gpu:0
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --job-name=pi_example
#SBATCH --output=output_pi_example.out
#SBATCH --time=00:30:00

#scripts/run_pi_example.sh 

n_workers=$1

python python/pi.py --cluster-type local --n-workers ${n_workers} --n-tasks 128 --samples-per-task 1000000 
