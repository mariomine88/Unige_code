import os
import sys
import time
import numpy
import argparse
import ray

from ray_load_data import ray_load_data

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report

bandwidth = 1.0
def weight_function(x):
    global bandwidth
    return numpy.exp(-0.5 * x ** 2 / bandwidth ** 2)

def main(args):
    """
    t0 = time.time()
    if args.n_workers >= 1:
        ray.init(num_cpus = args.n_workers, object_store_memory = 24 * 1024 ** 3)
        print()
        print()
        print('client ready after waiting', time.time() - t0, 'seconds', flush = True)
        print()
        print()
    """
    #
    data = ray_load_data(args, use_pandas = True)
    X_train = data['train']['X'][:10_000_000]
    y_train = data['train']['y'][:10_000_000].flatten()
    X_test = data['test']['X']
    y_test = data['test']['y'].flatten()
    del data
    #
    if args.technique == 'knn':
        list_of_parameters = [int(s) for s in args.n_neighbors.split(sep = ':')]
    elif args.technique == 'kde':
        list_of_parameters = [float(s) for s in args.bandwidth.split(sep = ':')]
    #
    for _parameter_ in list_of_parameters:
            clf = None
            print(f"{args.technique} training started ... ", flush = True)
            t0 = time.time()
            if args.technique in ['knn']:
                #
                clf = KNeighborsClassifier(n_neighbors = _parameter_,
                                            weights = 'distance',
                                            algorithm = 'ball_tree', #leaf_size = 1_000,
                                            n_jobs = args.n_workers)
            elif args.technique == 'kde':
                bandwidth = _parameter_
                clf = KNeighborsClassifier(n_neighbors = 100,
                                            weights = weight_function,
                                            algorithm = 'ball_tree', leaf_size = 1_000,
                                            n_jobs = args.n_workers)
            clf.fit(X_train, y_train)
            #
            print(f"training {args.technique} with {_parameter_} required {time.time() - t0} seconds", flush = True)
            #
            #
            for subset in ['test']: # ['train', 'test']:
                print(f"{args.technique} for {subset} subset predicting started ... ", flush = True)
                t0 = time.time()
                y_true = y_test
                y_pred = list()
                for i in range(0, len(X_test), args.block_size):
                    print('.', end = '', flush = True)
                    y_pred.append(clf.predict(X_test[i : i + args.block_size]))
                y_pred = numpy.array(y_pred)
                print(f"predicting with {args.technique} using {_parameter_} for {subset} subset required {time.time() - t0} seconds", flush = True)
                t0 = time.time()
                cm = confusion_matrix(y_true, y_pred, labels = [0, 1])
                print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1], digits = 3))
                print(f'Computing metrics for {subset} subset required {time.time() - t0} seconds', flush = True)

    print('Bye!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'test_kdeknn_in_local.py',
                description = 'Testing memory-based techniques: KDE and KNN',
                epilog = 'That\'s all folks!!!')
    parser.add_argument('--n-workers',    dest = 'n_workers',    type = int, default = 5,       help = 'Number of workers in the cluster')
    parser.add_argument('--n-threads',    dest = 'n_threads',    type = int, default = 1,       help = 'Number of threads per the worker')
    parser.add_argument('--cluster-type', dest = 'cluster_type', type = str, default = 'local', help = 'Cluster type to use. One of local, ssh and kubernetes')
    parser.add_argument('--technique',    dest = 'technique',    type = str, default = 'xgbc',  help = 'XGBoostTree classifier type')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000,    help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--bandwidth',    dest = 'bandwidth',    type = str, default = "1",     help = 'Bandwidth for KDE')
    parser.add_argument('--n-neighbors',  dest = 'n_neighbors',  type = str, default = "5",     help = 'K for KNN')
    parser.add_argument('--pca-components', dest = 'pca_components',  type = int, default = 0, help = 'Greater than zero PCA is applied, otherwise samples are kept in the original input space')

    main(parser.parse_args())
