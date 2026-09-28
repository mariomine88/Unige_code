import os
import sys
import numpy
from matplotlib import pyplot

from sklearn.metrics import pairwise_distances

filename = None
do_save_fig = False
results_dir = None
clustering_type = 'kmeans'
compute_distance_matrix = False

for i in range(len(sys.argv)):
    if sys.argv[i] == '--filename':
        filename = sys.argv[i + 1]
    elif sys.argv[i] == '--kmeans':
        clustering_type = 'kmeans'
    elif sys.argv[i] == '--results-dir':
        results_dir = sys.argv[i + 1]
        do_save_fig = True
    elif sys.argv[i] == '--save-figs':
        do_save_fig = True
    elif sys.argv[i] == '--distance-matrix':
        compute_distance_matrix = True

mat = numpy.genfromtxt(filename, delimiter = ';')

mat = mat / mat.sum(axis = 1).reshape(-1, 1)

height_inches = 8
if compute_distance_matrix:
    mat = pairwise_distances(mat)
    width_inches = height_inches
else:
    width_inches = min(max(height_inches, mat.shape[1] * 0.4), 30)

fig, axis = pyplot.subplots(nrows = 1, ncols = 1, figsize = (width_inches, height_inches))
#
if compute_distance_matrix:
    axis.matshow(mat, cmap = pyplot.cm.Greens, alpha = 1.0)
    axis.set_xlabel('Target classes')
    axis.set_ylabel('Target classes')
    axis.set_title('Distances between the patterns of the target classes')
    contents_type = 'distance-matrix'
else:
    axis.matshow(mat, cmap = pyplot.cm.Blues, alpha = 1.0)
    axis.set_xlabel('Clusters')
    axis.set_ylabel('Target classes')
    axis.set_title('Conditional probabilities')
    contents_type = 'conditional-probabilities'
pyplot.tight_layout()

figure_filename = os.path.basename(filename).replace('.csv', '').replace('cluster-distribution', contents_type)

if do_save_fig and results_dir is not None:
    #pyplot.savefig(f'{results_dir}/conditional-probabilities-{clustering_type}-{mat.shape[0]:02d}-{mat.shape[1]:04d}.svg', format = 'svg')
    pyplot.savefig(f'{results_dir}/{figure_filename}.png', format = 'png')
else:
    pyplot.show()
