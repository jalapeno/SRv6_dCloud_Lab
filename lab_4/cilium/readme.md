1. Kubeadm init:
```
kubeadm init --config kubeadm-init.yaml
```

2. Add cilium helm repo
```
helm repo add isovalent https://helm.isovalent.com
```

3. Install Cilium 16.5 on Rome
```
helm install cilium isovalent/cilium --version 1.16.5  --namespace kube-system -f cilium-enterprise.yaml
```

1. Helm get values
```
helm get values cilium -n kube-system
```

1. Untaint cp node
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

1. verify daemonset
```
kubectl get ds cilium -n kube-system
```

1. Cilium config
```
kubectl apply -f bgp-config.yaml 
kubectl apply -f srv6-locator-pool.yaml 
kubectl apply -f vrf-carrots.yaml 
```

1. verify peers
```
cilium bgp peers
```

1. verify routes
Usage:
  cilium bgp routes <available | advertised> <afi> <safi> [vrouter <asn>] [peer|neighbor <address>] [flags]
```
cilium bgp routes available ipv4 mpls_vpn
cilium bgp routes advertised ipv4 mpls_vpn
cilium bgp routes available ipv6 unicast
cilium bgp routes advertised ipv6 unicast
```

1. verify sidmanager
``` 
kubectl get sidmanager -o custom-columns="NAME:.metadata.name,ALLOCATIONS:.spec.locatorAllocations"
```

pod ip address
```
kubectl get pod -n carrots carrots0 -o jsonpath="{.status.podIPs}"
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