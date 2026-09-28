# Lab practice 2 on ensembles of trees: Random Forest, Extremely Randomized Trees and Gradient-Boosted Trees

In this lab practice, that will extent two sessions,
students are going to run training and inferencing tasks
similar to the tasks carried out in the previous lab practice.
The same two datasets are used in this lab practice:
the well known [MNIST Digits Database](https://huggingface.co/datasets/ylecun/mnist)
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
  physical computer using several cores) or a Kubernetes cluster
  (executed on several physical computers governed by the Kubernetes system).

- Know how to use the two different configurations mentioned above.

- Continue becoming familiar with the format the results of all the classifiers based on
  different ML techniques are provided. 

- Notice and understand why, in some cases, the execution of some experiments lasts
  longer in a distributed environment than in a local CPU or a local cluster.
  Usually it is due to the communication overhead.

- Also notice and understand when it is not worth to distribute small- and medium-size
  workloads because the communication overhead and some operations to distribute
  the data among workers require too much time than the time needd to run
  the workload on a local cpu.

- Last but not least, also to notice which ML techniques are more suitable than others
  to be distributed.

- Discover how to use the Scikit-Learn implementation of ensembles on distributed environments like RAY clusters. The trees can be built independently in ensembles like _Random Forest_ and _Extra Trees_, however, **Data Parallelism** can not be applied in the same way it was applied in the case of _KMeans_ and _GMM_ clustering techniques. In this two kinds of ensembles, each worker needs the whole dataset to start building each tree starting at the root node, so it is not possible to distribute **data shards**, instead, the whole training dataset is copied in to the memory of each worker.

  **QUESTION:** Given this situation, which could it be an important limitation of these kinds of ensembles when working with large enough datasets?

  In the implementation for _Random Forest_ and _Extra Trees_ used in this lab practice for the CHBMIT EEG dataset, the distribution of the workload for each configuration has been done by building the independent trees separately, asking each worker to build an ensemble with _**T**_ trees (or estimators), so if it is needed to build an ensemble with 1000 trees on a RAY cluster with 10 workers, then each worker is asked to build an ensemble with 100 trees. Strategically, using the method *predict_proba()* on each ensemble of 100 trees and aggregating all the outputs, the prediction of the 1000 trees is computed. This way, an **ensemble of ensembles** is used.
  **QUESTION:** Do you think this strategy could mitigate the problem of memory consumption when working with large enough datasets?
  **QUESTION:** Do you think this strategy by-passes the limitation of workload parallelisation of the Scikit-Learn implementation for _Random Forest_ and _Extra Trees_?
  
- Discover how to use RAY Tune to apply **Task Parallelism** instead of **Data Parallelism** to evaluate the same model with different configurations of the hyperparameters. This has only been applied in the case of Gradient Boosted Trees.


## <a name="exercises"></a>Table of the six exercises to do in this lab practice (remember: not in one single lab session)


|ML technique|MNist Digits|CHBMIT EEG|
|----------:|:----------------|:----|
|Random Forest|[launch-digits-rf.sh](../lab_digits/workspace/scripts/launch-digits-rf.sh)|[launch-chbmit-rf.sh](../lab_chbmit/workspace/scripts/launch-chbmit-rf.sh)|
|Extra Trees|[launch-digits-ert.sh](../lab_digits/workspace/scripts/launch-digits-ert.sh)|[launch-chbmit-ert.sh](../lab_chbmit/workspace/scripts/launch-chbmit-ert.sh)|
|Gradient-Boosted Trees|[launch-digits-gbt.sh](../lab_digits/workspace/scripts/launch-digits-gbt.sh)|[launch-chbmit-gbt.sh](../lab_chbmit/workspace/scripts/launch-chbmit-gbt.sh)|


