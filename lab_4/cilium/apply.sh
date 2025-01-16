#! /bin/bash

kubectl apply -f bgp-cluster-config.yaml 
kubectl apply -f bgp-peer-config.yaml 
kubectl apply -f bgp-vrf-config.yaml 
kubectl apply -f bgp-locator-advert-config.yaml 
kubectl apply -f srv6-locator-pool.yaml 
kubectl apply -f vrf-carrots.yaml 
