"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.0
    Date: October 2021
    Universitat Politecnica de Valencia
    Technical University of Valencia TU.VLC

"""

import sys
import time
import math
import numpy


import ray

from sklearn.neighbors import KernelDensity

#########################################################################################################
@ray.remote
def ray_train_kde_per_label(label, est, x_ref):
    return (label, est.fit(x_ref))
#########################################################################################################
@ray.remote
def ray_score_per_label(est, sample):
    return est.score_samples(sample).reshape(-1, 1)
#########################################################################################################
def cpu_train_kde_per_label(label, est, x_ref):
    return (label, est.fit(x_ref))
#########################################################################################################
def cpu_score_per_label(est, sample):
    return est.score_samples(sample).reshape(-1, 1)
#########################################################################################################

class KernelClassifier:
    """
    This class implements a classifier based on Kernel Density Estimator.

    The purpose is to classify each sample according to the class with higher probability density.

    """
    
    def __init__(self, band_width = None, n_jobs = 1, chunk_size = 1000):
        self.num_target_classes = None
        self.dim = None
        self.targets = None
        self.samples = None
        self.sizes = None
        self.band_width = band_width
        self.n_jobs = n_jobs
        self.chunk_size = chunk_size
        self.kernel = 'gaussian' # This could be a parameter for the constructor, but the
                                 # current implementation of MyKernel.py doesn't allow a
                                 # different kernel type.
    # ------------------------------------------------------------------------------

    def fit(self, X, y):
        # Get the labels
        self.targets = numpy.unique(y)
        self.num_target_classes = len(self.targets)
        # Get the sample dimension
        self.dim = X.shape[1]
        # Establish the value of 'band_width' if not set previously
        if self.band_width is None:
            self.band_width = "scott"

        self.kd_estimators = {}
        for label in self.targets:
            self.kd_estimators[label] = KernelDensity(bandwidth = self.band_width,
                                                        kernel = 'gaussian',
                                                        metric = 'euclidean',
                                                        algorithm = 'auto')

        # Separate the training samples of each class in order to do the estimation
        if self.n_jobs > 1:
            X_refs = {label:ray.put(X[y == label]) for label in self.targets}
            futures = [ray_train_kde_per_label.remote(label, self.kd_estimators[label], X_refs[label]) for label in self.targets]
            results = ray.get(futures)
            self.kd_estimators = {label:est for label, est in results}
        else:
            for label in self.targets:
                self.kd_estimators[label] = cpu_train_kde_per_label(label, self.kd_estimators[label], X[y == label])
        #
        return self
    # ------------------------------------------------------------------------------

    def predict_proba(self, sample):
        assert type(sample) is numpy.ndarray
        assert len(sample.shape) == 2
        #########################################################################################################
        if self.n_jobs > 1:
            sample_ref = ray.put(sample)
            futures = [ray_score_per_label.remote(self.kd_estimators[label], sample_ref) for label in self.targets]
            results = ray.get(futures)
            densities = numpy.hstack(results)
        else:
            densities = numpy.hstack([cpu_score_per_label(self.kd_estimators[label], sample) for label in self.targets])
        
        densities -= densities.max(axis = 1).reshape(-1, 1)
        densities = numpy.exp(densities)
        probs = densities / densities.sum()
        return probs
    # ------------------------------------------------------------------------------

    def predict(self, sample):
        probs = self.predict_proba(sample)
        if len(probs.shape) == 1:
            return probs.argmax()
        else:
            return probs.argmax(axis = 1)
    # ------------------------------------------------------------------------------
