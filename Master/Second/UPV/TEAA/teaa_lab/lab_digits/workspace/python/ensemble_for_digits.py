"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 3.0
    Date: October 2024

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

try:
    import joblib
    from joblib import Parallel, delayed
    from ray.util.joblib import register_ray
except:
    raise Exception("joblib and ray are required")

import xgboost
import ray
from ray import tune

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import confusion_matrix, classification_report, f1_score
from utils_for_results import save_results

# ------------------------------------------------------------------------------------------------------------------------
def estimate_random_forest(args, X, y, n_estimators, max_depth):

    if args.verbose > 1: print(type(X), X.shape, y.shape, 'n_estimators', n_estimators, 'max_depth', max_depth)

    register_ray()

    with joblib.parallel_backend('ray'):
        rf = RandomForestClassifier(
                n_estimators = n_estimators,
                max_depth = max_depth,
                criterion = 'gini',
                class_weight = "balanced",
                n_jobs = args.n_jobs,
                verbose = args.verbose
        )
        rf.fit(X, y)

    return rf
# ------------------------------------------------------------------------------------------------------------------------
def estimate_extra_trees(args, X, y, n_estimators, max_depth):

    if args.verbose > 1: print(type(X), X.shape, y.shape, 'n_estimators', n_estimators, 'max_depth', max_depth)

    register_ray()

    with joblib.parallel_backend('ray'):
        ert = ExtraTreesClassifier(
                n_estimators = n_estimators,
                max_depth = max_depth,
                criterion = 'gini',
                class_weight = "balanced",
                n_jobs = args.n_jobs,
                verbose = args.verbose
        )
        ert.fit(X, y)

        return ert
# ------------------------------------------------------------------------------------------------------------------------
def train_one_gbc(config):
    # Retrieves the training and validation data from the RAY Object Store
    X_train = ray.get(config['X_train'])
    y_train = ray.get(config['y_train'])
    X_test = ray.get(config['X_test'])
    y_test = ray.get(config['y_test'])

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

    # Evalutes the classifier twice, with training and testing subsets
    starting_time = time.time()
    y_pred = gbc.predict(X_train)
    train_confusion_matrix = confusion_matrix(y_train, y_pred)
    train_classification_report = classification_report(y_train, y_pred, digits = 3, zero_division = 1.0)
    train_f1_score_macro_avg = f1_score(y_train, y_pred, average = 'macro')
    train_inference_time = time.time() - starting_time

    starting_time = time.time()
    y_pred = gbc.predict(X_test)
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
def rf_for_digits(args, train_data, test_data):
    ensemble_for_digits(args, train_data, test_data, technique = 'rf')

def ert_for_digits(args, train_data, test_data):
    ensemble_for_digits(args, train_data, test_data, technique = 'ert')

def gbt_for_digits(args, train_data, test_data):
    ensemble_for_digits(args, train_data, test_data, technique = 'gbt')

