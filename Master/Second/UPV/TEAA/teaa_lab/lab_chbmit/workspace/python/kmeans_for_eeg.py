"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.2
    Date: September 2025

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

import ray

from utils_for_results import save_results

try:
    from sklearnex import patch_sklearn
except:
    patch_sklearn = None

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
@ray.remote
def compute_joint_probabilities_map(_ref_, kmeans_model, K):
    counters = numpy.zeros([K, len(kmeans_model.cluster_centers_)])
    assert type(_ref_) == dict
    X = _ref_['X']
    y_true = _ref_['y'].flatten()

    distances = kmeans_model.transform(X, squared = True)
    k_pred = distances.argmin(axis = 1)
    for y, k in zip(y_true, k_pred):
        counters[int(y), k] += 1
    #
    return counters
# ----------------------------------------------------------------------------------------
"""
@ray.remote
def ray_kmeans_distances(_dict_, kmeans_model, squared = True):
    return kmeans_model.transform(_dict_['X'], squared = squared)
"""
# --------------------------------------------------------------------------------
@ray.remote
def kmeans_predict(_dict_, kmeans_model):
    if patch_sklearn is not None: patch_sklearn()
    return kmeans_model.predict(_dict_['X']) # the RayKMeans.predict() method performs the computations per block
# --------------------------------------------------------------------------------
@ray.remote
def get_metadata(_dict_):
    l = list()
    for i in range(len(_dict_['X'])):
        # PATIENT, INDEX, TTS, LABEL, CLUSTER = 0, 1, 2, 3, 4
        l.append([_dict_['patient'][i], _dict_['index'][i], _dict_['tts'][i], _dict_['label'][i]])
    return l
