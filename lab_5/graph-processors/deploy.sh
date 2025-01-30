#!/bin/sh

kubectl apply -f igp-graph.yaml
sleep 5
kubectl apply -f ipv4-graph.yaml
sleep 5
kubectl apply -f ipv6-graph.yaml
sleep 5
kubectl apply -f srv6-localsids.yaml
