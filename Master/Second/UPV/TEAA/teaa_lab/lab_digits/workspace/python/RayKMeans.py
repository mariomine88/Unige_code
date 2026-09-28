import os
import time
import numpy
import ray


@ray.remote
def ray_compute_cluster_stats(_ref_, centroids, block_size):
    if type(_ref_) == dict:
        X_chunk = _ref_['X']
    else:
        X_chunk = _ref_

    labels = numpy.hstack(
        [
            numpy.argmin(((X_chunk[i:i + block_size, None, :] - centroids[None, :, :]) ** 2).sum(axis = 2), axis = 1)
                for i in range(0, len(X_chunk), block_size)
        ]
    )
    counts = numpy.zeros(len(centroids))
    sums = numpy.zeros_like(centroids)
    wssse = 0
    for i in range(len(centroids)):
        mask = (labels == i)
        counts[i] = mask.sum()
        wssse += ((X_chunk[mask, :] - centroids[i]) ** 2).sum()
        if counts[i] > 0:
            sums[i] = X_chunk[mask].sum(axis = 0)
    return counts, sums, wssse

def cpu_compute_cluster_stats(_ref_, centroids, block_size):
    if type(_ref_) == dict:
        X_chunk = _ref_['X']
    else:
        X_chunk = _ref_

    labels = numpy.hstack(
        [
            numpy.argmin(((X_chunk[i:i + block_size, None, :] - centroids[None, :, :]) ** 2).sum(axis = 2), axis = 1)
                for i in range(0, len(X_chunk), block_size)
        ]
    )
    counts = numpy.zeros(len(centroids))
    sums = numpy.zeros_like(centroids)
    wssse = 0
    for i in range(len(centroids)):
        mask = (labels == i)
        counts[i] = mask.sum()
        wssse += ((X_chunk[mask, :] - centroids[i]) ** 2).sum()
        if counts[i] > 0:
            sums[i] = X_chunk[mask].sum(axis = 0)
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
    def __init__(self, n_clusters, n_workers, n_init = 1, tolerance = 1.0e-6, max_iter = 1000, block_size = 1000, verbose = 0):
        self.n_clusters = n_clusters
        self.n_workers = n_workers
        self.n_init = n_init
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.verbose = verbose
        self.block_size = block_size
        #
        self.cluster_centers_ = None
        #
        self.wssse_ = numpy.inf
        self.n_iter_ = -1
        self.n_features_in = -1
        self.seconds_per_iteration_ = 0

    def fit(self, X = None, X_refs = None):
        """
            Runs Lloyd algorithm for the indicated number of iterations leaving
            the cluster centers corresponding to lower WSSSE.

            This method assumes the programmer already initialised the Ray
            environment by means of invoking `ray.init()`
        """
        if X_refs is None:
            # Split into chunks for workers if not yet
            if self.n_workers > 1:
                X_chunks = numpy.array_split(X, self.n_workers)
                #X_refs = [ray.put(chunk) for chunk in X_chunks]
                X_refs = [ray.put({'X': chunk}) for chunk in X_chunks]
            else:
                #X_refs = [X]
                X_chunks = numpy.array_split(X, max(1, len(X) // 10_000))
                #X_refs = [chunk for chunk in X_chunks]
                X_refs = [ray.put({'X': chunk}) for chunk in X_chunks]
            # Distribute data to Ray
            # Repeat the process according to the number of initialisations indicated by the programmer

        for _ in range(self.n_init):
            if self.verbose > 0:
                print(f"Initialisation {_ + 1} starts ...", flush = True)
                
            # Initialize random centroids
            if X_refs is not None:
                @ray.remote
                def ray_random_choice(_dict_, K):
                    X = _dict_['X']
                    if K < len(X):
                        return X[numpy.random.choice(len(X), K, replace = False)]
                    else:
                        return X
                # --------------------------------------------------------------------------
                futures = [ray_random_choice.remote(_ref_, self.n_clusters) for _ref_ in X_refs]
                _X_ = numpy.vstack(ray.get(futures))
                centroids = _X_[numpy.random.choice(len(_X_), self.n_clusters, replace = False)]
                del _X_
            else:
                centroids = X[numpy.random.choice(len(X), self.n_clusters, replace = False)]

            seconds, iteration_counter, wssse = self.lloyd(centroids, X_refs)

            if wssse < self.wssse_:
                self.wssse_ = wssse
                self.n_iter_ = iteration_counter
                self.seconds_per_iteration_ = seconds / iteration_counter
                self.cluster_centers_ = centroids
            #
        #
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
                results = [cpu_compute_cluster_stats(X_chunk, centroids, self.block_size) for X_chunk in X_refs]
            
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

    def transform(self, X, squared = True):
        bs = self.block_size
        if squared:
            return numpy.vstack(
                [
                    ((X[i:i + bs, None, :] - self.cluster_centers_[None, :, :]) ** 2).sum(axis = 2)
                        for i in range(0, len(X), bs)
                ]
            )
        else:
            return numpy.vstack(
                [
                    numpy.sqrt(((X[i:i + bs, None, :] - self.cluster_centers_[None, :, :]) ** 2).sum(axis = 2))
                        for i in range(0, len(X), bs)
                ]
            )

    def predict(self, X):
        return numpy.argmin(self.transform(X, squared = True), axis = 1)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',    default = 2, type = int, help = 'Verbosity level')
    #
    parser.add_argument('--n_workers',  default = 1, type = int, help = 'Number of jobs to run using joblib or other approach. With no effect when launching in a Spark cluster')
    parser.add_argument('--n_clusters', default = 30, type = int, help = 'Number of clusters for KMeans')
    parser.add_argument('--n_samples',  default = 1_00_000, type = int, help = 'Number of samples')
    parser.add_argument('--n_features', default = 50, type = int, help = 'Number of features')
    parser.add_argument('--n_init',     default = 1, type = int, help = 'Number of initialisations')

    args = parser.parse_args()

    print(f"Run with configuration: {args}", flush = True)

    # Code for testing the class RayKMeans
    from sklearn.datasets import make_blobs
    if args.n_workers >= 1: ray.init(num_cpus = args.n_workers)
    X, _ = make_blobs(n_samples = args.n_samples, centers = args.n_clusters, n_features = args.n_features, random_state = 42)

    kmeans = RayKMeans(n_clusters = args.n_clusters, n_workers = args.n_workers, n_init = args.n_init, verbose = args.verbose)
    kmeans.fit(X)

    print(f"WSSSE: {kmeans.wssse_:.3f}  reached at iteration {kmeans.n_iter_} using {kmeans.seconds_per_iteration_:.6f} seconds per iteration", flush = True)
    """
    k_pred = kmeans.predict(X[:10])
    print(k_pred.shape)
    print(k_pred)
    k_dist = kmeans.transform(X[:10])
    print(k_dist.shape)
    print(k_dist)
    """
