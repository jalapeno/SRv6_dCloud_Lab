#! /bin/bash

kubectl apply -f bgp-config.yaml 
kubectl apply -f srv6-locator-pool.yaml 
kubectl apply -f vrf-carrots.yaml 
