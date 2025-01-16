#! /bin/bash

kubectl apply -f 01-bgp-cluster.yaml 
kubectl apply -f 02-bgp-peer.yaml 
kubectl apply -f 03-bgp-node-override.yaml 
kubectl apply -f 04-bgp-advert.yaml 
kubectl apply -f 05-bgp-vrf.yaml 
kubectl apply -f 06-srv6-locator-pool.yaml 
kubectl apply -f 07-vrf-carrots.yaml 
