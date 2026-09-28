"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 3.0
    Date: October 2025

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for using Kernel Density Estimators (KDE)
    to classify each sample into one of the target classes.
"""
import os
import sys
import time
import pickle
import math
import numpy
import heapq
import ray

from RayKMeans import RayKMeans

from sklearn.metrics.pairwise import euclidean_distances

from RayKMeans import RayKMeans
from NearestNeighbours import KDE_Classifier, KNN_Classifier

from utils_for_eeg import do_prediction_considering_sequenciality
from utils_for_results import save_results

# ------------------------------------------------------------------------------------------------------------------------
def kde_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test):
    #
    assert args.technique in ['kde', 'knn']
    #
    list_of_kmeans_codebook_sizes = [int(s) for s in args.codebookSize.split(sep = ':')]
    print('list of kmeans codebook sizes', list_of_kmeans_codebook_sizes)
    if args.technique == 'kde':
        list_of_bandwidths = [float(s) for s in args.bandWidth.split(sep = ':')]
        print('list of bandwidths', list_of_bandwidths, flush = True)
    elif args.technique == 'knn':
        list_of_Ks = [int(s) for s in args.K.split(sep = ':')]
        print('list of K', list_of_Ks, flush = True)
    #
    use_ray_kde = len(train_data) != num_samples_train # to decide whether running in local CPU with no RAY cluster (local or kubernetes)
    #
    PATIENT, INDEX, TTS, LABEL, PROBS = 0, 1, 2, 3, 4
    #
    models_dict = dict()
    models_dict['minimum'] = dict()
    for codebook_size in list_of_kmeans_codebook_sizes:
        # REMEMBER THAT codebook_size = 0 MEANS NOT TO DO A PREVIOUS KMEANS, i.e., DO NOT APPLY ML SCALABILITY
        if codebook_size == 0:
            codebook_size = 'no_kmeans'
        # THIS FOR ALSO LOADS MODELS FROM DISK IF THEY WERE PREVIOUSLY TRAINED
        models_dict[codebook_size] = dict()
        #
        for target_class in args.labels:
            starting_time = time.time()
            training_has_been_carried_out = False
            #
            kmeans_models_dir = f'{args.models_dir}/{args.patient}/{args.format}/target_class_{target_class}'
            os.makedirs(kmeans_models_dir, exist_ok = True)
            if codebook_size != 'no_kmeans':
                codebook_filename = f'{kmeans_models_dir}/kmeans-{args.patient}-{args.format}-{args.task}-{codebook_size:04d}.npy'
            else:
                codebook_filename = f'{kmeans_models_dir}/kmeans-{args.patient}-{args.format}-{args.task}-{codebook_size}.npy'
            #
            if os.path.exists(codebook_filename):
                with open(codebook_filename, 'rb') as f:
                    kmeans_model = pickle.load(f)
                    f.close()
            else: # else-if os.path.exists
                kmeans_model = RayKMeans(
                    n_clusters = codebook_size if codebook_size != 'no_kmeans' else -1,
                    n_workers = args.n_workers,
                    n_init = 1,
                    tolerance = 1.0e-4,
                    max_iter = 300,
                    block_size = args.block_size,
                    verbose = args.verbose
                )
                if use_ray_kde:
                    # ---------------------------------------------------------------------------------------------------
                    @ray.remote
                    def filter_by_target_class(_dict_, target_class):
                        y       = _dict_['y']
                        X       = _dict_['X'      ][y == target_class].copy()
                        label   = _dict_['y'      ][y == target_class].copy()
                        tts     = _dict_['tts'    ][y == target_class].copy()
                        patient = _dict_['patient'][y == target_class].copy()
                        index   = _dict_['index'  ][y == target_class].copy()
                        return {'X': X, 'y': label, 'label': label, 'patient': patient, 'tts': tts, 'index': index}
                    # ---------------------------------------------------------------------------------------------------
                    @ray.remote
                    def count_samples(_dict_):
                        return len(_dict_['X'])
                    # ---------------------------------------------------------------------------------------------------
                    train_data_one_target_class = [filter_by_target_class.remote(_ref_, target_class) for _ref_ in train_data]
                    num_samples_train_one_target_class = sum(ray.get([count_samples.remote(_ref_) for _ref_ in train_data_one_target_class]))
                    #############################################################################################################
                    ### Skip empty data shards after filtering by target class
                    #############################################################################################################
                    tdotc = ray.get(train_data_one_target_class)
                    _temp_ = list()
                    for i in range(len(tdotc)):
                        print(f'kde_for_eeg(target_class = {target_class})', len(train_data_one_target_class), tdotc[i]['X'].shape, num_samples_train_one_target_class, flush = True)
                        if len(tdotc[i]['X']) > 0:
                            _temp_.append(train_data_one_target_class[i])
                    del tdotc
                    train_data_one_target_class = _temp_
                    #############################################################################################################
                    ### Skip empty data shards after filtering by target class
                    #############################################################################################################
                else:
                    X_one_class = numpy.array([x[4] for x in train_data if x[LABEL] == target_class])
                    num_samples_train_one_target_class = len(X_one_class)
                # end-if use_ray_kde

                do_fit = True
                if codebook_size == 'no_kmeans' or num_samples_train_one_target_class <= 2 * codebook_size:
                    kmeans_model.n_clusters = num_samples_train_one_target_class
                    if args.verbose > 0:
                        if codebook_size == 'no_kmeans':
                            print(f"INFO: No KMeans generated for target class {target_class} according to the configuration. Working with {kmeans_model.n_clusters} for target class {target_class}.", flush = True)
                        else:
                            print(f"INFO: No KMeans generated for target class {target_class} with {codebook_size} clusters because {num_samples_train_one_target_class} examples are not enough!!! {kmeans_model.n_clusters} components are used instead.", flush = True)
                    if use_ray_kde:
                        # ---------------------------------------------------------------------------------------------------
                        @ray.remote
                        def get_samples(_dict_):
                            return _dict_['X']
                        # ---------------------------------------------------------------------------------------------------
                        kmeans_model.cluster_centers_ = numpy.vstack(ray.get([get_samples.remote(_ref_) for _ref_ in train_data_one_target_class]))
                    else:
                        kmeans_model.cluster_centers_ = X_one_class.copy()
                    kmeans_model.wssse_ = 0
                    kmeans_model.n_iter_ = 0
                    kmeans_model.n_features_in = kmeans_model.cluster_centers_.shape[1]
                    kmeans_model.seconds_per_iteration_ = 0
                    do_fit = False

                if do_fit:
                    training_has_been_carried_out = True
                    if use_ray_kde:
                        kmeans_model.fit(X_refs = train_data_one_target_class)
                    else:
                        kmeans_model.fit(X = X_one_class)
                    # end-if use_ray_kde
                    with open(codebook_filename, 'wb') as f:
                        pickle.dump(kmeans_model, f)
                        f.close()
                    #
                # end-if do_fit
                if use_ray_kde:
                    for _ref_ in train_data_one_target_class: del _ref_
                else:
                    del X_one_class
                # end-if use_ray_kde
            # end-if-else os.path.exists
            models_dict[codebook_size][target_class] = kmeans_model
            if codebook_size != 'no_kmeans' and target_class not in models_dict['minimum']:
                models_dict['minimum'][target_class] = kmeans_model
            #
            kmeans_estimation_time = time.time() - starting_time
            if training_has_been_carried_out:
                # save KPIs to measure the quality of the clusterings
                kpis_filename = f'{args.log_dir}/{args.technique}_kmeans-{args.format}-{args.patient}-kpis.csv'
                print_header = not os.path.exists(kpis_filename)
                with open(kpis_filename, 'at') as f:
                    if print_header:
                        print('task;target_class;codebook_size;kmeans_estimation_time;execution_environment', file = f)
                    print(f'{args.task};{target_class};{codebook_size};{kmeans_estimation_time:.4f};{args.exec_environment_id}', file = f)
                    f.close()
                #
            # end-if training_has_been_carried_out
        # end-for target_class
    # end-for codebook_size
    if use_ray_kde:
        # ---------------------------------------------------------------------------------------------------
        @ray.remote
        def get_metadata(_dict_):
            l = list()
            for i in range(len(_dict_['X'])):
                #                 PATIENT,              INDEX,              TTS,              LABEL,      PROBS = 0, 1, 2, 3, 4
                l.append([_dict_['patient'][i], _dict_['index'][i], _dict_['tts'][i], _dict_['label'][i], None])
            return l
        # --------------------------------------------------------------------------------
        dict_of_prediction = dict()
        for subset, data in zip(['train', 'test'], [train_data, test_data]):
            futures = [get_metadata.remote(_ref_) for _ref_ in data]
            #prediction = [t for l in ray.get(futures) for t in l]
            prediction = list()
            for l in ray.get(futures):
                prediction += l
            dict_of_prediction[subset] = prediction
    else:
        dict_of_prediction = {
            'train': [[t[PATIENT], t[INDEX], t[TTS], t[LABEL], None] for t in train_data],
             'test': [[t[PATIENT], t[INDEX], t[TTS], t[LABEL], None] for t in  test_data],
        }
    #########################################################################################################
    for codebook_size in list_of_kmeans_codebook_sizes:
        # REMEMBER THAT codebook_size = 0 MEANS NOT TO DO A PREVIOUS KMEANS, i.e., DO NOT APPLY ML SCALABILITY
        if codebook_size == 0:
            codebook_size = 'no_kmeans'
        #
        X_train = dict()
        for label in args.labels:
            if label in models_dict[codebook_size]:
                X_train[label] = models_dict[codebook_size][label].cluster_centers_
            else:
                X_train[label] = models_dict['minimum'][label].cluster_centers_
        #
        starting_time = time.time()
        if args.technique == 'kde':
            model = KDE_Classifier(bandwidth = 1.0, K = 100, block_size = args.block_size)
            model.fit(X = X_train, y = None)
            training_time = time.time() - starting_time
            print(f'training a {args.technique} classifier with {codebook_size} and for all bandwidths required {training_time} seconds', flush = True)
        elif args.technique == 'knn':
            model = KNN_Classifier(K = 3, block_size = args.block_size)
            model.fit(X = X_train, y = None)
            training_time = time.time() - starting_time
            print(f'training a {args.technique} classifier with {codebook_size} and for all K required {training_time} seconds', flush = True)
        #
        if use_ray_kde:
            _model_ref_ = ray.put(model)
        #
        list_of_hyperparameters = list_of_bandwidths if args.technique == 'kde' else list_of_Ks
        for hyperparameter in list_of_hyperparameters:
            #
            if args.technique == 'kde':
                model.bandwidth = hyperparameter # just in case, this is redundant with the call to method predict_proba()
                # ------------------------------------------------------------------------------------------------------
                @ray.remote
                def set_bandwidth(_model_, bandwidth):
                    _model_.bandwidth = bandwidth
                    return None
                # ------------------------------------------------------------------------------------------------------
                futures = [set_bandwidth.remote(_model_ref_, hyperparameter)]
                ray.get(futures)
            elif args.technique == 'knn':
                model.K = hyperparameter
                # ------------------------------------------------------------------------------------------------------
                @ray.remote
                def set_K(_model_, K):
                    _model_.K = K
                    return None
                # ------------------------------------------------------------------------------------------------------
                futures = [set_K.remote(_model_ref_, hyperparameter)]
                ray.get(futures)
            #
            data_subsets = {'train' : train_data, 'test' : test_data}
            #
            for subset in ['train', 'test']:
                #
                prediction = dict_of_prediction[subset]
                #
                inference_time = time.time()
                if use_ray_kde:
                    # ------------------------------------------------------------------------------------------------------
                    @ray.remote
                    def kde_predict(_dict_, _model_, bandwidth: float):
                        return _model_.predict_proba(X = _dict_['X'], bandwidth = bandwidth)
                    # ------------------------------------------------------------------------------------------------------
                    @ray.remote
                    def knn_predict(_dict_, _model_, K: int):
                        return _model_.predict_proba(X = _dict_['X'], K = K)
                    # ------------------------------------------------------------------------------------------------------
                    if args.technique == 'kde':
                        futures = [kde_predict.remote(_ref_, _model_ref_, bandwidth = hyperparameter) for _ref_ in data_subsets[subset]]
                    elif args.technique == 'knn':
                        futures = [knn_predict.remote(_ref_, _model_ref_, K = hyperparameter) for _ref_ in data_subsets[subset]]
                    probs = numpy.vstack(ray.get(futures))
                else:
                    if args.technique == 'kde':
                        probs = model.predict_proba(X = data_subsets[subset], bandwidth = hyperparameter)
                    elif args.technique == 'knn':
                        probs = model.predict_proba(X = data_subsets[subset], K = hyperparameter)

                for i in range(len(prediction)):
                    prediction[i][PROBS] = probs[i]

                computing_proba_time_lapse = time.time() - inference_time

                if args.verbose > 0:
                    print(f'computing probs for {subset} subset required {computing_proba_time_lapse} seconds', flush = True)
                            
                y_true, y_pred = do_prediction_considering_sequenciality(
                            labels = args.labels,
                            prediction = prediction,
                            y_proba = probs,
                            DELTA = args.delta,
                )
                inference_time = time.time() - inference_time
                #prediction.sort(key = lambda x: f'{x[PATIENT]}-{x[INDEX]:010d}')
                if args.verbose > 0:
                    if codebook_size == 'no_kmeans':
                        if args.technique == 'kde':
                            print(f'prediction complete for {subset} with no kmeans and bandwidth {hyperparameter} lasting {inference_time} seconds', flush = True)
                        elif args.technique == 'knn':
                            print(f'prediction complete for {subset} with no kmeans and K {hyperparameter} lasting {inference_time} seconds', flush = True)
                    else:
                        if args.technique == 'kde':
                            print(f'prediction complete for {subset} with cb_size {codebook_size} and bandwidth {hyperparameter} lasting {inference_time} seconds', flush = True)
                        elif args.technique == 'knn':
                            print(f'prediction complete for {subset} with cb_size {codebook_size} and K {hyperparameter} lasting {inference_time} seconds', flush = True)

                if args.verbose > 0:
                    print(subset, len(y_true), len(y_pred), inference_time, 'seconds', flush = True)

                if codebook_size == 'no_kmeans':
                    if args.technique == 'kde':
                        filename_prefix = f'{args.technique}-{args.format}-{args.patient}-{args.task}-{codebook_size}-{hyperparameter:.3f}-{args.exec_environment_id}'
                    elif args.technique == 'knn':
                        filename_prefix = f'{args.technique}-{args.format}-{args.patient}-{args.task}-{codebook_size}-{hyperparameter:02d}-{args.exec_environment_id}'
                else:
                    if args.technique == 'kde':
                        filename_prefix = f'{args.technique}-{args.format}-{args.patient}-{args.task}-{codebook_size:04d}-{hyperparameter:.3f}-{args.exec_environment_id}'
                    elif args.technique == 'knn':
                        filename_prefix = f'{args.technique}-{args.format}-{args.patient}-{args.task}-{codebook_size:04d}-{hyperparameter:02d}-{args.exec_environment_id}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
            # for subset
        # for bandwidth 
        if use_ray_kde:
            del _model_ref_
        del model
    # for codebook_size 
# --------------------------------------------------------------------------------
