import os
import sys
import time
import math
import numpy
import argparse

import ray

from ray_load_data import ray_load_data

from sklearn.metrics import confusion_matrix, classification_report

from lbg import lbg
from BallTree import BallTree

# ----------------------------------------------------------------------------------------
@ray.remote
def ray_filter_by_target_class(_dict_, class_id):
    X = _dict_['X']
    assert len(X.shape) == 2
    y = _dict_['y']
    return {'X': X[y == class_id]}
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_knn_predict(_dict_, ball_tree, K, block_size):
    X = _dict_['X']
    y_true = _dict_['y'].flatten().tolist()
    y_pred = list()
    for i in range(0, len(X), block_size):
        y_pred += ball_tree.predict(X[i : i + block_size], K)
    #
    return confusion_matrix(y_true, y_pred, labels = [0, 1])
# ----------------------------------------------------------------------------------------
# -------------------------------------------------------------------------
def kde_kernel(d, h):
    return math.exp(-(d * d) / (2 * h * h))
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
@ray.remote
def ray_kde_predict(_dict_, ball_tree, K, bandwidth, block_size):
    X = _dict_['X']
    y_true = _dict_['y'].flatten().tolist()
    y_pred = list()
    for i in range(len(X)):
        densities = ball_tree.get_kde(X[i], K, kde_kernel, bandwidth, 2)
        y_pred.append(densities.argmax())
    #
    return confusion_matrix(y_true, y_pred, labels = [0, 1])
# -------------------------------------------------------------------------

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
    data = ray_load_data(args, use_pandas = False)
    #
    target_classes = [0, 1]
    t0 = time.time()
    codebooks = dict()
    list_of_codebook_sizes = list()
    for tc in target_classes:
        codebooks[tc] = dict()
        models_dir = f'{args.models_dir}/target_class_{tc}'
        os.makedirs(models_dir, exist_ok = True)
        if args.do_train:
            X_refs = [ray_filter_by_target_class.remote(_Xy_, tc) for _Xy_ in data['train']['Xy_refs']]
            WSSSE, codebook = lbg({'Xy_refs': X_refs[:len(X_refs) // 10]},
                                    n_workers = args.n_workers,
                                    tolerance = 1.0e-4,
                                    codebook = numpy.random.randn(1, data['train']['X_sample'].shape[1]),
                                    max_n_clusters = args.max_components,
                                    max_iter = 300,
                                    models_dir = models_dir,
                                    verbose = 2)
            print('target class', tc, 'WSSSE', WSSSE, 'shape of the final codebook', codebook.shape)
            del X_refs

        for root, dirs, filenames in os.walk(models_dir):
            filenames.sort()
            for model_filename in [fn for fn in filenames if fn.endswith('.npy')]:
                with open(models_dir + '/' + model_filename, 'rb') as f:
                    codebook = numpy.load(f)
                    WSSSE = numpy.load(f)[0]
                    f.close()
                cb_size = len(codebook)
                if cb_size >= 10:
                    codebooks[tc][cb_size] = codebook
                    list_of_codebook_sizes.append(cb_size)
                # if
            # for model_ 
        # for root
    # for tc
    if args.do_train:
        print(f"computing kmeans for {args.technique} required {time.time() - t0} seconds", flush = True)

    ball_trees = dict()
    for cb_size in numpy.unique(list_of_codebook_sizes):
        _x_ = list()
        _y_ = list()
        for tc in target_classes:
            _x_.append(codebooks[tc][cb_size])
            _y_.append(numpy.ones(cb_size, dtype = int) * int(tc))
        X_train = numpy.vstack(_x_)
        del _x_
        y_train = numpy.hstack(_y_)
        del _y_

        ball_trees[cb_size] = BallTree(min_samples_to_split = max(100, int(math.ceil(math.sqrt(cb_size)))))
        ball_trees[cb_size].fit(X_train, y_train)

    print(f"training with {args.technique} required {time.time() - t0} seconds", flush = True)

    if args.do_inference:
        for subset in ('test', ): # ('train', 'test'):
            for cb_size in numpy.unique(list_of_codebook_sizes):
                if args.technique == 'knn':
                    t0 = time.time()
                    futures = [ray_knn_predict.remote(_Xy_ref_, ball_trees[cb_size], args.K, args.block_size) for _Xy_ref_ in data[subset]['Xy_refs']]
                    cm = sum(ray.get(futures))
                    print(f"predicting with {args.technique} using a codebook of {cb_size} clusters and K = {args.K} for {subset} subset required {time.time() - t0} seconds", flush = True)
                elif args.technique == 'kde':
                    t0 = time.time()
                    futures = [ray_kde_predict.remote(_Xy_ref_, ball_trees[cb_size], args.K, args.bandwidth, args.block_size) for _Xy_ref_ in data[subset]['Xy_refs']]
                    cm = sum(ray.get(futures))
                    print(f"predicting with {args.technique} using a codebook of {cb_size} clusters and bandwidth = {args.bandwidth} for {subset} subset required {time.time() - t0} seconds", flush = True)
                else:
                    raise Exception(f'Unssuported technique {args.technique}')
                print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1], digits = 3), flush = True)
            # for
        # for
    # if args.do_inference

    del codebooks
    del ball_trees
    for subset in ('train', 'test'):
        del data[subset]
    del data

    print('Bye!!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'test_kdeknn.py',
                description = 'Testing KDE or KNN',
                epilog = 'That\'s all folks!!!')
    parser.add_argument('--n-workers', dest = 'n_workers', type = int, default = 5, help = 'Number of workers in the cluster')
    parser.add_argument('--n-threads', dest = 'n_threads', type = int, default = 1, help = 'Number of threads per the worker')
    parser.add_argument('--cluster-type', dest = 'cluster_type', type = str, default = 'local', help = 'Cluster type to use. One of local, ssh and kubernetes')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000, help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--technique',    dest = 'technique',    type = str, default = 'kmeans', help = 'Clustering / Density estimation technique: kmeans or gmm')
    parser.add_argument('--models-dir',   dest = 'models_dir',   type = str, default = 'models', help = 'Models dir where to save or load the models')
    parser.add_argument('--max-components', dest = 'max_components',  type = int, default = 512, help = 'Max number of components in KMeans codebook or GMM')
    parser.add_argument('--K', dest = 'K',  type = int, default = 3, help = 'K nearest neighbours')
    parser.add_argument('--bandwidth', dest = 'bandwidth',  type = float, default = 1, help = 'Bandwidth to apply KDE on the K nearest neighbours')
    parser.add_argument('--pca-components', dest = 'pca_components',  type = int, default = 0, help = 'Greater than zero PCA is applied, otherwise samples are kept in the original input space')
    parser.add_argument('--do-train', dest = 'do_train', action = 'store_true', help = 'Whether to run train procedure')
    parser.add_argument('--do-not-train', dest = 'do_train', action = 'store_false', help = 'Whether to run train procedure')
    parser.add_argument('--do-inference', dest = 'do_inference', action = 'store_true', help = 'Whether to evaluate the performance')
    parser.add_argument('--do-not-inference', dest = 'do_inference', action = 'store_false', help = 'Whether to evaluate the performance ')
    parser.set_defaults(do_train = True)
    parser.set_defaults(do_inference = True)

    main(parser.parse_args())
