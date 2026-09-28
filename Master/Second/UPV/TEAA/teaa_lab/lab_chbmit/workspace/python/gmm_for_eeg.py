"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 2.0
    Date: September 2025

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for using Gaussian Mixture Models (GMM) to compute the
    conditional probability density of a sample with respect to each 
    target class.
"""
import os
import time
import pickle
import numpy
import ray

from RayGMM import RayGMM
from utils_for_results import save_results

# ------------------------------------------------------------------------------------------------------------------------
def gmm_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test):
    #
    list_of_gmm_components = [int(s) for s in args.componentsGMM.split(sep = ':')]
    print('sizes for GMM', list_of_gmm_components, flush = True)
    #
    use_ray_gmm = len(train_data) != num_samples_train # to decide whether running in local CPU with no RAY cluster (local or kubernetes)
    #
    PATIENT, INDEX, TTS, LABEL, PROBS = 0, 1, 2, 3, 4
    #
    models_dict = dict()
    models_dict['minimum'] = dict()
    for gmm_components in list_of_gmm_components:
        # THIS FOR ALSO LOADS MODELS FROM DISK IF THEY WERE PREVIOUSLY TRAINED
        models_dict[gmm_components] = dict()
        starting_time = time.time()
        training_has_been_carried_out = False
        #
        for target_class in args.labels:
            #
            models_dir = f'{args.models_dir}/{args.format}/target_class_{target_class}'
            os.makedirs(models_dir, exist_ok = True)
            gmm_filename = f'{models_dir}/gmm-{args.patient}-{args.format}-{args.task}-{gmm_components:04d}.npy'
            #
            gmm = RayGMM(
                n_clusters = gmm_components,
                n_workers = args.n_workers,
                covar_type = args.covarType,
                tolerance = 1.0e-4,
                dim = args.input_dim,
                block_size = args.block_size,
                n_init = 1,
                verbose = args.verbose
            )

            if os.path.exists(gmm_filename):
                with open(gmm_filename, 'rb') as f:
                    gmm.means_ = numpy.load(f)
                    gmm.covs_ = numpy.load(f)
                    gmm.weights_ = numpy.load(f)
                    (gmm.log_likelihood_, gmm.n_iter_, gmm.n_features_in, gmm.seconds_per_iteration_) = numpy.load(f)
                    gmm.n_clusters = gmm.means_.shape[0]
                    f.close()
            # end-if os.path.exists
            else:
                if use_ray_gmm:
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
                else:
                    X_one_class = numpy.array([x[4] for x in train_data if x[LABEL] == target_class])
                    num_samples_train_one_target_class = len(X_one_class)
                # end-if use_ray_gmm

                do_fit = True
                if num_samples_train_one_target_class <= 100 * gmm_components:
                    gmm.n_clusters = max(1, num_samples_train_one_target_class // 100)
                    print(f"WARNING: No GMM generated for target class {target_class} with {gmm_components} components because {num_samples_train_one_target_class} examples are not enough!!! {gmm.n_clusters} components are used instead.", flush = True)
                    if target_class in models_dict['minimum']:
                        del gmm
                        gmm = models_dict['minimum'][target_class]
                        do_fit = False

                if do_fit:
                    training_has_been_carried_out = True
                    if use_ray_gmm:
                        gmm.fit(train_data_one_target_class)
                    else:
                        gmm.fit(X_one_class)
                    # end-if use_ray_gmm

                    with open(gmm_filename, 'wb') as f:
                        numpy.save(f, gmm.means_)
                        numpy.save(f, gmm.covs_)
                        numpy.save(f, gmm.weights_)
                        numpy.save(f, [gmm.log_likelihood_, gmm.n_iter_, gmm.n_features_in, gmm.seconds_per_iteration_])
                        f.close()
                    #
                if use_ray_gmm:
                    for _ref_ in train_data_one_target_class: del _ref_
                else:
                    del X_one_class
                # end-if use_ray_gmm
            # end-if-else os.path.exists
            models_dict[gmm_components][target_class] = gmm
            if target_class not in models_dict['minimum']:
                models_dict['minimum'][target_class] = gmm
            #
        # end-for target_class
        gmm_estimation_time = time.time() - starting_time
        if training_has_been_carried_out:
            # save KPIs to measure the quality of the clusterings
            kpis_filename = f'{args.log_dir}/gmm-{args.format}-{args.patient}-kpis.csv'
            print_header = not os.path.exists(kpis_filename)
            with open(kpis_filename, 'at') as f:
                if print_header:
                    print('gmm_components;seconds;task;execution_environment', file = f)
                print(f'{gmm_components};{gmm_estimation_time};{args.task};{args.exec_environment_id}', file = f)
                f.close()
            #
        # end-if training_has_been_carried_out
    # end-for gmm_components

    #
    DELTA = args.delta # as each sample comes every 2 seconds
    #
    data_subsets = {'train' : train_data, 'test' : test_data}

    for subset in ['train', 'test']:
        #
        data = data_subsets[subset]
        if use_ray_gmm:
            X = None
            # ---------------------------------------------------------------------------------------------------
            @ray.remote
            def get_metadata(_dict_):
                l = list()
                for i in range(len(_dict_['X'])):
                    #                 PATIENT,              INDEX,              TTS,              LABEL,      PROBS = 0, 1, 2, 3, 4
                    l.append([_dict_['patient'][i], _dict_['index'][i], _dict_['tts'][i], _dict_['label'][i], None])
                return l
            # --------------------------------------------------------------------------------
            futures = [get_metadata.remote(_ref_) for _ref_ in data]
            prediction = [t for l in ray.get(futures) for t in l]
        else:
            X = numpy.array([x[4] for x in data])
            prediction = [[t[PATIENT], t[INDEX], t[TTS], t[LABEL], None] for t in data]
        #
        gmms = [None] * len(args.labels)
        for gmm_components in list_of_gmm_components:
            for target_class in args.labels:
                if models_dict[gmm_components] is not None and target_class in models_dict[gmm_components]:
                    gmms[target_class] = models_dict[gmm_components][target_class]

            if use_ray_gmm:
                # ---------------------------------------------------------------------------------------------------
                @ray.remote
                def my_score_samples(_dict_, gmms):
                    return numpy.hstack([gmm.score_samples(_dict_['X']).reshape(-1, 1) for gmm in gmms])
                # ---------------------------------------------------------------------------------------------------
                futures = [my_score_samples.remote(_ref_, gmms) for _ref_ in data]
                log_densities = numpy.vstack(ray.get(futures))
            else:
                log_densities = numpy.hstack([gmm.score_samples(X).reshape(-1, 1) for gmm in gmms])

            densities = numpy.exp(log_densities)
            probs = densities / numpy.maximum(densities.sum(axis = 1).reshape(-1, 1), 1.0e-58)
            print('probs.shape = ', probs.shape, flush = True)
            print(f"predicting with {args.technique} using a GMM with a maximum of {gmm_components} components for {subset} subset required {time.time() - starting_time} seconds", flush = True)

            for i in range(len(probs)):
                prediction[i][PROBS] = probs[i]

            if X is not None:
                del X
                X = None
            ####################################################################################################################
            starting_time = time.time()
            #
            y_true_and_pred = list()
            probabilities = numpy.zeros(len(args.labels))
            fifo = list()
            t = 0
            counter = 0
            previous_patient = -1
            previous_index = 0
            while t < len(prediction):
                current_patient, current_index, current_tts, current_label, current_probabilities = prediction[t]
                #
                if current_patient != previous_patient or current_index != previous_index + 1:
                    probabilities[:] = 0.0
                    counter = 0
                    fifo = list()
                #
                probabilities += current_probabilities
                fifo.append(current_probabilities)
                counter += 1
                if counter >= DELTA:
                    k = probabilities.argmax()
                    y_true_and_pred.append((current_label, k))
                    #
                    probabilities -= fifo[0]
                    fifo.pop(0)
                #
                previous_patient = current_patient
                previous_index = current_index
                t += 1
            # end of while t
            y_true = numpy.array([x[0] for x in y_true_and_pred])
            y_pred = numpy.array([x[1] for x in y_true_and_pred])
            elapsed_time = time.time() - starting_time
            ####################################################################################################################
            #
            print(subset, len(y_true), len(y_pred), f'classification required {elapsed_time} seconds', flush = True)
            filename_prefix = f'gmm-{args.format}-{args.patient}-{args.task}-{gmm_components:04d}-{args.exec_environment_id}'
            save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = elapsed_time, labels = args.labels)
        #
# --------------------------------------------------------------------------------
