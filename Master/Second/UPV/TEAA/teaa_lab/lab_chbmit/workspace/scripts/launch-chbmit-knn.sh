#!/bin/bash -eu

mkdir -p logs results models

if [ -z ${USER} ]
then
    USER=$(logname)
fi

##############################################################################################
#
# Students have to modify the following environment variables in order to run experiments
# using different configurations.
#
#patient_list="03 07 08 10 12 13 15 16 22 24"
patient_list="03"
#patient_list="ALL"
#kmeans_codebook_sizes="100 200 300 500 700 1000 2000 0"
kmeans_codebook_sizes="100 0"
list_of_K="3 5 7 11 13"
#list_of_K="5"
#format_list="pca136 21x14"
format_list="pca136" # format exclusive to work with single patients
#format_list="pca141" # format exclusive for all patients
#format_list="21x14" # format valid for both configurations of patients
##############################################################################################


for patient in ${patient_list}
do
    if [ "${patient}" != "ALL" ]
    then
        patient="chb${patient}"
    fi

    for format in ${format_list}
    do
        for cb_size in ${kmeans_codebook_sizes}
        do
            for K in ${list_of_K}
            do
                for n_workers in 8
                do
                    sbatch \
                        --cpus-per-task=${n_workers} \
                        --output=logs/output_chbmit_knn_based_classifier_${patient}_${format}_${cb_size}_${K}_${n_workers}.out \
                        ./scripts/slurm_run_chbmit_knn.sh --patient ${patient} --format ${format} --cb_size ${cb_size} --K ${K} --n_workers ${n_workers}
                done
            done
        done
    done
done
