"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 2.0
    Date: February 2024

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
import heapq

try:
    import joblib
    from joblib import Parallel, delayed
    joblib_is_available = True
except:
    joblib_is_available = False

from sklearn.metrics.pairwise import euclidean_distances
import dask
import dask.bag as db

from eeg_load_data import from_bag_to_samples
from lbg import lbg, load_codebook, lbg_local_cpu

from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from BallTree import BallTree
from utils_for_results import save_results


# --------------------------------------------------------------------------------
def filter_by_target_class(_data_blocks_, target_class):
    filtered_data_blocks = []
    for _data_block_ in _data_blocks_:
        y = _data_block_['y']
        x = _data_block_['X'][y == target_class].copy()
        y = _data_block_['y'][y == target_class].copy()
        if len(x) > 0:
            filtered_data_blocks.append({'X': x, 'y': y})
    return filtered_data_blocks
# ------------------------------------------------------------------------------------------------------------------------
def count_map(_data_blocks_):
    return [sum([len(_data_block_['X']) for _data_block_ in _data_blocks_])]
# ------------------------------------------------------------------------------------------------------------------------
def _knn_train_ball_tree_map(_data_blocks_):
    # only works with one data block per partition
    if len(_data_blocks_) == 1:
        X = _data_blocks_[0]['X']
        y = _data_blocks_[0]['y']
    else:
        X = numpy.vstack([d['X'] for d in _data_blocks_])
        y = numpy.hstack([d['y'] for d in _data_blocks_])

    bt = BallTree(min_samples_to_split = 100).fit(X, y)
    return [bt]
# ------------------------------------------------------------------------------------------------------------------------
def _knn_predict_proba_ball_tree_map(_list_of_bts_, samples, K):
    bt = _list_of_bts_[0] # only one BallTree was generated per partition
    l = list()
    for x in samples:
        _knn_to_x_ = bt.get_knn_dist_and_labels(x, K)
        _knn_to_x_.sort()
        l.append(_knn_to_x_)
    return [l]
# ------------------------------------------------------------------------------------------------------------------------
def _knn_predict_proba_ball_tree_fold(a, b):
    new_l = list()
    assert len(a) == len(b)
    for i in range(len(a)):
        _k_ = max(len(a[i]), len(b[i]))
        c = a[i] + b[i]
        c.sort()
        new_l.append(c[:_k_])
    # returns a list of lists, being each one the concatenation of the previous lists per sample
    return new_l
# ------------------------------------------------------------------------------------------------------------------------
def natural_merge(a, b, K):
    c = []
    i = 0
    j = 0
    while len(c) < K and i < len(a) and j < len(b):
        if a[i][0] <= b[j][0]:
            c.append(a[i])
            i += 1
        else:
            c.append(b[j])
            j += 1
    while len(c) < K and i < len(a):
        c.append(a[i])
        i += 1
    while len(c) < K and j < len(b):
        c.append(b[i])
        j += 1

    return c
# ------------------------------------------------------------------------------------------------------------------------
def _knn_predict_proba_map(_data_blocks_, samples, K):
    assert type(samples) is numpy.ndarray
    l = [[]] * len(samples)
    for _data_block_ in _data_blocks_:
        distances = euclidean_distances(samples, _data_block_['X'], squared = True)
        indices = numpy.argsort(distances)
        assert len(distances) == len(samples)
        y_true = _data_block_['y'].tolist()
        for i in range(len(samples)):
            dist = distances[i].tolist()
            indx = indices[i][:K].tolist()
            a = [(dist[j], y_true[j]) for j in indx]
            #
            if len(l[i]) == 0:
                l[i] = a
            else:
                b = l[i]
                c = []
                while len(c) < K:
                    if len(b) > 0 and b[0][0] <= a[0][0]: # we know len(a) is always greater than len(b)
                        c.append(b[0])
                        b.pop(0)
                    else:
                        c.append(a[0])
                        a.pop(0)
                del a
                del b
                l[i] = c # natural_merge(l[i], a, K) coding here is faster
                #l[i] = natural_merge(l[i], a, K)
    return [l]
# ------------------------------------------------------------------------------------------------------------------------
def _knn_predict_proba_fold(a, b):
    new_l = list()
    assert len(a) == len(b)
    #assert len(a[0]) == len(b[0])
    for i in range(len(a)):
        _k_ = max(len(a[i]), len(b[i]))
        #c = a[i] + b[i]
        #c.sort()
        #new_l.append(c[:_k_])
        new_l.append(natural_merge(a[i], b[i], _k_))
    # returns a list of lists, being each one the concatenation of the previous lists per sample
    return new_l
