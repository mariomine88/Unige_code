import os
import sys
import time
import json
import dask
from dask.distributed import LocalCluster, SSHCluster, Client
from dask_kubernetes.operator import KubeCluster, make_cluster_spec
from dask_kubernetes.operator.kubecluster.kubecluster import CreateMode


def create_cluster(n_workers = 1, threads_per_worker = 1, cluster_type = 'local', connect_only = True):

    #image = 'ghcr.io/dask/dask:latest'
    image = 'docker.io/jonander/teaa:test4'

    # Preparing the configuration for Kubernetes
    config = {
        "name": "testing2",
        "n_workers": n_workers,
        "image" : image,
        "resources": {
                        "requests":  {"cpu": "1", "memory": "6Gi"},
                        "limits":  {"cpu": "1", "memory": "6Gi"}
                    }
    }
    cluster_spec = make_cluster_spec(**config)
    #cluster_spec['spec']['worker']['spec']['containers'][0]['image'] = image
    cluster_spec['spec']['worker']['spec']['containers'][0]['volumeMounts'] = [{'mountPath': '/data', 'name': 'teaa-data', 'mountOptions': 'ro'}]
    cluster_spec['spec']['worker']['spec']['volumes'] = [{'name': 'teaa-data',
                                                          'mountOptions': ['hard', 'nfsvers=4.2', 'type=nfs4'],
                                                          'nfs': {'server': '192.168.1.1', 'path': '/bigdata/disk/teaa' , 'readOnly': True}}]
    with open('cluster-spec.json', 'wt') as f:
        print(json.dumps(cluster_spec, indent = 4), file = f)
        f.close()

    # Preparing the list of hosts for SSH clusters
    list_of_hosts = list()
    list_of_hosts.append('192.168.1.1') # the one that playes the role of scheduler
    for i in range(5):
        list_of_hosts.append(f'192.168.1.{2 * i + 1}') # the physical nodes that will run the worker instances
    
    if cluster_type == 'local':
        cluster = LocalCluster(name="my-dask-cluster", n_workers = n_workers, threads_per_worker = threads_per_worker) # 16 // n_workers)
    elif cluster_type == 'ssh':
        cluster = SSHCluster(hosts = list_of_hosts,
                                connect_options = {'preferred_auth': 'publickey', 'known_hosts': None},
                                worker_options = {'n_workers': n_workers, 'nthreads': threads_per_worker}, #, 'memory_limit': f'10GB' },
                                scheduler_options = {'port': 0, 'dashboard_address': ':8797' }
                            )
        cluster.scale(n_workers)
    elif cluster_type == 'kubernetes':
        cluster = KubeCluster(custom_cluster_spec = cluster_spec, shutdown_on_close = False)
                                #create_mode = CreateMode.CONNECT_ONLY if connect_only else CreateMode.CREATE_OR_CONNECT,
        #cluster.adapt(minimum = n_workers, maximum = n_workers + 10)
    else:
        raise Exception(f"cluster type {cluster_type} not recognized!")
    #
    return cluster


if __name__ == '__main__':
    #freeze_support()
    cluster = create_cluster(n_workers = 5, cluster_type = 'local', connect_only = False)
    client = cluster.get_client()
    client.submit(lambda: 1 + 1)
    print(cluster)
    print(client)
    print()
    #
    for path in ['/etc/resolv.conf',
                 '/bigdata',
                 '/bigdata/disk',
                 '/bigdata/disk/teaa',
                 '/bigdata/disk/teaa/synthetic_data',
                 '/bigdata/disk/teaa/synthetic_data/parquet.train/',
                 '/bigdata/disk/teaa/synthetic_data/parquet.test/',
                 '/bigdata/disk/teaa/synthetic_data/parquet.train/part.0.parquet',
                 '/bigdata/disk/teaa/text/goodreads_reviews_dedup/',
                 '/bigdata/disk/teaa/text/goodreads_reviews_dedup/part_0000.json.gz',
                 '/data/',
                 '/data/synthetic_data/',
                 '/data/synthetic_data/parquet.train/',
                 '/data/synthetic_data/parquet.test/',
                 '/data/synthetic_data/parquet.test/part.0.parquet',
                 '/data/text/goodreads_reviews_dedup/part_0000.json.gz']:
        print(path)
        if os.path.exists(path):
            if os.path.isfile(path):
                print(f'    {path} exists, it size is {os.path.getsize(path)} bytes')
            elif os.path.isdir(path):
                print(f'    {path} exists, and it is a directory')
            else:
                print(f'    {path} exists, but I do not know what it is')
    print()
    #
    client.close()
    cluster.close()
