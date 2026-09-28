import numpy
import dask.dataframe as dd

# --------------------------------------------------------------------------------------------------------------
def gather_samples(l, block_size = None, n_features = 20):
    x_columns = [f'x{i + 1:02d}' for i in range(n_features)]
    y_columns = ['y'] #[f'y{i + 1:02d}' for i in range(n_features)]
    #
    r = []
    x = []
    y = []
    for e in l:
        x.append(numpy.array([float(e[k]) for k in x_columns]))
        y.append(numpy.array([float(e[k]) for k in y_columns]))
        if block_size is not None and len(x) == block_size:
            r.append({'X': numpy.array(x), 'y': numpy.array(y)})
            x = []
            y = []
        #
    #
    if len(x) > 0:
        r.append({'X': numpy.array(x), 'y': numpy.array(y)})
    return r
# --------------------------------------------------------------------------------------------------------------
def filter_by_target_class(data, target_class = None):
    assert target_class is not None
    r = []
    for _data_block_ in data:
        x = _data_block_['X']
        y = _data_block_['y'].flatten()
        x = x[y == target_class, :]
        y = y[y == target_class]
        if len(x) > 0:
            r.append({'X': x, 'y': y})
    return r
# --------------------------------------------------------------------------------------------------------------
def load_dask_dataframe(path = None):
    # executed with client.submit() to ensure the pods' local filesystems are accessed, where the nfs directory is visible
    if path is None:
        path = '/data/synthetic_data/parquet.train'
    return dd.read_parquet(path)
# --------------------------------------------------------------------------------------------------------------
def load_data_delayed(path = None, n_features = 20):
    # executed with client.submit() to ensure the pods' local filesystems are accessed, where the nfs directory is visible
    if path is None:
        path = '/data/synthetic_data/parquet.train'
    df = dd.read_parquet(path)
    data = df[[f'x{i + 1:02d}' for i in range(n_features)] + ['y']].to_dask_array(lengths = True)
    X = data[:, 0:n_features]
    y = data[:, n_features].astype(int)
    return X, y
# --------------------------------------------------------------------------------------------------------------
