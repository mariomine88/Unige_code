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
#patient_list="03"
patient_list="ALL"
#gmm_components_list="10 20 30 50 70 100"
gmm_components_list="10"
#format_list="pca136 21x14"
#format_list="pca136" # format exclusive to work with single patients
format_list="pca141" # format exclusive for all patients
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
        for gmm_components in ${gmm_components_list}
        do
            for n_workers in 8
            do
                sbatch \
                    --cpus-per-task=${n_workers} \
                    --output=logs/output_chbmit_gmm_based_classifier_${patient}_${format}_${gmm_components}_${n_workers}.out \
                    ./scripts/slurm_run_chbmit_gmm.sh --patient ${patient} --format ${format} --gmm_components ${gmm_components} --n_workers ${n_workers}
            done
        done
    done
done
