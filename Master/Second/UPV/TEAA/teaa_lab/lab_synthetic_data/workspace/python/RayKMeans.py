import os
import sys
import time
import numpy
import pandas
import ray

from sklearn.metrics.pairwise import euclidean_distances

@ray.remote
def ray_sample(_ref_, n):
    X_chunk = _ref_['X']
    return X_chunk[numpy.random.choice(len(X_chunk), n, replace = False)].copy()

@ray.remote
def ray_compute_cluster_stats(_ref_, centroids, block_size):
    counts = numpy.zeros(len(centroids))
    sums = numpy.zeros_like(centroids)
    wssse = 0
    X_chunk = _ref_['X']
    X_chunks_of_chunk = numpy.array_split(X_chunk, max(1, len(X_chunk) // block_size))
    for X_chunk_chunk in X_chunks_of_chunk:
        if len(X_chunk_chunk.shape) == 1:
            X_chunk_chunk = X_chunk_chunk.reshape(1, -1)

        distances = euclidean_distances(X_chunk_chunk, centroids, squared = True)
        labels = numpy.argmin(distances, axis = 1)

        for i in range(len(centroids)):
            mask = (labels == i)
            _counts_i_ = mask.sum()
            wssse += ((X_chunk_chunk[mask, :] - centroids[i]) ** 2).sum()
            if _counts_i_ > 0:
                sums[i] += X_chunk_chunk[mask].sum(axis = 0)
                counts[i] += _counts_i_
        #
    #
    return counts, sums, wssse

def cpu_compute_cluster_stats(_ref_, centroids, block_size):
    counts = numpy.zeros(len(centroids))
    sums = numpy.zeros_like(centroids)
    wssse = 0
    X_chunk = _ref_['X']
    X_chunks_of_chunk = numpy.array_split(X_chunk, max(1, len(X_chunk) // block_size))
    for X_chunk_chunk in X_chunks_of_chunk:
        if len(X_chunk_chunk.shape) == 1:
            X_chunk_chunk = X_chunk_chunk.reshape(1, -1)

        distances = euclidean_distances(X_chunk_chunk, centroids, squared = True)
        labels = numpy.argmin(distances, axis = 1)

        for i in range(len(centroids)):
            mask = (labels == i)
            _counts_i_ = mask.sum()
            wssse += ((X_chunk_chunk[mask, :] - centroids[i]) ** 2).sum()
            if _counts_i_ > 0:
                sums[i] += X_chunk_chunk[mask].sum(axis = 0)
                counts[i] += _counts_i_
        #
    #
    return counts, sums, wssse


class RayKMeans:
    """
        Class to implement Lloyd algorithm to adjust `n_clusters` centroids
        given the input data.

        It is assumed the input data will be a numpy nd-array that will be
        split in the `fit()` method.

        Be carefull that the split + ray.put() duplicates data in RAM memory,
        what can be an important problem in computers where the distribution
        of the computation will be done locally using the cores of a multicore
        CPU.
    """
    def __init__(self, n_clusters, n_workers,
                    n_init = 1,
                    tolerance = 1.0e-6,
                    max_iter = 1000,
                    verbose = 0,
                    block_size = 1000,
                    codebook = None):
        #
        self.n_clusters = n_clusters
        self.n_workers = n_workers
        self.n_init = n_init
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.verbose = verbose
        self.block_size = block_size
        #
        self.cluster_centers_ = codebook
        #
        self.wssse_ = numpy.inf
        self.n_iter_ = -1
        self.n_features_in = -1
        self.seconds_per_iteration_ = 0
        #

    def fit(self, X):
        """
            Runs Lloyd algorithm for the indicated number of iterations leaving
            the cluster centers corresponding to lower WSSSE.

            This method assumes the programmer already initialised the Ray
            environment by means of invoking `ray.init()`

            X can be a numpy.ndarray or a list of numpy refs created by Ray

            So this method is agnostic about whether it is running on Ray 
        """
        if type(X) == numpy.ndarray:
            if len(X) > 2 * self.block_size:
                X_refs = [{'X': _x_} for _x_ in numpy.array_split(X, len(X) // self.block_size)]
            elif len(X) > self.block_size:
                X_refs = [{'X': _x_} for _x_ in numpy.array_split(X, 2)]
            else:
                X_refs = [{'X': X}]
        else:
            X_refs = X # we assume X is already a list of numpy remote references in RAY system memory

        # Repeat the process according to the number of initialisations indicated by the programmer
        if self.cluster_centers_ is None:
            for _ in range(self.n_init):
                if self.verbose > 0:
                    print(f"Initialisaton {_ + 1} starts for {self.n_clusters} clusters ...", flush = True)
                
                # Initialize random centroids
                if type(X) == numpy.ndarray:
                    centroids = X[numpy.random.choice(len(X), self.n_clusters, replace = False)] # This will fail if working on RAY
                else:
                    n = 1 + self.n_clusters // len(X_refs)
                    futures = [ray_sample.remote(_ref_, n) for _ref_ in X_refs]
                    results = numpy.vstack(ray.get(futures))
                    centroids = results[numpy.random.choice(len(results), self.n_clusters, replace = False)]

                if self.verbose > 0:
                    print(f"Starting Lloyd for {self.n_clusters} clusters ...", flush = True)
                seconds, iteration_counter, wssse = self.lloyd(centroids, X_refs)

                if wssse < self.wssse_:
                    self.wssse_ = wssse
                    self.n_iter_ = iteration_counter
                    self.seconds_per_iteration_ = seconds / iteration_counter
                    self.cluster_centers_ = centroids
                #
            #
        else:
            if self.verbose > 0:
                print(f"Starting Lloyd for {self.n_clusters} clusters ...", flush = True)
            seconds, iteration_counter, wssse = self.lloyd(self.cluster_centers_, X_refs)
            self.wssse_ = wssse
            self.n_iter_ += iteration_counter
            self.seconds_per_iteration_ = seconds / iteration_counter

        return self


    def lloyd(self, centroids, X_refs):
        # Run iterations
        starting_time = time.time()
        iteration_counter = 0
        previous_wssse = 0
        total_wssse = 0
        while True:
            t0 = time.time()
            if self.n_workers >= 1:
                futures = [ray_compute_cluster_stats.remote(X_ref, centroids, self.block_size) for X_ref in X_refs]
                results = ray.get(futures)
            else:
                results = [cpu_compute_cluster_stats(X_ref, centroids, self.block_size) for X_ref in X_refs]
            
            total_counts = numpy.zeros(self.n_clusters)
            total_sums = numpy.zeros_like(centroids)
            total_wssse = 0
            for counts, sums, wssse in results:
                total_counts += counts
                total_sums += sums
                total_wssse += wssse

            iteration_counter += 1

            # Avoid divide-by-zero
            nonzero = total_counts > 0
            centroids[nonzero] = total_sums[nonzero] / total_counts[nonzero].reshape(-1, 1)
            change = abs((total_wssse - previous_wssse) / total_wssse)
            if self.verbose > 1:
                print(f"Iteration {iteration_counter} done with WSSSE = {total_wssse:.3f} and change = {change:.8e} lasting {time.time() - t0:.6f} seconds", flush = True)

            if self.max_iter > 0 and iteration_counter >= self.max_iter:
                print(f"Max iterations reached: {iteration_counter}, Lloyd algorithm did not converge!", flush = True)
                break
            if change < self.tolerance:
                break
            
            previous_wssse = total_wssse
        #
        return time.time() - starting_time, iteration_counter, total_wssse

    def transform(self, X):
        if type(X) == numpy.ndarray:
            distances = list()
            X_chunks = numpy.array_split(X, max(1, len(X) // self.block_size))
            for X_chunk in X_chunks:
                distances.append(euclidean_distances(X_chunk, self.cluster_centers_, squared = False))
            return numpy.vstack(distances)
        else: # we assume X is a list of numpy remote references
            futures = [ray_transform.remote(X_ref, self.cluster_centers_, self.block_size) for X_ref in X]
            results = ray.get(futures)
            return numpy.vstack(results)

    def predict(self, X):
        if type(X) == numpy.ndarray:
            true_labels = None
            predicted_clusters = list()
            X_chunks = numpy.array_split(X, max(1, len(X) // self.block_size))
            for X_chunk in X_chunks:
                predicted_clusters.append(numpy.argmin(euclidean_distances(X_chunk, self.cluster_centers_, squared = True), axis = 1).reshape(-1, 1))
            return numpy.vstack(predicted_clusters), true_labels
        else: # we assume X is a list of numpy remote references
            futures = [ray_predict.remote(X_ref, self.cluster_centers_, self.block_size) for X_ref in X]
            results = ray.get(futures)
            true_labels = list()
            predicted_clusters = list()
            for _pc_, _tl_ in results:
                true_labels.append(_tl_)
                predicted_clusters.append(_pc_)
            return numpy.vstack(predicted_clusters), numpy.vstack(true_labels)
# --------------------------------------------------------------------------------------------------------------------------------------
@ray.remote
def ray_predict(_ref_, centroids, block_size):
    true_labels = _ref_['y'].reshape(-1, 1)
    predicted_clusters = list()
    X = _ref_['X']
    X_chunks = numpy.array_split(X, max(1, len(X) // block_size))
    for X_chunk in X_chunks:
        predicted_clusters.append(numpy.argmin(euclidean_distances(X_chunk, centroids, squared = True), axis = 1).reshape(-1, 1))
    return numpy.vstack(predicted_clusters), true_labels
# --------------------------------------------------------------------------------------------------------------------------------------
@ray.remote
def ray_transform(_ref_, centroids, block_size):
    distances = list()
    X = _ref_['X']
    X_chunks = numpy.array_split(X, max(1, len(X) // block_size))
    for X_chunk in X_chunks:
        distances.append(euclidean_distances(X_chunk, centroids, squared = False))
    return numpy.vstack(distances)
# --------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',    default = 0, type = int, help = 'Verbosity level')
    #
    parser.add_argument('--n_workers',  default = 1, type = int, help = 'Number of jobs to run using joblib or other approach. With no effect when launching in a Spark cluster')
    parser.add_argument('--n_clusters', default = 100, type = int, help = 'Number of clusters for KMeans')
    #parser.add_argument('--n_samples',  default = 1_000_000, type = int, help = 'Number of samples')
    #parser.add_argument('--n_features', default = 11, type = int, help = 'Number of features')
    parser.add_argument('--n_init',     default = 1, type = int, help = 'Number of initialisations')

    args = parser.parse_args()

    print(f"Run with configuration: {args}", flush = True)

    # Code for testing the class RayKMeans
    if args.n_workers >= 1: ray.init(num_cpus = args.n_workers)
    t0 = time.time()
    df = pandas.read_parquet("/data/synthetic_data/parquet.test")
    X = df[df.columns[:-1]].to_numpy()
    del df
    print(f"read_parquet(): loaded {len(X)} samples of {X.shape[1]} features in {time.time() - t0:.6f} seconds.", flush = True)
    #sys.exit(0)

    if args.n_workers >= 1:
        X_refs = [ray.put({'X': chunk}) for chunk in numpy.array_split(X, 10)]
    else:
        X_refs = [{'X': chunk} for chunk in numpy.array_split(X, 10)]

    kmeans = RayKMeans(n_clusters = args.n_clusters, n_workers = args.n_workers, n_init = args.n_init, tolerance = 1.0e-4, verbose = args.verbose)
    kmeans.fit(X_refs)

    distances = kmeans.transform(X_refs)
    print('distances.shape =', distances.shape)

    print(f"WSSSE: {kmeans.wssse_:.3f}  reached at iteration {kmeans.n_iter_} using {kmeans.seconds_per_iteration_:.6f} seconds per iteration", flush = True)
    """
    k_pred = kmeans.predict(X[:10])
    print(k_pred.shape)
    print(k_pred)
    k_dist = kmeans.transform(X[:10])
    print(k_dist.shape)
    print(k_dist)
    """