def ensemble_for_digits(args, train_data, test_data, technique = None):
    list_of_n_estimators = [int(s) for s in args.numEstimators.split(sep = ':')]
    list_of_max_depth = [int(s) for s in args.maxDepth.split(sep = ':')]

    print('list of num of estimators', list_of_n_estimators, flush = True)
    print('list of max depths', list_of_max_depth, flush = True)

    X = train_data['x']
    y = train_data['y']

    if technique in ['rf', 'ert']:
        for n_estimators in list_of_n_estimators:
            for max_depth in list_of_max_depth:
                ensemble_filename = f'{args.models_dir}/{technique}-pca-{args.pcaComponents:04d}-n_estimators-{n_estimators:04d}-max_depth-{max_depth:02d}.pkl'

                training_time = 0.0
                if os.path.exists(ensemble_filename):
                    with open(ensemble_filename, 'rb') as f:
                        model = pickle.load(f)
                        f.close()
                else:
                    training_time = time.time()
                    if technique == 'rf':
                        model = estimate_random_forest(args, X, y, n_estimators, max_depth)
                    elif technique == 'ert':
                        model = estimate_extra_trees(args, X, y, n_estimators, max_depth)
                    #elif technique == 'gbt':
                    #    model = estimate_gradient_boosted_trees(args, X, y, n_estimators, max_depth)
                    else:
                        raise Exception(f'technique {technique} is unknown')
                    training_time = time.time() - training_time
                    print(f'{technique} {n_estimators} {max_depth} {args.exec_environment_id} {args.n_jobs} required {training_time} seconds', flush = True)

                    ### DO NOT SAVE: TOO DISK SPACE BECAUSE OF TOO MODELS WHEN TRAINING IS FAST ENOUGH 
                    ### with open(ensemble_filename, 'wb') as f:
                    ###     pickle.dump(model, f)
                    ###     f.close()
                    ### DO NOT SAVE: TOO DISK SPACE BECAUSE OF TOO MODELS WHEN TRAINING IS FAST ENOUGH 
                    
                # Save KPIs to measure the quality of the clusterings
                print_header = not os.path.exists(f'{args.log_dir}/{technique}-kpis.csv')
                log_file = open(f'{args.log_dir}/{technique}-kpis.csv', 'at')
                if print_header:
                    print('pca;n_estimators;max_depth;training_time;subset;inference_time;f1_score_macro_avg;execution_environment;n_jobs', file = log_file)
                # if
                #
                data_subsets = {'train' : train_data, 'test' : test_data}
                #
                for subset in ['train', 'test']:
                    #
                    inference_time = time.time()
                    data = data_subsets[subset]
                    with joblib.parallel_backend('ray'):
                        y_pred = model.predict(data['x'])
                    y_true = data['y']
                    f1_score_macro_avg = f1_score(y_true, y_pred, average = 'macro')
                    inference_time = time.time() - inference_time
                    print(f'{args.pcaComponents};{n_estimators};{max_depth};{training_time:.3f};{subset};{inference_time:.3f};{f1_score_macro_avg:.3f};{args.exec_environment_id};{args.n_jobs}', file = log_file)

                    if args.verbose > 0: print(subset, len(y_true), len(y_pred), inference_time, 'seconds', flush = True)

                    filename_prefix = f'{technique}-pca-{args.pcaComponents:04d}-n_estimators-{n_estimators:04d}-max_depth-{max_depth:02d}'
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
            "n_estimators": tune.grid_search(list_of_n_estimators),
            "max_depth": tune.grid_search(list_of_max_depth),
            #"min_child_weight": tune.choice([1, 2, 3]),
            #"subsample": tune.uniform(0.5, 1.0),
            #"subsample": 1.0,
            #"eta": tune.loguniform(1e-4, 1e-1),
            "eta": 0.3,
            "num_class": 10,
            'X_train': ray.put(train_data['x']),
            'y_train': ray.put(train_data['y']),
            'X_test': ray.put(test_data['x']),
            'y_test': ray.put(test_data['y']),
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

        print_header = not os.path.exists(f'{args.log_dir}/{technique}-kpis.csv')
        log_file = open(f'{args.log_dir}/{technique}-kpis.csv', 'at')
        if print_header:
            print('pca;n_estimators;max_depth;global_time;training_time;subset;inference_time;f1_score_macro_avg;execution_environment;n_jobs', file = log_file)
        for subset in ['train', 'test']:
            for _row_ in df.iterrows():
                row = _row_[1]
                n_estimators = row['n_estimators']
                max_depth = row['max_depth']
                training_time = row[f'training_time']
                inference_time = row[f'{subset}_inference_time']
                f1_score_macro_avg = row[f'{subset}_f1_score_macro_avg']
                print(f'{args.pcaComponents};{n_estimators};{max_depth};{global_time:.3f};{training_time:.3f};{subset};{inference_time:.3f};{f1_score_macro_avg:.3f};{args.exec_environment_id};{args.n_jobs}', file = log_file)
                filename_prefix = f'{technique}-pca-{args.pcaComponents:04d}-n_estimators-{n_estimators:04d}-max_depth-{max_depth:02d}'
                save_results(f'{args.results_dir}/{subset}', filename_prefix, y_true = None, y_pred = None, elapsed_time = inference_time, labels = args.labels,
                            _cm_ = numpy.array(row[f'{subset}_confusion_matrix']),
                            _cr_ = row[f'{subset}_classification_report'])
        # end-for
        log_file.close()
    # end-elif technique in ['gbt']
# --------------------------------------------------------------------------------
