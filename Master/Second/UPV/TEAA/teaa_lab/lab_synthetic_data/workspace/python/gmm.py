"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 3.0
    Date: February 2022
    Universitat Politecnica de Valencia
    Technical University of Valencia TU.VLC

    Gaussian Mixture Models

"""

import os
import sys
import numpy

class GMM:
    """
        n_components: one by default
          covar_type: can be 'diagonal' or 'full' or 'tied' or 'tied_diagonal' or 'spherical'
                 dim: two by default
    """

    covar_types = ['diagonal', 'full', 'tied', 'tied_diagonal', 'spherical']
    covar_diagonal_types = ['diagonal', 'tied_diagonal', 'spherical']
    covar_tied_types = ['tied', 'tied_diagonal']

    def __init__(self, n_components = 1, dim = 2, covar_type = 'diagonal', min_var = 1.0e-5, _for_accumulating = False):
        
        if covar_type not in GMM.covar_types:
            raise Exception('GMM(): incorrect covar type: %s' % covar_type)

        self.min_var          = min_var
        self.covar_type       = covar_type
        self.dim              = dim
        #
        self.log_2_pi         = dim * numpy.log(2 * numpy.pi)
        #
        self.n_components     = n_components
        #
        self.prioris          = numpy.ones(n_components) / n_components
        self.mu = []
        self.sigma = []
        self.L = []
        self.sigma_diag_inv = []
        for c in range(self.n_components):
            self.mu.append(numpy.zeros(dim))
            self.sigma.append(numpy.zeros([dim, dim]))
            self.sigma_diag_inv.append(numpy.ones(dim))
            self.L.append(numpy.zeros([dim, dim]))
        #
        self.log_prioris      = numpy.log(self.prioris)
        self.log_determinants = numpy.ones(n_components)
        #
        self.acc_posteriors = numpy.zeros(n_components)
        self.acc_sample_counter = numpy.zeros(n_components)
        self.log_likelihood = 0.0
        #
        if not _for_accumulating:
            identity = numpy.identity(self.dim)
            for c in range(self.n_components):
                self.sigma[c][:, :] = identity[:, :] 
            #
            self.compute_derived_parameters()
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def initialize_from(self, samples):
        if type(samples) == list:
            sample = samples[0]
        else:
            sample = samples
        if len(sample.shape) != 2 or sample.shape[1] != self.dim:
            raise Exception('GMM.initialize_from(): received an incorrect sample for this GMM')
        #
        self.prioris = numpy.ones(self.n_components) / self.n_components
        #
        for c in range(self.n_components):
            #self.mu[c][:] = samples[ numpy.random.randint(len(samples)) , :]
            if type(samples) == list:
                self.mu[c] = samples[numpy.random.randint(len(samples))][0].copy()
            else:
                self.mu[c] = samples[numpy.random.randint(len(samples))].copy()
            self.sigma[c] = numpy.identity(self.dim)
        #
        self.compute_derived_parameters()
    # ------------------------------------------------------------------------------
    def initialize_from_centroids(self, centroids):
        if type(centroids) == list or (type(centroids) == numpy.ndarray and len(centroids.shape) == 2):
            if len(centroids) != self.n_components:
                raise Exception('GMM.initialize_from_centroids() needs as many centroids as GMM components')
            for c in range(self.n_components):
                self.mu[c] = centroids[c].copy()
        elif type(centroids) == numpy.ndarray and len(centroids.shape) == 1:
            if self.n_components != 1:
                raise Exception('GMM.initialize_from_centroids() needs as many centroids as GMM components')
            self.mu[0] = centroids.copy()
        else:
            raise Exception('GMM.initialize_from_centroids() received an unexpected configuration')

        self.prioris = numpy.ones(self.n_components) / self.n_components
        self.compute_derived_parameters()
    # ------------------------------------------------------------------------------
    def update_parameters(self, other):
        #
        if not isinstance(other, type(self)) and type(other).__name__ not in ['GMM', 'gmm.GMM']:
            raise Exception('GMM.update_parameters(): received an improper object instead of another GMM')
        if self.n_components != other.n_components:
            raise Exception('GMM.update_parameters(): received an GMM object incompatible with the current one')
        #
        self.prioris = other.acc_posteriors / other.acc_sample_counter.sum()
        #if other.acc_sample_counter.min() == 0:
        #    raise Exception('GMM.update_parameters(): gaussian %d with zero samples' % other.acc_sample_counter.argmin())
        if self.prioris.min() < 1.0e-200:
            other.save_to_text('wrong-gmm')
            raise Exception('GMM.update_parameters(): gaussian %d with zero probability' % self.prioris.argmin())
        #while self.prioris.min() < 1.0e-200:
        #    other.remove_gaussian(self.prioris.argmin())
        #    self.prioris = other.acc_posteriors / other.acc_sample_counter.sum()
        if abs(self.prioris.sum() - 1.0) > 1.0e-5:
            other.save_to_text('wrong-gmm')
            raise Exception('GMM.update_parameters(): sum of prioris is not equal to one: %e ' % self.prioris.sum())

        self.log_prioris  = numpy.log(self.prioris)

        for c in range(self.n_components):
            #
            self.mu[c]    = other.mu[c]    / other.acc_posteriors[c]
            self.sigma[c] = other.sigma[c] / other.acc_posteriors[c]
            if self.covar_type in GMM.covar_diagonal_types:
                self.sigma[c] = self.sigma[c] - numpy.diag(self.mu[c] * self.mu[c])
            else:
                self.sigma[c] = self.sigma[c] - numpy.outer(self.mu[c], self.mu[c])
            #
            for i in range(self.dim):
                self.sigma[c][i, i] = max(self.sigma[c][i, i], self.min_var)
            #
            # This is needed in the splitting process
            self.acc_sample_counter[c] = other.acc_sample_counter[c]
        #
        self.compute_derived_parameters()
        self.log_likelihood = other.log_likelihood
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def compute_derived_parameters(self):
        #
        self.log_prioris = numpy.log(self.prioris)
        #
        if self.covar_type == 'spherical' :
            identity = numpy.identity(self.dim)
            for c in range(self.n_components):
                self.sigma[c][:, :] = identity[:, :]
        elif self.covar_type in GMM.covar_tied_types:
            #_sigma = numpy.average(self.sigma, axis = 0)
            _sigma = sum(self.sigma) / self.n_components
            for c in range(self.n_components):
                self.sigma[c][:, :] = _sigma

        for c in range(self.n_components):
            #
            if self.covar_type == 'spherical' :
                self.L[c] = numpy.identity(self.dim)
                self.log_determinants[c] = 2 * numpy.log(numpy.diag(self.L[c])).sum() # det(sigma) = det(L)*det(L)
            elif self.covar_type in GMM.covar_diagonal_types:
                self.L[c] = numpy.diag(numpy.sqrt(numpy.diag(self.sigma[c])))
                self.log_determinants[c] = numpy.log(numpy.diag(self.sigma[c])).sum()
            else:
                try:
                    self.L[c] = numpy.linalg.cholesky(self.sigma[c])
                except Exception as e: 
                    self.save_to_text('wrong-gmm')
                    print(c)
                    print(numpy.diag( self.sigma[c]))
                    print(self.sigma[c])
                    #sys.exit(100)
                    raise e
                self.log_determinants[c] = 2 * numpy.log(numpy.diag(self.L[c])).sum() # det(sigma) = det(L)*det(L)
            # We compute this in any case, but it is used only when working with diagonal covariance matrices.
            self.sigma_diag_inv[c] = 1.0 / numpy.diag(self.sigma[c])
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def mahalanobis(self, sample):
        #
        if len(sample.shape) > 1 or sample.shape[0] != self.dim:
            raise Exception('GMM.mahalanobis(): received an incorrect sample for this GMM')
        #
        _dists = numpy.zeros(self.n_components)
        if self.covar_type in ['full', 'tied'] :
            for c in range(self.n_components):
                d = sample - self.mu[c]
                v = numpy.linalg.solve(self.L[c], d)
                _dists[c] = numpy.dot(v, v)
        else:
            for c in range(self.n_components):
                d = sample - self.mu[c]
                d = d * d
                d *= self.sigma_diag_inv[c]
                _dists[c] = d.sum()
            
        return _dists
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def mahalanobis_batch(self, sample):
        #
        if len(sample.shape) != 2 or sample.shape[0] != self.dim:
            raise Exception('GMM.mahalanobis_batch(): received an incorrect sample for this GMM ' + str(sample.shape) + '  ' + str(self.dim))
        #
        _dists = numpy.zeros([self.n_components, sample.shape[1]])

        if self.covar_type in ['full', 'tied'] :
            """
                In the case of full covariance matrix self.L[c] contains the Cholesky decomposition of self.sigma[c],
                the covariance matrix of class 'c'.
                Then for each sample we compute v in L*v = d, by solving the equation, where d is the difference vector
                of the sample with respect to the mean of the class 'c'.
                As v = d*L^-1, then v*v, the dot product, is d.T*L.T^-1 * L^-1 * d, that is the Mahalanobis distance
            """
            for c in range(self.n_components):
                for i in range(sample.shape[1]):
                    d = sample[:, i] - self.mu[c]
                    v = numpy.linalg.solve(self.L[c], d)
                    _dists[c,i] = numpy.dot(v, v)
        else:
            """
                In the case of diagonal covariance matrices, computing the Mahalanobis distance is very simple.
                We can directly divide the squared distances by sigma, the diagonal covariance matrix. But this
                vector with the main diagonal of the covariance matrix must be expanded thans to numpy.newaxis
                to a number of columns matching the number of samples in the batch. Finally .sum(axis=0) computes
                the Mahalanobis distances of the samples with respect to the mean of the class 'c'.
            """
            for c in range(self.n_components):
                d = sample - self.mu[c][:, numpy.newaxis]
                d = d * d
                d *= self.sigma_diag_inv[c][:, numpy.newaxis]
                _dists[c] = d.sum(axis = 0)
        """
            _dists is a (C x B) matrix, where C is the number of classes in the GMM and B the number of samples
            in the batch. Each component is the Mahalanobis distance of the sample 'i' to the class 'c'.
        """
        return _dists
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def log_densities(self, sample, with_a_priori_probs = True):
        _dists = self.mahalanobis(sample)
        if with_a_priori_probs:
            return self.log_prioris - 0.5 * (_dists + self.log_determinants + self.log_2_pi)
        else:
            return - 0.5 * (_dists + self.log_determinants + self.log_2_pi)
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def log_densities_batch(self, sample, with_a_priori_probs = True):
        _dists = self.mahalanobis_batch(sample)
        """
            _dists is a matrix of (C x B) where C is the number of classes in the GMM and B is the number of samples in the batch

            Thanks to numpy in Python we can applay the formula to compute the log_densities (log of conditional probability densities)
            in one line of code, because Python expands it properly over all the components. Sometimes we have to explicity tell numpy 
            to expand some arrays to match the dimension of other arrays. That's why we use numpy.newaxis

            so:
                _log_densities is a matrix of (C x B) where C is the number of classes in the GMM and B is the number of samples in the batch
        """
        if with_a_priori_probs:
            _log_densities = self.log_prioris[:, numpy.newaxis] - 0.5 * (_dists + self.log_determinants[:,numpy.newaxis] + self.log_2_pi)
        else:
            _log_densities = - 0.5 * (_dists + self.log_determinants[:,numpy.newaxis] + self.log_2_pi)
        #
        return _log_densities
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def posteriors(self, sample):
        _log_densities = self.log_densities(sample)
        #print(" ".join(' {:10.4e}'.format(x) for x in _log_densities))
        _max_log_density = _log_densities.max()
        _densities = numpy.exp(_log_densities - _max_log_density)
        _log_likelihood = numpy.log(_densities.sum()) + _max_log_density
        #print(" ".join(' {:10.4e}'.format(x) for x in _densities))
        return _densities / _densities.sum(), _log_likelihood
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def classify(self, sample):
        _posteriors, _logL = self.posteriors(sample)
        return _posteriors.argmax()
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def posteriors_batch(self, sample):
        _log_densities = self.log_densities_batch(sample)
        _max_log_density = _log_densities.max(axis = 0)
        _densities = numpy.exp(_log_densities - _max_log_density)
        _log_likelihood = numpy.log(_densities.sum(axis = 0)) + _max_log_density
        '''
        if _log_likelihood.any() > 0.0:
            print("posteriors_batch()", _log_likelihood)
            print("posteriors_batch()", _densities.sum(axis = 0))
        '''
        return _densities / _densities.sum(axis = 0), _log_likelihood
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def classify_batch(self, samples):
        _posteriors, _logL = self.posteriors_batch(samples)
        _predict = numpy.zeros(samples.shape[1], dtype = int) 
        _predict[:] = numpy.argmax(_posteriors, axis = 0)
        return _predict
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def accumulate_sample(self, sample, stable_gmm):
        #
        if not isinstance(stable_gmm, type(self)) and type(stable_gmm).__name__ not in ['GMM', 'gmm.GMM']:
            raise Exception('GMM.accumulate_sample(): received an improper object instead of another GMM')
        #
        if len(sample.shape) > 1 or sample.shape[0] != self.dim:
            raise Exception('GMM.accumulate_sample(): received an incorrect sample for this GMM %d %d %d' % (len(sample.shape),sample.shape[0],self.dim))
        #
        _posteriors, _log_likelihood = stable_gmm.posteriors(sample)

        self.acc_posteriors += _posteriors
        c = numpy.argmax(_posteriors)
        self.acc_sample_counter[c] += 1.0
        self.log_likelihood += _log_likelihood
        #
        diagonal_covar = self.covar_type in GMM.covar_diagonal_types
        #
        for c in range(self.n_components):
            self.mu[c] +=  _posteriors[c] * sample 
            #diffs = sample - stable_gmm.mu[c]
            if diagonal_covar:
                #self.sigma[c] += numpy.diag((diffs * diffs) * _posteriors[c])
                self.sigma[c] += numpy.diag((sample * sample) * _posteriors[c])
            else:
                #self.sigma[c] += numpy.outer(diffs, diffs) * _posteriors[c]
                self.sigma[c] += numpy.outer(sample, sample) * _posteriors[c]
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def accumulate_sample_batch(self, sample, stable_gmm):
        #
        if not isinstance(stable_gmm, type(self)) and type(stable_gmm).__name__ not in ['GMM', 'gmm.GMM']:
            raise Exception('GMM.accumulate_sample(): received an improper object instead of another GMM')
        #
        if len(sample.shape) != 2 or sample.shape[0] != self.dim:
            raise Exception('GMM.accumulate_sample(): received an incorrect sample for this GMM %d %d %d' % (len(sample.shape), sample.shape[0],self.dim))
        #
        """
            Computes the 'a posteriori' probabilities of every sample.
            In the case sample is just a one dimensional array representing a single sample this algorithm expects that sample is a one-dimensional array
            of dim components.
            But if is a matrix (a two-dimensional array), then this algorithm expects that each sample is a column, and then the number of rows must be
            equal to dim.

            Due to the previous consideration, _posteriors can be both, a one-dimensional vector with C components, where C is the number of classes,
            or a two-dimensional array of C x B, where B is the number of samples in the batch.
        """
        _posteriors, _log_likelihood = stable_gmm.posteriors_batch(sample)

        """
            self.acc_posteriors is an array with C components, where C is the number of classes,
            accumulating by the axis 1 we sum the 'a posterior' probabilities of all the samples in the batch per class.
            Summing in axis 1 means that we get the sum of every column and the result is a column vector with C rows
        """
        self.acc_posteriors += _posteriors.sum(axis = 1)
        c = _posteriors.argmax(axis = 0)
        for k in c: self.acc_sample_counter[k] += 1.0
        self.log_likelihood += _log_likelihood.sum()

        diagonal_covar = self.covar_type in GMM.covar_diagonal_types
        for c in range(self.n_components):
            """
                _posteriors[c] is a vector (one-dimensional array) with B components, one per sample in the batch.
                sample is a matrix (two-dimensional array) with 'dim' rows and B columns, one column per sample in the batch.
                Python performs the product by replicating the vector _posteriors[c] 'dim' times in order to ensure the
                element-wise product, the (1 x B) vector is expanded to (dim x B) in order to match the dimensionality of 'sample'
                Finally, sum(axis=1) performs the accumulation for getting a vector of 'dim' components that with the
                sum of all the columns per row.
            """
            self.mu[c] +=  (_posteriors[c] * sample).sum(axis = 1)
            """
                The average vector of each class 'c' is expanded for matching a (dim x B) matrix in order to get
                the differences of all the samples in the batch with respect to the mean vector of class 'c',
                and all for each component of each sample, the are 'dim' components.

                Since 'diffs' is a (dim x B) matrix we have to perform a different strategy denpending on whether
                we are working with the full covariance matrix or not.

                FULL COVAR:
                        diffs.shape[1] -- number of samples in the batch.
                        for each sample in the batch:   
                            builds the square matrix of the squared differences corresponding to one sample --> numpy.outer( diffs[:,i], diffs[:,i] )
                            multiply this matrix by the 'a posteriori' probability of the class 'c' given the sample 'i' --> matrix * _posteriors[c,i]
                            accumulate the weighted squared differences to the covariance matrix

                DIAG COVAR:
                        ( diffs * diffs ) * _posteriors[c]  -- squared differences of each sample with respect to the mean of class 'c'
                        ( ... ).sum(axis=1) )               -- accumulation per component in 'dim' dimensions over all the samples in the batch.
                        self.sigma[c] += numpy.diag( ... )  -- the method diag() converts into a square matrix the vector with the accumulated and weighted squared differences
                    
            """
            #diffs = sample - stable_gmm.mu[c][:, numpy.newaxis]
            if diagonal_covar:
                #self.sigma[c] += numpy.diag(((diffs * diffs) * _posteriors[c] ).sum(axis = 1))
                self.sigma[c] += numpy.diag(((sample * sample) * _posteriors[c]).sum(axis = 1))
            else:
                #for i in range(diffs.shape[1]):
                    #self.sigma[c] += numpy.outer(diffs[:, i], diffs[:, i]) * _posteriors[c, i]
                for i in range(sample.shape[1]):
                    self.sigma[c] += numpy.outer(sample[:, i], sample[:, i]) * _posteriors[c, i]
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def add(self, other):
        #
        if not isinstance(other, type(self)) and type(other).__name__ not in ['GMM', 'gmm.GMM']:
            raise Exception(f'GMM.add(): received an improper object instead of another GMM: {type(other)}')
        #
        for c in range(self.n_components):
            self.mu[c]                 = self.mu[c]    + other.mu[c]
            self.sigma[c]              = self.sigma[c] + other.sigma[c]
        #
        self.acc_posteriors     = self.acc_posteriors     + other.acc_posteriors
        self.acc_sample_counter = self.acc_sample_counter + other.acc_sample_counter
        self.log_likelihood     = self.log_likelihood     + other.log_likelihood
    # ------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------            
    def show_means(self):
        for c in range(self.n_components):
            print(self.mu[c])
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def compute_AIC_and_BIC(self, logL):
        #
        num_samples = self.acc_sample_counter.sum()
        logN = numpy.log(max(1.0, num_samples))
        #
        m = 0
        if self.covar_type == 'spherical':
            # Free parameters are the means, the a priori probabilities
            m = self.n_components * (self.dim + 1)
            #
        elif self.covar_type == 'tied_diagonal':
            # Free parameters are the means, the a priori probabilities and
            # only one time the elements of the diagonal covariance matrix
            m = self.n_components * (self.dim + 1) + self.dim
            #
        elif self.covar_type == 'diagonal':
            # Free parameters are the means, the a priori probabilities and
            # the elements of the diagonal covariance matrix of each Gaussian
            m = self.n_components * (self.dim + 1 + self.dim)
            #
        elif self.covar_type == 'tied':
            # Free parameters are the means, the a priori probabilities and
            # the elements of the full tied covariance matrix
            m = self.n_components * (self.dim + 1) + self.dim * self.dim
            #
        else:
            # Free parameters are the means, the a priori probabilities and
            # the elements of the full covariance matrix of each Gaussian
            m = self.n_components * (self.dim + 1 + self.dim * self.dim)
            #
        #
        aic =     2 * m - 2 * logL
        bic =  logN * m - 2 * logL
        #
        return aic, bic
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def purge(self, log_file = None):
        #
        for i in range(self.n_components):
            log_file.write("class %d with %d samples assigned\n" % (i, self.acc_sample_counter[i]))
        for i in range(self.n_components):
            if self.acc_sample_counter[i] == 0:
                log_file.write("class %d with mean %s \n" % (i, str(self.mu[i])))
        #
        if min(self.acc_sample_counter) == 0:
            if log_file is not None:
                log_file.write("Purging classes with 0 samples assigned. Passing from %d to " % self.n_components)
            #
            self.prioris = self.prioris[self.acc_sample_counter != 0].copy()
            self.log_prioris  = numpy.log(self.prioris)
            #
            temp_mu = []
            temp_sigma = []
            temp_L = []
            temp_sigma_diag_inv = []
            for i in range(self.n_components):
                if self.acc_sample_counter[i] > 0:
                    temp_mu.append(self.mu[i])
                    temp_sigma.append(self.sigma[i])
                    temp_L.append(self.L[i])
                    temp_sigma_diag_inv.append(self.sigma_diag_inv[i])
            #
            self.mu = temp_mu
            self.sigma = temp_sigma
            self.L = temp_L
            self.sigma_diag_inv = temp_sigma_diag_inv
            #
            self.n_components = len(self.prioris)
            #
            self.acc_sample_counter = self.acc_sample_counter[self.acc_sample_counter != 0].copy()
            #
            self.log_determinants = numpy.ones(self.n_components)
            self.acc_posteriors = numpy.zeros(self.n_components)
            #
            if log_file is not None:
                log_file.write("%d gaussians\n" % self.n_components)
            #
            self.compute_derived_parameters()
        #
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def split(self, log_file = None, force = False):
        if log_file is None: log_file = sys.stdout
        if force or self.n_components < 4:
            max_c = self.n_components
            for c in range(max_c): self.split_gaussian(c)
        else:
            # Number of Samples per Gaussian
            nsg = []
            for i in range(self.n_components):
                nsg.append([self.acc_sample_counter[i], i])
            nsg.sort(reverse = True)
            # Trace of Sigma per Gaussian
            tsg = []
            for i in range(self.n_components):
                #tsg.append([numpy.diag(self.sigma[i]).sum(), i])
                #tsg.append([numpy.log(numpy.diag(self.sigma[i])).sum(), i])
                tsg.append([self.log_determinants[i], i])
            tsg.sort(reverse = True)
            #
            for c in range(self.n_components):
                log_file.write(" %4d   nsg %3d %16.6f     tsg %3d %16.6f\n" % (c, nsg[c][1], nsg[c][0], tsg[c][1], tsg[c][0]))
            #
            _counter = 0
            if self.covar_type in ['spherical', 'tied', 'tied_diagonal']:
                """
                    If the co-variance matrix is share among all the Gaussians
                    only the criterion based on the number of samples is used
                    to split clusters.
                """
                self.split_gaussian(nsg[0][1])
                _counter += 1

            elif abs(nsg[0][0] - nsg[-1][0]) < 1.0e-3:
                """
                    If the number of samples per Gaussian is not informed, then,
                    only the criterion based on the trace of the determinant is used
                    to split clusters.
                """
                self.split_gaussian(tsg[0][1])
                _counter += 1
                for c in range(1, len(tsg) //2):
                    if (tsg[c - 1][0] - tsg[c][0]) > (tsg[c][0] - tsg[c + 1][0]):
                        break
                    self.split_gaussian(tsg[c][1])
                    _counter += 1
            else:
                """
                    Splits those Gaussians which are in the first half of both lists.
                    But guaranteeing at least one is split.
                """
                candidates = [0] * len(nsg)
                max_c = len(nsg) // 2
                i = 0
                while max(candidates) < 2 or i <= max_c:
                    candidates[nsg[i][1]] += 1
                    candidates[tsg[i][1]] += 1
                    i += 1
                #
                nsg.sort(key = lambda x: x[1])
                tsg.sort(key = lambda x: x[1])
                for c in range(len(candidates)):
                    if candidates[c] == 2:
                        log_file.write("splitting component: %4d   nsg %3d %16.6f     tsg %3d %16.6f\n" % (c, nsg[c][1], nsg[c][0], tsg[c][1], tsg[c][0]))
                        self.split_gaussian(c)
                        _counter += 1
                #
            if _counter == 0:
                # When no Gaussian were split in the previous step two are split:
                self.split_gaussian(nsg[0][1]) # Split the Gaussian with more samples
                self.split_gaussian(tsg[0][1]) # Split the most disperse Gaussian 
            #
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def split_gaussian(self, c):
        #
        for i in range(self.n_components):
            if self.mu[c].sum() == 0:
                raise Exception("The mean is completely zero!")
            if numpy.diag(self.sigma[c]).sum() == 0:
                raise Exception("The diagonal is completely zero!")
        #
        self.n_components     = self.n_components + 1
        #
        self.prioris          = numpy.hstack([self.prioris, 0.0])
        self.prioris[-1]      = self.prioris[c] / 2
        self.prioris[c]       = self.prioris[c] / 2
        self.log_prioris      = numpy.log(self.prioris)
        #
        self.mu.append(numpy.zeros( self.dim))
        if self.covar_type in GMM.covar_diagonal_types:
            _pseudo_volume_ = 1.0
            v = numpy.sqrt(numpy.diag(self.sigma[c]))
            self.mu[-1][:]  = self.mu[c] + _pseudo_volume_ * v
            self.mu[c][:]   = self.mu[c] - _pseudo_volume_ * v
            #self.mu[-1][:]  = self.mu[c] + _pseudo_volume_ * v[:, -1]
            #self.mu[c][:]   = self.mu[c] - _pseudo_volume_ * v[:, -1]
        else:
            w, v = numpy.linalg.eigh(self.sigma[c])
            _pseudo_volume_ = 1.0
            #_pseudo_volume_ = 0.5 * numpy.sqrt(numpy.diag(self.sigma[c]))
            _v_ = v[:, -1].copy()
            _norm_m_ = numpy.linalg.norm(self.mu[c]) 
            _norm_v_ = numpy.linalg.norm(_v_) 
            #_v_ = _norm_m_ * _v_ / _norm_v_ 
            _v_ = _v_ / _norm_v_ 
            self.mu[-1][:]  = self.mu[c] + _pseudo_volume_ * _v_
            self.mu[c][:]   = self.mu[c] - _pseudo_volume_ * _v_
        #
        self.sigma.append(numpy.copy(self.sigma[c]))
        self.sigma_diag_inv.append(numpy.copy(self.sigma_diag_inv[c]))
        self.L.append(numpy.copy(self.L[c]))
        self.log_determinants = numpy.ones(self.n_components)
        #
        self.acc_posteriors = numpy.zeros(self.n_components)
        self.acc_sample_counter = numpy.zeros(self.n_components)
        self.log_likelihood = 0.0
        #
        self.compute_derived_parameters()
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def clone(self):
        #    
        new_gmm = GMM(n_components = self.n_components, dim = self.dim, covar_type = self.covar_type, min_var = self.min_var)
        #
        new_gmm.prioris = self.prioris.copy()
        for c in range(self.n_components):
            new_gmm.mu[c][:]               = self.mu[c][:]
            new_gmm.sigma[c][:,:]          = self.sigma[c][:,:]
            new_gmm.sigma_diag_inv[c][:]   = self.sigma_diag_inv[c][:]
            new_gmm.L[c][:,:]              = self.L[c][:,:]
        #
        new_gmm.log_prioris      = numpy.log(new_gmm.prioris)
        new_gmm.log_determinants = numpy.ones(new_gmm.n_components)
        #
        new_gmm.acc_posteriors = numpy.zeros(new_gmm.n_components)
        new_gmm.acc_sample_counter = numpy.zeros(new_gmm.n_components)
        new_gmm.log_likelihood = 0.0
        new_gmm.compute_derived_parameters()
        #
        return new_gmm
    # ---------------------------------------------------------------------------------            

    def drop_duplicated_gaussians(self):
        #
        prioris = list()
        mu = list()
        sigma = list()
        L = list()
        sigma_diag_inv = list()
        for c in range(self.n_components):
            min_relative_diff = 1.0e+200
            for i in range(len(mu)):
                relative_diff = sum((self.mu[c] - mu[i]) ** 2) / (1.0e-5 + sum(self.mu[c] ** 2))
                min_relative_diff = min(relative_diff, min_relative_diff)
            if min_relative_diff >= 1.0e-4:
                prioris.append(self.prioris[c])
                mu.append(self.mu[c])
                sigma.append(self.sigma[c])
                L.append(self.L[c])
                sigma_diag_inv.append(self.sigma_diag_inv[c])
        #
        self.prioris = numpy.array(prioris)
        self.prioris /= self.prioris.sum()
        self.mu = mu
        self.sigma = sigma
        self.L = L
        self.sigma_diag_inv = sigma_diag_inv
        self.n_components = len(mu)
        #
        self.log_prioris = numpy.log(self.prioris)
        self.log_determinants = numpy.ones(self.n_components)
        #
        self.acc_posteriors = numpy.zeros(self.n_components)
        self.acc_sample_counter = numpy.zeros(self.n_components)
        self.log_likelihood = 0.0
        self.compute_derived_parameters()
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def save_to_text(self, prefix_name):
        filename = '%s-%04d.txt' % (prefix_name, self.n_components)
        if os.path.exists(filename):
            if os.path.isfile(filename):
                os.rename(filename, filename.replace('txt', 'bak'))
            else:
                raise Exception('Cannot overwrite %s' % filename)
        #            
        f = open(filename, 'wt')
        f.write('n_components %d\n' % self.n_components)
        f.write('dim %d\n' % self.dim)
        f.write('covar_type %s\n' % self.covar_type)
        for c in range(self.n_components):
            f.write('priori %e\n' % self.prioris[c])
            f.write('mean ')
            #for k in range(self.dim):
            #    f.write(' %16.8e ' % self.mu[c][k])
            f.write(' '.join( '{:16.8e}'.format(x) for x in self.mu[c]))
            f.write('\n')
            f.write('sigma \n')
            for k in range(self.dim):
                #for l in range(self.dim):
                #    f.write( ' %16.8e ' % self.sigma[c][k,l] )
                f.write(' '.join( '{:16.8e}'.format(x) for x in self.sigma[c][k]))
                f.write('\n')
        f.close()
    # ---------------------------------------------------------------------------------            

    # ---------------------------------------------------------------------------------            
    def load_from_text(self, filename):
        flag_memory_reserved = False
        f = open(filename, 'rt')
        c = -1
        k = -1
        for line in f:
            parts = line.split()

            if parts[0] == 'n_components':
                self.n_components = int(parts[1])

            elif parts[0] == 'dim':
                self.dim = int(parts[1])

            elif parts[0] == 'covar_type':
                self.covar_type = parts[1]

            elif parts[0] == 'priori':

                if not flag_memory_reserved:

                    self.prioris          = numpy.zeros(self.n_components)
                    self.log_prioris      = numpy.zeros(self.n_components)
                    self.mu               = list() # self.n_components * [numpy.zeros(self.dim)]
                    self.sigma            = list() # self.n_components * [numpy.zeros([self.dim, self.dim ])]
                    self.sigma_diag_inv   = list() # self.n_components * [numpy.zeros(self.dim)]
                    self.L                = list() # self.n_components * [numpy.zeros([self.dim, self.dim ])]
                    self.log_2_pi         = self.dim * numpy.log(2 * numpy.pi)
                    self.log_determinants = numpy.ones(self.n_components)

                    self.acc_posteriors = numpy.zeros(self.n_components)
                    self.acc_sample_counter = numpy.zeros(self.n_components)
                    self.log_likelihood = 0.0

                    flag_memory_reserved = True

                c += 1
                self.prioris[c] = float(parts[1])

            elif parts[0] == 'mean':
                self.mu.append(numpy.array([float(value) for value in parts[1:]]))

            elif parts[0] == 'sigma':
                self.sigma.append(numpy.zeros([self.dim, self.dim ]))
                self.sigma_diag_inv.append(numpy.zeros(self.dim))
                self.L.append( numpy.zeros([self.dim, self.dim ]))
                """
                for k in range(self.dim):
                    line = f.readline()
                    parts = line.split()
                    self.sigma[c][k,:] = [float(value) for value in parts]
                """
                k = 0
            elif 0 <= k < self.dim:
                self.sigma[c][k, :] = [float(value) for value in parts]
                k += 1
        #
        f.close()
        self.compute_derived_parameters()
    # ---------------------------------------------------------------------------------            
