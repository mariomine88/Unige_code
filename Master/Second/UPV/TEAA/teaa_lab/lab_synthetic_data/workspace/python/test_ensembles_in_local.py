import os
import sys
import time
import numpy
import argparse
import ray

from ray_load_data import ray_load_data

from xgboost import XGBClassifier
import xgboost as xgb

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import confusion_matrix, classification_report

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
    list_of_n_estimators = [int(s) for s in args.n_estimators.split(sep = ':')]
    list_of_max_depths = [int(s) for s in args.max_depth.split(sep = ':')]
    #
    for n_estimators in list_of_n_estimators:
        for max_depth in list_of_max_depths:
            clf = None
            print(f"{args.technique} training started ... ", flush = True)
            t0 = time.time()
            if args.technique in ['gbt', 'xgbc']:
                #
                xgb.set_config(nthread = args.n_workers)
                print(xgb.get_config())
                #
                clf = XGBClassifier(n_estimators = n_estimators, max_depth = max_depth, learning_rate = 1, objective = 'binary:logistic')
            elif args.technique == 'rf':
                clf = RandomForestClassifier(n_estimators = n_estimators,
                                      max_depth = max_depth,
                                      criterion = 'gini',
                                      class_weight = 'balanced',
                                      n_jobs = args.n_workers,
                                      verbose = 1)
            elif args.technique == 'ert':
                clf = ExtraTreesClassifier(n_estimators = n_estimators,
                                    max_depth = max_depth,
                                    criterion = 'gini',
                                    class_weight = 'balanced',
                                    n_jobs = args.n_workers,
                                    verbose = 1)
            clf.fit(X_train, y_train)
            #
            print(f"training {args.technique} with {n_estimators} estimators and max_depth = {max_depth} required {time.time() - t0} seconds", flush = True)
            #
            #
            for subset in ['test']: # ['train', 'test']:
                print(f"{args.technique} for {subset} subset predicting started ... ", flush = True)
                t0 = time.time()
                y_true = y_test
                y_pred = clf.predict(X_test)
                print(f"predicting with {args.technique} using {n_estimators} estimators and a max_depth = {max_depth} for {subset} subset required {time.time() - t0} seconds", flush = True)
                t0 = time.time()
                cm = confusion_matrix(y_true, y_pred, labels = [0, 1])
                print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1], digits = 3))
                print(f'Computing metrics for {subset} subset required {time.time() - t0} seconds', flush = True)

    print('Bye!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'test_ensembles.py',
                description = 'Testing Ensembles based on Random Forest or Extremely Randomized Trees',
                epilog = 'That\'s all folks!!!')
    parser.add_argument('--n-workers',    dest = 'n_workers',    type = int, default = 5,       help = 'Number of workers in the cluster')
    parser.add_argument('--n-threads',    dest = 'n_threads',    type = int, default = 1,       help = 'Number of threads per the worker')
    parser.add_argument('--cluster-type', dest = 'cluster_type', type = str, default = 'local', help = 'Cluster type to use. One of local, ssh and kubernetes')
    parser.add_argument('--technique',    dest = 'technique',    type = str, default = 'xgbc',  help = 'XGBoostTree classifier type')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000,    help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--max-depth',    dest = 'max_depth',    type = str, default = "5",     help = 'Max depth for the trees')
    parser.add_argument('--n-estimators', dest = 'n_estimators', type = str, default = "50",    help = 'Number of threes in ensembles')
    parser.add_argument('--pca-components', dest = 'pca_components',  type = int, default = 0, help = 'Greater than zero PCA is applied, otherwise samples are kept in the original input space')

    main(parser.parse_args())