# --------------------------------------------------------------------------------
def kmeans_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test):

    from RayKMeans import RayKMeans
    #from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score

    # Prepares the list of codebook sizes to explore
    list_of_num_clusters = [int(cb_size) for cb_size in args.codebookSize.split(sep = ':')]
    print('list number of clusters/codebook sizes:', list_of_num_clusters, flush = True)

    technique = 'kmeans'

    if len(train_data) == num_samples_train: # running in local CPU with no RAY cluster (local or kubernetes)
        # creates samples by removing patient id, index, tts and label
        samples = numpy.array([x[4] for x in train_data])
        c_E = samples.mean(axis = 0)
        use_ray_kmeans = False
    else:
        samples = None
        @ray.remote
        def sum_X(_dict_):
            return _dict_['X'].sum(axis = 0)
        futures = [sum_X.remote(_ref_) for _ref_ in train_data]
        c_E = sum(ray.get(futures)) / num_samples_train
        use_ray_kmeans = True
    print(f'working with {num_samples_train} for training', flush = True)

    for num_clusters in list_of_num_clusters:
        codebook_filename = f'{args.models_dir}/{technique}-{args.format}-{args.patient}-{num_clusters:04d}.pkl'
        if os.path.exists(codebook_filename):
            with open(codebook_filename, 'rb') as f:
                kmeans_model = pickle.load(f)
                f.close()
            
            print(f'loaded codebook for {num_clusters}', flush = True)
            time_lapse_clustering = 0
        else: # Build the model (cluster the data)
            print(f'running KMeans for creating a codebook with {num_clusters} clusters', flush = True)
            starting_time = time.time()
            kmeans_model = RayKMeans(
                                n_clusters = num_clusters,
                                n_workers = args.n_workers,
                                n_init = 1,
                                tolerance = 1.0e-3,
                                block_size = args.block_size,
                                verbose = args.verbose
            )
            if use_ray_kmeans:
                kmeans_model.fit(X_refs = train_data)
            else:
                kmeans_model.fit(X = samples)
            ending_time = time.time()
            print(f'processing time lapse for {num_clusters} clusters {ending_time - starting_time} seconds', flush = True)
            time_lapse_clustering = ending_time - starting_time

            if args.verbose > 1:
                print(len(kmeans_model.cluster_centers_), kmeans_model.cluster_centers_[0].shape, flush = True)

            with open(codebook_filename, 'wb') as f:
                pickle.dump(kmeans_model, f)
                f.close()

        # save KPIs to measure the quality of the clusterings
        if time_lapse_clustering > 0:
            starting_time = time.time()
            if use_ray_kmeans:
                futures = [kmeans_predict.remote(_ref_, kmeans_model) for _ref_ in train_data]
                k_pred = numpy.hstack(ray.get(futures))
            else:
                k_pred = kmeans_model.predict(samples)
            k_counts = numpy.bincount(k_pred)
            WSSSE = kmeans_model.wssse_
            BCSS = sum([k_counts[c] * sum((kmeans_model.cluster_centers_[c] - c_E) ** 2) for c in range(num_clusters)])
            calinski_harabasz_index = (BCSS * (num_samples_train - num_clusters)) / (WSSSE * (num_clusters - 1))
            @ray.remote
            def db_S_i(_dict_, kmeans_model):
                X = _dict_['X']
                distances = kmeans_model.transform(X, squared = True)
                k_pred = distances.argmin(axis = 1)
                S = numpy.array([distances[k_pred == k, k].sum() for k in range(kmeans_model.n_clusters)])
                # S[i] is the temporary sum of distances to samples in cluster i to its centroid
                return S
            # -----------------------------------------------
            futures = [db_S_i.remote(_ref_, kmeans_model) for _ref_ in train_data]
            S = numpy.sqrt(sum(ray.get(futures)) / k_counts)
            assert S.shape == (num_clusters,)
            from sklearn.metrics.pairwise import euclidean_distances
            M = euclidean_distances(kmeans_model.cluster_centers_, kmeans_model.cluster_centers_, squared = False)
            assert M.shape == (num_clusters, num_clusters)
            R = numpy.zeros([num_clusters, num_clusters])
            for i in range(num_clusters):
                if k_counts[i] > 0:
                    for j in range(num_clusters):
                        R[i, j] = (S[i] + S[j]) / M[i, j] if i != j and k_counts[j] > 0 else 0
                else:
                    R[i, :] = 0
            davies_bouldin_index = sum([R[i,:].max() for i in range(num_clusters)]) / num_clusters
            """
            if samples is None:
                @ray.remote
                def get_samples(_dict_):
                    return _dict_['X']
                # ----------------------------
                futures = [get_samples.remote(_ref_) for _ref_ in train_data]
                samples = numpy.vstack(ray.get(futures))
            calinski_harabasz_index = calinski_harabasz_score(samples, k_pred)
            davies_bouldin_index = davies_bouldin_score(samples, k_pred)
            """
            ending_time = time.time()

            print('computing metrics time lapse for', num_clusters, 'clusters', ending_time - starting_time, 'seconds')

            print(f'Within Set Sum of Squared Error (WSSSE) is {WSSSE} and normalized per sample is {WSSSE / num_samples_train}')
            print(f'Calinski Harabasz index for {num_clusters} clusters is {calinski_harabasz_index}')
            print(f'Davies Bouldin index for {num_clusters} clusters is {davies_bouldin_index}', flush = True)

            print_header = not os.path.exists(f'{args.log_dir}/kmeans-{args.format}-{args.patient}-kpis.csv')
            with open(f'{args.log_dir}/kmeans-{args.format}-{args.patient}-kpis.csv', 'at') as f:
                if print_header:
                    print('codebook_size;WSSSE_per_sample;Calinski_Harabasz_index;Davies_Bouldin_index;seconds;execution_environment', file = f)
                print(f'{num_clusters};{WSSSE / num_samples_train};{calinski_harabasz_index};{davies_bouldin_index};{time_lapse_clustering};{args.exec_environment_id}', file = f)
                f.close()
        #
        starting_time = time.time()
        if use_ray_kmeans:
            futures = [compute_joint_probabilities_map.remote(_ref_, kmeans_model, len(args.labels)) for _ref_ in train_data]
            counters = sum(ray.get(futures))
        else:
            k_pred = kmeans_model.predict(samples)
            counters = numpy.zeros([len(args.labels), num_clusters])
            for i in range(len(train_data)):
                label = train_data[i][3]
                j = k_pred[i]
                counters[label, j] += 1
            #
        f = open(f'{args.models_dir}/cluster-distribution-{args.format}-{args.patient}-{args.task}-{num_clusters:04d}.csv', 'wt')
        for l in range(len(counters)):
            print(";".join("{:.0f}".format(v) for v in counters[l]), file = f)
        f.close()
        #
        ending_time = time.time()
        print('computing and saving conditional probabilities time lapse for', num_clusters, 'clusters', ending_time - starting_time, 'seconds', flush = True)
        #
        @ray.remote
        def get_cluster_and_tts(_ref_, kmeans_model):
            assert type(_ref_) == dict
            X = _ref_['X']
            tts = _ref_['tts'].flatten()
            #
            k_pred = kmeans_model.predict(X)
            l = [[k, t] for k, t in zip(k_pred, tts)]
            #
            return l
        # ------------------------------------------------------------------------------------------
        """
        futures = [get_cluster_and_tts.remote(_ref_, kmeans_model) for _ref_ in train_data]
        cluster_and_tts = [(k, t) for l in ray.get(futures) for k, t in l]
        tts_bins = [
            -100 * 60, # up to infinity after a seizure
             -10 * 60, # up to 10 minutes after a seizure
                  -10, # up to 10 seconds after a seizure
                   10, # within a seizure
              10 * 60, # up to 10 minutes before a seizure
              20 * 60, # up to 20 minutes before a seizure
              30 * 60, # up to 30 minutes before a seizure
              60 * 60, # up to 60 minutes before a seizure
         10 * 60 * 60, # up to 10 hours before a seizure
        ]
        histograms = list()
        for cluster_id in range(num_clusters):
            tts_per_cluster = [t[1] for t in cluster_and_tts if t[0] == cluster_id]
            histograms.append(numpy.histogram(tts_per_cluster, tts_bins))
        del cluster_and_tts
        #
        f = open(f'{args.models_dir}/histograms-{args.format}-{args.patient}-{num_clusters:04d}.csv', 'wt')
        edges = histograms[0][1]
        print(";".join("from {:.1f} to {:.1f}".format(float(edges[i-1]), float(edges[i])) for i in range(1, len(edges))), file = f)
        for hist, edges in histograms:
            print(";".join("{:.0f}".format(v) for v in hist), file = f)
        f.close()
        """

    ####################################################################
    if samples is not None:
        del samples
        samples = None
    # end if args.doTraining

    if args.doClassification or args.doBinaryClassification:
        for num_clusters in list_of_num_clusters:
            codebook_filename = f'{args.models_dir}/{technique}-{args.format}-{args.patient}-{num_clusters:04d}.pkl'
            with open(codebook_filename, 'rb') as f:
                kmeans_model = pickle.load(f)
                f.close()
            #
            print(f'loaded codebook for {num_clusters}', time.time(), flush = True)

            # Load the conditional probabilities
            target_class_a_priori_probabilities, cond_prob_cluster_per_target_class = load_conditional_probabilities(f'{args.models_dir}/cluster-distribution-{args.format}-{args.patient}-{args.task}-{num_clusters:04d}.csv')

            # this is a copy of the version used above during training
            def assign_sample_to_cluster(t):
                # remember, each item in the RDD object is a tuple with five elements: patient ID, sample index, tts, true labe and the sample
                patient, index, tts, label, sample = t 
                j = kmeans_model.predict(sample)
                # returns a tuple with the patient ID, sample index, tts, true label and cluster index
                return (patient, index, tts, label, j)
            #
        
            data_subsets = {'train' : train_data, 'test' : test_data}
            #
            PATIENT, INDEX, TTS, LABEL, CLUSTER = 0, 1, 2, 3, 4
            #
            DELTA = args.delta # as each sample comes every 2 seconds, this is one minute -- TO BE SET AS COMMAND LINE PARAMETER
            for subset in ['train', 'test']:
                print('computing cluster assignation', flush = True)
                starting_time = time.time()
                data = data_subsets[subset]
                #
                if use_ray_kmeans:
                    futures = [kmeans_predict.remote(_ref_, kmeans_model) for _ref_ in data]
                    k_pred = numpy.hstack(ray.get(futures))
                    futures = [get_metadata.remote(_ref_) for _ref_ in data]
                    cluster_assignation = [ca for l in ray.get(futures) for ca in l]
                    #
                    for i in range(len(cluster_assignation)):
                        cluster_assignation[i].append(k_pred[i])
                else:
                    samples = numpy.array([x[4] for x in data])
                    k_pred = kmeans_model.predict(samples)
                    #
                    cluster_assignation = []
                    for i in range(len(data)):
                        t = data[i]
                        cluster_assignation.append((t[0], t[1], t[2], t[3], k_pred[i]))
                    #
                #
                cluster_assignation.sort(key = lambda x: f'{x[PATIENT]}-{x[INDEX]:010d}')
                #
                elapsed_time = time.time() - starting_time
                print(f'cluster assignation required {elapsed_time} seconds', flush = True)
                print('performing classification', flush = True)
                starting_time = time.time()
                #
                y_true_and_pred = list()
                probabilities = numpy.zeros(len(args.labels))
                t = 0
                counter = 0
                previous_patient = -1
                previous_index = 0
                while t < len(cluster_assignation):
                    current_patient, current_index, current_tts, current_label, current_cluster = cluster_assignation[t]
                    #
                    if current_patient != previous_patient or current_index != previous_index + 1:
                        probabilities[:] = 0.0
                        counter = 0
                    #
                    densities = cond_prob_cluster_per_target_class[:, current_cluster]
                    probabilities += densities / max(1.0e-5, densities.sum())
                    counter += 1
                    if counter >= DELTA:
                        k = probabilities.argmax()
                        y_true_and_pred.append((current_label, k))
                        #
                        oldest_j = cluster_assignation[t - DELTA][CLUSTER]
                        densities = cond_prob_cluster_per_target_class[:, oldest_j]
                        probabilities -= densities / max(1.0e-5, densities.sum())
                    #
                    previous_patient = current_patient
                    previous_index = current_index
                    t += 1
                # end of while t
                y_true = numpy.array([x[0] for x in y_true_and_pred])
                y_pred = numpy.array([x[1] for x in y_true_and_pred])
                elapsed_time = time.time() - starting_time

                print(subset, len(y_true), len(y_pred), f'classification required {elapsed_time} seconds', flush = True)

                print('generating and saving results', flush = True)
                starting_time = time.time()
                filename_prefix = f'kmeans-{args.format}-{args.patient}-{args.task}-{num_clusters:04d}-{args.exec_environment_id}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = elapsed_time, labels = args.labels)
                elapsed_time = time.time() - starting_time
                print(f'generating and saving results required {elapsed_time} seconds', flush = True)

                if samples is not None:
                    del samples
            #
    # end if args.doClassification
# --------------------------------------------------------------------------------
