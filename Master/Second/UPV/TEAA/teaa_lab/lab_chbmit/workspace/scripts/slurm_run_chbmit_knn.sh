#!/bin/bash -eu
#SBATCH -p docencia
#SBATCH --ntasks=1
#SBATCH --gres=gpu:0
#SBATCH --cpus-per-task=32
#SBATCH --job-name=chbmit_knn_based_classifier
#SBATCH --output=logs/output_chbmit_knn_based_classifier.out
#SBATCH --time=02:00:00
#SBATCH --open-mode=append
#

mkdir -p logs results models

##############################################################################################
### MAIN
##############################################################################################
#
# Run this command as one of the following examples:
#
#  sbatch --output="logs/output_chbmit_knn_based_classifier.out"  scripts/launch-chbmit-knn.sh --patient chb03 --format pca136 --cb_size 200 --K 7 --n_workers 32
#  sbatch --output="logs/output_chbmit_knn_based_classifier.out"  scripts/launch-chbmit-knn.sh --patient ALL   --format pca141 --cb_size 200 --K 7 --n_workers 32
# 
#  Change the patient according to the configuration you have to use; using ALL for all-patients tasks.    
#  Set the number of estimators and max depths required in the tasks you have to run.
#  IMPORTANT: use only one patient at a time, being ALL the key for running all-patients tasks.
#
##############################################################################################

patient="none"
cb_size="none"
K="none"
format="none"
n_workers="none"

while [ $# -ge 1 ]
do
    case $1 in
        --patient)
            patient="$2"
            shift
            ;;
        --format)
            format="$2"
            shift
            ;;
        --cb_size)
            cb_size="$2"
            shift
            ;;
        --K)
            K="$2"
            shift
            ;;
#        --cluster-type)
#            cluster_type="$2"
#            shift
#            ;;
        --n_workers)
            n_workers="$2"
            shift
            ;;
    esac
    shift
done

if [ "${patient}" = "none" ]
then
    echo "patient not specified in the command line!"
    exit 1
fi
if [ "${format}" = "none" ]
then
    echo "format not specified in the command line!"
    exit 2
fi
if [ "${cb_size}" = "none" ]
then
    echo "cb_size not specified in the command line!"
    exit 3
fi
if [ "${K}" = "none" ]
then
    echo "K not specified in the command line!"
    exit 4
fi
if [ "${n_workers}" = "none" ]
then
    echo "n_workers not specified in the command line!"
    exit 5
fi

#cluster_type="none"
cluster_type="local" # no other choice when working with TENSOR
#cluster_type="kubernetes"

case ${cluster_type} in
    local|local_cluster)
        kubecluster_options=" --clusterMode --n-workers=${n_workers} --cluster-type=local " # using this configuration nproc must be 1
        RAY_SUBMIT=""
        nproc=1
        njobs=1
        nthreads=1
        ;;
    kubernetes|kubecluster)
        kubecluster_options=" --clusterMode --n-workers=70 --cluster-type=kubernetes " # using this configuration nproc must be 1
        RAY_SUBMIT="scripts/ray_submit.sh"
        nproc=1
        njobs=1
        nthreads=1
        ;;
    *)
        kubecluster_options=" --n-workers=1 --cluster-type=${cluster_type} " # using this configuration you can set the variable nproc to the number of cores 
        RAY_SUBMIT=""
        nproc=$(nproc)
        if [ ${nproc} -gt 32 ]
        then
            nproc=32
        fi
        njobs=1
        nthreads=$((${nproc} / ${njobs}))
        if [ ${nthreads} -lt 1 ]
        then
            nthreads=1
        fi
        ;;
esac

##############################################################################################
###### CONFIGURATION OF THE EXECUTION ENVIRONMENT ############################################
##############################################################################################
unset DISPLAY

# OMP_NUM_THREADS should be equal to nproc / njobs, e.g., for KMeans it is not possible to indicate njobs, so OMP_NUM_THREADS should be nproc
export OMP_NUM_THREADS=${nthreads}
export MKL_NUM_THREADS=${nthreads}  # use this in case MKL is enabled in the computer 
export OPENBLAS_NUM_THREADS=${nthreads} # set just in case OpenBLAS is enabled
export NUMEXPR_NUM_THREADS=${nthreads} # as far as I know, this is not enabled, but just in case
export BLIS_NUM_THREADS=${nthreads} # as far as I know, this is not enabled, but just in case
##############################################################################################
###### CONFIGURATION OF THE EXECUTION ENVIRONMENT ############################################
##############################################################################################


for task in doBinaryClassification doClassification
do
    ${RAY_SUBMIT} python python/generic_ml_eeg.py ${patient} \
                    --technique knn \
                    ${kubecluster_options} \
                    --n_jobs ${njobs} \
                    --codebookSize ${cb_size} \
                    --K ${K} --do-not-use-ball-trees \
                    --format ${format} \
                    --no-doStandardScaling \
                    --block-size 1000 \
                    --doTraining \
                    --${task} \
                    --user ${USER} \
                    --verbose 2 --delta 1
done
