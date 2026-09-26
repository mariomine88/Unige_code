#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --time=5:00
#SBATCH --partition=cna

export OMP_NUM_THREADS=8

echo "=== n=1024 ==="
mpiexec ./matrix_summa_blocked   1024
mpiexec ./matrix_summa_simd_ref  1024
mpiexec ./matrix_summa_simd_own  1024

echo "=== n=2048 ==="
mpiexec ./matrix_summa_blocked   2048
mpiexec ./matrix_summa_simd_ref  2048
mpiexec ./matrix_summa_simd_own  2048

echo "=== n=4096 ==="
mpiexec ./matrix_summa_blocked   4096
mpiexec ./matrix_summa_simd_ref  4096
mpiexec ./matrix_summa_simd_own  4096