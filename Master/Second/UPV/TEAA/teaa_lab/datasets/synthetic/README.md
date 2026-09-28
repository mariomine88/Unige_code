# Synthetic dataset

This dataset was generated on purpose to test how Dask Local and 
Kubernetes Clusters could reduce the running times of both training 
and inferencing workloads on large enough datasets.

## Description of the samples

## How the dataset was generated

The code for generating this synthetic dataset can be seen in
[generate_synthetic_data.py](../../lab_synthetic_data/workspace/python/generate_synthetic_data.py)

In this code dataset is generated then stored in a Dask DataFrame and, finally, stored in [_parquet_](https://parquet.apache.org/) format.


