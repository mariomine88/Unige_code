"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 3.0
    Date: October 2025

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for using Random Forest (RF)
                        or Extremely Randomized Trees (ERT)
                        or Gradient Boosted Trees (GBT)
    to classify each sample into one of the target classes.
"""
import os
import sys
import time
import pickle
import math
import numpy

import xgboost
import ray
from ray import tune

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import confusion_matrix, classification_report, f1_score
from utils_for_eeg import distribute, do_prediction_considering_sequenciality
from utils_for_results import save_results

# ------------------------------------------------------------------------------------------------------------------------
def cpu_estimate_random_forest(args, X, y, n_estimators, max_depth):

    if args.verbose > 1: print(type(X), X.shape, y.shape, 'n_estimators', n_estimators, 'max_depth', max_depth)

    rf = RandomForestClassifier(
            n_estimators = n_estimators,
            max_depth = max_depth,
            criterion = 'gini',
            class_weight = "balanced",
            n_jobs = args.n_workers,
            verbose = args.verbose
    )
    rf.fit(X, y)

    return rf
# ------------------------------------------------------------------------------------------------------------------------
@ray.remote
def ray_estimate_random_forest(_dict_, n_estimators, max_depth):
    rf = RandomForestClassifier(
            n_estimators = n_estimators,
            max_depth = max_depth,
            criterion = 'gini',
            class_weight = "balanced",
            n_jobs = 1,
            verbose = 0,
    )
    rf.fit(ray.get(_dict_['X']), ray.get(_dict_['y']))
    return rf
# ------------------------------------------------------------------------------------------------------------------------
def cpu_estimate_extra_trees(args, X, y, n_estimators, max_depth):

    if args.verbose > 1: print(type(X), X.shape, y.shape, 'n_estimators', n_estimators, 'max_depth', max_depth)

    ert = ExtraTreesClassifier(
            n_estimators = n_estimators,
            max_depth = max_depth,
            criterion = 'gini',
            class_weight = "balanced",
            n_jobs = args.n_workers,
            verbose = args.verbose
    )
    ert.fit(X, y)

    return ert
# ------------------------------------------------------------------------------------------------------------------------
@ray.remote
def ray_estimate_extra_trees(_dict_, n_estimators, max_depth):
    ert = ExtraTreesClassifier(
            n_estimators = n_estimators,
            max_depth = max_depth,
            criterion = 'gini',
            class_weight = "balanced",
            n_jobs = 1,
            verbose = 0
    )
    ert.fit(ray.get(_dict_['X']), ray.get(_dict_['y']))
    return ert
# ------------------------------------------------------------------------------------------------------------------------
def train_one_gbc(config):
    # Retrieves the training and validation data from the RAY Object Store
    X_train = ray.get(config['X_train'])
    y_train = ray.get(config['y_train'])
    X_test = ray.get(config['X_test'])
    y_test = ray.get(config['y_test'])
    prediction_train = ray.get(config['prediction_train'])
    prediction_test = ray.get(config['prediction_test'])

    # Train the classifier
    starting_time = time.time()
    gbc = xgboost.XGBClassifier(
        objective = config['objective'],
        n_estimators = config['n_estimators'],
        max_depth = config['max_depth'],
        learning_rate = config['eta'],
        num_class = config['num_class'],
        booster = 'gbtree',
        tree_method = 'hist',
        n_jobs = 1
    )
    gbc.fit(X_train, y_train)
    training_time = time.time() - starting_time

    # Evalutes the classifer twice, with training and testing subsets
    starting_time = time.time()
    #y_pred = gbc.predict(X_train)
    y_true, y_pred = do_prediction_considering_sequenciality(
                labels = config['labels'],
                prediction = prediction_train,
                y_proba = gbc.predict_proba(X_train),
                DELTA = config['DELTA'],
    )
    train_confusion_matrix = confusion_matrix(y_train, y_pred)
    train_classification_report = classification_report(y_train, y_pred, digits = 3, zero_division = 1.0)
    train_f1_score_macro_avg = f1_score(y_train, y_pred, average = 'macro')
    train_inference_time = time.time() - starting_time

    starting_time = time.time()
    #y_pred = gbc.predict(X_test)
    y_true, y_pred = do_prediction_considering_sequenciality(
                labels = config['labels'],
                prediction = prediction_test,
                y_proba = gbc.predict_proba(X_test),
                DELTA = config['DELTA'],
    )
    test_confusion_matrix = confusion_matrix(y_test, y_pred)
    test_classification_report = classification_report(y_test, y_pred, digits = 3, zero_division = 1.0)
    test_f1_score_macro_avg = f1_score(y_test, y_pred, average = 'macro')
    test_inference_time = time.time() - starting_time

    # Return prediction f1 score macro average
    tune.report(
        {
                           'n_estimators': config['n_estimators'],
                              'max_depth': config['max_depth'],
                          'training_time': training_time,
                 'train_confusion_matrix': train_confusion_matrix,
            'train_classification_report': train_classification_report,
               'train_f1_score_macro_avg': train_f1_score_macro_avg,
                   'train_inference_time': train_inference_time,
                  'test_confusion_matrix': test_confusion_matrix,
             'test_classification_report': test_classification_report,
                'test_f1_score_macro_avg': test_f1_score_macro_avg,
                    'test_inference_time': test_inference_time,
                                   'done': True,
        }
    )
# -----------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
def rf_for_eeg(      args, train_data, num_samples_train, test_data, num_samples_test):
    ensemble_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test, technique = 'rf')

def ert_for_eeg(     args, train_data, num_samples_train, test_data, num_samples_test):
    ensemble_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test, technique = 'ert')

def gbt_for_eeg(     args, train_data, num_samples_train, test_data, num_samples_test):
    ensemble_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test, technique = 'gbt')

def ensemble_for_eeg(args, train_data, num_samples_train, test_data, num_samples_test, technique = None):
    list_of_n_estimators = [int(s) for s in args.numEstimators.split(sep = ':')]
    list_of_max_depth = [int(s) for s in args.maxDepth.split(sep = ':')]

    print('list of num of estimators', list_of_n_estimators, flush = True)
    print('list of max depths', list_of_max_depth, flush = True)

    use_ray_for_ensembles = len(train_data) != num_samples_train
    #
    PATIENT, INDEX, TTS, LABEL, PROBS = 0, 1, 2, 3, 4

    starting_time = time.time()
    if use_ray_for_ensembles:
        # ---------------------------------------------------------------------------------------------------
        @ray.remote
        def get_X(_dict_):
            return _dict_['X']
        # ---------------------------------------------------------------------------------------------------
        @ray.remote
        def get_y(_dict_):
            return numpy.array(_dict_['label'])
        # ---------------------------------------------------------------------------------------------------
        @ray.remote
        def get_metadata(_dict_):
            l = list()
            for i in range(len(_dict_['X'])):
                #                 PATIENT,              INDEX,              TTS,              LABEL,      PROBS = 0, 1, 2, 3, 4
                l.append([_dict_['patient'][i], _dict_['index'][i], _dict_['tts'][i], _dict_['label'][i], None])
            return l
        # --------------------------------------------------------------------------------
        # this could raise OOM problems
        futures = [get_X.remote(_ref_) for _ref_ in train_data]
        X_train = numpy.vstack(ray.get(futures))
        futures = [get_y.remote(_ref_) for _ref_ in train_data]
        y_train = numpy.hstack(ray.get(futures))
        futures = [get_X.remote(_ref_) for _ref_ in  test_data]
        X_test  = numpy.vstack(ray.get(futures))
        futures = [get_y.remote(_ref_) for _ref_ in  test_data]
        y_test  = numpy.hstack(ray.get(futures))
        futures = [get_metadata.remote(_ref_) for _ref_ in train_data]
        prediction_train = [t for l in ray.get(futures) for t in l]
        futures = [get_metadata.remote(_ref_) for _ref_ in  test_data]
        prediction_test  = [t for l in ray.get(futures) for t in l]
    else:
        X_train = numpy.array([x[4    ] for x in train_data])
        y_train = numpy.array([x[LABEL] for x in train_data])
        X_test  = numpy.array([x[4    ] for x in  test_data])
        y_test  = numpy.array([x[LABEL] for x in  test_data])
        prediction_train = [[t[PATIENT], t[INDEX], t[TTS], t[LABEL], None] for t in train_data]
        prediction_test  = [[t[PATIENT], t[INDEX], t[TTS], t[LABEL], None] for t in  test_data]

    local_data = {
        'train': {
            'X' : X_train,
            'y' : y_train,
            'prediction' : prediction_train,
        },
        'test': {
            'X' : X_test,
            'y' : y_test,
            'prediction' : prediction_test,
        },
    }
    remote_data = {
        'train' : train_data,
        'test' : test_data,
    }

    if use_ray_for_ensembles:
        _remote_ref_ = {
            'X' : ray.put(local_data['train']['X']),
            'y' : ray.put(local_data['train']['y']),
        }

    elapsed_time = time.time() - starting_time
    print(f"preparing the data to be used with Scikit-Learn classifiers that will be executed on the RAY backend required {elapsed_time} seconds", flush = True)

    if technique in ['rf', 'ert']:
        for n_estimators in list_of_n_estimators:
            for max_depth in list_of_max_depth:
                ensemble_filename = f'{args.models_dir}/{technique}-{args.patient}-{args.format}-{args.task}-{n_estimators:04d}-{max_depth:02d}.pkl'

                training_time = 0.0
                if os.path.exists(ensemble_filename):
                    with open(ensemble_filename, 'rb') as f:
                        model = pickle.load(f)
                        f.close()
                else:
                    training_time = time.time()
                    model = None
                    references_to_models = None
                    if use_ray_for_ensembles:
                        distributed_n_estimators = distribute(n_estimators, len(train_data))
                        if technique == 'rf':
                            futures = [ray_estimate_random_forest.remote(_remote_ref_, n, max_depth) for n in distributed_n_estimators]
                        elif technique == 'ert':
                            futures = [ray_estimate_extra_trees.remote(_remote_ref_, n, max_depth) for n in distributed_n_estimators]
                        references_to_models = futures 
                        models_in_local = ray.get(futures)
                        #print(len(references_to_models))
                        #for i in range(len(references_to_models)):
                        #    print(type(references_to_models[i]), type(models_in_local[i]))
                    else: 
                        X = local_data['train']['X']
                        y = local_data['train']['y']
                        if technique == 'rf':
                            model = cpu_estimate_random_forest(args, X, y, n_estimators, max_depth)
                        elif technique == 'ert':
                            model = cpu_estimate_extra_trees(args, X, y, n_estimators, max_depth)
                        else:
                            raise Exception(f'technique {technique} is unknown')
                        X = None
                        y = None
                    #
                    # At this point exclusively one variable will be not None: model or references_to_models
                    #
                    training_time = time.time() - training_time
                    print(f'{technique} {n_estimators} {max_depth} required {training_time} seconds on {args.exec_environment_description}', flush = True)

                    ### DO NOT SAVE: TOO DISK SPACE BECAUSE OF TOO MODELS WHEN TRAINING IS FAST ENOUGH 
                    ### with open(ensemble_filename, 'wb') as f:
                    ###     pickle.dump(model, f)
                    ###     f.close()
                    ### DO NOT SAVE: TOO DISK SPACE BECAUSE OF TOO MODELS WHEN TRAINING IS FAST ENOUGH 
                    
                # Save KPIs to measure the quality of the clusterings
                print_header = not os.path.exists(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv')
                log_file = open(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv', 'at')
                if print_header:
                    print('patient;format;task;n_estimators;max_depth;training_time;subset;inference_time;f1_score_macro_avg;exec_environment', file = log_file, flush = True)
                # if
                #
                DELTA = args.delta # as each sample comes every 2 seconds
                #
                for subset in ['train', 'test']:
                    inference_time = time.time()
                    if use_ray_for_ensembles:
                        # ----------------------------------------------------------------------------------------------------------
                        @ray.remote
                        def ray_predict_proba(_dict_, models_refs, block_size):
                            X = _dict_['X']
                            models_ = [ray.get(_mref_) for _mref_ in models_refs]
                            #y_proba = sum([m.predict_proba(X) for m in models_])
                            y_proba = numpy.vstack(
                                [
                                    sum([m.predict_proba(_x_) for m in models_])
                                        for _x_ in numpy.array_split(X, max(1, len(X) // block_size))
                                ]
                            )
                            return y_proba
                        # ----------------------------------------------------------------------------------------------------------
                        data = remote_data[subset]
                        futures = [ray_predict_proba.remote(_ref_, references_to_models, args.block_size) for _ref_ in data]
                        y_proba = numpy.vstack(ray.get(futures))
                        prediction = local_data[subset]['prediction']
                    else:
                        data = local_data[subset]
                        y_proba = model.predict_proba(data['X'])
                        prediction = data['prediction']
                    # end-if
                    print(f'prediction complete for {subset} lasting {time.time() - inference_time} seconds on {args.exec_environment_description}', flush = True)
                    #prediction.sort(key = lambda x: f'{x[PATIENT]}-{x[INDEX]:010d}')
                    #
                    y_true, y_pred = do_prediction_considering_sequenciality(labels = args.labels, prediction = prediction, y_proba = y_proba, DELTA = args.delta)

                    f1_score_macro_avg = f1_score(y_true, y_pred, average = 'macro')
                    inference_time = time.time() - inference_time
                    print(f'{args.patient};{args.format};{args.task};{n_estimators};{max_depth};{training_time:.3f};{subset};{inference_time:.3f};{f1_score_macro_avg:.3f};{args.exec_environment_id}', file = log_file, flush = True)

                    if args.verbose > 0: print(subset, len(y_true), len(y_pred), inference_time, 'seconds', flush = True)

                    filename_prefix = f'{technique}-{args.format}-{args.patient}-{args.task}-{n_estimators:04d}-{max_depth:02d}-{args.exec_environment_id}'
                    save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true, y_pred, elapsed_time = inference_time, labels = args.labels)
                # end-for subset
            # end-for max_depth 
        # end-for n_estimators 
        log_file.close()
    elif technique in ['gbt']:
        ########################################################################################################################################
        ### TASK PARALLELISATION USING RAY TUNE
        ########################################################################################################################################
        ### First, define the configuration to perform the grid search
        ########################################################################################################################################
        config = {
            "objective": "multi:softmax",
            #"eval_metric": ["mlogloss", "merror"],
            "n_estimators": tune.grid_search(sorted(list_of_n_estimators, reverse = True)),
            "max_depth": tune.grid_search(sorted(list_of_max_depth, reverse = True)),
            #"min_child_weight": tune.choice([1, 2, 3]),
            #"subsample": tune.uniform(0.5, 1.0),
            #"subsample": 1.0,
            #"eta": tune.loguniform(1e-4, 1e-1),
            "eta": 0.3,
            "num_class": len(args.labels),
            'X_train': ray.put(local_data['train']['X']),
            'y_train': ray.put(local_data['train']['y']),
            'prediction_train': ray.put(local_data['train']['prediction']),
            'X_test': ray.put(local_data['test']['X']),
            'y_test': ray.put(local_data['test']['y']),
            'prediction_test': ray.put(local_data['test']['prediction']),
            'DELTA': args.delta,
            'labels': args.labels,
        }
        ########################################################################################################################################
        ### Second, create the Tuner, not necessary the number of samples when using tune.grid_search, see the config above
        ########################################################################################################################################
        tuner = tune.Tuner(
            train_one_gbc,
            #tune_config=tune.TuneConfig(num_samples=len(list_of_n_estimators) * len(list_of_max_depth)),
            param_space=config,
        )
        ########################################################################################################################################
        ### Third, execute the fit() method of the tuner that will be in charge of distributing all tasks for completing the grid search
        ########################################################################################################################################
        starting_time = time.time()
        results = tuner.fit()
        global_time = time.time() - starting_time

        ########################################################################################################################################
        ### Fourth, get all the results corresponding to all the evaluated configurations via a Pandas DataFrame
        ########################################################################################################################################
        starting_time = time.time()
        df = results.get_dataframe()

        print_header = not os.path.exists(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv')
        log_file = open(f'{args.log_dir}/{technique}-{args.format}-{args.patient}-kpis.csv', 'at')
        if print_header:
            print('patient;format;task;n_estimators;max_depth;global_time;training_time;subset;inference_time;f1_score_macro_avg;execution_environment', file = log_file, flush = True)
        for subset in ['train', 'test']:
            for _row_ in df.iterrows():
                row = _row_[1]
                n_estimators = row['n_estimators']
                max_depth = row['max_depth']
                training_time = row[f'training_time']
                inference_time = row[f'{subset}_inference_time']
                f1_score_macro_avg = row[f'{subset}_f1_score_macro_avg']
                print(f'{args.patient};{args.format};{args.task};{n_estimators};{max_depth};{global_time:.3f};{training_time:.3f};{subset};{inference_time:.3f};{f1_score_macro_avg:.3f};{args.exec_environment_id}', file = log_file, flush = True)
                filename_prefix = f'{technique}-{args.format}-{args.patient}-{args.task}-n_estimators-{n_estimators:04d}-max_depth-{max_depth:02d}-{args.exec_environment_id}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true = None, y_pred = None, elapsed_time = inference_time, labels = args.labels,
                            _cm_ = numpy.array(row[f'{subset}_confusion_matrix']),
                            _cr_ = row[f'{subset}_classification_report'])
        # end-for
        log_file.close()
    # end-elif technique in ['gbt']
# --------------------------------------------------------------------------------
