# Lab practice 3 on memory-based techniques: Kernel Density Estimation and K-Nearest Neighbours

In this lab practice, that will extent two sessions,
students are going to run training and inferencing tasks,
similar to the previous two lab practices,
and using the same two datasets:
the well known [MNIST Digits Database](https://yann.lecun.com/exdb/mnist/)
and
the [CHB-MIT Scalp EEG Database](https://physionet.org/lightwave/?db=chbmit/1.0.0).
A detailed explanation about how data from the second database are preprocessed can be
found [here](../datasets/chbmit).


The goals of this lab practice are that students:

- Discover the different possibilities to run heavy workloads.
  The first one consists in using a subset or all the cores of a CPU thanks to
  low level parallelisation provided by the implementation of some algorithms
  available in Numpy and Scikit Learn.
  The second possiblity is based on the use of several workers (containers)
  running on a RAY cluster, which can be a local cluster (executed on a single
  physical computer) or a Kubernetes cluster (executed on several physical computers
  governed by the Kubernetes system).

- Know how to use the two different configurations mentioned above.

- Become more familiar with the format the results of all the classifiers based on
  different ML techniques are provided. 

- Notice and understand why, in some cases, the execution of some experiments lasts
  longer in a distributed environment than in a local CPU.
  Usually it is due to the communication overhead.

- Also notice and understand when it is not worth to distribute small- and medium-size
  workloads because the communication overhead and some operations to distribute
  the data among workers require too much time than the required time to run
  the workload on a local cpu.

- notice which ML techniques are more suitable than others to be distributed.

- Discover how to use Scikit-Learn models on distributed environments like RAY thanks
  to the `joblib` Python package.

- New for this lab practice, notice how performing a previous clustering using KMeans
  to reduce the size of the training set used for inferencing could have a strong
  impact on the inference running times while the performance (in terms of F1 macro average)
  is slightly lower, or as you will see in some cases, it could even improve.
  It is relevant students put their attention on this aspect and discuss the obtained
  results taking it into account.


## <a name="exercises"></a>Table of the four exercises to do in this lab practice (remember: not in one single lab session)


|ML technique|MNist Digits|CHBMIT EEG|
|----------:|:----------------|:----|
|Kernel Density Estimation|[launch-digits-kde.sh](../lab_digits/workspace/scripts/launch-digits-kde.sh)|[launch-chbmit-kde.sh](../lab_chbmit/workspace/scripts/launch-chbmit-kde.sh)|
|K-Nearest Neighbours|[launch-digits-knn.sh](../lab_digits/workspace/scripts/launch-digits-knn.sh)|[launch-chbmit-knn.sh](../lab_chbmit/workspace/scripts/launch-chbmit-knn.sh)|


As in the previous tow lab practices, to run each experiment you have to do similar steps.
However, in this case, it is not necessary to make a copy of the shell script and then modify it,
you can provide command-line parameters to choose the different configurations.

Let us see some examples, but remember that for each task (i.e., exercise,
the configurations assigned to each working group are in the CSV files available in PoliformaT).

Run an experiment with a given configuration for MNIST Digits Database:

```bash
cd
cd teaa_lab/lab_digits/workspace
sbatch --job-name="digits-kde" \
    --output="logs/output_digits_kde_based_classifier.out" \
    scripts/launch-digits-kde.sh --codebookSize "0:100:200:500:1000" --band-widths "0.1:0.2:0.5:1.0:2.0:3.0" --pca-components "37 41 53 71 0.95"
```

Let's see another configuration for MNIST Digits Database:

```bash
cd
cd teaa_lab/lab_digits/workspace
sbatch --job-name="digits-knn" \
    --output="logs/output_digits_knn_based_classifier.out" \
    scripts/launch-digits-knn.sh --codebookSize "0:100:200:500:1000" --K "3:5:7:9:11:13" --pca-components "37 41 53 71 0.95"
```

Remember that for Digits only one execution environment is used, so it is not required
to indicate any option related to it.


Run an experiment with a given configuration for CHBMIT EEG Database:

```bash
cd
cd teaa_lab/lab_chbmit/workspace
sbatch --job-name="chbmit-chb03-kde" \
    --output="logs/output_chbmit_kde_based_classifier.out" \
    scripts/launch-chbmit-kde.sh --patient 03 --codebookSize "0:8192" --format pca136 --local-cpu
```

You can change the output filename to reflect the configuration in use. 
Put your attention on the command-line options `--job-name` and `--output`, both are options for the `sbatch` command,
while the other options are the ones passed to the shell script that is going to be executed. 
In this case, only the patient `chb03` will be used, with and without a previous KMeans to reduce
the size of the samples from the training set used for inferencing. No KMeans that is specified using the 0;
and by indicating 8192, then LBG is applied starting from one cluster, and then only the codebook sizes
power of 2 from 64 up to 8192 will be used. In some cases, 8192 will not be reached, depending on the samples 
available for each target class in the training subset. Which ones have been finally used will be reflected
in the generated results.
Regarding the bandwidths, all the configured bandwidths in the shell script are used by default; we recommend to use all them.

Let us run another configuration for CHBMIT EEG Database:

```bash
cd
cd teaa_lab/lab_chbmit/workspace
sbatch --job-name="chbmit-ALL-knn" \
    --output="logs/output_chbmit_knn_based_classifier.out" \
    scripts/launch-chbmit-kde.sh --patient ALL --codebookSize "8192" --format pca141 --cluster-type local
```

The scripts accept three different configurations of the execution environment:

- `--local-cpu` to indicate that no RAY cluster should be used. 

  In this case, depending on the ML technique the number of cores/processors, the number of jobs, and the number of threads are configured in the shell script.

- `--local` to indicate that the RAY local cluster should be used. 

  In this case, the number of cores/processors, jobs and threads is set to 1, becuase the number workers will be 14.

- `--kubecluster` to indicate that the RAY Kubernetes cluster should be used. 

  In this case, the number of cores/processors, jobs and threads is set to 1, becuase the number workers will be 70.


Repeat similar steps for each one of the four exercises indicated in the previous table according to the configurations assigned to your group.


## How to download the results from the server to your desktop computer or laptop:

Previously you have to create, if not existing yet, a directory in your computer where to download all the results,
asuming you are in a Windows laptop, you can use the following sequence of commands to be executed in the console.
Remember to replace `<username>` with your username and `<servername>` with the name of the server used in
the lab practices of this subject.

The command `sftp` will ask you for the same password you already use to login into the server via `ssh`.
In fact, `sftp` and `ssh` are commands of the Secure Shell client.

Shell script to use as starting point to download the results obtained with the MNist Digits database:

```bash
mkdir digits_results
cd digits_results

sftp <username>@<servername>:teaa_lab/lab_digits/workspace
mget -r results
```

Shell script to use as starting point to download the results obtained with the CHBMIT EEG database:

```bash
mkdir chbmit_results
cd chbmit_results

sftp <username>@<servername>:teaa_lab/lab_chbmit/workspace
mget -r results
```

### Summary of available results:

The results of all the students and the ones already generated by the professor can be found [here](../whole_results),
where the shell scripts and the Python scripts to obtain these results are also available.


## Code files to inspect

### The Python code students have to start becoming familiar with for tasks using the MNist Digits database is in the following files:

- [generic_ml_digits.py](../lab_digits/workspace/python/generic_ml_digits.py) -- the same from previous lab practices
- [kde_for_digits.py](../lab_digits/workspace/python/kde_for_digits.py)
- [knn_for_digits.py](../lab_digits/workspace/python/knn_for_digits.py)
- [NearestNeighbours.py](../lab_digits/workspace/python/NearestNeighbours.py) -- this code includes also the use of KNN
- [load_mnist.py](../lab_digits/workspace/python/load_mnist.py) -- the same from previous lab practices
- [utils_for_results.py](../lab_digits/workspace/python/utils_for_results.py) -- the same from previous lab practices


### The Python code students have to start becoming familiar with for tasks using the CHBMIT EEG database is in the following files:

- [generic_ml_eeg.py](../lab_chbmit/workspace/python/generic_ml_eeg.py) -- the same from previous lab practices
- [eeg_load_data.py](../lab_chbmit/workspace/python/eeg_load_data.py) -- the same from previous lab practices
- [kde_for_eeg.py](../lab_chbmit/workspace/python/kde_for_eeg.py) -- this code includes also the use of KNN
- [NearestNeighbours.py](../lab_chbmit/workspace/python/NearestNeighbours.py) -- this code includes also the use of KNN
- [utils_for_results.py](../lab_chbmit/workspace/python/utils_for_results.py) -- the same from previous lab practices


## Final considerations

Some details students must consider for executing distinct configurations:

- The number of PCA components to reduce the dimensionality of the input space to more manegeable dimensions.
  You will see that once reached a sufficient value no improvements are observed by increasing it.

_You do not have to run all the configurations because the results are already computed
and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
There is no time to execute all the runs by all the groups of students._

Remember to ask assisstance first time you interact with the results.

