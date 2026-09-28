"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 2.1
    Date: April 2024

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for using K-Nearest Neighbours (KNN)
    to classify each sample into one of the target classes.
"""
import os
import sys
import time
import pickle
import math
import numpy

import joblib
import ray
from ray.util.joblib import register_ray

from sklearn.cluster import KMeans
#from sklearn.neighbors import KNeighborsClassifier
from NearestNeighbours import KDE_Classifier, KNN_Classifier

from utils_for_results import save_results


# ------------------------------------------------------------------------------------------------------------------------
def estimate_knn(args, X, y, codebook_size, K):

    if args.verbose > 1: print(type(X), X.shape, y.shape, 'codebook_size', codebook_size, 'K', K)

    with joblib.parallel_backend('ray'):

        knn = KNeighborsClassifier(n_neighbors = K, algorithm = 'auto', n_jobs = args.n_jobs)
        knn.fit(X, y)

        return knn
# ------------------------------------------------------------------------------------------------------------------------
def knn_for_digits(args, train_data, test_data):
    list_of_kmeans_codebook_sizes = [int(s) for s in args.codebookSize.split(sep = ':')]
    list_of_Ks = [int(s) for s in args.K.split(sep = ':')]

    technique = 'knn'
    #ray.init()
    #register_ray()

    print('list of kmeans codebook sizes', list_of_kmeans_codebook_sizes)
    print('list of K', list_of_Ks)
    #

    X = train_data['x']
    y = train_data['y']

    labels = numpy.unique(y)

    #######################################################################################################
    if 'x_refs' not in train_data:
        train_data['x_refs'] = [ray.put(chunk) for chunk in numpy.array_split(train_data['x'], args.n_jobs)]
    if 'x_refs' not in test_data:
        test_data['x_refs']  = [ray.put(chunk) for chunk in numpy.array_split( test_data['x'], args.n_jobs)]
    #######################################################################################################

    for codebook_size in list_of_kmeans_codebook_sizes:

        kmeans_time = 0
        if codebook_size > 0:
            kmeans_time = time.time()
            new_X = list()
            new_y = list()
            for label in labels:
                x_for_label = X[y == label]
                #kmeans = KMeans
                if len(x_for_label) > codebook_size:
                    #with joblib.parallel_backend('ray'):
                    kmeans_model = KMeans(n_clusters = codebook_size,
                                                init = 'k-means++',
                                                n_init = 5,
                                                tol = 1.0e-7,
                                                algorithm = 'lloyd')
                    kmeans_model.fit(x_for_label)
                    new_X.append(kmeans_model.cluster_centers_)
                    new_y.append(numpy.ones(len(kmeans_model.cluster_centers_), dtype = numpy.int32) * label)
                else:
                    new_X.append(x_for_label)
                    new_y.append(y[y == label])
            kmeans_time = time.time() - kmeans_time
            X_train = numpy.vstack(new_X)
            y_train = numpy.hstack(new_y)
        else:
            X_train = X
            y_train = y
                
        for K in list_of_Ks:
            model_filename = f'{args.models_dir}/{technique}-{codebook_size:04d}-{K:02d}.pkl'

            if os.path.exists(model_filename):
                with open(model_filename, 'rb') as f:
                    model = pickle.load(f)
                    f.close()
            else:
                training_time = time.time()
                #model = estimate_knn(args, X_train, y_train, codebook_size, K)
                model = KNN_Classifier(K = K, block_size = args.block_size)
                model.fit(X_train, y_train)
                training_time = time.time() - training_time + kmeans_time
                print(f'{technique} {codebook_size} {K} required {training_time:.3f} seconds (kmeans time was {kmeans_time:.3f} seconds)')
                    
                # save KPIs to measure the quality of the clusterings
                print_header = not os.path.exists(f'{args.log_dir}/{technique}-kpis.csv')
                with open(f'{args.log_dir}/{technique}-kpis.csv', 'at') as f:
                    if print_header:
                        print('pca;codebook_size;K;seconds;execution_environment;n_jobs', file = f)
                    print(f'{args.pcaComponents};{codebook_size};{K};{training_time};{args.exec_environment_id};{args.n_jobs}', file = f)
                    f.close()
                #
                ### DO NOT SAVE, TOO DISK SPACE & TOO MODELS & TRAINED FAST ENOUGH 
                ### with open(model_filename, 'wb') as f:
                ###     pickle.dump(model, f)
                ###     f.close()
            # if
        
            #
            data_subsets = {'train' : train_data, 'test' : test_data}
            _model_ref_ = ray.put(model)
            for subset in ['train', 'test']:
                #
                inference_time = time.time()
                data = data_subsets[subset]
                #with joblib.parallel_backend('ray'):
                #    y_pred = model.predict(data['x'])
                # ------------------------------------------------------------------------------------------------------
                @ray.remote
                def knn_predict(_x_, _model_, K: int):
                    return _model_.predict(X = _x_, K = K).flatten()
                # ------------------------------------------------------------------------------------------------------
                futures = [knn_predict.remote(_ref_, _model_ref_, K = K) for _ref_ in data_subsets[subset]['x_refs']]
                y_pred = numpy.hstack(ray.get(futures))
                y_true = data['y']
                inference_time = time.time() - inference_time

                saving_results_time = time.time()
                filename_prefix = f'{technique}-pca-{args.pcaComponents:04d}-cb_size-{codebook_size:04d}-K-{K:02d}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
                saving_results_time = time.time() - saving_results_time
                if args.verbose > 0:
                    print(f"subset {subset}, sizes {len(y_true)} vs {len(y_pred)}, inference_time = {inference_time:.3f} seconds and saving results lasted {saving_results_time:.3f} seconds")
            # for subset
        # for K 
    # for codebook_size 
# --------------------------------------------------------------------------------
