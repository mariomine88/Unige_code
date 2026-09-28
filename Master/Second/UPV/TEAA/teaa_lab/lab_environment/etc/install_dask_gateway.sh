#!/bin/bash

RELEASE=dask-gateway
NAMESPACE=dask-gateway

sudo microk8s helm upgrade $RELEASE dask-gateway \
    --repo=https://helm.dask.org \
    --install \
    --namespace $NAMESPACE \
    --values dask-gateway-config.yaml

