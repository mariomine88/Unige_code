import os
import sys
import time
import numpy
import ray

from sklearn.metrics.pairwise import euclidean_distances

from RayKMeans import RayKMeans

@ray.remote
def ray_compute_variances(_dict_, codebook, block_size):
    variances = numpy.zeros(codebook.shape)
    counters = numpy.zeros(len(codebook))
    #
    X = _dict_['X']
    assert len(X.shape) == 2
    #
    for _x_ in numpy.array_split(X, max(1, len(X) // block_size)):
        #
        distances = euclidean_distances(_x_, codebook, squared = True)
        predict = distances.argmin(axis = 1)
        for k in range(len(codebook)):
            mask = (predict == k)
            _counter_ = sum(mask)
            if _counter_ > 0:
                variances[k] += ((_x_[mask] - codebook[k]) ** 2).sum(axis = 0)
                counters[k] += _counter_
        #
    #
    return counters, variances

def cpu_compute_variances(_dict_, codebook, block_size):
    variances = numpy.zeros(codebook.shape)
    counters = numpy.zeros(len(codebook))
    #
    X = _dict_['X']
    assert len(X.shape) == 2
    #
    for _x_ in numpy.array_split(X, max(1, len(X) // block_size)):
        #
        distances = euclidean_distances(_x_, codebook, squared = True)
        predict = distances.argmin(axis = 1)
        for k in range(len(codebook)):
            mask = (predict == k)
            _counter_ = sum(mask)
            if _counter_ > 0:
                variances[k] += ((_x_[mask] - codebook[k]) ** 2).sum(axis = 0)
                counters[k] += _counter_
        #
    #
    return counters, variances



def lbg(data,
        n_workers,
        tolerance = 1.0e-5,
        max_iter = 300,
        codebook = None,
        max_n_clusters = None,
        verbose = 0,
        models_dir = 'models',
        block_size = 1000
       ):
    #
    assert codebook is not None
    assert 'Xy_refs' in data.keys() or 'X' in data.keys()
    #
    _X_ = data['Xy_refs'] if 'Xy_refs' in data.keys() else data['X']
    #
    if verbose > 0:
        print('Starting LBG algorithm for a codebook with shape', codebook.shape, flush = True)
    #
    if max_n_clusters is None:
        max_n_clusters = len(codebook) * 2
    #
    model_filename = f'{models_dir}/codebook_{len(codebook):04d}.npy'
    if os.path.exists(model_filename): # override the codebook
        with open(model_filename, 'rb') as f:
            codebook = numpy.load(f)
            WSSSE = numpy.load(f)[0]
            f.close()
        print(f"loaded codebook of {len(codebook)} clusters", flush = True)
        do_fit = False
    else:
        do_fit = True
    #
    while len(codebook) <= max_n_clusters:
        kmeans = RayKMeans(n_clusters = len(codebook), n_workers = n_workers, n_init = 1, tolerance = tolerance, verbose = verbose)
        kmeans.cluster_centers_ = codebook
        #
        if do_fit: # use the codebook provided as input or the one generated in the previous iteration
            kmeans.fit(_X_)
            WSSSE = kmeans.wssse_
            codebook = kmeans.cluster_centers_
            #
            with open(model_filename, 'wb') as f:
                numpy.save(f, codebook)
                numpy.save(f, numpy.array([WSSSE]))
                f.close()
        #
        if len(codebook) >= max_n_clusters: break
        #
        # do the split only if the codebook didn't existed
        #
        model_filename = f'{models_dir}/codebook_{2 * len(codebook):04d}.npy'
        if os.path.exists(model_filename):
            with open(model_filename, 'rb') as f:
                codebook = numpy.load(f)
                WSSSE = numpy.load(f)[0]
                f.close()
                kmeans.cluster_centers_ = codebook
                kmeans.wssse_ = WSSSE
            print(f"loaded codebook of {len(codebook)} clusters", flush = True)
            do_fit = False
        else:
            # do the split
            t0 = time.time()
            if n_workers >= 1:
                futures = [ray_compute_variances.remote(X_ref, codebook, block_size) for X_ref in _X_]
                results = ray.get(futures)
            elif type(_X_) == numpy.ndarray:
                results = [cpu_compute_variances({'X': _X_}, codebook, block_size)]
            else:
                results = [cpu_compute_variances(X_chunk, codebook, block_size) for X_chunk in _X_]
        
            variances = numpy.zeros(codebook.shape)
            counters = numpy.zeros(len(codebook))
            for _counters_, _variances_ in results:
                counters += _counters_
                variances += _variances_
            #
            counters = numpy.maximum(1, counters) # to avoid division by zero
            sigmas = numpy.sqrt(variances / counters.reshape(-1, 1))
            codebook = numpy.vstack([codebook + sigmas, codebook - sigmas])
            print(f"split codebook up to {len(codebook)} clusters required {time.time() - t0:.6f} seconds", flush = True)
            do_fit = True
    #
    return WSSSE, codebook
