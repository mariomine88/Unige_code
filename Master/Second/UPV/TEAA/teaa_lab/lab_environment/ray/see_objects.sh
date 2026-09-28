#!/bin/bash


for object in rayclusters pv pvc pods svc
do
    echo " "
    echo " "
    echo "================ ${object} ============"
    microk8s kubectl get ${object}
done

echo " "
echo " "
echo "================ describing ray cluster head ============"
microk8s kubectl describe svc ray-cluster-head
