1. Kubeadm init:
```
kubeadm init --config kubeadm-init.yaml
```

2. Install Cilium 16.5 on Rome
```
helm install cilium isovalent/cilium --version 1.16.5  --namespace kube-system -f cilium-enterprise.yaml
```

3. Helm get values
```
helm get values cilium -n kube-system
```

4. Untaint cp node
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

5. verify daemonset
```
kubectl get ds cilium -n kube-system
```

6. Cilium config
```
kubectl apply -f bgp-config.yaml 
kubectl apply -f srv6-locator-pool.yaml 
kubectl apply -f vrf-carrots.yaml 
```

7. verify peers
```
cilium bgp peers
```

8. verify routes
Usage:
  cilium bgp routes <available | advertised> <afi> <safi> [vrouter <asn>] [peer|neighbor <address>] [flags]
```
cilium bgp routes available ipv4 mpls_vpn
cilium bgp routes advertised ipv4 mpls_vpn
```

1. verify sidmanager
``` 
kubectl get sidmanager -o custom-columns="NAME:.metadata.name,ALLOCATIONS:.spec.locatorAllocations"
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