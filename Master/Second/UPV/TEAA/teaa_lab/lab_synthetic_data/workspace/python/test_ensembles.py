import os
import sys
import time
import numpy
import argparse
import ray

import joblib
from ray.util.joblib import register_ray

from ray_load_data import ray_load_data

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import confusion_matrix, classification_report

# ----------------------------------------------------------------------------------------
@ray.remote
def ray_random_forest_train(_dict_, config):
    X = _dict_['X']
    y = _dict_['y']
    #
    clf = RandomForestClassifier(n_estimators = config['n_estimators'],
                                  max_depth = config['max_depth'],
                                  criterion = config['criterion'],
                                  class_weight = config['class_weight'],
                                  n_jobs = config['n_jobs'],
                                  verbose = config['verbose'])
    #
    clf.fit(X, y.flatten())
    #
    return clf
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_extra_trees_train(_dict_, config):
    X = _dict_['X']
    y = _dict_['y']
    #
    clf = ExtraTreesClassifier(n_estimators = config['n_estimators'],
                                max_depth = config['max_depth'],
                                criterion = config['criterion'],
                                class_weight = config['class_weight'],
                                n_jobs = config['n_jobs'],
                                verbose = config['verbose'])
    clf.fit(X, y.flatten())
    #
    return clf
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_my_predict(_dict_, clfs):
    X = _dict_['X']
    y_true = _dict_['y'].flatten()
    #
    y_pred = list()
    #
    probs = sum([clf.predict_proba(X) for clf in clfs])
    y_pred = probs.argmax(axis = 1).flatten()
    #
    return confusion_matrix(y_true, y_pred, labels = [0, 1])
# ----------------------------------------------------------------------------------------

def main(args):
    t0 = time.time()
    if args.n_workers >= 1:
        ray.init(num_cpus = args.n_workers, object_store_memory = 24 * 1024 ** 3)
        print()
        print()
        print('client ready after waiting', time.time() - t0, 'seconds', flush = True)
        print()
        print()
    #
    data = ray_load_data(args)
    #
    list_of_n_estimators = [int(s) for s in args.n_estimators.split(sep = ':')]
    list_of_max_depths = [int(s) for s in args.max_depth.split(sep = ':')]
    #
    for n_estimators in list_of_n_estimators:
        for max_depth in list_of_max_depths:
            clfs = None
            bst = None
            gbc = None
            print(f"{args.technique} training started ... ", flush = True)
            t0 = time.time()
            if args.technique.lower() in ['rf', 'randomforest', 'random-forest']:
                register_ray()
                rf_config = {'n_estimators': max(1, n_estimators // args.n_workers),
                                'max_depth': max_depth,
                                'criterion': 'gini',
                             'class_weight': 'balanced',
                                   'n_jobs': 1,
                                  'verbose': 1}
                retries = 3
                successful_training = False
                futures = [ray_random_forest_train.remote(_xy_ref_, rf_config) for _xy_ref_ in data['train']['Xy_refs']]
                clfs = ray.get(futures)
                successful_training = True
            #
            elif args.technique.lower() in ['ert', 'extratrees', 'extra-trees']:
                ert_config = {'n_estimators': max(1, n_estimators // args.n_workers),
                                 'max_depth': max_depth,
                                 'criterion': 'gini',
                              'class_weight': 'balanced',
                                    'n_jobs': 1,
                                   'verbose': 1}
                retries = 3
                successful_training = False
                futures = [ray_extra_trees_train.remote(_xy_ref_, ert_config) for _xy_ref_ in data['train']['Xy_refs']]
                clfs = ray.get(futures)
                successful_training = True
            #
            else:
                print(f"Unknown technique {args.technique}. Then, nothing to do!!")
            #
            print(f"training {args.technique} with {n_estimators} estimators and max_depth = {max_depth} required {time.time() - t0} seconds")
            #
            assert clfs is not None
            for subset in ('test'): # ('train', 'test'):
                print(f"{args.technique} for {subset} subset predicting started ... ", flush = True)
                t0 = time.time()
                futures = [ray_my_predict.remote(_xy_ref_, clfs) for _xy_ref_ in data[subset]['Xy_refs']]
                cm = sum(ray.get(futures))
                print(f"predicting with {args.technique} using {n_estimators} estimators and a max_depth = {max_depth} for {subset} subset required {time.time() - t0} seconds", flush = True)
                t0 = time.time()
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
    parser.add_argument('--technique',    dest = 'technique',    type = str, default = 'rf',    help = 'Random Forest / Extra Trees / XGBoostTree classifier type')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000,    help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--max-depth',    dest = 'max_depth',    type = str, default = "5",     help = 'Max depth for the trees')
    parser.add_argument('--n-estimators', dest = 'n_estimators', type = str, default = "50",    help = 'Number of threes in ensembles')
    parser.add_argument('--pca-components', dest = 'pca_components',  type = int, default = 0, help = 'Greater than zero PCA is applied, otherwise samples are kept in the original input space')

    main(parser.parse_args())
