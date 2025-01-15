## Cilium Lab Appendix 1: Other Useful Commands
The following commands can all be run from the rome:

1. Self explanatory Cilium BGP commands:
```
cilium bgp routes advertised ipv4 mpls_vpn 
cilium bgp routes available ipv4 mpls_vpn
cilium bgp routes available ipv4 unicast
cilium bgp routes available ipv6 unicast
```

2. Isovalent/Cilium/eBPF commands:

  Get VRF info:
  ```
  kubectl get isovalentvrf -o yaml
  ```

  Get SRv6 Egress Policy info (SRv6 L3VPN routing table):
  ```
  kubectl get IsovalentSRv6EgressPolicy
  kubectl get IsovalentSRv6EgressPolicy -o yaml
  ```
  Get detail on a specific entry:
  ```
  kubectl get IsovalentSRv6EgressPolicy bgp-control-plane-16bbd4214d4e691ddf412a6a078265de02d8cff5a3c4aa618712e8a1444477a9 -o yaml
  ```

  Get Cilium eBPF info for SID, VRF, and SRv6 Policy - note: first run kubectl get pods to get the cilium agent pod names:
  ```
  cisco@rome:~$ kubectl get pods -n kube-system
  NAME                                    READY   STATUS    RESTARTS      AGE
  cilium-zczvb                       1/1     Running   0          7h57m
  ```

  Then run cilium-dbg ebpf commands (Note: the cilium agent pod name is dynamic so you'll need to replace cilium-zczvb with the pod name from your Rome node):
  The first command outputs the nodes' local SID table
  The second command outputs the nodes' local VRF table
  The third command outputs a summary of the nodes' srv6 l3vpn routing table
  ```
  kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 sid
  kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 vrf
  kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 policy
  ```

  Example output:
  ```
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$   kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 sid
  Defaulted container "cilium-agent" out of: cilium-agent, config (init), mount-cgroup (init), apply-sysctl-overwrites (init), mount-bpf-fs (init), wait-for-node-init (init), clean-cilium-state (init), install-cni-binaries (init)
  SID                  VRF ID
  fc00:0:a061:e95c::   1000107
  fc00:0:a061:8edf::   1000010
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$   kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 vrf
  Defaulted container "cilium-agent" out of: cilium-agent, config (init), mount-cgroup (init), apply-sysctl-overwrites (init), mount-bpf-fs (init), wait-for-node-init (init), clean-cilium-state (init), install-cni-binaries (init)
  Source IP            Destination CIDR   VRF ID
  10.200.0.134         0.0.0.0/0          1000107
  10.200.0.175         0.0.0.0/0          1000107
  10.200.0.199         0.0.0.0/0          1000010
  2001:db8:200::17fb   0.0.0.0/0          1000107
  2001:db8:200::3a09   0.0.0.0/0          1000010
  2001:db8:200::3bdc   0.0.0.0/0          1000107
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$   kubectl exec -n kube-system cilium-zczvb -- cilium-dbg bpf srv6 policy
  Defaulted container "cilium-agent" out of: cilium-agent, config (init), mount-cgroup (init), apply-sysctl-overwrites (init), mount-bpf-fs (init), wait-for-node-init (init), clean-cilium-state (init), install-cni-binaries (init)
  VRF ID    Destination CIDR   SID
  1000010   10.200.0.0/24      fc00:0:a061:8edf::
  1000107   10.9.9.1/32        fc00:0:1111:e005::
  1000107   10.101.3.0/24      fc00:0:1111:e005::
  1000107   10.107.2.0/24      fc00:0:7777:e005::
  1000107   10.200.0.0/24      fc00:0:a061:e95c::
  1000107   40.0.0.0/24        fc00:0:7777:e005::
  1000107   50.0.0.0/24        fc00:0:7777:e005::
  ```

  Get Cilium global config:
  ```
  kubectl get configmap -n kube-system cilium-config -o yaml
  ```
