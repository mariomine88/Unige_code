# Lab environment

## Computing infrastructure (HW and SW)

- One bare metal computer with [AMD EPYC 9474F CPU](https://www.amd.com/en/products/processors/server/epyc/4th-generation-9004-and-8004-series/amd-epyc-9474f.html)
  - 48 physical / 96 logical cores
  - 512 GB of RAM
- Linux [Ubuntu](https://www.ubuntu.com) 24 LTS
- [Python](https://www.python.org/) + [Numpy](https://numpy.org/) + [Scikit Learn](https://scikit-learn.org/stable/) + [Pandas](https://pandas.pydata.org/)
- [RAY](https://www.ray.io/) to distribute training and, in some cases, inference workloads

## [RAY](https://www.ray.io/)

   **Scale ML & AI Computing**

   **RAY** facilitates us to work with different kind of objects by storing them in the **RAY distributed data storage**

   A **Numpy** array can be split into chunks following the strategy of _data sharding_, each chunk can be uploaded to the RAY distributed data storage using the method `ray.put()` that returns a reference to it. The references to objects in the distributed data storage are used when invoking different _remote_ methods in the context of RAY.

   In most of our examples, we are going to use just references to _remote_ objects when invoking _remote_ methods in the context of RAY. This way, we will easily apply the ***map-reduce*** programming strategy for distributing workloads by
   following the ***data parallelism*** paradigm.

   Using [RAY](https://www.ray.io/) from Python code we will dynamically create and use both
   local and [Kubernetes](https://kubernetes.io/docs/concepts/) clusters in a transparent way from the point of view of code.
   The local ones offer us the possibility of use all or some of the cores in a single computing node,
   while the [Kubernetes](https://kubernetes.io/docs/concepts/) allow us to use many more cores (let us say _workers_) that will be
   distributed among the available cores in all the nodes.

   Before of diving deeper into the details of the **RAY** programming style, it is a good step to obtain a [global overview](https://docs.ray.io/en/latest/ray-overview/index.html) of what **RAY** offers, in particular the Python decorators.

## Our configuration

### Setup in your computer

1. Installation and Configuration of [RAY](https://www.ray.io/) on student's computers

   Let us prepare the local environment to work with **RAY** before continuing. Then, we can run some of the examples.

   The first step is to install [miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install) and prepare a virtual environment and installing all the necessary packages. It is suggested all students run this first in their personal computer.

   A _YAML_ configuration file is provided [ray.yaml](ray/ray.yaml)

   NOTICE: We have to enter in the `ray` directory provided in this repository, where the necessary _YAML_ file and _shell_ script are located: [ray.yaml](ray/ray.yaml) and [ray.sh](ray/ray.sh)

   ```bash
    conda env create -f ray.yaml
   ```

   If all the steps done so far ran correctly, then we have to activate the **RAY** environment and then install **RAY** and other packages by executing the shell script [ray.sh](ray/ray.sh):

   ```bash
    conda activate ray

    ./ray.sh
   ```

### Setup in [Tensor](https://alfresco.dsic.upv.es/share/s/55isZNUUQ1KZvSkTiqM4Rw)

1. Installation and Configuration of [RAY](https://www.ray.io/) in `tensor.dsic.upv.es` ([the user&#39;s guide for this cluster](https://alfresco.dsic.upv.es/share/s/55isZNUUQ1KZvSkTiqM4Rw))

   In this case, an environment is already configurated in a shared folder for this subject `/opt/asig/teaa-cd/miniconda3`.

   So, **you don't need to install anything** and **you don't need to create a new** ***conda*** **environment**, all is available in such directory.

   All you need to do is activating the `base` environment as indicated below. To avoid any possible misunderstanding, let us notice you that instead of using `ray` as the name for the already available and configured environment, in this case the name is `base`.

   How to persistently activate the ***conda*** environment for your user account in `tensor.dsic.upv.es` in two steps:

   - First step

   ```bash
    /opt/asig/teaa-cd/miniconda3/bin/conda init
   ```
   - Second step

     Log out from your user acccount in `tensor.dsic.upv.es` and log in again. If no errors, then you will have the `base` environment activated and you will be able to run the examples of lab practice 0.
2. [SLURM](https://slurm.schedmd.com/documentation.html)

   **SLURM** is an open source, fault-tolerant, and highly scalable cluster management and job scheduling system for large and small Linux clusters.

   **SLURM** requires no kernel modifications for its operation and is relatively self-contained.

   As a cluster workload manager, **SLURM** has three key functions.

   - First, it allocates exclusive and/or non-exclusive access to resources (computing nodes) to users for some duration of time so they can perform work.
   - Second, it provides a framework for starting, executing, and monitoring work (normally a parallel job) on the set of allocated nodes.
   - Finally, it arbitrates contention for resources by managing a queue of pending work.

   Example of shell script to enqueue a job in **SLURM**:

   ```
   #!/bin/bash
   #SBATCH -p docencia
   #SBATCH --job-name=test_job
   #SBATCH --output=test_job_output_1.txt
   #SBATCH --ntasks=1
   #SBATCH --time=00:01:00

   echo "Hello, SLURM!"
   date
   sleep 10
   date
   echo "bye, bye!!!"
   ```
   And, if the name of the _shell script_ is `test_job_1.sh`, it can be executed using the command `sbatch` according to the following command-line example:

   ```console
    sbatch ./test_job_1.sh
   ```
   The lines in the _shell script_ starting with `#SBATCH` are processed by the **SLURM** manager.

   Finally, we can see the queued and running jobs using the command `squeue`
3. **Running a simple example**, one of the examples you have to run in the lab session for introducing this lab environment is the Python code to compute an approximation to $\pi$ based on the Monte Carlo method.

   - First, let us see the Python code [pi.py](../lab_practice_0/workspace/python/pi.py) to understand the jobs that are executed in this example.
   - Second, let us see the shell-script to run it from the command line [run-pi-example.sh](../lab_practice_0/workspace/scripts/run_pi_example.sh)
     to understand how to indicate with parameters the jobs that are executed in this example.
   - Third, let us see the shell-script to run this example using **SLURM** [slurm_run_pi_example.sh](../lab_practice_0/workspace/scripts/slurm_run_pi_example.sh)
     to see some of the details and **SLURM**-specific parameters to enqueue jobs.
4. **Job monitoring**

   Checking queued and running jobs:

   ```console
   squeue
   ```
   Checking user's queue:

   ```console
   squeue -u user
   ```
   Canceling jobs:

   ```console
   scancel JOBID
   ```
   System info:

   ```console
   sinfo
   ```
