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

from sklearn.metrics.pairwise import euclidean_distances

class KernelClassifier:
    """
    This class implements a classifier based on Kernel Density Estimator.

    The purpose is to classify each sample according to the class with higher probability density.

    """
    
    def __init__(self, bandwidth = None, K = 100, n_jobs = 1, block_size = 1000):
        self.num_target_classes = None
        self.dim = None
        self.targets = None
        self.samples = None
        self.sizes = None
        self.bandwidth = bandwidth
        self.K = K
        self.n_jobs = n_jobs
        self.block_size = block_size
        self.kernel = 'gaussian' # This could be a parameter for the constructor, but the
                                 # current implementation of MyKernel.py doesn't allow a
                                 # different kernel type.
    # ------------------------------------------------------------------------------
    def fit(self, X, y = None):
        #
        if type(X) == numpy.ndarray:
            assert type(y) == numpy.ndarray
            assert len(X) == len(y)
            # Get the labels
            self.target_classes = numpy.unique(y)
            # Get the sample dimension
            self.dim = X.shape[1]
            # Separate the training samples of each class in order to do the estimation
            self.samples = dict()
            self.sizes = dict()
            self.samples_norm_squared = dict()
            self.list_of_indices = dict()
            for label in self.target_classes:
                _x_ = X[y == label]
                self.sizes[label] = len(_x_)
                self.samples[label] = numpy.array_split(_x_, max(1, len(_x_) // self.block_size))
                self.samples_norm_squared[label] = list()
                for x_chunk in self.samples[label]:
                    self.samples_norm_squared[label].append((x_chunk ** 2).sum(axis = 1))
            # end-for k
        elif type(X) == dict:
            assert y is None
            # Get the labels
            self.target_classes = list(X.keys())
            # Prepare the attributes of the model
            self.dim = None
            self.samples = dict()
            self.sizes = dict()
            self.samples_norm_squared = dict()
            for label in self.target_classes:
                _x_ = X[label]
                self.sizes[label] = len(_x_)
                self.samples[label] = numpy.array_split(_x_, max(1, len(_x_) // self.block_size))
                self.samples_norm_squared[label] = list()
                for x_chunk in self.samples[label]:
                    self.samples_norm_squared[label].append((x_chunk ** 2).sum(axis = 1))

                # Get the sample dimension
                if self.dim is None:
                    self.dim = _x_.shape[1]
                else:
                    assert self.dim == _x_.shape[1]
                # end-if
            # end-for

        # Establish the value of 'bandwidth' if not set previously
        if self.bandwidth is None:
            self.bandwidth = math.sqrt(self.dim)

        return self
    # ------------------------------------------------------------------------------
    def kernel_for_probs(self, X, bandwidth = None):
        assert type(X) is numpy.ndarray
        assert len(X.shape) == 2
        #
        if bandwidth is None:
            bandwidth = self.bandwidth
        #
        alpha = -0.5 / (bandwidth ** 2)
        #
        X_chunks = numpy.array_split(X, max(1, len(X) // self.block_size))
        densities = list()

        for i in range(len(X_chunks)):

            _x_ = X_chunks[i]
            _xx_ = (_x_ ** 2).sum(axis = 1).reshape(-1, 1)

            _d_ = list()

            for label in self.target_classes:
                squared_distances = list() 
                for _y_, _yy_ in zip(self.samples[label], self.samples_norm_squared[label]):
                    _dists_ = euclidean_distances(
                        X = _x_,
                        Y = _y_,
                        squared = True,
                        X_norm_squared = _xx_,
                        Y_norm_squared = _yy_,
                    )
                    _dists_.sort(axis = 1)
                    squared_distances.append(_dists_[:, :self.K].copy())
                    del _dists_
                # end-for
                squared_distances = numpy.hstack(squared_distances)
                squared_distances.sort(axis = 1)

                _d_.append(numpy.exp(alpha * squared_distances[:, :self.K]).sum(axis = 1).reshape(-1, 1))
            # end-for
            densities.append(numpy.hstack(_d_))
        #
        densities = numpy.vstack(densities)
        return densities / numpy.maximum(1.0e-8, densities.sum(axis = 1).reshape(-1, 1))
    # ------------------------------------------------------------------------------
    def predict_proba(self, X, bandwidth = None):
        assert type(X) == numpy.ndarray and len(X.shape) == 2
        return self.kernel_for_probs(X, bandwidth)
    # ------------------------------------------------------------------------------
    def predict(self, X, bandwidth = None):
        return self.predict_proba(X, bandwidth).argmax(axis = 1)
    # ------------------------------------------------------------------------------
