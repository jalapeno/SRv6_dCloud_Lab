#!/bin/sh

kubectl delete -f igp-graph.yaml
kubectl delete -f ipv4-graph.yaml
kubectl delete -f ipv6-graph.yaml
kubectl delete -f srv6-localsids.yaml
