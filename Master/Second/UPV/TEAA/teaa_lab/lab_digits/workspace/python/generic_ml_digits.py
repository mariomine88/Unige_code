"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 2.2
    Date: April 2024
    Universitat Politecnica de Valencia
    Technical University of Valencia TU.VLC

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is generic for being used with several ML techniques but Neural Network
"""

import sys
import os
import argparse
import numpy
import time

from sklearn.decomposition import PCA
from load_mnist import load_mnist
from utils_for_results import save_results

import ray

def main(args):
    args.exec_environment_id = 'local'
    ray.init(num_cpus = args.n_jobs)

    args.log_dir     = f'{args.baseDir}/{args.logDir}/{args.technique}'
    args.models_dir  = f'{args.baseDir}/{args.modelsDir}/{args.technique}'
    args.results_dir = f'{args.baseDir}/{args.resultsDir}/{args.technique}'
    os.makedirs(args.log_dir,     exist_ok = True)
    os.makedirs(args.models_dir,  exist_ok = True)
    os.makedirs(args.results_dir, exist_ok = True)

    X, y = load_mnist()
    X = X / 255.0
    print(X.shape, y.shape)
    X_train, X_test = X[:60000], X[60000:]
    y_train, y_test = y[:60000], y[60000:]
    #
    pca = PCA(n_components = args.pcaComponents if args.pcaComponents <= 1.0 else int(args.pcaComponents))
    pca.fit(X_train)
    X_train = pca.transform(X_train)
    X_test = pca.transform(X_test)
    print(X_train.shape, y_train.shape)
    print(X_test.shape, y_test.shape)

    args.pcaComponents = X_train.shape[1]

    args.labels = numpy.unique(y_train)
    print('labels', args.labels)

    train_data = {'x' : X_train, 'y': y_train}
    test_data  = {'x' : X_test,  'y': y_test}

    # Now, depending on the ML technique chosen by the user one code is going to be used
    if args.technique == 'kmeans':
        from kmeans_for_digits import kmeans_for_digits
        kmeans_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'gmm':
        from gmm_for_digits import gmm_for_digits
        gmm_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'rf':
        from ensemble_for_digits import rf_for_digits
        rf_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'ert':
        from ensemble_for_digits import ert_for_digits
        ert_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'gbt':
        from ensemble_for_digits import gbt_for_digits
        gbt_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'kde':
        from kde_for_digits import kde_for_digits
        kde_for_digits(args = args, train_data = train_data, test_data = test_data)
    elif args.technique == 'knn':
        from knn_for_digits import knn_for_digits
        knn_for_digits(args = args, train_data = train_data, test_data = test_data)
    #



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--technique',  default='kmeans', type=str, help='ML technique name: kmeans, gmm, rf, ert, gbt, kde, knn')
    parser.add_argument('--baseDir',    default='.',              type=str, help='Directory base from which create the directories for models, results and logs')
    parser.add_argument('--modelsDir',  default='models/digits',  type=str, help='Directory to save models --if it is the case')
    parser.add_argument('--resultsDir', default='results/digits', type=str, help='Directory where to store the results')
    parser.add_argument('--logDir',     default='logs/digits',    type=str, help='Directory where to store the logs --if it is the case')
    parser.add_argument('--verbose',    default=0, type=int, help='Verbosity level')
    #
    parser.add_argument('--pcaComponents',  default=37, type=float, help='Number of components of PCA an integer > 1 or a float in the range [0,1[')
    #
    parser.add_argument('--numEstimators',  default="100:200", type=str, help='Colon separated list of number of trees in ensembles of trees: RF, ERT, and GBT ')
    parser.add_argument('--maxDepth',       default="5:7",     type=str, help='Colon separated list of the max depth of each tree in ensembles of trees: RF, ERT, and GBT')
    parser.add_argument('--impurity',       default="gini",    type=str, help='Impurity type. Valid options in XGBoost are pending to be investigateda, Not effect so far.')
    #
    parser.add_argument('--covarType',      default="diagonal", type=str, help='Covariance matrix type: diagonal or full')
    parser.add_argument('--componentsGMM',  default="10:20:30", type=str, help='Max numbers of components for Gaussian Mixture Models')
    parser.add_argument('--codebookSize',   default="100:200:300", type=str, help='Colon separated list of the codebook sizes to apply kmeans (maybe before KDE when using it)')
    parser.add_argument('--bandWidth',      default="0.1:0.2:0.5:1.0:2.0", type=str, help='Colon separated list of the band width for the KDE classifier')
    parser.add_argument('--K',              default="2:3:5:7:9:11:13", type=str, help='Colon separated list of the n_neighbors width for the KNN classifier')
    #
    parser.add_argument('--n_jobs',         default=1,    type=int, help='Number of jobs to run using joblib or other approach. With no effect when launching in a Spark cluster')
    parser.add_argument('--batchSize',      default=500,  type=int, help='Number of samples in a batch. Currently effective for GMM')
    parser.add_argument('--block_size',     default=1000, type=int, help='Block size to make as cache-friendly the matrix operations')

    main(parser.parse_args())
