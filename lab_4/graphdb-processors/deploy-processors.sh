#/bin/sh

kubectl apply -f linkstate-node-ext.yaml
sleep 2

kubectl apply -f linkstate-edge-v4.yaml
kubectl apply -f linkstate-edge-v6.yaml
sleep 2

kubectl apply -f ebgp-processor.yaml
sleep 2

kubectl apply -f ipv4-topology.yaml
kubectl apply -f ipv6-topology.yaml

