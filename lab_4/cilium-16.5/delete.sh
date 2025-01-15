#! /bin/bash

kubectl delete -f bgp-cluster-config.yaml 
kubectl delete -f bgp-peer-config.yaml 
kubectl delete -f bgp-vrf-config.yaml 
kubectl delete -f bgp-locator-advert-config.yaml 
kubectl delete -f srv6-locator-pool.yaml 
kubectl delete -f vrf-carrots.yaml 
