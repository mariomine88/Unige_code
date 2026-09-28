import os
import sys
import re
import subprocess

from matplotlib import pyplot

save_figures_on_file = False # True

re_filter = re.compile('(ensemble|gmm_|kde_|knn_|kmeans_).+-kubernetes-70-workers-.+\\.out$')
out_files = list()

def load_filenames(dirname, re_filter, out_files):
    run_ls = subprocess.Popen(["ls", dirname], stdout = subprocess.PIPE)
    for filename in run_ls.stdout:
        filename = filename.decode().strip()
        if re_filter.match(filename):
            out_files.append(dirname + '/' + filename)

load_filenames("results", re_filter, out_files)
load_filenames("results/ert.bak", re_filter, out_files)
load_filenames("results/gbt.bak", re_filter, out_files)
load_filenames("results/rf.bak", re_filter, out_files)

#for fn in out_files: print(fn)

training_times = dict()
extract = subprocess.Popen(["bash",  "scripts/extract_training_times.sh"], stdout = subprocess.PIPE)
for line in extract.stdout:
    components = line.decode().strip().split()
    technique = components[1]
    if technique not in training_times: training_times[technique] = dict()
    if technique == 'gmm':
        # training gmm pca 0 components      1 seconds      7.884 total       7.884
        pca = int(components[3])
        n_components = int(components[5])
        seconds = float(components[7])
        total_seconds = float(components[9])
        if pca not in training_times[technique]: training_times[technique][pca] = dict()

        if n_components in training_times[technique][pca]:
            training_times[technique][pca][n_components]['seconds'] += seconds
            training_times[technique][pca][n_components]['total_seconds'] += total_seconds
        else:
            training_times[technique][pca][n_components] = {'seconds': seconds, 'total_seconds': total_seconds}
    #
    elif technique in ['rf', 'ert', 'gbt']:
        # training gbt pca 0 n_estimators    200 max_depth   6 seconds    247.305 total    1646.283
        pca = int(components[3])
        n_estimators = int(components[5])
        max_depth = int(components[7])
        seconds = float(components[9])
        total_seconds = float(components[11])
        if pca not in training_times[technique]: training_times[technique][pca] = dict()

        if n_estimators not in training_times[technique][pca]: training_times[technique][pca][n_estimators] = dict()

        if max_depth in training_times[technique][pca][n_estimators]:
            training_times[technique][pca][n_estimators][max_depth]['seconds'] += seconds
            training_times[technique][pca][n_estimators][max_depth]['total_seconds'] += total_seconds
        else:
            training_times[technique][pca][n_estimators][max_depth] = {'seconds': seconds, 'total_seconds': total_seconds}
    #
    elif technique in ['kde', 'knn', 'kmeans']:
        # training kde pca 0 codebook_size   4096 seconds   2467.472 total   10755.651
        # training kmeans pca 0 codebook_size   1024 seconds   1199.688 total    3374.875
        pca = int(components[3])
        codebook_size = int(components[5])
        seconds = float(components[7])
        total_seconds = float(components[9])
        if pca not in training_times[technique]: training_times[technique][pca] = dict()

        if codebook_size in training_times[technique][pca]:
            training_times[technique][pca][codebook_size]['seconds'] += seconds
            training_times[technique][pca][codebook_size]['total_seconds'] += total_seconds
        else:
            training_times[technique][pca][codebook_size] = {'seconds': seconds, 'total_seconds': total_seconds}

            

extract.stdout.close()

egrep = subprocess.Popen(["egrep",  "  macro avg  |predicting with "] + out_files, stdout = subprocess.PIPE)

list_of_techniques = ['kmeans', 'gmm', 'ert', 'rf', 'gbt', 'kde', 'knn']
results = list()

