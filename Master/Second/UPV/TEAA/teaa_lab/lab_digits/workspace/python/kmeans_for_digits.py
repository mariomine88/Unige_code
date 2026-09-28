"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.2
    Date: August 2025

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for using KMeans to generate a codebook that properly
    combined with conditional probabilities is used to create a classifier
"""
import os
import sys
import time
import pickle
import math
import numpy

from utils_for_results import save_results
from load_mnist import load_mnist

from sklearnex import patch_sklearn

# --------------------------------------------------------------------------------
def load_conditional_probabilities(counter_pairs_filename):
    counter_pairs = None
    with open(counter_pairs_filename, 'rt') as f:
        counter_pairs = list()
        for line in f:
            counter_pairs.append([float(x) for x in line.split(';')])
        f.close()
        counter_pairs = numpy.array(counter_pairs)

    '''
        Compute the conditional probabilities

        'counter_pairs' contains the counters of how many times a cluster has been observed per target class,
            rows represent target classes
            columns represent clusters

            Normalizing by rows we get the conditional probabilities of each cluster with respect to each target class:

                Pr(cluster | target_class)
    '''
    #counter_pairs += 1 # smoothing

    # Compute the conditional probabilities of each cluster with respect to each target classes
    pr_cluster_target_class = counter_pairs / numpy.maximum(1.0, counter_pairs.sum(axis = 1).reshape(-1, 1))

    # Compute the a priori probabilities of target classes
    target_class_a_priori_probabilities = counter_pairs.sum(axis = 1) / counter_pairs.sum()

    return target_class_a_priori_probabilities, pr_cluster_target_class
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
def kmeans_for_digits(args, train_data, test_data):

    patch_sklearn()

    # The next two lines are mutually exclusive:
    #from sklearn.cluster import KMeans # Use this one to run the experiments with low level parallelisation with Numpy and Scikit Learn
    from RayKMeans import RayKMeans # Use this one to run the experiments using RAY in the configuration of a local cluster (one physical machine)
    from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, euclidean_distances

    # Prepares the list of codebook sizes to explore
    list_of_num_clusters = [int(cb_size) for cb_size in args.codebookSize.split(sep = ':')]
    print('list number of clusters/codebook sizes:', list_of_num_clusters, flush = True)

    technique = 'kmeans'

    # creates samples by removing patient id, index, tts and label
    samples = train_data['x']
    num_samples = len(samples)
    c_E = samples.mean(axis = 0)
    print(f'working with {num_samples} for training', flush = True)

    for num_clusters in list_of_num_clusters:
        codebook_filename = f'{args.models_dir}/{technique}-pca-{args.pcaComponents:04d}-num_clusters-{num_clusters:04d}.pkl'
        if os.path.exists(codebook_filename):
            with open(codebook_filename, 'rb') as f:
                kmeans_model = pickle.load(f)
                f.close()
            
            print(f'loaded codebook for {num_clusters}', flush = True)
            time_lapse_clustering = 0
        else: # Build the model (cluster the data)
            print(f'running KMeans for creating a codebook with {num_clusters} clusters', flush = True)
            starting_time = time.time()
            # The next two lines are mutually exclusive:
            #kmeans_model = KMeans(n_clusters = num_clusters, init = 'k-means++', n_init = 5, tol = 1.0e-9, algorithm = 'lloyd') # Use this one to run the experiments with low level parallelisation with Numpy and Scikit Learn
            kmeans_model = RayKMeans(n_clusters = num_clusters, n_workers = args.n_jobs, n_init = 5, tolerance = 1.0e-4, verbose = args.verbose) # Use this one to run the experiments using RAY in the configuration of a local cluster (one physical machine)
            kmeans_model.fit(X = samples)
            ending_time = time.time()
            print(f'processing time lapse for {num_clusters} clusters {ending_time - starting_time} seconds', flush = True)
            time_lapse_clustering = ending_time - starting_time

            if args.verbose > 1:
                print(len(kmeans_model.cluster_centers_), kmeans_model.cluster_centers_[0].shape, flush = True)

            with open(codebook_filename, 'wb') as f:
                pickle.dump(kmeans_model, f)
                f.close()

        starting_time = time.time()
        distances_to_clusters = kmeans_model.transform(samples)
        predicted_k = distances_to_clusters.argmin(axis = 1)
        d = distances_to_clusters.min(axis = 1)
        d2 = d * d
        WSSSE = d2.sum()
        calinski_harabasz_index = calinski_harabasz_score(samples, predicted_k)
        davies_bouldin_index = davies_bouldin_score(samples, predicted_k)
        ending_time = time.time()

        print('computing metrics time lapse for', num_clusters, 'clusters', ending_time - starting_time, 'seconds')

        print(f'Within Set Sum of Squared Error (WSSSE) is {WSSSE} and normalized per sample is {WSSSE / num_samples}')
        print(f'Calinski Harabasz index for {num_clusters} clusters is {calinski_harabasz_index}')
        print(f'Davies Bouldin index for {num_clusters} clusters is {davies_bouldin_index}')

        # save KPIs to measure the quality of the clusterings
        if time_lapse_clustering > 0:
            kpis_filename = f'{args.log_dir}/{technique}-pca-{args.pcaComponents:04d}-kpis.csv'
            print_header = not os.path.exists(kpis_filename)
            with open(kpis_filename, 'at') as f:
                if print_header:
                    print('pca;codebook_size;WSSSE_per_sample;Calinski_Harabasz_index;Davies_Bouldin_index;seconds;execution_environment;n_jobs', file = f)
                print(f'{args.pcaComponents};{num_clusters};{WSSSE / num_samples};{calinski_harabasz_index};{davies_bouldin_index};{time_lapse_clustering};{args.exec_environment_id};{args.n_jobs}', file = f)
                f.close()
        #
        y_true = train_data['y']
        #
        counters = numpy.zeros([len(args.labels), num_clusters])
        for i in range(len(y_true)):
            counters[y_true[i], predicted_k[i]] += 1
        #
        counters_filename = f'{args.models_dir}/{technique}-cluster-distribution-pca-{args.pcaComponents:04d}-num_clusters-{num_clusters:04d}.csv'
        f = open(counters_filename, 'wt')
        for l in range(len(counters)):
            print(";".join("{:.0f}".format(v) for v in counters[l]), file = f)
        f.close()
        #
        ####################################################################

        # Load the conditional probabilities
        target_class_a_priori_probabilities, cond_prob_cluster_per_target_class = load_conditional_probabilities(counters_filename)

        data_subsets = {'train' : train_data, 'test' : test_data}

        for subset in ['train', 'test']:
            starting_time = time.time()
            data = data_subsets[subset]
            k_pred = kmeans_model.predict(data['x'])
            y_prob = target_class_a_priori_probabilities * numpy.array([cond_prob_cluster_per_target_class[:, k] for k in k_pred])
            y_pred = y_prob.argmax(axis = 1)
            y_true = data['y']
            inference_time = time.time() - starting_time

            if args.verbose > 0: print(subset, len(y_true), len(y_pred), inference_time, 'seconds')

            filename_prefix = f'{technique}-pca-{args.pcaComponents:04d}-num_clusters-{num_clusters:04d}'
            save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
        # for subset
    # for num_clusters
# --------------------------------------------------------------------------------
