import os
import sys
import time
import numpy
import pandas

import dask.dataframe as dd

from sklearn.datasets import make_classification
#from sklearn.model_selection import train_test_split

if __name__ == '__main__':

    n_samples_train      = 10 ** 8
    n_samples_test       = 10 ** 6
    n_samples            = n_samples_train + n_samples_test
    n_features           = 20
    n_classes            = 2
    n_clusters_per_class = 8
    n_informative        = 4
    random_state         = 1

    t0 = time.time()
    X, y = make_classification(n_samples = n_samples,
                               n_features = n_features,
                               n_informative = n_informative,
                               n_classes = n_classes,
                               n_clusters_per_class = n_clusters_per_class,
                               random_state = random_state)
    print(f"generating {n_samples} data samples required {time.time() - t0} seconds", flush = True)

    data = dict()
    data['train'] = dict()
    data['train']['X'] = X[:n_samples_train ]
    data['train']['y'] = y[:n_samples_train ]
    data['test'] = dict()
    data['test']['X']  = X[ n_samples_train:]
    data['test']['y']  = y[ n_samples_train:]

    for subset in ('train', 'test'):

        parquet_dir = f"/bigdata/disk/teaa/synthetic_data/parquet.2.{subset}"

        X = data[subset]['X']
        y = data[subset]['y']

        print(f"target classes distribution for {subset} subset is {numpy.bincount(y)}")

        if not os.path.exists(parquet_dir):

            t0 = time.time()
            column_def = {f'x{i + 1:02d}': X[:,i] for i in range(X.shape[1])}
            column_def['y'] = y
            df = pandas.DataFrame(column_def)
            print(f"creating the pandas dataframe for {subset} subset required {time.time() - t0} seconds", flush = True)

            t0 = time.time()
            df = dd.from_pandas(df, npartitions = 70)
            print(f"converting the dask dataframe for {subset} subset from the pandas dataframe required {time.time() - t0} seconds", flush = True)

            t0 = time.time()
            os.makedirs(parquet_dir, exist_ok = True)
            df.to_parquet(parquet_dir)
            print(f"saving {subset} data to parquet required {time.time() - t0} seconds")