state = 'discovering'
for line in egrep.stdout:
    #print(line.decode().strip())
    components = line.decode().strip().split(sep = ':')
    filename = components[0]
    components = components[1].split()

    if state == 'discovering':
        if components[0] == 'predicting':
            d = {'technique': components[2]}
            if d['technique'] not in list_of_techniques:
                print(line)
                raise Exception(f"Found an unknown technique: {d['technique']}")
            previous_filename = filename
            for i in range(3, len(components)):
                s = components[i]
                if   s ==   'clusters': d['clusters']   = int(components[i - 1])
                elif s == 'estimators': d['estimators'] = int(components[i - 1])
                elif s == 'components': d['components'] = int(components[i - 1])
                elif s ==  'max_depth': d['max_depth']  = int(components[i + 2])
                elif s ==          'K': d['K']          = int(components[i + 2])
                elif s ==  'bandwidth': d['bandwidth']  = float(components[i + 2])
                elif s ==     'subset': d['subset']     = components[i - 1]
                elif s ==    'seconds': d['seconds']    = float(components[i - 1])
            state = 'waiting for macro avg'
    #
    elif state == 'waiting for macro avg':
        if components[0] == 'macro' and components[1] == 'avg':
            assert filename == previous_filename
            fn_split = re.split('_|-', filename)
            d['pca'] = 0
            skip = False
            for i in range(len(fn_split)):
                if fn_split[i] == 'pca':
                    if fn_split[i - 1] != 'no':
                        d['pca'] = int(fn_split[i + 1])
                elif fn_split[i] == 'covar':
                    if fn_split[i + 1] != 'diagonal':
                        skip = True

            if d['technique'] == 'gmm' and d['components'] > 300: skip = True
            if d['subset'] == 'train': skip = True
            #if d['subset'] == 'test': skip = True

            if not skip:
                #print(d)
                d['macro avg'] = float(components[4])
                if d['technique'] in ['gmm']:
                    d['training total seconds'] = training_times[d['technique']][d['pca']][d['components']]['total_seconds']
                elif d['technique'] in ['kmeans', 'kde', 'knn']:
                    d['training total seconds'] = training_times[d['technique']][d['pca']][d['clusters']]['total_seconds']
                elif d['technique'] in ['rf', 'ert', 'gbt']:
                    d['training total seconds'] = training_times[d['technique']][d['pca']][d['estimators']][d['max_depth']]['total_seconds']
                else:
                    assert False
                results.append(d)
                #print(d)
        state = 'discovering'

egrep.stdout.close()

fig, axis = pyplot.subplots(nrows = 1, ncols = 1, figsize = (12, 8))
for technique in list_of_techniques:
    x = list()
    y = list()
    for d in results:
        if d['technique'] == technique:
            x.append(d['seconds'])
            y.append(d['macro avg'])
    if len(x) > 0:
        axis.scatter(x, y, label = technique, alpha = 1.0)
    else:
        print(f'len(x) = {len(x)} for technique {technique}')
axis.grid()
axis.set_xlabel('Running time at inference in seconds')
axis.set_ylabel('F1 macro average')
axis.set_title('Performance of several ML techniques using a Kubernetes cluster with the testing subset')
axis.legend()
pyplot.tight_layout()
if save_figures_on_file:
    os.makedirs('figures', exist_ok = True)
    pyplot.savefig('figures/f1_macro_avg_vs_inference_running_time.svg', format = 'svg')
else:
    pyplot.show()

fig, axis = pyplot.subplots(nrows = 1, ncols = 1, figsize = (12, 8))
for technique in list_of_techniques:
    x = list()
    y = list()
    for d in results:
        if d['technique'] == technique:
            x.append(d['training total seconds'])
            y.append(d['macro avg'])
    if len(x) > 0:
        axis.scatter(x, y, label = technique, alpha = 1.0)
    else:
        print(f'len(x) = {len(x)} for technique {technique}')
axis.grid()
axis.set_xlabel('Training running time in seconds')
axis.set_ylabel('F1 macro average')
axis.set_title('Performance of several ML techniques using a Kubernetes cluster with the testing subset')
axis.legend()
pyplot.tight_layout()
if save_figures_on_file:
    pyplot.savefig('figures/f1_macro_avg_vs_training_running_time.svg', format = 'svg')
else:
    pyplot.show()
