#!/bin/sh

kubectl apply -f igp-graph.yaml
kubectl apply -f ipv4-graph.yaml
kubectl apply -f ipv6-graph.yaml
kubectl apply -f srv6-localsids.yaml
