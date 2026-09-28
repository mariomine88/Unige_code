# Lab practice 1 on KMeans and GMM

In this lab practice, that will extent two sessions,
students are going to run training and inferencing tasks 
using two datasets:
the well known [MNIST Digits Database](https://huggingface.co/datasets/ylecun/mnist)
and
the [CHB-MIT Scalp EEG Database](https://physionet.org/lightwave/?db=chbmit/1.0.0).
A detailed explanation about how data from the second database are preprocessed can be
found [here](../datasets/chbmit).


The goals of this lab practice are that students:

- Discover the possibility of using several workers running on a RAY cluster, which can be a local cluster (executed on a single
  physical computer using several cores) or a Kubernetes cluster
  (executed on several physical computers governed by the Kubernetes system).
  **Since the academic year 2026/2027, i.e., since the machine `tensor.dsic.upv.es`
  is used for the lab practices, it is not possible to work with a Kubernetes cluster**.

- Know how to use the configuration mentioned above.

- Become familiar with the format of the results of all the classifiers based on
  different ML techniques are provided. 

`Remember to update the GitLab repository. Usually, there are some software updates.`

   ```bash
   cd
   cd teaa_lab
   git pull
   ```

# <a name="exercises"></a>List of exercises to do in this lab practice (remember: not in one single lab session)

# K-Means Experiments

## KMeans on MNIST Digits database:

   Obtain several codebooks with the **Lloyd**'s algorithm for K-Means using the provided
   code that only uses the configurations to run on the local computer.
   In this case the parallelised version provided in the code is implemented in Ray.

   The Python code students have to start becoming familiar with is in the following files:

   - [generic_ml_digits.py](../lab_digits/workspace/python/generic_ml_digits.py)
   - [kmeans_for_digits.py](../lab_digits/workspace/python/kmeans_for_digits.py)
   - [load_mnist.py](../lab_digits/workspace/python/load_mnist.py)
   - [utils_for_results.py](../lab_digits/workspace/python/utils_for_results.py)
   - [see_conditional_probabilities.py](../lab_digits/workspace/python/see_conditional_probabilities.py)

   The Python code is executed using previously configured shell-scripts, for this first exercise the
   shell-script to use is [launch-digits-kmeans.sh](../lab_digits/workspace/scripts/launch-digits-kmeans.sh)
   that in turn invokes [slurm_run_digits_kmeans.sh](../lab_digits/workspace/scripts/slurm_run_digits_kmeans.sh).
   Students can do some changes in 
   [launch-digits-kmeans.sh](../lab_digits/workspace/scripts/launch-digits-kmeans.sh),
   as indicated in the comments, to run experiments with different configurations.
   As it can be observed in 
   [launch-digits-kmeans.sh](../lab_digits/workspace/scripts/launch-digits-kmeans.sh),
   the 
   [slurm_run_digits_kmeans.sh](../lab_digits/workspace/scripts/slurm_run_digits_kmeans.sh)
   is executed by submitting a job to the SLURM queue manager.
   As you already know from the introductory lab practice (a.k.a. lab practice 0):

   ```bash
   cd
   cd teaa_lab/lab_digits/workspace
   mkdir -p logs models results
   ./scripts/launch-digits-kmeans.sh
   ```

   **It is very important to edit the shell-script**
   [launch-digits-kmeans.sh](../lab_digits/workspace/scripts/launch-digits-kmeans.sh),
   **before executing it to fit your execution requirements**.

   Some details students must consider when executing distinct configurations:

   - The number of PCA components to reduce the dimensionality of the input space to more manegeable dimensions.
     You will see that **once reached a sufficient number of components (dimensions in the latent space)
     no further improvements are observed by increasing it**.

   <!--
   _You do not have to run all the configurations because the results are already computed
   and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
   There is no time to execute all the runs by all the groups of students._
   **Probably, the precomputed results would be updated due to some improvements.**
   If it is the case, you will be noticed.
   -->

   Remember to ask for assisstance the first time you interact with the results.

   You can see the evolution of the criteria 
   [Calinski-Harabasz](https://scikit-learn.org/stable/modules/clustering.html#calinski-harabasz-index)
   and
   [Davies-Bouldin](https://scikit-learn.org/stable/modules/clustering.html#davies-bouldin-index)
   in CSV files you can find in the `logs` directory. For this particular lab exercise in `logs/digits/kmeans`.
   Please, remember that these criteria are _not designed to determine the optimal number of clusters_ for a given data set.

   Are you able to obtain some preliminary conclusions about the similarities between some digits which are reflected,
   somehow, in the conditional probabilities you can visualize in the slides of unit 1?

   
1. See and discuss with your colleague the obtained results corresponding to a KMeans-based classifier.

   You can see the results in the directory `results/digits/kmeans/test'.

   All these results, for both training and testing subsets, give us different KPIs, important to focus
   your attention on the F1 macro average, that is the less optimistic metric.

   ```bash
   cd
   cd teaa_lab/lab_digits/workspace
   grep "^   macro avg " results/digits/kmeans/test/*.txt | sort -nk 6
   ```

   **Validate with the professor during the lab sessions you understand the obtained results**.


##  KMeans on CHB-MIT Scalp EEEG dataset (applied to each patient individually):

   Obtain several codebooks with the **Lloyd**'s algorithm of K-Means using
   a local RAY cluster with given number of workers. **Recall that it is not possible to use a RAY cluster on Kubernetes**.

   You have to specify the number of workers in the shell script. The number of workers is set to a default value.
   Students must change it to run distinct experiments and analyze the impact of the number of workers in the running time.

   The Python code is ready to run on two configurations: a local RAY cluster and a RAY cluster on Kubernetes.
   As already commented, we are going to use only a local RAY cluster in this academic year.
   The shell script that launches the Python code could use several configurable options, but it has been modified to only use a local RAY cluster.
   In any case, it is important to become familiar with the Python code and do not worry if you cannot understand all.
   Professors will highlight the relevant details in relation to the use of RAY in Python in the classroom.
   It is important to highlight that using RAY, the Python code to use a local RAY cluster or a RAY cluster on Kubernetes is exactly the same;
   the unique difference is in how the Python code is invoked from the shell scripts.

   These a are the Python files you must inspect and become familiar with:

   - [generic_ml_eeg.py](../lab_chbmit/workspace/python/generic_ml_eeg.py)
   - [eeg_load_data.py](../lab_chbmit/workspace/python/eeg_load_data.py)
   - [kmeans_for_eeg.py](../lab_chbmit/workspace/python/kmeans_for_eeg.py)
   - [RayKMeans.py](../lab_chbmit/workspace/python/RayKMeans.py)
   - [utils_for_results.py](../lab_chbmit/workspace/python/utils_for_results.py)

   As mentioned, the Python code is executed using previously configured shell-scripts, for this exercise the
   shell-script to use is [launch-chbmit-kmeans.sh](../lab_chbmit/workspace/scripts/launch-chbmit-kmeans.sh)
   which in turn invokes [slurm_run_chbmit_kmeans.sh](../lab_chbmit/workspace/scripts/slurm_run_chbmit_kmeans.sh).

   [launch-chbmit-kmeans.sh](../lab_chbmit/workspace/scripts/launch-chbmit-kmeans.sh)
   must be executed from the command line to submit the corresponding jobs to the SLURM queue manager as you already know:

   ```bash
   cd
   cd teaa_lab/lab_chbmit/workspace
   mkdir -p logs models results
   ./scripts/launch-chbmit-kmeans.sh
   ```

   **Important to edit the shell-script**
   [launch-chbmit-kmeans.sh](../lab_chbmit/workspace/scripts/launch-chbmit-kmeans.sh)
   **before executing it to fit your execution requirements in terms of the number of workers
   to use and the configuration of patients, formats, etc.**

   The results will be available at the end of executions in `results/chbmit/kmeans`.

   Remember to ask for assisstance the first time you have to configure the shell-scripts.

   <!--
   _You do not have to run all the configurations because the results are already computed
   and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
   There is no time to execute all the runs by all the groups of students._
   **Probably, the precomputed results would be updated due to some improvements.**
   If it is the case, you will be noticed.
   -->

   Remember to ask for assisstance the first time you interact with the results.

   You can see the evolution of the criteria 
   [Calinski-Harabasz](https://scikit-learn.org/stable/modules/clustering.html#calinski-harabasz-index)
   and
   [Davies-Bouldin](https://scikit-learn.org/stable/modules/clustering.html#davies-bouldin-index)
   in CSV files you can find in the directory `logs/chbmit/kmeans`.
   Please, remember these indexes are not designed to determine the optimal number of clusters for a given data set.


##  KMeans on CHB-MIT Scalp EEEG dataset (applied to all patients):

   In this case, all the sessions of patients from CHB01 to CHB16 are used to train and all the sessions
   of patients from CHB17 to CHB24 are used as test.

   Use the same Python code and shell scripts than in the previous exercise by properly changing the configuration to use `patient=ALL` and `format=pca141` or `format=21x14`.
   Validate with the professor you are using the correct configuration.
   Maybe some configurations with all the patients will not fit in the resources available in the computer.

# Gaussian Mixture Model Experiments

##  GMM on MNIST Digits Database

   Obtain one GMM per target class, with several number components per GMM,
   using the _Expectation Maximisation (EM)_ algorithm implemented in
   [RayGMM.py](../lab_digits/workspace/python/RayGMM.py).
   <!--
   [_Scikit Learn_](https://scikit-learn.org/stable/modules/mixture.html#mixture),
   in particular using objects of the class
   [`GaussianMixture`](https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html#sklearn.mixture.GaussianMixture).
   -->

   The Python code students have to start becoming familiar with is in the following files, some of them already used previously 
   when working with _KMeans_:

   - [generic_ml_digits.py](../lab_digits/workspace/python/generic_ml_digits.py)
   - [gmm_for_digits.py](../lab_digits/workspace/python/gmm_for_digits.py)
   - [RayGMM.py](../lab_digits/workspace/python/RayGMM.py)
   - [load_mnist.py](../lab_digits/workspace/python/load_mnist.py)
   - [utils_for_results.py](../lab_digits/workspace/python/utils_for_results.py)

   The Python code is executed using previously configured shell-scripts, for this exercise the
   shell-script to use is
   [launch-digits-gmm.sh](../lab_digits/workspace/scripts/launch-digits-gmm.sh)
   which in turn invokes 
   [slurm_run_digits_gmm.sh](../lab_digits/workspace/scripts/slurm_run_digits_gmm.sh).

   [launch-digits-gmm.sh](../lab_digits/workspace/scripts/launch-digits-gmm.sh)
   must be executed from the command line to submit the corresponding jobs to the SLURM queue manager as you already know:

   ```bash
   cd
   cd teaa_lab/lab_digits/workspace
   mkdir -p logs models results
   ./scripts/launch-digits-gmm.sh
   ```

   **Important to edit the shell-script**
   [launch-digits-gmm.sh](../lab_digits/workspace/scripts/launch-digits-gmm.sh)
   **before executing it to fit your execution requirements**.

   Some details students must consider for executing distinct configurations:

   - The number of PCA components to reduce the dimensionality of the input space to more manegeable dimensions.
     You will see that once reached a sufficient number of compoments no further improvements are observed by increasing it.

   - The value for the number of components of the GMM of each target class varies from 5 to 70, you will see
     that small values of this configuration parameter are enough to obtain good results.

   - Both **full** and **diagonal** convariance matrix types are used.
     For the **full** covariance matrices it is important to change the minimum value allowed for variances.

     The number of GMM components must be lower when using the **full** covariance matrix than when using
     the **diagonal** covariance matrix. Using the **full** covariance matrix smaller values for the number 
     of GMM components reach good results and the running time of the EM for each GMM does not last too much time.

   - Minimum value for the variances. Using **diagonal** covariance matrices this value can be 1.0e-5 or smaller,
     but if the training fails due to the lack of precision on arithmetic operations, then use a higher value.
     In the case of **full** covariance matrices, this problem arises earlier, so a value of 1.0 is enough for
     many configurations, you can try smaller values, 0.5 for instance.

   <!--
   _You do not have to run all the configurations because the results are already computed
   and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
   There is no time to execute all the runs by all the groups of students._
   **Probably, the precomputed results would be updated due to some improvements.**
   If it is the case, you will be noticed.
   -->

   Remember to ask for assisstance the first time you interact with the results.

   You can see the evolution of the criteria 
   [Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC)](https://scikit-learn.org/stable/modules/linear_model.html#aic-bic)
   in CSV files you can find in the directory `logs/digits/gmm`.


## GMM on CHB-MIT Scalp EEEG dataset (applied to each patient individually):

   Obtain one GMM per target class, with several number components per GMM,
   using the _Expectation Maximisation (EM)_ algorithm. 

   In this exercise, only our implementation of GMM for RAY is used,
   [RayGMM.py](../lab_chbmit/workspace/python/RayGMM.py), for the
   configuration of a local RAY cluster, not for the configuration of a RAY cluster on Kubernetes.

   The Python code students have to start becoming familiar with is in the following files,
   some of them already used previously when working with _KMeans_:

   - [generic_ml_eeg.py](../lab_chbmit/workspace/python/generic_ml_eeg.py)
   - [gmm_for_eeg.py](../lab_chbmit/workspace/python/gmm_for_eeg.py)
   - [RayGMM.py](../lab_chbmit/workspace/python/RayGMM.py)
   - [utils_for_results.py](../lab_chbmit/workspace/python/utils_for_results.py)

   The Python code is executed using previously configured shell-scripts, for this exercise the
   shell-script to use is
   [launch-chbmit-gmm.sh](../lab_chbmit/workspace/scripts/launch-chbmit-gmm.sh)
   which in turns invokes 
   [slurm_run_chbmit_gmm.sh](../lab_chbmit/workspace/scripts/slurm_run_chbmit_gmm.sh).

   [launch-chbmit-gmm.sh](../lab_chbmit/workspace/scripts/launch-chbmit-gmm.sh)
   must be executed from the command line to submit the corresponding jobs to the SLURM queue manager as you already know:

   ```bash
   cd
   cd teaa_lab/lab_chbmit/workspace
   mkdir -p logs models results
   ./scripts/launch-chbmit-gmm.sh
   ```

   **Important to edit the shell-script**
   [launch-chbmit-gmm.sh](../lab_chbmit/workspace/scripts/launch-chbmit-gmm.sh)
   **before executing it to fit your execution requirements**.

   <!--
   _You do not have to run all the configurations because the results are already computed
   and available [here](https://drive.google.com/drive/folders/1ganeFM4I4vOQJvtJig1ZUuSA1MfihtZi?usp=drive_link).
   There is no time to execute all the runs by all the groups of students._
   **Probably, the precomputed results would be updated due to some improvements.**
   If it is the case, you will be noticed.
   -->


## GMM on CHB-MIT Scalp EEEG dataset (applied to all patients):

   In this case, as previously commented when using KMeans,
   all the sessions of patients from CHB01 to CHB16 are used to train and all the sessions
   of patients from CHB17 to CHB24 are used as test.

   Use the same Python code and shell scripts than in the previous exercise by properly changing the configuration to use `patient=ALL` and `format=pca141` or `format=21x14`.
   Validate with the professor you are using the correct configuration.
   Maybe some configurations with all the patients will not fit in the resources available in the computer.

## Fetching the results from tensor to your local computer

If you want to retrieve the logs and results from your experiments to your local computer, you can run the following command (for example, for digits and kmeans, you should change this to get other results):


   ```bash
   scp -r USER@alumno.upv.es@tensor.dsic.upv.es:/home/alumno.upv.es/USER/teaa_lab/lab_digits/workspace/logs .
   scp -r USER@alumno.upv.es@tensor.dsic.upv.es:/home/alumno.upv.es/USER/teaa_lab/lab_digits/workspace/results .
   ```