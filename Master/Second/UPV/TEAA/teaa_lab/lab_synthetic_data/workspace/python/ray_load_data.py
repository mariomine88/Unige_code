from typing import Dict
import numpy
import pandas
import ray

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
def ray_load_data(args, use_pandas = False):
    # BEGIN: Loading data
    # we have to provide the list of the attributes/columns representing the input space
    # and the same for the output space
    #
    pca = None
    data = {'train': None, 'test': None}
    x_columns = [f'x{i + 1:02d}' for i in range(20)]
    for subset in ('train', 'test'):
        if args.n_workers >= 1 and not use_pandas:
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
            print(f"{subset} data partitioned into {len(Xy_refs)} chunks")
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
    data['X_dim'] = data['train']['X_sample'].shape[1]
    data['target_classes'] = [0, 1]
    #
    return data
    # END: Loading data
