#!/bin/sh

kubectl delete -f linkstate-node-ext.yaml
kubectl delete -f linkstate-edge-v4.yaml
kubectl delete -f linkstate-edge-v6.yaml
kubectl delete -f ebgp-processor.yaml
kubectl delete -f ipv4-topology.yaml
kubectl delete -f ipv6-topology.yaml
kubectl delete -f srv6-localsids.yaml

