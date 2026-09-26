#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=5:00
#SBATCH --partition=cna

export OMP_NUM_THREADS=32
mpiexec ./matrix_mpi_omp 4096