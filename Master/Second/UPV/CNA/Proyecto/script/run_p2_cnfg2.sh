#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=16
#SBATCH --time=5:00
#SBATCH --partition=cna

export OMP_NUM_THREADS=16
mpiexec ./matrix_mpi_omp 4096