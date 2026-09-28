import os
import sys
import numpy
import pickle
from sklearn.datasets import fetch_openml

def load_mnist():
    #
    hostname = os.uname()[1]
    home = os.getenv('HOME')
    #
    if hostname in ['tensor', 'tensor.dsic.upv.es', 'tensor.upvnet.upv.es']:
        filename = '/opt/asig/teaa-cd/data/ml_data/mnist_784.npz'
    elif home is not None:
        dirname = os.path.join(home, "ml_data")
        os.makedirs(dirname, exist_ok = True)
        filename = os.path.join(dirname, 'mnist_784.npz')
    else:
        filename = '/data/digits/mnist_784.npz' # This will fail in Windows machines
    #
    if os.path.exists(filename):
        npz = numpy.load(filename, allow_pickle = True)
        X, y = npz['X'], npz['y']
    else:
        # This fails from the master of the Spark cluster because it is not allowed to access internet
        X, y = fetch_openml('mnist_784', version = 'active', return_X_y = True, parser = 'auto')
        numpy.savez(filename, X = X, y = y)
    #
    y = numpy.array([int(_) for _ in y])
    return X, y
