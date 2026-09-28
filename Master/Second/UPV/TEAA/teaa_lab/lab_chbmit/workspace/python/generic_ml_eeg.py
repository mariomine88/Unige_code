"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 2.0
    Date: September 2024

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is generic for being used with several ML techniques but Neural Network
"""

import sys
import os
import time
import argparse
import numpy

#from sklearnex import patch_sklearn
#patch_sklearn()

from utils_for_results import save_results
from eeg_load_data import load_csv_from_eeg

def main(args, sc, db, ray):

    hostname = os.uname()[1]
    num_partitions = (60 * 70) // 10
    if hostname in ['tensor', 'tensor.dsic.upv.es', 'tensor.upvnet.upv.es']:
        data_dir = '/opt/asig/teaa-cd/data/chbmit/data'
        hdfs_url = None
        num_partitions = args.n_workers
    elif args.cluster_type == 'kubernetes':
        data_dir = '/data/chbmit/data'
        hdfs_url = None
        num_partitions = args.n_workers
    elif hostname in ['eibds01', 'eibds01.mbda', 'eibds01.inf.upv.es', 'paradigm']:
        data_dir = '/data/chbmit/data'
        hdfs_url = 'hdfs://eibds01.mbda:8020'
        num_partitions = args.n_workers
    elif hostname in ['teaa-master-ubuntu22', 'teaa-master-ubuntu22.dsicv.upv.es']:
        data_dir = None
        hdfs_url = 'hdfs://teaa-master-ubuntu22:8020'
        num_partitions = 60
    else:
        print('')
        print('')
        print('Unsupported computing node', hostname)
        print('')
        print('')
        return None

    #sc.setCheckpointDir(hdfs_url + '/system')

    do_z_transform = args.doStandardScaling or (args.format == '21x14')

    args.task = 'binary-classification' if args.doBinaryClassification else 'multiclass-classification'

    args.log_dir     = f'{args.baseDir}/{args.logDir}/{args.technique}'
    if args.technique in ('gmm', 'gbt', 'kde', 'knn'):
        args.models_dir  = f'{args.baseDir}/{args.modelsDir}/{args.technique}/{args.task}'
    else:
        args.models_dir  = f'{args.baseDir}/{args.modelsDir}/{args.technique}'
    args.results_dir = f'{args.baseDir}/{args.resultsDir}/{args.technique}/{args.patient}'

    os.makedirs(args.log_dir,     exist_ok = True)
    os.makedirs(args.models_dir,  exist_ok = True)
    os.makedirs(args.results_dir, exist_ok = True)

    if sc is not None:
        # Apache SPARK
        if args.patient == 'ALL':
            train_filenames = [f'{hdfs_url}/data/chbmit/21x14/chbmit-chb{i:02d}-{args.format}-time-to-seizure.csv' for i in range(1,17)]
            test_filenames  = [f'{hdfs_url}/data/chbmit/21x14/chbmit-chb{i:02d}-{args.format}-time-to-seizure.csv' for i in range(17,25)]
        else:
            train_filenames = [f'{hdfs_url}/data/chbmit/21x14/chbmit-{args.patient}-{args.format}-time-to-seizure-train.csv']
            test_filenames  = [f'{hdfs_url}/data/chbmit/21x14/chbmit-{args.patient}-{args.format}-time-to-seizure-test.csv']
    else:
        # DASK or RAY
        if args.patient == 'ALL':
            #train_filenames = [f'{data_dir}/21x14/chbmit-chb{i:02d}-{args.format}-time-to-seizure.csv.gz' for i in range(1,17)]
            #test_filenames  = [f'{data_dir}/21x14/chbmit-chb{i:02d}-{args.format}-time-to-seizure.csv.gz' for i in range(17,25)]
            train_filenames = [f'{data_dir}/train/{args.format}/train{i:03d}.csv.gz' for i in range(70)]
            test_filenames  = [f'{data_dir}/test/{args.format}/test{i:03d}.csv.gz'   for i in range(70)]
        else:
            train_filenames = [f'{data_dir}/21x14/chbmit-{args.patient}-{args.format}-time-to-seizure-train.csv.gz']
            test_filenames  = [f'{data_dir}/21x14/chbmit-{args.patient}-{args.format}-time-to-seizure-test.csv.gz']

    # Loads and repartitions the data
    starting_time = time.time()
    rdd_train = load_csv_from_eeg(sc, db, ray, train_filenames, num_partitions = num_partitions, do_binary_classification = args.doBinaryClassification)
    rdd_test  = load_csv_from_eeg(sc, db, ray,  test_filenames, num_partitions = num_partitions, do_binary_classification = args.doBinaryClassification)
    elapsed_time = time.time() - starting_time
    print(f'data loading required {elapsed_time} seconds', flush = True)

    if sc is not None:
        # Apache Spark RDD
        rdd_train = rdd_train.repartition(num_partitions)
        rdd_test  =  rdd_test.repartition(num_partitions)
        num_samples_train = rdd_train.count()
        num_samples_test = rdd_test.count()
    elif db is not None:
        # Dask Bag
        new_num_partitions = max(70, args.n_workers)
        starting_time = time.time()
        if rdd_train.npartitions != new_num_partitions:
            rdd_train = rdd_train.repartition(new_num_partitions)
        if rdd_test.npartitions != new_num_partitions:
            rdd_test  =  rdd_test.repartition(new_num_partitions)
        elapsed_time = time.time() - starting_time
        num_samples_train = rdd_train.count().compute()
        num_samples_test = rdd_test.count().compute()
        if elapsed_time > 1.:
            print(f'repartitioning required {elapsed_time} seconds', flush = True)
    elif ray is not None:
        # RAY Dataset
        # ----------------------------------------------------------------------------------------
        @ray.remote
        def ray_compute_count(_dict_):
            X = _dict_['X']
            assert len(X.shape) == 2
            return X.shape[0]
        # ----------------------------------------------------------------------------------------
        futures = [ray_compute_count.remote(_ref_) for _ref_ in rdd_train]
        results = ray.get(futures)
        num_samples_train = sum(results)
        futures = [ray_compute_count.remote(_ref_) for _ref_ in rdd_test]
        results = ray.get(futures)
        num_samples_test = sum(results)
        # ----------------------------------------------------------------------------------------
        @ray.remote
        def get_input_dim(_dict_):
            return _dict_['X'].shape[1]
        # ----------------------------------------------------------------------------------------
        futures = [get_input_dim.remote(_ref_) for _ref_ in rdd_train[:1]]
        args.input_dim = ray.get(futures)[0]
        #
    else:
        num_samples_train = len(rdd_train)
        num_samples_test = len(rdd_test)
        args.input_dim = rdd_train[0][4].shape[0]

    # BEGIN: Computation of the standard scalation
    if do_z_transform:
        starting_time = time.time()
        if args.verbose > 0:
            print('Scaling to zero mean and unit variance', flush = True)
        if sc is not None:
            # Apache Spark
            mean = rdd_train.map(lambda sample: sample[4]).reduce(lambda x, y: x + y) / rdd_train.count()
            variance = rdd_train.map(lambda sample: (sample[4] - mean) ** 2).reduce(lambda x, y: x + y) / rdd_train.count()
            sigma = numpy.maximum(1.0e-3, numpy.sqrt(variance))
            #
            #                                         patient,   index,     tts,       true_label, sample
            rdd_train = rdd_train.map(lambda sample: (sample[0], sample[1], sample[2], sample[3], (sample[4] - mean) / sigma))
            rdd_test  =  rdd_test.map(lambda sample: (sample[0], sample[1], sample[2], sample[3], (sample[4] - mean) / sigma))
            #
        elif db is not None:
            # Dask Bag
            mean = rdd_train.map(lambda sample: sample[4]).fold(lambda x, y: x + y).compute() / num_samples_train
            variance = rdd_train.map(lambda sample: (sample[4] - mean) ** 2).fold(lambda x, y: x + y).compute() / num_samples_train
            sigma = numpy.maximum(1.0e-3, numpy.sqrt(variance))
            #
            #                                         patient,   index,     tts,       true_label, sample
            rdd_train = rdd_train.map(lambda sample: (sample[0], sample[1], sample[2], sample[3], (sample[4] - mean) / sigma)) # .compute()
            rdd_test  =  rdd_test.map(lambda sample: (sample[0], sample[1], sample[2], sample[3], (sample[4] - mean) / sigma)) # .compute()
            #
        elif ray is not None:
            # RAY (from Ray.Dataset)
            # ----------------------------------------------------------------------------------------
            @ray.remote
            def ray_compute_mean(_dict_):
                X = _dict_['X']
                assert len(X.shape) == 2
                return X.sum(axis = 0)
            # ----------------------------------------------------------------------------------------
            @ray.remote
            def ray_compute_variances(_dict_, mean):
                X = _dict_['X']
                assert len(X.shape) == 2
                var = ((X - mean.reshape(1, -1)) ** 2).sum(axis = 0)
                return var
            # ----------------------------------------------------------------------------------------
            @ray.remote
            def ray_apply_z_transform(_dict_, mean, sigma):
                _dict_['X'] = (_dict_['X'] - mean.reshape(1, -1)) / sigma.reshape(1, -1)
                return _dict_
            # ----------------------------------------------------------------------------------------
            futures = [ray_compute_mean.remote(_ref_) for _ref_ in rdd_train]
            results = ray.get(futures)
            mean = numpy.vstack(results).sum(axis = 0) / num_samples_train
            futures = [ray_compute_variances.remote(_ref_, mean) for _ref_ in rdd_train]
            results = ray.get(futures)
            variance = sum(results) / num_samples_train
            sigma = numpy.maximum(1.0e-3, numpy.sqrt(variance))
            #
            futures = [ray_apply_z_transform.remote(_ref_, mean, sigma) for _ref_ in rdd_train]
            for _ref_ in rdd_train: del _ref_
            rdd_train = futures
            futures = [ray_apply_z_transform.remote(_ref_, mean, sigma) for _ref_ in rdd_test]
            for _ref_ in rdd_test: del _ref_
            rdd_test = futures
            print(f"train data partitioned into {len(rdd_train)} chunks")
            print(f"test data partitioned into {len(rdd_test)} chunks")
        else:
            mean = sum([sample[4] for sample in rdd_train]) / num_samples_train
            variance = sum([(sample[4] - mean) ** 2 for sample in rdd_train]) / num_samples_train
            sigma = numpy.maximum(1.0e-3, numpy.sqrt(variance))
            for i in range(len(rdd_train)):
                rdd_train[i][4] = (rdd_train[i][4] - mean) / sigma
            for i in range(len(rdd_test)):
                rdd_test[i][4] = (rdd_test[i][4] - mean) / sigma
        #
        elapsed_time = time.time() - starting_time
        print(f'scaling required {elapsed_time} seconds', flush = True)

        if args.verbose > 2:
            print('mean', mean)
            print('sigma', sigma)
    # END: Computation the standard scalation

    if sc is not None:
        # Apache Spark
        rdd_train.persist()
        rdd_test.persist()
        print('|rdd_train| =', num_samples_train, 'num partitions = ', rdd_train.getNumPartitions())
        print('|rdd_test| =', num_samples_test, 'num partitions = ', rdd_test.getNumPartitions())
    elif db is not None:
        # Dask Bag
        starting_time = time.time()
        rdd_train = rdd_train.persist()
        rdd_test = rdd_test.persist()
        print('|rdd_train| =', num_samples_train, 'num partitions = ', rdd_train.npartitions)
        print('|rdd_test| =', num_samples_test, 'num partitions = ', rdd_test.npartitions)
        elapsed_time = time.time() - starting_time
        print(f'persisting and counting samples required {elapsed_time} seconds', flush = True)
    else:
        # RAY or reading local CSV files
        print('|rdd_train| =', num_samples_train)
        print('|rdd_test| =', num_samples_test)

    starting_time = time.time()
    if sc is not None:
        # Apache Spark
        l1 = rdd_train.map(lambda sample: (sample[3], 1)).reduceByKey(lambda x, y: x + y).collect()
        l2 =  rdd_test.map(lambda sample: (sample[3], 1)).reduceByKey(lambda x, y: x + y).collect()
        labels = [x[0] for x in (l1 + l2)]
    elif db is not None:
        # Dask Bag
        l1 = rdd_train.map(lambda sample: (sample[3], 1)).foldby(lambda s: s[0], lambda x, y: x + y).compute()
        l2 =  rdd_test.map(lambda sample: (sample[3], 1)).foldby(lambda s: s[0], lambda x, y: x + y).compute()
        labels = [x[0] for x in (l1 + l2)]
    elif ray is not None:
        # RAY
        @ray.remote
        def ray_get_label(_dict_):
            label = _dict_['label']
            assert len(label.shape) == 1
            return numpy.unique(label).tolist()
        # ----------------------------------------------------------------------------
        futures = [ray_get_label.remote(_ref_) for _ref_ in rdd_train]
        l1 = [item for l in ray.get(futures) for item in l]
        futures = [ray_get_label.remote(_ref_) for _ref_ in rdd_test]
        l2 = [item for l in ray.get(futures) for item in l]
        labels = l1 + l2
    else:
        # Local text files
        l1 = [sample[3] for sample in rdd_train]
        l2 = [sample[3] for sample in rdd_test]
        labels = l1 + l2
    args.labels = [int(x) for x in list(numpy.unique(labels))]
    elapsed_time = time.time() - starting_time
    print(f'getting the labels of the target classes required {elapsed_time} seconds', flush = True)

    print('labels', args.labels, flush = True)

    # Each tuple in the RDD has (patient, time-to-seizure, label, features)

    # Now, depending on the ML technique chosen by the user one code is going to be used
    if args.technique == 'kmeans':
        from kmeans_for_eeg import kmeans_for_eeg
        kmeans_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'gmm':
        from gmm_for_eeg import gmm_for_eeg
        gmm_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'rf':
        from ensemble_for_eeg import rf_for_eeg
        rf_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'ert':
        from ensemble_for_eeg import ert_for_eeg
        ert_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'gbt':
        from ensemble_for_eeg import gbt_for_eeg
        gbt_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'kde':
        from kde_for_eeg import kde_for_eeg
        kde_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    elif args.technique == 'knn':
        #from knn_for_eeg import knn_for_eeg
        #knn_for_eeg(args = args, train_data = rdd_train, test_data = rdd_test)
        from kde_for_eeg import kde_for_eeg
        kde_for_eeg(args = args, train_data = rdd_train, num_samples_train = num_samples_train, test_data = rdd_test, num_samples_test = num_samples_test)
    #

    if sc is not None: # Apache Spark specific instructions
        rdd_train.unpersist()
        rdd_test.unpersist()

# end of the method main()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    #
    parser.add_argument('patient', type=str, help='Patient identifier')
    #
    parser.add_argument('--technique', default='kmeans', type=str, help='ML technique name: kmeans, gmm, rf, ert, gbt, kde, knn')
    #
    parser.add_argument('--doTraining', dest='doTraining', action='store_true')
    parser.add_argument('--no-doTraining', dest='doTraining', action='store_false')
    parser.set_defaults(doTraining = True)
    parser.add_argument('--doClassification', dest='doClassification', action='store_true')
    parser.add_argument('--no-doClassification', dest='doClassification', action='store_false')
    parser.set_defaults(doClassification = True)
    parser.add_argument('--doBinaryClassification', dest='doBinaryClassification', action='store_true')
    parser.add_argument('--no-doBinaryClassification', dest='doBinaryClassification', action='store_false')
    parser.set_defaults(doBinaryClassification = False)
    parser.add_argument('--doStandardScaling', dest='doStandardScaling', action='store_true')
    parser.add_argument('--no-doStandardScaling', dest='doStandardScaling', action='store_false')
    parser.set_defaults(doStandardScaling = False)
    #
    parser.add_argument('--delta',  default=15,  type=int, help='Delta for classifying samples taking into account the current sample and a subsequence of previous samples')
    parser.add_argument('--format',  default='21x14',  type=str, help='Data format (e.g., if PCA is applied use pca136 or pca141')
    #
    parser.add_argument('--verbose', default=0, type=int, help='Verbosity level')
    parser.add_argument('--codebookSize', default="100:200:300", type=str, help='Colon separated list of the codebook sizes to apply kmeans (maybe before KDE when using it)')
    parser.add_argument('--covarType', default="diagonal", type=str, help='Covariance matrix type: diagonal or full')
    parser.add_argument('--componentsGMM', default="10:20:30", type=str, help='Max numbers of components for Gaussian Mixture Models')
    parser.add_argument('--bandWidth', default="0.1:0.2:0.5:1.0:2.0", type=str, help='Colon separated list of the band width for the KDE classifier')
    parser.add_argument('--K', default="2:3:5:7:9:11:13", type=str, help='Colon separated list of the n_neighbors width for the KNN classifier')
    parser.add_argument('--use-ball-trees', dest='use_ball_trees', action='store_true', help='To use Ball Trees for KDE/KNN')
    parser.add_argument('--do-not-use-ball-trees', dest='use_ball_trees', action='store_false', help='To use Ball Trees for KDE/KNN')
    parser.set_defaults(use_ball_trees = False)
    parser.add_argument('--username',   default='cluster',        type=str, help='Username')
    parser.add_argument('--baseDir',    default='.',              type=str, help='Directory base from which create the directories for models, results and logs')
    parser.add_argument('--modelsDir',  default='models/chbmit',  type=str, help='Directory to save models --if it is the case')
    parser.add_argument('--resultsDir', default='results/chbmit', type=str, help='Directory where to store the results')
    parser.add_argument('--logDir',     default='logs/chbmit',    type=str, help='Directory where to store the logs --if it is the case')
    #
    parser.add_argument('--numEstimators', default="100:200", type=str, help='Colon separated list of number of trees in ensembles of trees: RF, ERT, and GBT ')
    parser.add_argument('--maxDepth', default="5:7", type=str, help='Colon separated list of the max depth of each tree in ensembles of trees: RF, ERT, and GBT')
    #
    parser.add_argument('--clusterMode', dest='clusterMode', action='store_true', help='To run the code on a Spark cluster')
    parser.set_defaults(clusterMode = False)
    parser.add_argument('--n_jobs',  default=1,  type=int, help='Number of jobs to run using joblib or other approach. With no effect when launching in a Spark cluster or a Daskcluster on Kubernetes')
    parser.add_argument('--n-workers', dest = 'n_workers', type = int, default = 5, help = 'Number of workers in the cluster')
    parser.add_argument('--n-threads', dest = 'n_threads', type = int, default = 1, help = 'Number of threads per the worker')
    parser.add_argument('--cluster-type', dest = 'cluster_type', type = str, default = 'local', help = 'Cluster type to use. One of local, ssh and kubernetes')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000, help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--batchSize',  default=500,  type=int, help='Number of samples in a batch. Currently effective for GMM')

    args = parser.parse_args()
    sc = None # Spark Context
    db = None # Dask Bag
    ray = None # RAY
    if args.clusterMode:
        import ray
        if args.cluster_type in ['local', 'local_cluster']:
            args.exec_environment_id = "ray_local_cluster"
            args.exec_environment_description = f"RAY local cluster with {args.n_workers} workers"
            hostname = os.uname()[1]
            if hostname.startswith('paradigm'):
                ray_mem_in_GB = 24
            elif hostname.startswith('eibds01'):
                ray_mem_in_GB = 56
            else:
                ray_mem_in_GB = 16
            ray.init(num_cpus = args.n_workers, object_store_memory = ray_mem_in_GB * 1024 ** 3)
        else:
            args.exec_environment_id = "ray_kubecluster"
            args.exec_environment_description = f"RAY Kubernetes cluster with {args.n_workers} workers"
            ray.init()
    else:
        db = None
        args.exec_environment_id = "local_cpu"
        args.exec_environment_description = "local CPU"

    main(args, sc, db, ray)

    if sc is not None:
        # Stops Spark Context
        sc.stop()
    if db is not None:
        # Closes the Dask client
        client.close()
        # Closes the connection with the Dask cluster
        cluster.close()
