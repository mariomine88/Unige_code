from typing import Dict
import os
import sys
import time
import numpy
import argparse
import pandas
import ray

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics import confusion_matrix, classification_report

from RayKMeans import RayKMeans
from RayGMM import RayGMM

from lbg import lbg

# ----------------------------------------------------------------------------------------
@ray.remote
def ray_gmm_predict(_dict_, gmms, block_size):
    # gmms contains one GMM per target class
    # gmms is a dict where keys are the ids of target classes
    target_classes = list(gmms.keys())
    target_classes.sort()
    X = _dict_['X']
    y = _dict_['y']
    yt = list()
    yp = list()
    for i in range(0, len(X), block_size):
        yt += y[i : i + block_size].tolist()
        scores = [gmms[key].score_samples(X[i: i + block_size]) for key in target_classes]
        scores = numpy.vstack(scores).T
        yp += scores.argmax(axis = 1).tolist()
    return yt, yp, len(X)
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_compute_count(_dict_):
    X = _dict_['X']
    assert len(X.shape) == 2
    return X.shape[0]
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_compute_mean(_dict_):
    X = _dict_['X']
    assert len(X.shape) == 2
    return X.sum(axis = 0)
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_compute_covar(_dict_, mean, block_size):
    X = _dict_['X']
    assert len(X.shape) == 2
    covar = numpy.zeros([X.shape[1], X.shape[1]])
    for _x_ in X:
        d = (_x_ - mean.reshape(1, -1))
        covar += numpy.outer(d, d)
    return covar
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_apply_pca(_dict_, eigenvectors):
    X = _dict_['X']
    assert len(X.shape) == 2
    y = _dict_['y'] if 'y' in _dict_ else None
    _X_ = numpy.dot(X, eigenvectors)
    if y is not None:
        return {'X': _X_, 'y': y}
    else:
        return {'X': _X_}
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_filter_by_target_class(_dict_, class_id):
    X = _dict_['X']
    assert len(X.shape) == 2
    y = _dict_['y']
    return {'X': X[y == class_id]}
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

    # BEGIN: Loading data
    # we have to provide the list of the attributes/columns representing the input space
    # and the same for the output space
    #
    t0 = time.time()
    pca = None
    data = {'train': None, 'test': None}
    x_columns = [f'x{i + 1:02d}' for i in range(20)]
    for subset in ('train', 'test'):
        if args.n_workers >= 1:
            ds = ray.data.read_parquet(f'/data/synthetic_data/parquet.{subset}')
            ########################################################################################
            def map_batch_to_X_y(batch: Dict[str, numpy.ndarray]) -> Dict[str, numpy.ndarray]:
                X = numpy.array([batch[col] for col in x_columns]).T
                y = batch['y']
                return {'X': X, 'y': y}
            ########################################################################################
            mds = ds.map_batches(map_batch_to_X_y, zero_copy_batch = True).materialize()
            Xy_refs = mds.to_numpy_refs()
            data[subset] = {'Xy_refs': Xy_refs}            
            _sample_ = mds.take(2)
            data[subset]['X_sample'] = numpy.array([_['X'] for _ in _sample_])
            data[subset]['y_sample'] = numpy.array([_['y'] for _ in _sample_])
            del mds
            del _sample_
            # **********************************************
            futures = [ray_compute_count.remote(_ref_) for _ref_ in Xy_refs]
            results = ray.get(futures)
            num_samples = sum(results)
            # **********************************************
            if args.pca_components > 0:
                if subset == 'train':
                    futures = [ray_compute_mean.remote(_ref_) for _ref_ in Xy_refs]
                    results = ray.get(futures)
                    mean = numpy.vstack(results).sum(axis = 0) / num_samples
                    futures = [ray_compute_covar.remote(_ref_, mean, args.block_size) for _ref_ in Xy_refs]
                    results = ray.get(futures)
                    covar = sum(results) / num_samples
                    #
                    eigenvalues, eigenvectors = numpy.linalg.eig(covar)
                    print('eigenvalues', type(eigenvalues), eigenvalues.shape, flush = True)
                    print('eigenvectors', type(eigenvectors), eigenvectors.shape, flush = True)
                    sorted_indices = numpy.argsort(eigenvalues)[::-1]
                    eigenvalues = eigenvalues[sorted_indices]
                    eigenvectors = eigenvectors[:, sorted_indices]
                    total_variance = numpy.sum(eigenvalues)
                    explained_variance = eigenvalues / total_variance
                    print('explained_variance sorted', explained_variance, flush = True)
                    for i in range(1, len(explained_variance)):
                        explained_variance[i] = explained_variance[i] + explained_variance[i - 1]
                    print('explained_variance sorted accumulated', explained_variance, flush = True)
                #
                futures = [ray_apply_pca.remote(_ref_, eigenvectors[:, :args.pca_components]) for _ref_ in Xy_refs]
                for _ref_ in Xy_refs: del _ref_
                Xy_refs = futures
                data[subset] = {'Xy_refs': Xy_refs}            
                _ref_ = ray.get(Xy_refs[0])
                data[subset]['X_sample'] = _ref_['X']
                data[subset]['y_sample'] = _ref_['y']
            # **********************************************
        else:
            df = pandas.read_parquet(f'/data/synthetic_data/parquet.{subset}')
            X = df[x_columns].to_numpy()
            y = df['y'].to_numpy()
            del df
            num_samples = len(X)
            data[subset] = {'X': X, 'y': y}
            data[subset]['X_sample'] = X[:2, :]
            data[subset]['y_sample'] = y[:2]
            # **********************************************
            if args.pca_components > 0:
                if subset == 'train':
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components = args.pca_components)
                    pca.fit(X)

                if pca is not None:
                    _X_ = pca.transform(X)
                    del X
                    X = _X_
                    data[subset]['X'] = X
                    data[subset]['X_sample'] = X[:2, :]
            # **********************************************
        #
        print(f"{subset} shape: ({num_samples}, {data[subset]['X_sample'].shape[1]})")
    #
    target_classes = [0, 1]
    X_dim = data['train']['X_sample'].shape[1]
    #
    # END: Loading data

    if args.technique.lower() == 'kmeans':
        if args.do_train:
            os.makedirs(args.models_dir, exist_ok = True)
            WSSSE, codebook = lbg(data['train'], args.n_workers,
                                    tolerance = args.tolerance,
                                    codebook = numpy.random.randn(1, data['train']['X_sample'].shape[1]),
                                    max_n_clusters = args.max_components,
                                    max_iter = 300,
                                    models_dir = args.models_dir,
                                    block_size = args.block_size,
                                    verbose = 2)
            print(WSSSE, codebook.shape)

        if args.do_inference:
            # here do the classification
            for root, dirs, filenames in os.walk(args.models_dir):
                filenames.sort()
                for model_filename in [fn for fn in filenames if fn.endswith('.npy')]:
                    with open(args.models_dir + '/' + model_filename, 'rb') as f:
                        codebook = numpy.load(f)
                        WSSSE = numpy.load(f)[0]
                        f.close()
                    if len(codebook) <= 1: continue
                    
                    kmeans = RayKMeans(n_clusters = len(codebook), codebook = codebook, n_workers = args.n_workers)

                    t0 = time.time()
                    if 'Xy_refs' in data['train']:
                        k_pred, y_true = kmeans.predict(data['train']['Xy_refs']) # expected y_true and k_pred
                    else:
                        k_pred, y_true = kmeans.predict(data['train']['X']) # expected k_pred, but y_true to be None
                    if y_true is None:
                        y_true = data['train']['y']
                    labels = numpy.unique(y_true)

                    conditional_probabilities = numpy.zeros([len(labels), len(codebook)])
                    num_splits = max(1, len(k_pred) // args.block_size)
                    for label in labels:
                        for k_pred_chunk, y_true_chunk in zip(numpy.array_split(k_pred, num_splits), numpy.array_split(y_true, num_splits)):
                            _cond_k_pred_ = k_pred_chunk[y_true_chunk == label]
                            for k in range(len(codebook)):
                                conditional_probabilities[label, k] += (_cond_k_pred_ == k).sum()

                    assert conditional_probabilities.shape == (len(target_classes), len(codebook))
                    conditional_probabilities /= conditional_probabilities.sum(axis = 1).reshape(-1, 1)

                    for subset in ('train', 'test'):
                        if subset == 'test':
                            t0 = time.time()
                            if 'Xy_refs' in data['train']:
                                k_pred, y_true = kmeans.predict(data[subset]['Xy_refs'])
                            else:
                                k_pred, y_true = kmeans.predict(data[subset]['X'])
                        if y_true is None:
                            y_true = data[subset]['y']
                        #
                        num_splits = max(1, len(k_pred) // args.block_size)
                        y_pred = list()
                        for k_pred_chunk in numpy.array_split(k_pred, num_splits):
                            y_pred.append(numpy.argmax(conditional_probabilities[:, k_pred_chunk.flatten()].T, axis = 1).reshape(-1, 1))
                        y_pred = numpy.vstack(y_pred)
                        print(y_true.shape, k_pred.shape, conditional_probabilities.shape, y_pred.shape)
                        cm = confusion_matrix(y_true, y_pred, labels = labels)
                        print(f"predicting with {args.technique} using a codebook with {len(codebook)} clusters for {subset} subset required {time.time() - t0} seconds", flush = True)
                        print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                        print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1], digits = 3))
                    # for
                # for
            # for 
        # if args.do_inference
    elif args.technique.lower() == 'gmm':
        #
        list_of_num_components = [2 ** n for n in range(1 + int(numpy.log(args.max_components)/numpy.log(2)))]
        #            
        if args.do_train:
            for tc in target_classes:
                #
                X_refs = [ray_filter_by_target_class.remote(_Xy_, tc) for _Xy_ in data['train']['Xy_refs']]
                #
                models_dir = f'{args.models_dir}/target_class_{tc}'
                os.makedirs(models_dir, exist_ok = True)
                #
                for num_components in list_of_num_components:
                    gmm = RayGMM(n_clusters = num_components,
                                n_workers = args.n_workers,
                                covar_type = args.covar_type,
                                tolerance = args.tolerance,
                                dim = X_dim,
                                n_init = 1,
                                verbose = 2)
                    model_filename = f"{models_dir}/gmm_{num_components:04d}.npy"
                    if os.path.exists(model_filename):
                        with open(model_filename, 'rb') as f:
                            gmm.means_ = numpy.load(f)
                            gmm.covs_ = numpy.load(f)
                            gmm.weights_ = numpy.load(f)
                            (gmm.log_likelihood_, gmm.n_iter_, gmm.n_features_in, gmm.seconds_per_iteration_) = numpy.load(f)
                            f.close()
                    else:
                        gmm.fit(X_refs)
                        with open(model_filename, 'wb') as f:
                            numpy.save(f, gmm.means_)
                            numpy.save(f, gmm.covs_)
                            numpy.save(f, gmm.weights_)
                            numpy.save(f, [gmm.log_likelihood_, gmm.n_iter_, gmm.n_features_in, gmm.seconds_per_iteration_])
                            f.close()

        if args.do_inference:
            models_dict = dict()
            for num_components in list_of_num_components:
                models_dict[num_components] = dict()
                for tc in target_classes:
                    model_filename = f'{args.models_dir}/target_class_{tc}/gmm_{num_components:04d}.npy'
                    gmm = RayGMM(n_clusters = num_components,
                                n_workers = args.n_workers,
                                covar_type = args.covar_type,
                                tolerance = args.tolerance,
                                dim = X_dim,
                                n_init = 1,
                                verbose = 2)
                    with open(model_filename, 'rb') as f:
                        gmm.means_ = numpy.load(f)
                        gmm.covs_ = numpy.load(f)
                        gmm.weights_ = numpy.load(f)
                        (gmm.log_likelihood_, gmm.n_iter_, gmm.n_features_in, gmm.seconds_per_iteration_) = numpy.load(f)
                        f.close()
                    models_dict[num_components][tc] = gmm
                # for tc
                gmms = models_dict[num_components]
                #
                for subset in ('train', 'test'):
                    t0 = time.time()
                    futures = [ray_gmm_predict.remote(Xy_ref, gmms, args.block_size) for Xy_ref in data[subset]['Xy_refs']]
                    results = ray.get(futures)
                    y_true = list()
                    y_pred = list()
                    num_samples = 0
                    for yt, yp, count in results:
                        y_true += yt
                        y_pred += yp
                        num_samples += count
                    cm = confusion_matrix(y_true, y_pred, labels = [0, 1])
                    print(f"predicting with {args.technique} using a GMM with {num_components} components for {subset} subset required {time.time() - t0} seconds", flush = True)
                    print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                    print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1], digits = 3))
                #
            # for num_components
    else:
        print(f"Unknown technique {args.technique}. Then, nothing to do!!")

    for subset in ('train', 'test'):
        del data[subset]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'test_lbg.py',
                description = 'Testing LBG for KMeans or fit and split for GMM',
                epilog = 'That\'s all folks!!!')
    parser.add_argument('--n-workers', dest = 'n_workers', type = int, default = 5, help = 'Number of workers in the cluster')
    parser.add_argument('--n-threads', dest = 'n_threads', type = int, default = 1, help = 'Number of threads per the worker')
    parser.add_argument('--cluster-type', dest = 'cluster_type', type = str, default = 'local', help = 'Cluster type to use. One of local, ssh and kubernetes')
    parser.add_argument('--block-size',   dest = 'block_size',   type = int, default = 1000, help = 'Block size into which gather samples to speedup algebraic computations')
    parser.add_argument('--technique',    dest = 'technique',    type = str, default = 'kmeans', help = 'Clustering / Density estimation technique: kmeans or gmm')
    parser.add_argument('--covar-type',   dest = 'covar_type',   type = str, default = 'diagonal', help = 'Covariance matrix type for GMMs: diagonal or full')
    parser.add_argument('--gmm-filename', dest = 'gmm_filename', type = str, default = None, help = 'Filename with the GMM to start the fit and split process')
    parser.add_argument('--models-dir',   dest = 'models_dir',   type = str, default = 'models', help = 'Models dir where to save or load the models')
    parser.add_argument('--max-components', dest = 'max_components',  type = int, default = 1024, help = 'Max number of components in KMeans codebook or GMM')
    parser.add_argument('--pca-components', dest = 'pca_components',  type = int, default = 0, help = 'Greater than zero PCA is applied, otherwise samples are kept in the original input space')
    parser.add_argument('--tolerance', dest = 'tolerance',  type = float, default = 1.0e-4, help = 'Tolerance to consider clustering (KMeans or GMM) converged')
    parser.add_argument('--do-train', dest = 'do_train', action = 'store_true', help = 'Whether to run train procedure')
    parser.add_argument('--do-not-train', dest = 'do_train', action = 'store_false', help = 'Whether to run train procedure')
    parser.add_argument('--do-inference', dest = 'do_inference', action = 'store_true', help = 'Whether to evaluate the performance')
    parser.add_argument('--do-not-inference', dest = 'do_inference', action = 'store_false', help = 'Whether to evaluate the performance ')
    parser.set_defaults(do_train = True)
    parser.set_defaults(do_inference = True)

    main(parser.parse_args())
