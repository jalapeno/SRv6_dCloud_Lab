#/bin/sh

kubectl delete -f linkstate-node-ext.yaml
sleep 2

kubectl delete -f linkstate-edge-v4.yaml
kubectl delete -f linkstate-edge-v6.yaml
sleep 2

kubectl delete -f ebgp-processor.yaml
sleep 2

kubectl delete -f ipv4-topology.yaml
kubectl delete -f ipv6-topology.yaml

