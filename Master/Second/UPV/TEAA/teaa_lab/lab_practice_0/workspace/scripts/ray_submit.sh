#!/bin/bash


RAY_IP_ADDR=$( microk8s kubectl describe svc ray-cluster-head | grep Endpoints | cut -f2 -d':' | tail -1 | awk '{ print $1 }')

ray job submit --address http://${RAY_IP_ADDR}:8265 --working-dir $(pwd) -- $*
