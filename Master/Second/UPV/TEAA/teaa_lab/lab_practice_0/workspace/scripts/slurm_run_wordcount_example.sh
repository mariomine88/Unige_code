#!/bin/bash
#SBATCH -p docencia
#SBATCH --gres=gpu:0
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --job-name=wordcount_example
#SBATCH --output=output_wordcount_example.out
#SBATCH --time=01:30:00

if [ $# -ne 2 ]
then
    echo "ERROR: incorrect number of command-line arguments!"
    exit 1
fi

n_files=$1
n_workers=$2

python python/wordcount.py --cluster-type local --n-workers ${n_workers} --num-files ${n_files} | grep "^WC" >wc_local_${n_files}_files_${n_workers}_workers.out