As in the previous lab practice, for running each experiment you have to do the same steps:

  1. Update the repository
     ```bash
     cd
     cd teaa_lab
     git pull
     ```

     In the case you modified some of the original shell-scripts instead of working with copies of them, for updating the repository you will do the following steps
     that preserve your modifications. Anyway, be carefull with the management of the repository, you can always clean all and clone again the repository, but you may loose the changes you made:

     ```bash
     cd
     cd teaa_lab
     git stash
     git pull
     git stach pop
     ```

  1. Make a copy of the scripts to be executed:
     ```bash
     cd
     cd teaa_lab/lab_chbmit/workspace
     mkdir -p logs models results
     cp scripts/launch-chbmit-rf.sh scripts/launch-chbmit-rf-v1.sh
     ```

     You can use `v1` for version one, or use the labels you prefer, as well as to use different versions/labels for each configuration.

  1. Edit the copy of the script according to the execution environment you want to use and
     the configuration hyper-parameters indicated in the corresponding CSV file
     with the list of configurations assigned to each working group:

     ```bash
     nano scrits/launch-chbmit-rf-v1.sh
     ```

     Remember that for each task (i.e., exercise, the configurations assigned to each working group are in the CSV files available in PoliformaT).

  1. Run the experiment with a given configuration:
     ```bash
     sbatch scripts/launch-chbmit-rf-v1.sh
     ```

Repeat the previous steps for each one of the six exercises indicated in the previous table.

## How to download the results from the server to your desktop computer or laptop:

Previously you have to create, if not existing yet, a directory in your computer where to download all the results,
asuming you are in a Windows laptop, you can use the following sequence of commands to be executed in the console.
Remember to replace `<username>` with your username and `<servername>` with the name of the server used in the lab practices of this subject.

The command `sftp` will ask you for the same password you are already using to login into the server via `ssh`. In fact, `sftp` and `ssh` are commands of the Secure Shell client.

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

sftp <username>@<servername>:/teaa/<username>/
mget -r results
```

You can also download the results generated by other workgroups, or the ones generated by the professor:

```bash
mkdir chbmit_results
cd chbmit_results

sftp <username>@<servername>:/teaa/jon/
mget -r results
```

Remember that CSV files containing all the results for each use case and ML technique will be automatically generated and shared with you all.


## Code files to inspect

### The Python code students have to start becoming familiar with for tasks using the MNist Digits database is in the following files:

- [generic_ml_digits.py](../lab_digits/workspace/python/generic_ml_digits.py) (the same from previous lab practice)
- [ensemble_for_digits.py](../lab_digits/workspace/python/ensemble_for_digits.py)
- [load_mnist.py](../lab_digits/workspace/python/load_mnist.py) (the same from previous lab practice)
- [utils_for_results.py](../lab_digits/workspace/python/utils_for_results.py) (the same from previous lab practice)


### The Python code students have to start becoming familiar with for tasks using the CHBMIT EEG database is in the following files:

- [generic_ml_eeg.py](../lab_chbmit/workspace/python/generic_ml_eeg.py) (the same from previous lab practice)
- [eeg_load_data.py](../lab_chbmit/workspace/python/eeg_load_data.py) (the same from previous lab practice)
- [ensemble_for_eeg.py](../lab_chbmit/workspace/python/ensemble_for_eeg.py)
- [utils_for_results.py](../lab_chbmit/workspace/python/utils_for_results.py) (the same from previous lab practice)


## Final considerations

Some details students must consider for executing distinct configurations:

- The number of PCA components to reduce the dimensionality of the input space to more manegeable dimensions.
  You will see that once reached a sufficient value no improvements are observed by increasing it.
- The same applies to the number of trees/estimators per ensemble, and the max depth allowed at the time of building each single tree. For some of the hyperparameters using larger values does not improves performance but requires much more execution times for training and inferencing; you have to include a motivated discussion on this phenomenon in the report and the oral presentation. In the case of some hyperparameters, using larger values decreases the performance of the ML technique; a motivated discussion is required too in such cases.

_You do not have to run all the configurations because the results are already computed
and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
There is no time to execute all the runs by all the groups of students._

Remember to ask assisstance first time you interact with the results.
