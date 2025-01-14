1. Kubeadm init:
```
kubeadm init --config kubeadm-init.yaml
```

2. Install Cilium 16.5 on Rome
```
helm install cilium isovalent/cilium --version 1.16.5  --namespace kube-system -f cilium-enterprise.yaml
```

3. Untaint cp node
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

4. verify daemonset
```
kubectl get ds cilium -n kube-system
```

5. Cilium config
```
kubectl apply -f bgp-cluster-config.yaml 
kubectl apply -f bgp-peer-config.yaml 
kubectl apply -f srv6-locator-pool.yaml 
kubectl apply -f bgp-locator-advert.yaml 
```




### appendix

1. Helm upgrade - if necessary
```
helm upgrade cilium isovalent/cilium --version 1.16.5  --namespace kube-system -f cilium-enterprise.yaml
```

2. Uninstall
```
helm uninstall cilium -n kube-system
```