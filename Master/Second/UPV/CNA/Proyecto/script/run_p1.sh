#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=1
#SBATCH --time=5:00
#SBATCH --partition=cna

mpiexec ./1_matrix_mpi 2048