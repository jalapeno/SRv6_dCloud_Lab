#! /bin/bash

kubectl delete -f 01-bgp-cluster.yaml 
kubectl delete -f 02-bgp-peer.yaml 
kubectl delete -f 03-bgp-node-override.yaml 
kubectl delete -f 04-bgp-advert.yaml 
kubectl delete -f 05-bgp-vrf.yaml 
kubectl delete -f 06-srv6-locator-pool.yaml 
kubectl delete -f 07-vrf-carrots.yaml 
