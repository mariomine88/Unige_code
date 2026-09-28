"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.2
    Date: April 2024

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

from RayGMM import RayGMM

from utils_for_results import save_results

# ------------------------------------------------------------------------------------------------------------------------
def estimate_gmm(args, X, n_components):

    if args.verbose > 1: print(type(X), X.shape, 'n_components', n_components)

    """
    gmm = GaussianMixture(n_components = n_components,
                            covariance_type = args.covarType,
                            tol = 1.0e-4,
                            reg_covar = 1.0e-6,
                            max_iter = 1000,
                            n_init = 5,
                            init_params = 'k-means++',
                            verbose = args.verbose)
    """
    gmm = RayGMM(n_clusters = n_components,
                    n_workers = args.n_jobs,
                    covar_type = args.covarType,
                    tolerance = 1.0e-4,
                    max_iter = 1000,
                    n_init = 5,
                    dim = X.shape[1],
                    block_size = args.batchSize,
                    verbose = args.verbose)
    gmm.fit(X)

    return gmm
# ------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
def gmm_for_digits(args, train_data, test_data):

    # Prepares the list of codebook sizes to explore
    list_of_gmm_components = [int(s) for s in args.componentsGMM.split(sep = ':')]
    print('sizes for GMM', list_of_gmm_components)

    technique = 'gmm'

    # creates samples by removing patient id, index, tts and label
    samples = train_data['x']
    num_samples = len(samples)
    print(f'working with {num_samples} for training')

    for gmm_components in list_of_gmm_components:
        y_true = train_data['y']
        gmm_filename = f'{args.models_dir}/{technique}-pca-{args.pcaComponents:04d}-gmm_components-{gmm_components:04d}-covar-{args.covarType}.pkl'
        if os.path.exists(gmm_filename):
            with open(gmm_filename, 'rb') as f:
                gmm_model = pickle.load(f)
                f.close()
            
            print(f'loaded GMM for {gmm_components}')
            gmm_estimation_time = 0
        else: # Build the model by creating a GMM per target class
            #########################################################################################################
            def train_gmm_per_label(label):
                X = samples[y_true == label].copy()
                num_samples = len(X)
                print(f'working with {num_samples} samples from target class {label}')
                mgc = min(gmm_components, 1 + num_samples // 20)
                gmm = estimate_gmm(args = args, X = X, n_components = mgc)
                return (label, gmm)
            #########################################################################################################
            print(f'running training procedure for creating one GMM per target class with {gmm_components} GMM components')
            starting_time = time.time()
            gmm_model = {label:gmm for label, gmm in [train_gmm_per_label(label) for label in args.labels]}
            gmm_estimation_time = time.time() - starting_time
            print(f'processing time lapse for {gmm_components} GMM components {gmm_estimation_time} seconds')

            # save KPIs to measure the quality of the clusterings
            kpis_filename = f'{args.log_dir}/{technique}-pca-{args.pcaComponents:04d}-covar-{args.covarType}-kpis.csv'
            print_header = not os.path.exists(kpis_filename)
            with open(kpis_filename, 'at') as f:
                if print_header:
                    print('pca;gmm_components;seconds;execution_environment;n_jobs', file = f)
                print(f'{args.pcaComponents};{gmm_components};{gmm_estimation_time};{args.exec_environment_id};{args.n_jobs}', file = f)
                f.close()
            #
            with open(gmm_filename, 'wb') as f:
                pickle.dump(gmm_model, f)
                f.close()
        # if

        target_class_a_priori_probabilities = numpy.array([sum(y_true == label) / len(y_true) for label in args.labels])

        data_subsets = {'train' : train_data, 'test' : test_data}

        for subset in ['train', 'test']:
            starting_time = time.time()
            data = data_subsets[subset]
            X = data['x']
            y_true = data['y']

            #########################################################################################################
            def compute_densities(X, gmm):
                return gmm.score_samples(X).reshape(-1 ,1)
            #@ray.remote
            #def ray_compute_densities(_dict_, gmm):
            #    return gmm.score_samples(X).reshape(-1 ,1)
            #########################################################################################################

            if args.n_jobs > 1:
                list_of_densities = [compute_densities(X, gmm_model[label]) for label in args.labels]
            else:
                list_of_densities = [compute_densities(X, gmm_model[label]) for label in args.labels]
            densities = numpy.hstack(list_of_densities) # shape must be ((len(data), len(args.labels))
            densities = numpy.exp(densities - densities.max(axis = 1).reshape(-1, 1)) # from logs to densities
            #print(densities.shape)
            #print(y_true[0], 'd', densities[0])
            #print(y_true[1], 'd', densities[1])
            densities *= target_class_a_priori_probabilities
            probs = densities / numpy.maximum(densities.sum(axis = 1), 1.0e-58).reshape(-1, 1) # from densities to probs by normalisation
            y_pred = probs.argmax(axis = 1)
            #print(probs.shape, y_pred.shape, numpy.unique(y_pred))
            #print(y_true[0], 'p', probs[0], 'd', densities[0])
            #print(y_true[1], 'p', probs[1], 'd', densities[1])
            #input() 
            del densities
            del probs
            
            inference_time = time.time() - starting_time

            if args.verbose > 0: print(subset, len(y_true), len(y_pred), inference_time, 'seconds')

            filename_prefix = f'{technique}-pca-{args.pcaComponents:04d}-gmm_components-{gmm_components:04d}-covar-{args.covarType}'
            save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
        # for subset
    # for gmm_components
# --------------------------------------------------------------------------------
