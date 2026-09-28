import time
import ray
import numpy

# ----------------------------------------------------------------------------------------------------
def gaussian_pdf(X, mean, cov):
    D = X.shape[1]
    diff = X - mean
    if len(cov.shape) == 2: # full covariance matrices
        try:
            inv_cov = numpy.linalg.pinv(cov)
        except Exception(e):
            print('Try to use diagonal covariance matrices for this dataset')
            raise Exception(e)
        exponent = -0.5 * numpy.sum(diff @ inv_cov * diff, axis = 1)
        sign, logdet = numpy.linalg.slogdet(cov)
        assert sign > 0
        #norm_const = 1.0 / numpy.sqrt((2 * numpy.pi) ** D * numpy.linalg.det(cov))
        norm_const = 1.0 / numpy.sqrt((2 * numpy.pi) ** D * sign * numpy.exp(logdet))
    elif len(cov.shape) == 1: # diagonal covariance matrices
        exponent = -0.5 * numpy.sum((diff ** 2) / cov, axis = 1)
        norm_const = 1.0 / numpy.sqrt((2 * numpy.pi) ** D * numpy.prod(cov))
    else:
        raise Exception("gaussian_pdf(): incompatible covariance matrix")
    return norm_const * numpy.exp(exponent)
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
def local_e_step(X, means, covs, weights):
    N, D = X.shape
    K = len(means)
    gamma = numpy.zeros((N, K))

    for k in range(K):
        gamma[:, k] = weights[k] * gaussian_pdf(X, means[k], covs[k])

    likelihoods = numpy.maximum(gamma.sum(axis = 1), 1.0e-200)  # prevent log(0)
    log_likelihood = numpy.sum(numpy.log(likelihoods))

    gamma /= likelihoods[:, None]

    Nk = gamma.sum(axis = 0)
    means_sum = gamma.T @ X

    if len(covs[0].shape) == 2: # full covariance matrices
        covs_sum = [numpy.zeros((D, D)) for _ in range(K)]
        for k in range(K):
            diff = X - means[k]
            weighted_outer = (gamma[:, k][:, None] * diff).T @ diff
            covs_sum[k] += weighted_outer
    elif len(covs[0].shape) == 1: # diagonal covariance matrices
        covs_sum = [numpy.zeros(D) for _ in range(K)]
        for k in range(K):
            diff = X - means[k]
            weighted_inner = gamma[:, k][:, None] * (diff ** 2)
            #covs_sum[k] += weighted_inner
            covs_sum[k] += weighted_inner.sum(axis = 0)
    else:
        raise Exception("local_e_step(): incompatible covariance matrix")

    return Nk, means_sum, covs_sum, log_likelihood
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
@ray.remote
def ray_e_step(Xy_ref, means, covs, weights, block_size):
    if type(Xy_ref) == numpy.ndarray:
        X = Xy_ref
    else:
        X = Xy_ref['X']
    #
    return cpu_e_step(X, means, covs, weights, block_size)
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
def cpu_e_step(X, means, covs, weights, block_size):
    #
    n_features_in = X.shape[1]
    n_clusters = len(means)
    #
    X_chunks = numpy.array_split(X, max(1, len(X) // block_size))
    results = [local_e_step(X_chunk, means, covs, weights) for X_chunk in X_chunks]

    total_Nk = numpy.zeros(len(means))
    total_means_sum = numpy.zeros((len(means), n_features_in))
    if len(covs[0].shape) == 2: # full covariance matrices
        total_covs_sum = [numpy.zeros((n_features_in, n_features_in)) for _ in range(n_clusters)]
    else:
        total_covs_sum = [numpy.zeros(n_features_in) for _ in range(n_clusters)]
    total_ll = 0.0

    for Nk, means_sum, covs_sum, ll in results:
        total_Nk += Nk
        total_means_sum += means_sum
        total_ll += ll
        for k in range(n_clusters):
            total_covs_sum[k] += covs_sum[k]

    return total_Nk, total_means_sum, total_covs_sum, total_ll
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
@ray.remote
def ray_sample(_ref_, n):
    X_chunk = _ref_['X']
    if len(X_chunk) > n:
        return X_chunk[numpy.random.choice(len(X_chunk), n, replace = False)].copy()
    else:
        return X_chunk
# ----------------------------------------------------------------------------------------------------

class RayGMM:
    """
        Class to implement EM algorithm to adjust `n_clusters` means, covs and weights
        given the input data.

        It is assumed the input data will be a numpy nd-array that will be
        split in the `fit()` method.

        Be carefull that the split + ray.put() duplicates data in RAM memory,
        what can be an important problem in computers where the distribution
        of the computation will be done locally using the cores of a multicore
        CPU.
    """
    def __init__(self, n_clusters, n_workers, dim = -1, n_init = 1, tolerance = 1.0e-4, max_iter = 300, verbose = 0, covar_type = "full", block_size = 1000):
        self.n_clusters = n_clusters
        self.n_workers = n_workers
        self.n_init = n_init
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.verbose = verbose
        self.covar_type = covar_type
        self.block_size = block_size
        #
        self.means_ = None
        self.covs_ = None
        self.weights_ = None
        #
        self.log_likelihood_ = -numpy.inf
        self.n_iter_ = -1
        self.n_features_in = dim
        self.seconds_per_iteration_ = 0

    def fit(self, X):
        """
            Runs EM algorithm for the indicated number of iterations leaving
            the Gaussian means and covariances corresponding to lower log likelihood.

            This method assumes the programmer already initialised the Ray
            environment by means of invoking `ray.init()`
        """

        # Split into chunks for workers
        if type(X) == numpy.ndarray:
            if len(X) > 2 * self.block_size:
                if self.n_workers > 1:
                    X_refs = [ray.put({'X': _x_}) for _x_ in numpy.array_split(X, len(X) // self.block_size)]
                else:
                    X_refs = [_x_ for _x_ in numpy.array_split(X, len(X) // self.block_size)]
            elif len(X) > self.block_size:
                if self.n_workers > 1:
                    X_refs = [ray.put({'X': _x_}) for _x_ in numpy.array_split(X, 2)]
                else:
                    X_refs = [_x_ for _x_ in numpy.array_split(X, 2)]
            else:
                if self.n_workers > 1:
                    X_refs = [ray.put({'X': X})]
                else:
                    X_refs = [X]
        else:
            X_refs = X # we assume X is already a list of numpy remote references in RAY system memory

        # Repeat the process according to the number of initialisations indicated by the programmer
        self.log_likelihood_ = -numpy.inf
        for _ in range(self.n_init):
            if self.verbose > 0:
                print(f"Initialisaton {_ + 1} starts ...", flush = True)
                
            # Initialize random Gaussians
            weights = numpy.ones(self.n_clusters) / self.n_clusters
            # Initialize random centroids
            if type(X) == numpy.ndarray:
                means = X[numpy.random.choice(len(X), self.n_clusters, replace = False)] # This will fail if working on RAY
            else:
                futures = [ray_sample.remote(_ref_, self.n_clusters) for _ref_ in X_refs]
                results = numpy.vstack(ray.get(futures))
                means = results[numpy.random.choice(len(results), self.n_clusters, replace = False)]

            if self.covar_type == "full":
                covs = numpy.array([numpy.eye(self.n_features_in) for _ in range(self.n_clusters)])  # full covariances
            else:
                covs = numpy.array([numpy.ones(self.n_features_in) for _ in range(self.n_clusters)])  # diagonal covariances

            seconds, iteration_counter, log_likelihood, weights, means, covs = self.em_algorithm(weights, means, covs, X_refs)

            if log_likelihood > self.log_likelihood_:
                self.log_likelihood_ = log_likelihood
                self.n_iter_ = iteration_counter
                self.seconds_per_iteration_ = seconds / iteration_counter
                self.means_ = means
                self.covs_ = covs
                self.weights_ = weights
            #
        #
        return self


    def em_algorithm(self, weights, means, covs, X_refs):
        # --- EM iterations ---
        starting_time = time.time()
        prev_ll = -numpy.inf
        iteration_counter = 0
        while True:
            t0 = time.time()
            if self.n_workers >= 1 and type(X_refs[0]) != numpy.ndarray:
                futures = [ray_e_step.remote(X_ref, means, covs, weights, self.block_size) for X_ref in X_refs]
                results = ray.get(futures)
            else:
                results = [cpu_e_step(X_chunk, means, covs, weights, self.block_size) for X_chunk in X_refs]

            total_Nk = numpy.zeros(self.n_clusters)
            total_means_sum = numpy.zeros((self.n_clusters, self.n_features_in))
            if self.covar_type == "full":
                total_covs_sum = [numpy.zeros((self.n_features_in, self.n_features_in)) for _ in range(self.n_clusters)]
            else:
                total_covs_sum = [numpy.zeros(self.n_features_in) for _ in range(self.n_clusters)]

            total_ll = 0.0

            for Nk, means_sum, covs_sum, ll in results:
                total_Nk += Nk
                total_means_sum += means_sum
                total_ll += ll
                for k in range(self.n_clusters):
                    total_covs_sum[k] += covs_sum[k]

            weights = total_Nk / total_Nk.sum()
            means = total_means_sum / total_Nk[:, None]
            covs = [total_covs_sum[k] / total_Nk[k] for k in range(self.n_clusters)]

            #for k in range(self.n_clusters):
            #    print(k, 'sum(mean)', f"{means[k].sum():16.8e}", 'sum(cov)', f"{covs[k].sum():16.8e}", covs[k].min(), covs[k].max())

            self.n_features_in = means.shape[1]
            if self.covar_type == "full":
                min_diagonal_prod = 1.0e-8
                min_var = min_diagonal_prod ** (1.0 / self.n_features_in)
                for cov in covs:
                    for i in range(len(cov)):
                        #cov[i, i] = max(min_var, cov[i, i])
                        cov[i, i] += 1.0e-6
            else: 
                min_diagonal_prod = 1.0e-16
                min_var = min_diagonal_prod ** (1.0 / self.n_features_in)
                covs = [numpy.maximum(min_var, cov) for cov in covs]

            if total_ll != total_ll: # is NaN
                raise Exception("Try to use diagonal covariance matrices with this dataset")
            
            iteration_counter += 1
    
            change = (prev_ll - total_ll) / total_ll

            if self.verbose > 1:
                print(f"Iteration {iteration_counter}, {len(means)} components, log-likelihood: {total_ll:.2f}, change: {change:.7f}, time lapse: {time.time() - t0:.4f} seconds", flush = True)

            if self.max_iter > 0 and iteration_counter >= self.max_iter:
                print(f"Max iterations reached: {iteration_counter}, EM algorithm did not converge!", flush = True)
                break

            if numpy.abs(change) < self.tolerance:
                print(f"Converged at iteraton {iteration_counter}.")
                break

            prev_ll = total_ll

        return time.time() - starting_time, iteration_counter, total_ll, weights, means, covs


    def score_samples(self, X):
        gamma = numpy.zeros((len(X), self.n_clusters))

        for k in range(self.n_clusters):
            bs = self.block_size
            for i in range(0, len(gamma), bs):
                gamma[i:i + bs, k] = self.weights_[k] * gaussian_pdf(X[i:i + bs], self.means_[k], self.covs_[k])

        #return gamma.sum(axis = 1)
        return numpy.log(numpy.maximum(gamma.sum(axis = 1), 1.0e-200))


    def predict_proba(self, X):
        gamma = numpy.zeros((len(X), self.n_clusters))

        for k in range(self.n_clusters):
            bs = self.block_size
            for i in range(0, len(gamma), bs):
                gamma[i:i + bs, k] = self.weights_[k] * gaussian_pdf(X[i:i + bs], self.means_[k], self.covs_[k])

        likelihoods = numpy.maximum(gamma.sum(axis = 1), 1.0e-200)  # prevent log(0)
        gamma /= likelihoods[:, None]

        return gamma


    def predict(self, X):
        gamma = self.predict_proba(X)
        return numpy.argmax(gamma, axis = 1)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',    default = 2, type = int, help = 'Verbosity level')
    #
    parser.add_argument('--n_workers',  default = 1, type = int, help = 'Number of jobs to run using joblib or other approach')
    parser.add_argument('--n_clusters', default = 30, type = int, help = 'Number of clusters for GMM')
    parser.add_argument('--n_samples',  default = 100_000, type = int, help = 'Number of samples')
    parser.add_argument('--n_features', default = 50, type = int, help = 'Number of features')
    parser.add_argument('--n_init',     default = 1, type = int, help = 'Number of initialisations')
    parser.add_argument('--covar_type', default = "full", type = str, help = 'Covariance type [full or diag]')

    args = parser.parse_args()

    print(f"Run with configuration: {args}", flush = True)

    # Code for testing the class RayGMM
    from sklearn.datasets import make_blobs
    if args.n_workers > 1: ray.init(num_cpus = args.n_workers)
    X, _ = make_blobs(n_samples = args.n_samples, centers = args.n_clusters, n_features = args.n_features, random_state = 42)

    gmm = RayGMM(n_clusters = args.n_clusters, n_workers = args.n_workers, dim = X.shape[1], tolerance = 1.0e-5, n_init = args.n_init, verbose = args.verbose)
    gmm.fit(X)

    print(f"log-likelihood: {gmm.log_likelihood_:.3f}  reached at iteration {gmm.n_iter_} using {gmm.seconds_per_iteration_:.6f} seconds per iteration", flush = True)


    print(gmm.predict(X[:10]))
