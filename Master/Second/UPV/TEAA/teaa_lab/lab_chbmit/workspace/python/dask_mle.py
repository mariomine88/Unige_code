"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.0
    Date: May 2024
    Universitat Politecnica de Valencia
    Technical University of Valencia TU.VLC


    Maximum Likelihood Estimation using DASK

"""

import os
import sys
import time
import numpy

from gmm import GMM

import dask.bag as db

from concurrent.futures._base import CancelledError

# ---------------------------------------------------------------------------------            
def dask_mle_map(data, gmm: GMM):
    _temp_gmm = GMM(gmm.n_components, gmm.dim, gmm.covar_type, min_var = gmm.min_var, _for_accumulating = True)

    for _x_ in data:
        if type(_x_) == dict:
            x = _x_['X']
        else:
            x = _x_
        #
        if len(x.shape) == 2:
            _temp_gmm.accumulate_sample_batch(x.T, gmm)
        else:
            assert False
        #
    #
    return [_temp_gmm]
# ---------------------------------------------------------------------------------            
def dask_mle_reduce(gmm1, gmm2):
    gmm1.add(gmm2)
    return gmm1
# ---------------------------------------------------------------------------------            


class MLE:
    """
    """

# ---------------------------------------------------------------------------------            
    def __init__(self, covar_type = 'diagonal', dim = 1, log_dir = 'log', models_dir = 'models', min_var = 1.0e-5, max_iterations = 200):
        self.max_iterations = max_iterations
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok = True)
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok = True)
        self.min_var = min_var
        self.gmm = GMM(n_components = 1, dim = dim, covar_type = covar_type, min_var = self.min_var, _for_accumulating = False)
# ---------------------------------------------------------------------------------            

    """
        - samples must be a DASK BAG object
    """
# ---------------------------------------------------------------------------------            
    def standalone_epoch(self, samples : db.Bag, num_samples: int):
        retries = 3
        while retries > 0:
            try:
                self.gmm.update_parameters(samples.map_partitions(dask_mle_map, self.gmm).fold(dask_mle_reduce).compute())
                return self.gmm.log_likelihood / num_samples
            except CancelledError as e:
                retries -= 1
                if retries == 0:
                    raise e
                print('MLE.standalone_epoch(): retrying after exception of type', type(e), 'pending retries:', retries, flush = True)
            except Exception as e:
                print('MLE.standalone_epoch():', type(e), flush = True)
                raise e
        return None
# ---------------------------------------------------------------------------------            
    def expectation_maximization(self, samples = None, num_samples = -1, epsilon = 1.0e-5, log_file = None):
        if samples is None :
            raise Exception("Maximum Likelihood Estimation cannot be done without samples!")
        if type(samples) not in [db.Bag]:
            raise Exception("Maximum Likelihood Estimation. Non recognized data structure:: %s " % (type(samples)))
        if num_samples is None or num_samples <= 0:
            num_samples = samples.count().compute()
        close_log_file = False
        if log_file is None:
            log_file = open(self.log_dir + "/OUT", 'a')
            close_log_file= True
        #
        log_file.write('Starting MLE EM algorithm for %d components\n' %  self.gmm.n_components)
        log_file.flush()
        #
        iterations_after_epsilon_reached = 2 # 10
        iteration = 1
        relative_improvement = 1.0
        logL = 0.0
        #
        while iterations_after_epsilon_reached > 0  and  iteration <= self.max_iterations:
            #
            old_logL = logL
            #
            starting_time = time.time()
            logL = self.standalone_epoch(samples, num_samples)
            aic, bic = self.gmm.compute_AIC_and_BIC(logL * num_samples)
            time_lapse = time.time() - starting_time
            #
            self.gmm.save_to_text(self.models_dir + '/gmm')
            #
            relative_improvement = abs((logL - old_logL) / logL)
            log_file.write("iteration %5d  logL = %e  delta_logL = %e  aic = %e  bic = %e  time lapse %.6f seconds\n" % (iteration, logL, relative_improvement, aic, bic, time_lapse))
            log_file.flush()
            #
            iteration += 1
            if relative_improvement < epsilon: iterations_after_epsilon_reached -= 1
        #
        if close_log_file:
            log_file.close()
        #
        return logL
# ---------------------------------------------------------------------------------            
    def fit_and_split(self, samples: db.Bag, max_components = None, epsilon = 1.0e-5):
        #
        if samples is None :
            raise Exception("Maximum Likelihood Estimation cannot be done without samples!")
        if type(samples) != db.Bag:
            raise Exception("Maximum Likelihood Estimation cannot be done without a DASK BAG!")
        if max_components is None :
            raise Exception("Maximum Likelihood Estimation cannot be done without a limit in the number of components of the GMM!")

        num_samples = samples.count().compute()
        log_file = open(self.log_dir + "/OUT", 'a')
        self.dict_gmms = dict()
        last_computed_gmm = None
        logL = 0.0
        while self.gmm.n_components <= max_components:
            starting_time = time.time()
            logL = self.expectation_maximization(samples = samples, num_samples = num_samples, epsilon = epsilon, log_file = log_file)
            self.gmm.purge(log_file = log_file)
            #
            aic, bic = self.gmm.compute_AIC_and_BIC(logL * num_samples)
            time_lapse = time.time() - starting_time
            log_file.write("n_components %5d  logL = %e  aic %e  bic %e time lapse %.6f seconds\n" % (self.gmm.n_components, logL, aic, bic, time_lapse))
            log_file.flush()
            #
            self.dict_gmms[self.gmm.n_components] = last_computed_gmm = self.gmm.clone()
            #
            self.gmm.save_to_text(self.models_dir + '/gmm')
            self.gmm.split(log_file)
            self.gmm.save_to_text(self.models_dir + '/gmm')
        # ---------------------------------------------------------------------------
        log_file.write("MLE task completed when %d components where execeeded with %d\n" % (max_components, self.gmm.n_components))
        log_file.flush()
        log_file.close()
        self.gmm = last_computed_gmm
# ---------------------------------------------------------------------------------            
