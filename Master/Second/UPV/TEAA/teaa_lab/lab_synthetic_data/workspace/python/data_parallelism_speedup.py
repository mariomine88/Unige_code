import os
import sys
import re
import subprocess
import pandas
import json
import pprint

from matplotlib import pyplot

save_figures_on_file = True # True

re_filter = re.compile('kmeans_.+-local-[0-9]+-workers-.+\\.out$')
out_files = list()

run_ls = subprocess.Popen(["ls", "results"], stdout = subprocess.PIPE)

for filename in run_ls.stdout:
    filename = filename.decode().strip()
    if re_filter.match(filename):
        out_files.append('results/' + filename)

run_ls.stdout.close()
        
#for fn in out_files: print(fn)

#results/kmeans_based_classifier-local-14-workers-bs-1000.out
#results/kmeans_based_classifier-local-1-workers-bs-1000.out
#results/kmeans_based_classifier-local-20-workers-bs-1000.out
#results/kmeans_based_classifier-local-20-workers-bs-250.out
"""
first figure:
    title: "average time per iteration of Lloyd algorithm for KMeans vs codebook size"
    label x: codebook size
    label y: seconds
    --> one line (or bar) per number of workers

second figure:
    title: "average time per iteration of Lloyd algorithm for KMeans vs number of workers"
    label x: number of workers
    label y: seconds
    --> one line (or bar) per codebook size 

third figure:
    title: "speed up of the average time per iteration of Lloyd algorithm for KMeans vs number of workers
                (n_workers > 1 because for n_workers = 1 is the reference for computing the speedup)"
    label x: number of workers
    label y: seconds
    --> one line (or bar) per codebook size 
    --> theoretical speedup 
"""

data = dict()
for filename in out_files:
    parts = filename.strip('.out').split(sep = '-')
    pca = parts[1]
    if pca != 'no_pca': continue

    cluster_type = parts[2]
    assert cluster_type in ['local', 'kubernetes']
    n_workers = int(parts[3])
    block_size = int(parts[6])

    if cluster_type not in data:
        data[cluster_type] = dict()

    if n_workers not in data[cluster_type]:
        data[cluster_type][n_workers] = dict()

    if block_size not in data[cluster_type][n_workers]:
        data[cluster_type][n_workers][block_size] = {'training': {}, 'predicting': {}}

    current_dict = data[cluster_type][n_workers][block_size]
    print(filename, flush = True)
    with open(filename, 'rt') as f:
        for line in f:
            line = line.strip()
            if len(line) < 3: continue
            # print(line, flush = True)
            parts = line.split()
            if line.startswith('Starting Lloyd for '):
                # Starting Lloyd for 1 clusters ...
                n_clusters = int(parts[3])
                current_dict['training'][n_clusters] = {'mean': 0, 'count': 0}
                mean = 0
                count = 0
            elif line.startswith('Iteration '):
                # Iteration 1 done with WSSSE = 5266795973.579 and change = 1.00000000e+00 lasting 26.096072 seconds
                seconds = float(parts[-2])
                mean = (mean * count + seconds) / (count + 1)
                count += 1
                current_dict['training'][n_clusters]['count'] = count
                current_dict['training'][n_clusters]['mean'] = mean
            elif line.startswith('predicting with kmeans '):
                # predicting with kmeans using a codebook with 2 clusters for train subset required 19.738587379455566 seconds
                # predicting with kmeans using a codebook with 2 clusters for test subset required 0.15599274635314941 seconds
                n_clusters = int(parts[7])
                subset = parts[10]
                seconds = float(parts[-2])
                if n_clusters not in current_dict['predicting']:
                    current_dict['predicting'][n_clusters] = dict()
                current_dict['predicting'][n_clusters][subset] = seconds
            else:
                # ignore other lines
                pass
        f.close()

#pprint.pp(json.dumps(data))
#pprint.pp(data)

cluster_type_list = list()
n_workers_list = list()
block_size_list = list()
codebook_size_list = list()
seconds_list = list()
speedup_list = list()
for cluster_type in data.keys():
    seconds_one_worker = dict()
    l_w = list(data[cluster_type].keys())
    l_w.sort()
    for n_workers in l_w:
        for block_size in data[cluster_type][n_workers].keys():
            #
            if block_size not in seconds_one_worker:
                seconds_one_worker[block_size] = dict()
            #
            for n_clusters in data[cluster_type][n_workers][block_size]['training'].keys():
                cluster_type_list.append(cluster_type)
                n_workers_list.append(n_workers)
                block_size_list.append(block_size)
                codebook_size_list.append(n_clusters)
                seconds = data[cluster_type][n_workers][block_size]['training'][n_clusters]['mean']
                seconds_list.append(seconds)
                #
                if n_workers == 1:
                    seconds_one_worker[block_size][n_clusters] = seconds
                #
                #print(f"{block_size} {n_workers} {n_clusters}", flush = True)
                if n_clusters in seconds_one_worker[block_size]:
                    speedup_list.append(seconds_one_worker[block_size][n_clusters] / seconds)
                else:
                    speedup_list.append(None)

