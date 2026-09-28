import os
import sys
import time
import numpy
import argparse
import dask
import dask.dataframe as dd
from dask.distributed import Client
from create_cluster import create_cluster
from dask_load_data import gather_samples, load_dask_dataframe, load_data_delayed, filter_by_target_class

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics import confusion_matrix, classification_report

from gmm import GMM
from lbg import lbg
from dask_mle import MLE

# ----------------------------------------------------------------------------------------
def pca_transform(data, eigenvectors):
    out = list()
    for _data_block_ in data:
        assert type(_data_block_) == dict
        x = numpy.dot(_data_block_['X'], eigenvectors)
        y = _data_block_['y']
        out.append({'X': x, 'y': y})
    return out
# ----------------------------------------------------------------------------------------
def compute_conditional_probabilities_map(data, codebook, K):
    counters = numpy.zeros([K, len(codebook)])
    for _data_block_ in data:
        assert type(_data_block_) == dict
        x = _data_block_['X']
        y = _data_block_['y'].flatten()
        #
        assert len(x.shape) == 2
        assert len(y.shape) == 1
        #
        distances = euclidean_distances(x, codebook, squared = True)
        predict = distances.argmin(axis = 1)
        for i, k in enumerate(predict):
            counters[int(y[i]), k] += 1
        #
    #
    return [counters]
# ----------------------------------------------------------------------------------------
def compute_conditional_probabilities_reduce(a, b):
    # a[0] is counters
    return a + b
# ----------------------------------------------------------------------------------------
def kmeans_predict(data, codebook, conditional_probabilities):
    count_00 = 0
    count_01 = 0
    count_10 = 0
    count_11 = 0
    for _data_block_ in data:
        assert type(_data_block_) == dict
        x = _data_block_['X']
        distances = euclidean_distances(x, codebook, squared = True)
        predict = distances.argmin(axis = 1)
        y = list()
        for k in predict:
            y.append(conditional_probabilities[:, k].copy())
        y = numpy.array(y)
        #
        a = _data_block_['y'].flatten()
        b = y.argmax(axis = 1).flatten()
        #
        c01 = sum(b[a == 0])
        c11 = sum(b[a == 1])
        c10 = sum(a) - c11
        c00 = len(a) - sum(a) - c01
        #
        count_01 += c01
        count_11 += c11
        count_10 += c10
        count_00 += c00
        #
    return [[count_00, count_01, count_10, count_11]]
# ----------------------------------------------------------------------------------------
def reduce_after_predict(a, b):
    # a[0] count_00
    # a[1] count_01
    # a[2] count_10
    # a[3] count_11
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]]
# ----------------------------------------------------------------------------------------
def gmm_predict(data, gmms, target_classes):
    count_00 = 0
    count_01 = 0
    count_10 = 0
    count_11 = 0
    for _data_block_ in data:
        assert type(_data_block_) == dict
        x = _data_block_['X']
        y = list()
        for c in target_classes:
            log_densities = gmms[c].log_densities_batch(x.T).T
            y.append(numpy.exp(log_densities).sum(axis = 1))
        y = numpy.vstack(y).T
        #
        a = _data_block_['y'].flatten()
        b = y.argmax(axis = 1).flatten()
        #
        c01 = sum(b[a == 0])
        c11 = sum(b[a == 1])
        c10 = sum(a) - c11
        c00 = len(a) - sum(a) - c01
        #
        count_01 += c01
        count_11 += c11
        count_10 += c10
        count_00 += c00
        #
    return [[count_00, count_01, count_10, count_11]]
# ----------------------------------------------------------------------------------------

