import sys
import time
import numpy
import dask.bag as db

from sklearn.metrics.pairwise import euclidean_distances

from concurrent.futures._base import CancelledError

def lloyd_map(data, codebook):
    new_codebook = numpy.zeros(codebook.shape)
    counters = numpy.zeros(len(codebook))
    WSSSE = 0
    for _x_ in data:
        if type(_x_) == dict:
            x = _x_['X']
        else:
            x = _x_
        #
        if len(x.shape) == 2:
            distances = euclidean_distances(x, codebook, squared = True)
            predict = distances.argmin(axis = 1)
            WSSSE += distances.min(axis = 1).sum()
            for i, k in enumerate(predict):
                new_codebook[k, :] += x[i, :]
                counters[k] += 1
        elif len(x.shape) == 1:
            distances = euclidean_distances(x.reshape(1, -1), codebook, squared = True)
            k = distances[0].argmin()
            WSSSE += distances[0].min()
            new_codebook[k, :] += x
            counters[k] += 1
        else:
            assert False
        #
    #
    return [[counters, new_codebook, WSSSE]]

def lloyd_reduce(a, b):
    # a[0] counters
    # a[1] codebook
    # a[2] WSSSE
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def lloyd(bag : db.Bag,
          tolerance = 1.0e-5,
          max_iter = 300,
          codebook = None,
          verbose = 0
         ):
    #
    if verbose > 0:
        print('Starting Lloyd algorithm for a codebook with shape', codebook.shape, flush = True)
    #
    starting_time = time.time()
    old_WSSSE = 1
    delta_WSSSE = 1
    iteration = 1
    while iteration < max_iter and delta_WSSSE > tolerance:
        t0 = time.time()
        retries = 3
        while retries > 0:
            try:
                counters, new_codebook, WSSSE = bag.map_partitions(lloyd_map, codebook).fold(lloyd_reduce).compute()
                break
            except CancelledError as e:
                retries -= 1
                if retries == 0:
                    raise e
                print('KMeans.lloyd(): retrying after exception of type', type(e), 'pending retries:', retries, flush = True)
            except Exception as e:
                print('KMeans.lloyd():', type(e), flush = True)
                raise e
        """
        list_of_results = bag.map_partitions(lloyd_map, codebook).compute()
        counters = numpy.zeros(len(codebook))
        new_codebook = numpy.zeros(codebook.shape)
        WSSSE = 0
        for a, b, c in list_of_results:
            counters += a
            new_codebook += b
            WSSSE += c
        """
        counters = numpy.maximum(1, counters) # to avoid division by zero
        new_codebook = new_codebook / counters[:, None]
        shift = ((new_codebook - codebook) ** 2).sum()
        delta_WSSSE = abs(WSSSE - old_WSSSE) / max(WSSSE, old_WSSSE)
        old_WSSSE = WSSSE
        time_lapse = time.time() - t0
        codebook = new_codebook
        if verbose > 1 or verbose == 1 and iteration % 10 == 0:
            print(f'iteration: {iteration:4d}  WSSSE = {WSSSE:20.6f}  delta_WSSSE = {delta_WSSSE:12.8f}  shift = {shift:12.6f}  {time_lapse:10.6f} seconds', flush = True)
        iteration += 1
    if verbose > 0:
        print(f'Lloyd algorithm required {time.time() - starting_time:.6f} seconds converging for {len(codebook)} centroids', flush = True)
    return WSSSE, codebook
