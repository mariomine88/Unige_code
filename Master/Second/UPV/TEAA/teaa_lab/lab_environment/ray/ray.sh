#!/bin/bash


#conda env create -f ray.yaml
#conda activate ray

pip install --upgrade  pip numpy scikit-learn matplotlib plotly pandas pyarrow
pip install --upgrade  ipywidgets jupyterlab-vim jupyter jupyter-server-proxy tqdm nodejs
pip install --upgrade  ray "ray[client]" "ray[data,train,tune,rllib]"  ipympl
