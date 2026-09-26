#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --time=5:00
#SBATCH --partition=cna

export OMP_NUM_THREADS=8
mpiexec ./matrix_summa_blocked 4096