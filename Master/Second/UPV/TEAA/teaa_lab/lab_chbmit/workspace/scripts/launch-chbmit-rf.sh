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
#list_of_n_estimators="100 200 300 500 700 1000 2000"
list_of_n_estimators="100"
list_of_max_depth="3 5 7 9 11 13"
#list_of_max_depth="5"
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
        for n_estimators in ${list_of_n_estimators}
        do
            for max_depth in ${list_of_max_depth}
            do
                for n_workers in 8
                do
                    sbatch \
                        --cpus-per-task=${n_workers} \
                        --output=logs/output_chbmit_rf_based_classifier_${patient}_${format}_${n_estimators}_${max_depth}_${n_workers}.out \
                        ./scripts/slurm_run_chbmit_rf.sh --patient ${patient} --format ${format} --n_estimators ${n_estimators} --max_depth ${max_depth} --n_workers ${n_workers}
                done
            done
        done
    done
done