df = pandas.DataFrame(
    {
        'cluster_type' : cluster_type_list,
        'n_workers' : n_workers_list,
        'block_size' : block_size_list,
        'codebook_size' : codebook_size_list,
        'seconds' : seconds_list,
        'speedup' : speedup_list
    }
)
df.sort_values(by = ['cluster_type', 'n_workers', 'block_size', 'codebook_size'], inplace = True)
#print(df.describe(), flush = True)

"""
first figure:
    title: "average time per iteration of Lloyd algorithm for KMeans vs codebook size"
    label x: codebook size
    label y: seconds
    --> one line (or bar) per number of workers
"""
df2 = df.pivot(index = 'codebook_size', columns = ['cluster_type', 'block_size', 'n_workers'], values = 'seconds')
#df2 = df.pivot(index = 'codebook_size', columns = ['n_workers'], values = 'seconds')
#print(df2.describe(), flush = True)
for logy in ['no', 'yes']:
    df2.plot(kind = 'bar',
                logy = logy == 'yes',
                ylabel = 'seconds',
                title = "Average time per iteration of Lloyd algorithm for KMeans vs codebook size",
                figsize = (12, 8)
                )
    pyplot.tight_layout()
    if save_figures_on_file:
        os.makedirs('figures', exist_ok = True)
        pyplot.savefig(f'figures/seconds_vs_cb_size_logy_{logy}.svg', format = 'svg')
    else:
        pyplot.show()

"""
second figure:
    title: "average time per iteration of Lloyd algorithm for KMeans vs number of workers"
    label x: number of workers
    label y: seconds
    --> one line (or bar) per codebook size 
"""

"""
df2 = df.pivot(index = 'n_workers', columns = ['cluster_type', 'block_size', 'codebook_size'], values = 'seconds')
df2.plot(kind = 'bar', title = "Average time per iteration of Lloyd algorithm for KMeans vs number of workers")
pyplot.show()
"""

df2 = df[df.block_size == 1000].pivot(index = 'n_workers', columns = ['cluster_type', 'codebook_size'], values = 'seconds')
for logy in ['no', 'yes']:
    df2.plot(kind = 'bar',
                logy = logy == 'yes',
                ylabel = 'seconds',
                title = "Average time per iteration of Lloyd algorithm for KMeans vs number of workers",
                figsize = (12, 8)
                )
    pyplot.tight_layout()
    if save_figures_on_file:
        os.makedirs('figures', exist_ok = True)
        pyplot.savefig(f'figures/seconds_vs_n_workers_logy_{logy}.svg', format = 'svg')
    else:
        pyplot.show()

"""
df2 = df[df.block_size == 1000]
df2 = df2[df2.codebook_size >= 64]
df2 = df2[df2.codebook_size <= 256]
df2 = df2.pivot(index = 'n_workers', columns = ['cluster_type', 'codebook_size'], values = 'seconds')
df2.plot(kind = 'bar', title = "Average time per iteration of Lloyd algorithm for KMeans vs number of workers")
pyplot.show()
"""

"""
third figure:
    title: "speed up of the average time per iteration of Lloyd algorithm for KMeans vs number of workers
                (n_workers > 1 because for n_workers = 1 is the reference for computing the speedup)"
    label x: number of workers
    label y: seconds
    --> one line (or bar) per codebook size 
    --> theoretical speedup 
"""

df2 = df[df.block_size == 1000]
df2 = df2.pivot(index = 'n_workers', columns = ['cluster_type', 'codebook_size'], values = 'speedup')
df2.plot(kind = 'line',
            ylabel = 'SpeedUp',
            style = '.-',
            title = "SpeedUp of single iterations of Lloyd algorithm for KMeans vs number of workers",
            figsize = (12, 8)
            )
pyplot.plot([1, 2, 4, 8, 12, 16, 20], [1, 2, 4, 8, 12, 16, 20], c = 'black', lw = 3, alpha = 0.33, label = 'Theoretical upper bound')
pyplot.grid()
if save_figures_on_file:
    os.makedirs('figures', exist_ok = True)
    pyplot.savefig(f'figures/speedup_on_paradigm.svg', format = 'svg')
else:
    pyplot.show()