# ------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------
def estimate_knn(args, X, y, codebook_size, K):

    if args.verbose > 1:
        print(type(X), X.shape, y.shape, 'codebook_size', codebook_size, 'K', K, flush = True)

    #leaf_size = min(10000, len(X) // 10)
    #algorithm = 'ball_tree' if len(X) > 10**5 else 'auto'
    algorithm = 'auto'

    knn = KNeighborsClassifier(n_neighbors = K, algorithm = algorithm, n_jobs = args.n_jobs)
    knn.fit(X, y)

    return knn
# ------------------------------------------------------------------------------------------------------------------------
def knn_for_eeg(args, train_data, test_data):
    #assert type(train_data) is db.Bag
    #assert type( test_data) is db.Bag
    #
    list_of_kmeans_codebook_sizes = [int(s) for s in args.codebookSize.split(sep = ':')]
    list_of_Ks = [int(s) for s in args.K.split(sep = ':')]

    technique = 'knn'

    print('list of kmeans codebook sizes', list_of_kmeans_codebook_sizes)
    print('list of K', list_of_Ks, flush = True)

    if type(train_data) is db.Bag:
        starting_time = time.time()
        BS = args.block_size
        train_samples_bag, train_X = from_bag_to_samples(train_data, block_size = BS, generate_local_samples = True)
        test_samples_bag,   test_X = from_bag_to_samples( test_data, block_size = BS, generate_local_samples = True)
        elapsed_time = time.time() - starting_time
        print(f"preparing the data to be used with Scikit-Learn classifiers that will be executed on the Dask backend required {elapsed_time} seconds", flush = True)
    else:
        train_X = numpy.array([s[4] for s in train_data])
        train_y = numpy.array([s[3] for s in train_data])
        test_X  = numpy.array([s[4] for s in test_data])
        test_y  = numpy.array([s[3] for s in test_data])
    #

    PATIENT, INDEX, TTS, LABEL, PROBS = 0, 1, 2, 3, 4

    #########################################################################################################
    def compute_codebook_per_target_class(label, cb_size):
        kmeans_models_dir = f"{args.models_dir}/{args.patient}/{args.format}/target_class_{label}"
        os.makedirs(kmeans_models_dir, exist_ok = True)
        if type(train_data) is db.Bag:
            X = train_samples_bag.map_partitions(filter_by_target_class, label).persist()
            n = X.map_partitions(count_map).fold(lambda a, b: a + b).compute()
            while cb_size * 10 > n:
                cb_size = cb_size // 2
            print(f"label = {label} n = {n} out of {train_X.shape[0]}    cb_size = {cb_size}", flush = True)
            WSSE, codebook = lbg(X, tolerance = 1.0e-4, 
                                    codebook = numpy.random.randn(1, train_X.shape[1]),
                                    max_n_clusters = cb_size,
                                    max_iter = 300,
                                    models_dir = kmeans_models_dir,
                                    verbose = 2)
            del X
        else:
            X = train_X[train_y == label]
            n = len(X)
            while cb_size * 10 > n:
                cb_size = cb_size // 2
            print(f"label = {label} n = {n} out of {train_X.shape[0]}    cb_size = {cb_size}", flush = True)
            WSSE, codebook = lbg_local_cpu(X, tolerance = 1.0e-4, 
                                    codebook = numpy.random.randn(1, train_X.shape[1]),
                                    max_n_clusters = cb_size,
                                    max_iter = 300,
                                    models_dir = kmeans_models_dir,
                                    verbose = 1)
    #########################################################################################################
    def load_codebook_per_target_class(label, train_X_per_class, cb_size, min_cb_size = 64):
        kmeans_models_dir = f"{args.models_dir}/{args.patient}/{args.format}/target_class_{label}"
        size = 0
        for root, dirs, filenames in os.walk(kmeans_models_dir):
            filenames.sort()
            filenames = [fn for fn in filenames if fn.endswith('.npy')]
            filename = filenames[0]
            for fn in filenames:
                _size_ = int(fn[len('codebook_'):-4])
                if _size_ <= cb_size:
                    size = _size_
            #
        #
        assert filename is not None
        #
        codebook, WSSSE = load_codebook(kmeans_models_dir, size)
        #
        new_X = codebook if len(codebook) >= min_cb_size else train_X_per_class
        new_y = numpy.ones(len(new_X)) * label
        #
        return (new_X, new_y)
    #########################################################################################################
    log_max_cb_size = int(math.ceil(math.log(max(list_of_kmeans_codebook_sizes)) / math.log(2)))
    list_of_kmeans_codebook_sizes += numpy.logspace(6, log_max_cb_size, log_max_cb_size - 6 + 1, base = 2).astype(int).tolist()
    list_of_kmeans_codebook_sizes = numpy.unique(list_of_kmeans_codebook_sizes).tolist()
    print('definitive list of kmeans codebook sizes', list_of_kmeans_codebook_sizes)
    max_cb_size = 2 ** log_max_cb_size
    starting_time = time.time()
    for label in args.labels:
        print('computing codebook for target class', label, flush = True)
        compute_codebook_per_target_class(label, max_cb_size)
    kmeans_time = time.time() - starting_time
    print(f"computing the codebooks for all target classes required {kmeans_time} seconds", flush = True)
    #########################################################################################################

    if type(train_data) is db.Bag: # equivalent to test if args.exec_environment_id != 'local_cpu'
        if args.use_ball_trees:
            starting_time = time.time()
            model_bag = train_samples_bag.map_partitions(_knn_train_ball_tree_map).persist()
            training_time = time.time() - starting_time
            print(f'{technique} training using Ball Trees with no reduction with KMeans required {training_time} seconds', flush = True)
        #
        K = max(list_of_Ks)
        #
        if min(list_of_kmeans_codebook_sizes) == 0:
            starting_time = time.time()
            list_of_knn_for_training_subset = list()
            print('computing probs for training subset', end = '\n', flush = True)
            for i in range(0, len(train_X), args.block_size):
                x = train_X[i : i + args.block_size]
                if args.use_ball_trees:
                    l = model_bag.map_partitions(_knn_predict_proba_ball_tree_map, x, K).fold(_knn_predict_proba_ball_tree_fold).compute()
                else:
                    l = train_samples_bag.map_partitions(_knn_predict_proba_map, x, K).fold(_knn_predict_proba_fold).compute()
                list_of_knn_for_training_subset += l
                #print('.', end = '', flush = True)
                estimated_time = len(train_X) * (time.time() - starting_time) / (60 * (i + args.block_size))
                print(f'{time.time() - starting_time:20.3f}   {i:9d} out of {len(train_X)}   estimated time {estimated_time:.3f} minutess   ', end = '\r', flush = True)
            computing_proba_time_for_training_subset = time.time() - starting_time
            print(f'\ncomputing probs for training subset required {computing_proba_time_for_training_subset} seconds', flush = True)
            #
            starting_time = time.time()
            list_of_knn_for_testing_subset = list()
            print('computing probs for testing subset', end = '\n', flush = True)
            for i in range(0, len(test_X), args.block_size):
                x = test_X[i : i + args.block_size]
                if args.use_ball_trees:
                    l = model_bag.map_partitions(_knn_predict_proba_ball_tree_map, x, K).fold(_knn_predict_proba_ball_tree_fold).compute()
                else:
                    l = train_samples_bag.map_partitions(_knn_predict_proba_map, x, K).fold(_knn_predict_proba_fold).compute()
                list_of_knn_for_testing_subset += l
                #print('.', end = '', flush = True)
                estimated_time = len(test_X) * (time.time() - starting_time) / (60 * (i + args.block_size))
                print(f'{time.time() - starting_time:20.3f}   {i:9d} out of {len(test_X)}   estimated time {estimated_time:.3f} minutess   ', end = '\r', flush = True)
            computing_proba_time_for_testing_subset = time.time() - starting_time
            print(f'\ncomputing probs for testing subset required {computing_proba_time_for_testing_subset} seconds', flush = True)
        starting_time = time.time()
        prediction_train = train_data.map(lambda t: [t[0], t[1], t[2], t[3], None]).compute()
        prediction_test  =  test_data.map(lambda t: [t[0], t[1], t[2], t[3], None]).compute()
        elapsed_time = time.time() - starting_time
        print(f"preparing the data to be used with Scikit-Learn classifiers that will be executed on the Dask backend required {elapsed_time} seconds", flush = True)
        computing_times = {'train': computing_proba_time_for_training_subset, 'test': computing_proba_time_for_testing_subset}
    else:
        starting_time = time.time()
        prediction_train = [[t[0], t[1], t[2], t[3], None] for t in train_data]
        prediction_test  = [[t[0], t[1], t[2], t[3], None] for t in  test_data]
        elapsed_time = time.time() - starting_time
        print(f"preparing the data to be used with Scikit-Learn classifiers that will be executed on the local cpu required {elapsed_time} seconds", flush = True)
        computing_times = {'train': 0.0, 'test': 0.0}

    for codebook_size in list_of_kmeans_codebook_sizes:
        skip_this_codebook_size = False
        if codebook_size > 0:
            y = numpy.array([t[3] for t in prediction_train])
            xy = [load_codebook_per_target_class(label, train_X_per_class = train_X[y == label],
                                                        cb_size = codebook_size,
                                                        min_cb_size = 64) for label in args.labels]
            X_train = numpy.vstack([x for x, y in xy])
            y_train = numpy.hstack([y for x, y in xy])
            if max([len(y) for x, y in xy]) < codebook_size:
                skip_this_codebook_size = True
            del xy
        elif args.exec_environment_id == 'local_cpu':
            X_train = train_X
            y_train = train_y
        else:
            X_train = None
            y_train = None
        
        if skip_this_codebook_size: continue
                
        for K in list_of_Ks:
            if X_train is not None:
                starting_time = time.time()
                model = estimate_knn(args, X_train, y_train, codebook_size, K)
                training_time = time.time() - starting_time + kmeans_time
                print(f'{technique} {codebook_size} {K} required {training_time} seconds', flush = True)
            else:
                model = None
                training_time = 0
                    
            # save KPIs to measure the quality of the clusterings
            if training_time > 0:
                print_header = not os.path.exists(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv')
                with open(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv', 'at') as f:
                    if print_header:
                        print('codebook_size;K;seconds;execution_environment', file = f)
                    print(f'{codebook_size};{K};{training_time};{args.exec_environment_id}', file = f)
                    f.close()
                #
            #
            DELTA = args.delta # as each sample comes every 2 seconds
            #
            data_subsets = {'train' : train_data, 'test' : test_data}
            #
            for subset in ['train', 'test']:
                #
                inference_time = time.time()
                data = data_subsets[subset]
                if model is not None:
                    if type(data) is db.Bag:
                        if subset == 'test':
                            prediction = prediction_test
                            data_X = test_X
                        else:
                            prediction = prediction_train
                            data_X = train_X
                    else:
                        if subset == 'test':
                            data_X = test_X
                        else:
                            data_X = train_X
                        prediction = list()
                        for i in range(len(data)):
                            patient, index, tts, label, x = data[i]
                            prediction.append([patient, index, tts, label, None])
                    #########################################################################################################
                    def _predict_proba(i):
                        return model.predict_proba(data_X[i: i + args.block_size])
                    #########################################################################################################
                    if joblib_is_available: # and args.n_jobs > 1:
                        if False and type(data) is db.Bag: # DISABLED BECAUSE TAKES LONGER TO COMPLETE THE TASK
                            with joblib.parallel_config(backend = "dask"):
                                parallel = Parallel(n_jobs = 14)
                                probs = parallel(delayed(_predict_proba)(i) for i in range(0, len(data_X), args.block_size))
                        else:
                            #parallel = Parallel(n_jobs = args.n_jobs, prefer = "threads")
                            parallel = Parallel(n_jobs = 14, prefer = "threads")
                            probs = parallel(delayed(_predict_proba)(i) for i in range(0, len(data_X), args.block_size))
                    else:
                        probs = [_predict_proba(i) for i in range(0, len(data_X), args.block_size)]
                    #########################################################################################################
                    probs = numpy.vstack(probs)
                else:
                    if subset == 'test':
                        list_of_knn = list_of_knn_for_testing_subset
                        prediction = prediction_test
                    else:
                        list_of_knn = list_of_knn_for_training_subset
                        prediction = prediction_train

                    probs = list()
                    for l in list_of_knn:
                        p = numpy.zeros(len(args.labels))
                        for d, i in l[:K]: p[i] += 1
                        #p = numpy.bincount(l[:K], minlength = len(args.labels))
                        probs.append(p / p.sum())
                    probs = numpy.vstack(probs)

                for i in range(len(prediction)):
                    prediction[i][4] = probs[i]
                            
                print(f'prediction complete for {subset} with cb_size {codebook_size} and K {K} lasting {time.time() - inference_time} seconds', flush = True)
                #prediction.sort(key = lambda x: f'{x[PATIENT]}-{x[INDEX]:010d}')
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
                inference_time = time.time() - inference_time
                if codebook_size == 0:
                    inference_time += computing_times[subset]

                if args.verbose > 0: print(subset, len(y_true), len(y_pred), inference_time, 'seconds', flush = True)

                filename_prefix = f'{technique}-{args.format}-{args.patient}-{args.task}-{codebook_size:04d}-{K:02d}-{args.exec_environment_id}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
            # for subset
        # for K 
    # for codebook_size 
# --------------------------------------------------------------------------------
