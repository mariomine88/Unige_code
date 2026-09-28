import os
import sys
import time
import numpy
import dask.bag as db
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances

from lloyd import lloyd

from concurrent.futures._base import CancelledError

def lbg_map(data, codebook):
    variances = numpy.zeros(codebook.shape)
    counters = numpy.zeros(len(codebook))
    for _x_ in data:
        if type(_x_) == dict:
            x = _x_['X']
        else:
            x = _x_
        #
        if len(x.shape) == 2:
            if len(x) > 0:
                distances = euclidean_distances(x, codebook, squared = True)
                predict = distances.argmin(axis = 1)
                for i, k in enumerate(predict):
                    variances[k, :] += (x[i, :] - codebook[k, :]) ** 2
                    counters[k] += 1
        elif len(x.shape) == 1:
            distances = euclidean_distances(x.reshape(1, -1), codebook, squared = True)
            k = distances[0].argmin()
            variances[k, :] += (x[:] - codebook[k, :]) ** 2
            counters[k] += 1
        else:
            assert False
        #
    #
    return [[counters, variances]]

def lbg_reduce(a, b):
    # a[0] counters
    # a[1] variances
    return [a[0] + b[0], a[1] + b[1]]


def load_codebook(models_dir, cb_size):
    model_filename = f'{models_dir}/codebook_{cb_size:05d}.npy'
    if os.path.exists(model_filename):
        with open(model_filename, 'rb') as f:
            codebook = numpy.load(f)
            WSSSE = numpy.load(f)[0]
            f.close()
        return codebook, WSSSE
    else:
        return None, None

def save_codebook(models_dir, codebook, WSSSE):
    model_filename = f'{models_dir}/codebook_{len(codebook):05d}.npy'
    with open(model_filename, 'wb') as f:
        numpy.save(f, codebook)
        numpy.save(f, numpy.array([WSSSE]))
        f.close()
# ----------------------------------------------------------------

def lbg(bag : db.Bag,
        tolerance = 1.0e-5,
        max_iter = 300,
        codebook = None,
        max_n_clusters = None,
        verbose = 0,
        models_dir = 'models'
       ):
    #
    if verbose > 0:
        print('Starting LBG algorithm for a codebook with shape', codebook.shape, flush = True)
    #
    if max_n_clusters is None:
        max_n_clusters = len(codebook) * 2
    #
    _cb_ = None
    while len(codebook) <= max_n_clusters:
        if _cb_ is None:
            _cb_, _wssse_ = load_codebook(models_dir, len(codebook))
        #
        if _cb_ is None:
            WSSSE, codebook = lloyd(bag, tolerance, max_iter, codebook, verbose)
            save_codebook(models_dir, codebook, WSSSE)
        else:
            codebook = _cb_
            WSSSE = _wssse_
        #
        if len(codebook) >= max_n_clusters: break
        #
        _cb_, _wssse_ = load_codebook(models_dir, len(codebook) * 2)
        if _cb_ is not None:
            codebook = _cb_
            WSSSE = _wssse_
        else:
            retries = 3
            while retries > 0:
                try:
                    counters, variances = bag.map_partitions(lbg_map, codebook).fold(lbg_reduce).compute()
                    break
                except CancelledError as e:
                    retries -= 1
                    if retries == 0:
                        raise e
                    print('KMeans.lbg(): retrying after exception of type', type(e), 'pending retries:', retries, flush = True)
                except Exception as e:
                    print('KMeans.lbg():', type(e), flush = True)
                    raise e
            #
            counters = numpy.maximum(1, counters) # to avoid division by zero
            sigmas = numpy.sqrt(variances / counters[:, None])
            codebook = numpy.vstack([codebook + sigmas, codebook - sigmas])
    #
    return WSSSE, codebook
# ----------------------------------------------------------------
def lbg_local_cpu(X,
        tolerance = 1.0e-5,
        max_iter = 300,
        codebook = None,
        max_n_clusters = None,
        verbose = 0,
        models_dir = 'models'
       ):
    #
    if verbose > 0:
        print('Starting LBG algorithm for a codebook with shape', codebook.shape, flush = True)
    #
    if max_n_clusters is None:
        max_n_clusters = len(codebook) * 2
    #
    _cb_ = None
    while len(codebook) <= max_n_clusters:
        if _cb_ is None:
            _cb_, _wssse_ = load_codebook(models_dir, len(codebook))
        #
        if _cb_ is None:
            kmeans_model = KMeans(n_clusters = len(codebook), init = codebook, n_init = 1, tol = tolerance, max_iter = max_iter,algorithm = 'lloyd', verbose = verbose)
            kmeans_model.fit(X)
            codebook = kmeans_model.cluster_centers_
            WSSSE = kmeans_model.inertia_
            save_codebook(models_dir, codebook, WSSSE)
        else:
            codebook = _cb_
            WSSSE = _wssse_
        #
        if len(codebook) >= max_n_clusters: break
        #
        _cb_, _wssse_ = load_codebook(models_dir, len(codebook) * 2)
        if _cb_ is not None:
            codebook = _cb_
            WSSSE = _wssse_
        else:
            counters, variances = lbg_split_local_cpu(X, codebook)
            counters = numpy.maximum(1, counters) # to avoid division by zero
            sigmas = numpy.sqrt(variances / counters[:, None])
            codebook = numpy.vstack([codebook + sigmas, codebook - sigmas])
    #
    return WSSSE, codebook
# ----------------------------------------------------------------
def lbg_split_local_cpu(X, codebook):
    variances = numpy.zeros(codebook.shape)
    counters = numpy.zeros(len(codebook))

    BS = 1000
    for i in range(0, len(X), BS):
        x = X[i: i + BS]
        distances = euclidean_distances(x, codebook, squared = True)
        predict = distances.argmin(axis = 1)
        for i, k in enumerate(predict):
            variances[k, :] += (x[i, :] - codebook[k, :]) ** 2
            counters[k] += 1
        #
    #
    return counters, variances
