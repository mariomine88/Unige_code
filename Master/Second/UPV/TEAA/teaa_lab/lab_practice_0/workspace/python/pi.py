import os
import sys
import time
import random
import math
import numpy
from operator import add
import argparse
import ray

@ray.remote
class ProgressActor:
    def __init__(self, total_num_samples: int):
        self.total_num_samples = total_num_samples
        self.num_samples_completed_per_task = {}

    def report_progress(self, task_id: int, num_samples_completed: int) -> None:
        self.num_samples_completed_per_task[task_id] = num_samples_completed

    def get_progress(self) -> float:
        return (
            sum(self.num_samples_completed_per_task.values()) / self.total_num_samples
           )

@ray.remote
def sampling_task(num_samples: int, task_id: int,
        progress_actor: ray.actor.ActorHandle) -> int:
    num_inside = 0
    block = num_samples // 10
    for i in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if math.hypot(x, y) <= 1:
            num_inside += 1

        # Report progress arount 10 times during the calculation.
        if (i + 1) % block == 0:
            # This is async.
            progress_actor.report_progress.remote(task_id, i + 1)

    # Report the final progress.
    progress_actor.report_progress.remote(task_id, num_samples)
    return num_inside


def main(args):
    t0 = time.time()
    if args.cluster_type == 'local':
        ray.init(num_cpus = args.n_workers)
    else:
        ray.init()

    # Change this to match your cluster scale.
    NUM_SAMPLING_TASKS = args.n_tasks if args.n_tasks > 0 else args.n_workers
    NUM_SAMPLES_PER_TASK = args.samples_per_task
    TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK

    # Create the progress actor.
    progress_actor = ProgressActor.remote(TOTAL_NUM_SAMPLES)

    # Create and execute all sampling tasks in parallel. This is equivalent to do the MAP step
    futures = [ sampling_task.remote(NUM_SAMPLES_PER_TASK, i, progress_actor) for i in range(NUM_SAMPLING_TASKS) ]

    # Query progress periodically.
    while True:
        progress = ray.get(progress_actor.get_progress.remote())
        print(f"Progress: {int(progress * 100)}%")
        if progress == 1: break
        time.sleep(1)

    # Get all the sampling tasks results. This is equivalent to the REDUCE step
    total_num_inside = sum(ray.get(futures)) # This call blocks until all the results are actually computed
    pi = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
    print(f"Estimated value of π is: {pi}  using a total of {time.time() - t0:.6f} seconds", end = ' ')
    print(f"(n_workers: {args.n_workers}, n_tasks: {args.n_tasks}, samples_per_task: {args.samples_per_task}, cluster-type: {args.cluster_type})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'pi.py',
                description = 'Computing an approximation to PI by means of Monte Carlo',
                epilog = 'That\'s all folks!!!')
    parser.add_argument('--n-workers',
                        dest = 'n_workers',
                        type = int,
                        default = 5,
                        help = 'Number of workers in the cluster'
    )
    parser.add_argument('--n-tasks',
                        dest = 'n_tasks',
                        type = int,
                        default = 0,
                        help = 'Number of tasks if different of the number of workers: 0 means to use number of workers'
    )
    parser.add_argument('--samples-per-task',
                        dest = 'samples_per_task',
                        type = int,
                        default = 1_000_000,
                        help = 'Number of samples per the task'
    )
    parser.add_argument('--cluster-type',
                        dest = 'cluster_type',
                        type = str,
                        default = 'local',
                        help = 'Cluster type to use. One of local, ssh and kubernetes'
    )

    main(parser.parse_args())
