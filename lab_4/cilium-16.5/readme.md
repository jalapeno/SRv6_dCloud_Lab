Kubeadm init:
```
kubeadm init --config kubeadm-init.yaml
```

Install Cilium 16.5 on Rome

```
helm install cilium isovalent/cilium --version 1.16.5  --namespace kube-system -f cilium-enterprise.yaml
```

Uninstall
```
helm uninstall cilium -n kube-system
```

verify daemonset
```
kubectl get ds cilium -n kube-system
```