def main(args):
    t0 = time.time()
    cluster = create_cluster(n_workers = args.n_workers, threads_per_worker = args.n_threads, cluster_type = args.cluster_type, connect_only = False)
    cluster.scale(args.n_workers)
    client = Client(cluster, asynchronous = False)
    #client = cluster.get_client()
    print()
    print()
    print('client ready after waiting', time.time() - t0, 'seconds', flush = True)
    print()
    print(cluster)
    print(client)
    print()
    client.upload_file('lloyd.py')
    client.upload_file('lbg.py')
    client.upload_file('gmm.py')
    client.upload_file('dask_mle.py')
    client.upload_file('dask_load_data.py')

    # BEGIN: Loading data
    # we have to provide the list of the attributes/columns representing the input space
    # and the same for the output space
    #
    t0 = time.time()
    data = {'train': None, 'test': None}
    for subset in ('train', 'test'):
        df = client.submit(load_dask_dataframe, f'/data/synthetic_data/parquet.{subset}').result()
        if args.pca_components > 0:
            if subset == 'train':
                x_darray = df[[f'x{i + 1:02d}' for i in range(20)]].to_dask_array(lengths = True)
                print(type(x_darray), x_darray.shape, flush = True)
                covar = dask.array.cov(x_darray, rowvar = False)
                print(type(covar), covar.shape, flush = True)
                eigenvalues, eigenvectors = numpy.linalg.eig(covar.compute())
                print(type(eigenvalues), eigenvalues.shape, flush = True)
                print(type(eigenvectors), eigenvectors.shape, flush = True)
                sorted_indices = numpy.argsort(eigenvalues)[::-1]
                eigenvalues = eigenvalues[sorted_indices]
                eigenvectors = eigenvectors[:, sorted_indices]
                total_variance = numpy.sum(eigenvalues)
                explained_variance = eigenvalues / total_variance
                print(explained_variance, flush = True)
                for i in range(1, len(explained_variance)):
                    explained_variance[i] = explained_variance[i] + explained_variance[i - 1]
                print(explained_variance, flush = True)

            data[subset] = df.to_bag(format = 'dict').map_partitions(gather_samples, args.block_size).map_partitions(pca_transform, eigenvectors[:, :args.pca_components]).persist()
        else:
            data[subset] = df.to_bag(format = 'dict').map_partitions(gather_samples, args.block_size).persist()

    sample = data['train'].take(1)[0]
    input_dim = sample['X'].shape[1]
    print('train shape', sample['X'].shape, sample['y'].shape)
    sample = data['test'].take(1)[0]
    print('test shape', sample['X'].shape, sample['y'].shape)
    print(f"taking one sample from a dask bag, actual data loading and transformation, required {time.time() - t0:.6f} seconds", flush = True)
    print(f"loading data required {time.time() - t0:.6f} seconds", flush = True)
    target_classes = [0, 1]
    #
    # END: Loading data

    if args.technique.lower() == 'kmeans':
        if args.do_train:
            os.makedirs(args.models_dir, exist_ok = True)
            WSSSE, codebook = lbg(data['train'],
                                    tolerance = 1.0e-4,
                                    codebook = numpy.random.randn(1, input_dim),
                                    max_n_clusters = args.max_components,
                                    max_iter = 300,
                                    models_dir = args.models_dir,
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
                    conditional_probabilities = data['train'].map_partitions(compute_conditional_probabilities_map, codebook, len(target_classes)).fold(compute_conditional_probabilities_reduce).compute()
                    #print(conditional_probabilities.shape, flush = True)
                    #print(conditional_probabilities, flush = True)
                    assert conditional_probabilities.shape == (len(target_classes), len(codebook))
                    conditional_probabilities /= conditional_probabilities.sum(axis = 1).reshape(-1, 1)

                    for subset in ('train', 'test'):
                        t0 = time.time()
                        cm = data[subset].map_partitions(kmeans_predict, codebook, conditional_probabilities).fold(reduce_after_predict, initial = [0, 0, 0, 0]).compute()
                        cm = numpy.array([[int(cm[0]), int(cm[1])], [int(cm[2]), int(cm[3])]])
                        print(f"predicting with {args.technique} using a codebook with {len(codebook)} clusters for {subset} subset required {time.time() - t0} seconds", flush = True)
                        print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                        print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1]))
                    # for
                # for
            # for 
        # if args.do_inference
    elif args.technique.lower() == 'gmm':
        if args.do_train:
            for tc in target_classes:
                X = data['train'].map_partitions(filter_by_target_class, tc).persist()
                models_dir = f'{args.models_dir}/target_class_{tc}'
                os.makedirs(models_dir, exist_ok = True)
                mle = MLE(covar_type = args.covar_type,
                        min_var = 1.0e-5 if args.covar_type == 'diagonal' else 0.1,
                        dim = input_dim,
                        log_dir = models_dir,
                        models_dir = models_dir)
                #
                if args.gmm_filename is not None:
                    mle.gmm.load_from_text(args.gmm_filename)
                else:
                    for root, dirs, filenames in os.walk(models_dir):
                        filenames.sort()
                        filenames = [fn for fn in filenames if fn.endswith('.txt')]
                        if len(filenames) > 0:
                            mle.gmm.load_from_text(models_dir + '/' + filenames[-1])
                        #
                    #
                #
                mle.fit_and_split(samples = X, max_components = args.max_components, epsilon = 1.0e-4)
                del X

        if args.do_inference:
            models_dict = dict()
            list_n_components = list()
            for tc in target_classes:
                models_dict[tc] = dict()
                models_dir = f'{args.models_dir}/target_class_{tc}'
                for root, dirs, filenames in os.walk(models_dir):
                    filenames = [f'{models_dir}/{fn}' for fn in filenames if fn.endswith('.txt')]
                    filenames.sort()
                    for fn in filenames:
                        gmm = GMM()
                        gmm.load_from_text(fn)
                        models_dict[tc][gmm.n_components] = gmm
                        list_n_components.append(gmm.n_components)
                    #
                #
            #
            list_n_components = numpy.unique(list_n_components).tolist()
            #
            for nc in list_n_components:
                if nc <= args.max_components:
                    gmms = dict()
                    for tc in target_classes:
                        for key in sorted(models_dict[tc].keys()):
                            if key <= nc:
                                gmms[tc] = models_dict[tc][key]
                            else:
                                break
                    #
                    for subset in ('train', 'test'):
                        t0 = time.time()
                        cm = data[subset].map_partitions(gmm_predict, gmms, target_classes).fold(reduce_after_predict, initial = [0, 0, 0, 0]).compute()
                        cm = numpy.array([[int(cm[0]), int(cm[1])], [int(cm[2]), int(cm[3])]])
                        print(f"predicting with {args.technique} using a GMM with a maximum of {nc} components for {subset} subset required {time.time() - t0} seconds", flush = True)
                        print(f'  {cm[0,0]:10d}  {cm[0,1]:10d}\n  {cm[1,0]:10d}  {cm[1,1]:10d}\n')
                        print(classification_report([0, 0, 1, 1], [0, 1, 0, 1], sample_weight = cm.flatten(), labels = [0, 1]))
                    #
                #
            # 
    else:
        print(f"Unknown technique {args.technique}. Then, nothing to do!!")

    for subset in ('train', 'test'):
        del data[subset]

    print()
    print(cluster)
    print(client)
    print()
    client.close()
    if cluster is not None: cluster.close()


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
    parser.add_argument('--do-train', dest = 'do_train', action = 'store_true', help = 'Whether to run train procedure')
    parser.add_argument('--do-not-train', dest = 'do_train', action = 'store_false', help = 'Whether to run train procedure')
    parser.add_argument('--do-inference', dest = 'do_inference', action = 'store_true', help = 'Whether to evaluate the performance')
    parser.add_argument('--do-not-inference', dest = 'do_inference', action = 'store_false', help = 'Whether to evaluate the performance ')
    parser.set_defaults(do_train = True)
    parser.set_defaults(do_inference = True)

    main(parser.parse_args())
