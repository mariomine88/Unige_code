# Introduction to the lab environment

## Goals

1. Students are able to login into the server indicated by the professor.
1. Students change their default passwords.
1. Students learn how to cloning a GitHub repository.
1. Students learn how to run some basic examples using SLURM commands and monitor the queue of pending jobs.
1. Students learn how to run some examples for obtaining running times with different configurations.

## Exercises


1. Logging into Tensor

   ```console
   ssh LOGIN@alumno.upv.es@tensor.dsic.upv.es
   ````

   Where LOGIN is your UPVNET user (typically the username before @ in the UPV mail address).

1. Clone the GitHub

   ```bash
   cd
   git clone https://git.upv.es/jajorca/teaa_lab
   cd teaa_lab
   ls -l
   ```

1. Run basic SLURM example

   ```bash
   cd
   cd teaa_lab/lab_practice_0/workspace
   sbatch scripts/slurm_test_job_1.sh
   ```

   The contents of `slurm_test_job_1.sh` is:

   ```bash
   #!/bin/bash
   #SBATCH -p docencia
   #SBATCH --job-name=test_job
   #SBATCH --output=test_job_output_1.out
   #SBATCH --ntasks=1
   #SBATCH --time=00:01:00
   
   echo "Hello, SLURM!"
   date
   sleep 10
   date
   echo "Bye! Bye!"
   ```

   You can see the running and enqueued jobs using the following command:

   ```bash
   squeue
   ```

   The output of executing the job will saved in the specified file `test_job_output_1.out`


1. Run [pi.py](workspace/python/pi.py) using shell script [run_pi_example.sh](workspace/scripts/run_pi_example.sh)
   that invokes script [slurm_run_pi_example.sh](workspace/scripts/slurm_run_pi_example.sh) for several configurations
   of number of workers in a local **RAY** execution environment.

   ```bash
   ./scripts/run_pi_example.sh
   ```

   You can see the output of executing this example in the output files specified in the shell script
   [run_pi_example.sh](workspace/scripts/run_pi_example.sh) when invoking
   [slurm_run_pi_example.sh](workspace/scripts/slurm_run_pi_example.sh) for different configurations:

   ```bash
   less output_pi_example_with_1_workers.out
   ```

   ```bash
   grep seconds output_pi_example*.out | sort -nk 14
   ```

   In this example, students are going to see the Python code to learn how to use Python decorators for defining
   remote methods in the **RAY** context, and how to use **RAY** _actors_.
   With the remote methods plus the method `ray.get()` we can implement the _map-reduce_ strategy on distributed data.

   `ray.get()` retrieves the actual objects whose references are provided as parameters. 
   Then, performing the sum of all the partial counts, in this example, the global result is computed in the main program.


1. Run [wordcount.py](workspace/python/wordcount.py) using shell script
   [run_wordcount_example.sh](workspace/scripts/run_wordcount_example.sh)
   that invokes the script [slurm_run_wordcount_example.sh](workspace/scripts/slurm_run_wordcount_example.sh)

   ```batch
   ./scripts/run_wordcount_example.sh
   ```

   Similarly to the previous example, you can see the output of executing this example in the output files specified in the shell script
   [run_wordcount_example.sh](workspace/scripts/run_wordcount_example.sh) every time it invokes the script
   [slurm_run_wordcount_example.sh](workspace/scripts/slurm_run_wordcount_example.sh) 
   by using the same commands commented above.
   Additionally, in the wordcount example other files are created containing the top _N_ most frequent
   words and the time required to do the task.

   ```batch
   grep "^WC: total different" wc_*.out
   ```

   ```batch
   grep "^WC: time " wc_*.out | sort -nk 6
   ```


   In this example, students will see how to use the function `map_batches()` of the **RAY** class _DataSet_
   to run some user-defined methods on chunks of a dataset distributed on all the workers.
