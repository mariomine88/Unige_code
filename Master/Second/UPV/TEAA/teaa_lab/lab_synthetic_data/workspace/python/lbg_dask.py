import os
import sys
import time
import numpy
import dask.bag as db
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
    while len(codebook) <= max_n_clusters:
        model_filename = f'{models_dir}/codebook_{len(codebook):04d}.npy'
        if os.path.exists(model_filename):
            with open(model_filename, 'rb') as f:
                codebook = numpy.load(f)
                WSSSE = numpy.load(f)[0]
                f.close()
        else:
            WSSSE, codebook = lloyd(bag, tolerance, max_iter, codebook, verbose)
            #
            with open(model_filename, 'wb') as f:
                numpy.save(f, codebook)
                numpy.save(f, numpy.array([WSSSE]))
                f.close()
            #
        #
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
