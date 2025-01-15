# Lab 4: SRv6 for Kubernetes with Cilium [25 Min]

### Description
Note: This portion of the lab makes use of Cilium Enterprise, which is a licensed set of features. The Cilium SRv6 feature set is not available in the open source version. If you are interested in SRv6 on Cilium or other Enterprise features, please contact the relevant Cisco Isovalent sales team.  

Isovalent has also published a number of labs covering a wide range of Cilium, Hubble, and Tetragon features here:

https://cilium.io/labs/

The original lab was developed in partnership with Arkadiusz Kaliwoda, Cisco SE in EMEA SP

### Contents
* Description [LINK](#description)
* Validate Cilium Run State [LINK](#validate-cilium-run-state)
* Setup Cilium BGP Peering [LINK](#setup-cilium-bgp-peering)
* Cilium SRv6 SID manager and Locators [LINK](#cilium-srv6-sid-manager-and-locators)
* Establish Cilium VRFs [LINK](#establish-cilium-vrfs)
* Setup Cilium SRv6 Responder [LINK](#setup-cilium-srv6-responder)

### Validate Cilium Run State

Kubernetes and Cilium Enterprise are pre-installed on the Rome VM. All of the following steps are to be performed on the Rome VM unless otherwise specified.

1. SSH into the Rome VM and cd into the lab_4/cilium directory and check out the contents
   ```
   ssh cisco@198.18.128.103
   cd ~/SRv6_dCloud_lab/lab_4/cilium/
   ```

2. Run a couple commands to verify the Cilium Installation

   Display Cilium DaemonSet status:
   ```
   kubectl get ds -n kube-system cilium
   ```
   The output should show a single Cilium DaemonSets (ds) available, example:
   ```
   cisco@rome:~$   kubectl get ds -n kube-system cilium
   NAME     DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
   cilium   1         1         1       1            1           kubernetes.io/os=linux   94m
   ```
> [!NOTE]
> A Kubernetes DaemonSet is a feature that ensures a pod runs on all or some nodes in a Kubernetes cluster. DaemonSets are used to deploy background services, such as monitoring agents, log collectors, and storage volumes.


##  Setup Cilium BGP Peering
First a brief explanation of *`Kubernetes Custom Resource Definitions (CRDs)`*. 

Per: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/

*A custom resource is an extension of the Kubernetes API that is not necessarily available in a default Kubernetes installation. It represents a customization of a particular Kubernetes installation. However, many core Kubernetes functions are now built using custom resources, making Kubernetes more modular.*

Said another way, CRDs enable us to add, update, or delete Kubernetes cluster elements and their configurations. The add/update/delete action might apply to the cluster as a whole, a node in the cluster, an aspect of cluster networking or the CNI (aka, the work we'll do in this lab), or any given element or set of elements within the cluster including pods, services, daemonsets, etc.

A CRD applied to a single element in the K8s cluster would be analogous configuring BGP on a router. A CRD applied to multiple or cluster-wide would be analogous to adding BGP route-reflection to a network as a whole. 

CRDs come in YAML file format and in the next several sections of this lab we'll apply CRDs to the K8s cluster to setup Cilium BGP peering, establish Cilium SRv6 locator ranges, create VRFs, etc.

For the sake of simplicity in this lab we'll use iBGP peering between our Rome K8s node and our route reflectors xrd05 and xrd06. 

Here is a partial Cilium iBGP CRD (aka iBGP configuration) with notes:
```yaml
apiVersion: "cilium.io/v2alpha1"
kind: CiliumBGPPeeringPolicy
metadata:
  name: rome
spec:
  nodeSelector:
    matchLabels:
      kubernetes.io/hostname: rome    <--- node to which this portion of config belongs
  virtualRouters:
  - localASN: 65000                 <--- Rome's BGP ASN
    exportPodCIDR: true             <--- advertise local PodCIDR prefix
    mapSRv6VRFs: true               <--- SRv6 L3VPN
    srv6LocatorPoolSelector:        
      matchLabels:
        export: "true"              <--- advertise Locator prefix into BGP IPv6 underlay
    neighbors:
    - peerAddress: "10.0.0.5/32"   <--- ipv4 peer address for xrd05
      peerASN: 65000
      families:                     <--- address families for this BGP session
       - afi: ipv4
         safi: unicast
    - peerAddress: "fc00:0:5555::1/128"   <--- ipv6 peer address for xrd05
      peerASN: 65000
      families:
        - afi: ipv6               <--- address families for this BGP session
          safi: unicast
        - afi: ipv4                
          safi: mpls_vpn          <--- L3VPN AFI/SAFI
          
```

You may review the entire Cilium iBGP policy yaml here: [Cilium BGP](cilium/bgp-policy.yaml). 
Note: we'll be enabling Cilium to peer over both ipv4 and ipv6 with exchange of vpnv4 prefixes over the IPv6 sessions. Also, xrd05 and xrd06's peering sessions with Cilium inherited the vpnv4 address family configuration in the previous lab exercies when we applied the address family to the neighbor-group. 

1. Apply the Cilium iBGP policy - On the k8s control plane vm cd into the cilium directory and apply the Cilium BGP CRD
```
cd SRv6_dCloud_Lab/lab_4/cilium/
kubectl apply -f bgp-policy.yaml
```

1. On Rome verify Cilium BGP peering with the following cilium CLI:
  ```
  cilium bgp peers
  ```

  We expect to a pair of IPv6 sessions established and with advertisement and receipt of BGP NLRIs for ipv6 and ipv4/mpls_vpn (aka, SRv6 L3VPN). Example:
  ```
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$ cilium bgp peers
  Node   Local AS   Peer AS   Peer Address     Session State   Uptime   Family          Received   Advertised
  rome   65000      65000     fc00:0:5555::1   established     2m58s    ipv6/unicast    5          1    
                                                                        ipv4/mpls_vpn   4          0    
        65000      65000     fc00:0:6666::1   established     53s       ipv6/unicast    5          1    
                                                                        ipv4/mpls_vpn   4          0   
  ```

## Cilium SRv6 SID Manager and Locators
Per Cilium Enterprise documentation:
*The SID Manager manages a cluster-wide pool of SRv6 locator prefixes. You can define a prefix pool using the IsovalentSRv6LocatorPool resource. The Cilium Operator assigns a locator for each node from this prefix. In this example we'll allocate /48 bit uSID based locators.*

1. Define and apply a Cilium SRv6 locator pool, example: [srv6-locator-pool.yaml](cilium/srv6-locator-pool.yaml)

  From the SRv6_dCloud_Lab/lab_4/cilium directory on the Rome VM:
  ```
  kubectl apply -f srv6-locator-pool.yaml
  ```

2. Validate locator pool
```
kubectl get sidmanager -o yaml
```
or 
```
kubectl get sidmanager -o custom-columns="NAME:.metadata.name,ALLOCATIONS:.spec.locatorAllocations"
```

  The example output below shows Cilium having allocated locator prefixes as follows:
  #### rome: fc00:0:a09f::/48


  We'll want to keep track of the allocated locator prefixes as we'll need to redistribute them from BGP into ISIS later in the lab.

  Example output:
  ```yaml
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl get sidmanager -o yaml
  apiVersion: v1
  items:
  - apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6SIDManager
    metadata:
      creationTimestamp: "2025-01-13T22:55:05Z"
      generation: 5
      name: rome
      resourceVersion: "48034"
      uid: dd82d5d0-6d84-4cc8-ac31-ed2f3ce857f7
    spec:
      locatorAllocations:
      - locators:
        - behaviorType: uSID
          prefix: fc00:0:a061::/48    <------ Rome's dynamically allocated uSID prefix (Locator)
          structure:
            argumentLenBits: 0
            functionLenBits: 16
            locatorBlockLenBits: 32
            locatorNodeLenBits: 16
        poolRef: pool0
    status:
      sidAllocations: []
  kind: List
  metadata:
    resourceVersion: ""
  ```

## Establish Cilium VRFs
1. Add vrf(s) - this example also adds a couple alpine linux container pods to vrf carrots:
   [vrf-carrots.yaml](cilium/vrf-carrots.yaml)
```
kubectl apply -f vrf-carrots.yaml
```

2. Verify the VRF carrots pods are running:
```
kubectl get pods -n carrots
```

3. Verify Cilium has allocated a uDT4 SRv6 L3VPN SID on Rome:
```
kubectl get sidmanager rome -o yaml
```

  Example output from sidmanager:
  ```yaml
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl get sidmanager rome -o yaml
  apiVersion: isovalent.com/v1alpha1
  kind: IsovalentSRv6SIDManager
  metadata:
    creationTimestamp: "2025-01-13T22:55:05Z"
    generation: 5
    name: rome
    resourceVersion: "48158"
    uid: dd82d5d0-6d84-4cc8-ac31-ed2f3ce857f7
  spec:
    locatorAllocations:
    - locators:
      - behaviorType: uSID
        prefix: fc00:0:a061::/48    <----- Rome SRv6 Locator
        structure:
          argumentLenBits: 0
          functionLenBits: 16
          locatorBlockLenBits: 32
          locatorNodeLenBits: 16
      poolRef: pool0
  status:
    sidAllocations:
    - poolRef: pool0
      sids:
      - behavior: uDT4        <------ uDT4 with looking in VRF carrots
        behaviorType: uSID
        metadata: carrots
        owner: srv6-manager
        sid:
          addr: 'fc00:0:a061:e95c::'  <------ VRF carrots uSID Locator + Function
          structure:
            argumentLenBits: 0
            functionLenBits: 16
            locatorBlockLenBits: 32
            locatorNodeLenBits: 16
  ```

### Verify Cilium advertised L3vpn prefixes are reaching remote xrd nodes

1. On the xrd VM ssh to xrd01 and run some BGP verification commands. Note, we expect to see vpnv4 prefixes advertise from Rome, but ping will not work yet. In a few more steps we'll setup the SRv6 responder on Rome and ping will work.
  ```
  ssh cisco@clab-cleu25-xrd01
  show bgp vpnv4 unicast
  show bgp vpnv4 unicast rd 9:9 10.200.0.0/24
  ```

### More SRv6 L3VPN on Rome

1. optional: create vrf-radish:
  ```
  kubectl apply -f vrf-radish.yaml
  ```

2.  Run some kubectl commands to verify pod status, etc.
  ```
  kubectl get pods -A
  ```

  ```
  kubectl describe pod -n carrots carrots0
  ```
  The kubectl get pods -A command should show a pair of carrots pods up and running.

3. We can also run a kubectl command with a filter to simplify to output and get the pod's IP addresses:
  ```
  kubectl get pod -n carrots carrots0 -o=jsonpath="{.status.podIPs}"
  ```
  example output:
  ```
  [{"ip":"10.200.0.134"},{"ip":"2001:db8:200::17fb"}]
  ```

4. Exec into one of the carrotspod containers and ping the Cilium CNI gateway:
  ```
  kubectl exec -it -n carrots carrots0 -- sh
  ip route
  ping <the "default via" address in ip route output>
  ```

  Output should look something like:
  ```
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl exec -it -n carrots carrots0 -- sh
  / # ip route
  default via 10.200.0.60 dev eth0 
  10.200.0.60 dev eth0 scope link 
  / # ping 10.200.0.60
  PING 10.200.0.60 (10.200.0.60): 56 data bytes
  64 bytes from 10.200.0.60: seq=0 ttl=63 time=0.175 ms
  64 bytes from 10.200.0.60: seq=1 ttl=63 time=0.132 ms
  ^C
  --- 10.200.0.60 ping statistics ---
  2 packets transmitted, 2 packets received, 0% packet loss
  round-trip min/avg/max = 0.132/0.153/0.175 ms
  / # 
  ```

5. Exit the pod
```
exit
```

## Setup Cilium SRv6 Responder

1. Per the previous set of steps, once allocated SIDs appear, we need to annotate the node. This will tell Cilium to program eBPF egress policies on Rome: 
  ```
  kubectl annotate --overwrite nodes rome cilium.io/bgp-virtual-router.65000="router-id=10.107.1.1,srv6-responder=true"
  ```

2. Verify SRv6 Egress Policies:
  ```
  kubectl get IsovalentSRv6EgressPolicy -o yaml
  ```

  Example of partial output:
  ```yaml
  cisco@rome:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl get IsovalentSRv6EgressPolicy -o yaml

  apiVersion: v1
  items:
  - apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6EgressPolicy
    metadata:
      creationTimestamp: "2025-01-14T04:31:12Z"
      generation: 1
      name: bgp-control-plane-5587f17711c26c64d70cc0459d9183e37edf0ffce52f7e256e83da51175007da
      resourceVersion: "50187"
      uid: 0ba02fab-8a2e-40cd-aba1-f6944608a8f6
    spec:
      destinationCIDRs:
      - 40.0.0.0/24                          <---- destination prefix in VRF carrots (vrfID 1000107)
      destinationSID: 'fc00:0:7777:e005::'   <---- prefix is reachable via xrd07. Cilium/eBPF will encapsulate traffic using this SID
      vrfID: 1000107

  - apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6EgressPolicy
    metadata:
      creationTimestamp: "2025-01-14T04:31:12Z"
      generation: 1
      name: bgp-control-plane-ae23b020354bc6b90c24ac9b0fe096c9245446b1c288a7898c3aec23beb6726e
      resourceVersion: "50188"
      uid: fc2bb8eb-1178-4d5c-843a-1c25b07a885e
    spec:
      destinationCIDRs:
      - 10.101.3.0/24                         <---- destination prefix in VRF carrots (vrfID 100107)
      destinationSID: 'fc00:0:1111:e005::'    <---- prefix is reachable via xrd01. Cilium/eBPF will encapsulate traffic using this SID
      vrfID: 1000107
  - apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6EgressPolicy
    metadata:
      creationTimestamp: "2025-01-14T04:31:12Z"
      generation: 1
      name: bgp-control-plane-bf38e639ce6f64092a863f29f73d43ee1dd48179000b1a1598073f83c8c0ec31
      resourceVersion: "50190"
      uid: 46f84a6e-6732-4179-ad2d-ac449404efd8
    spec:
      destinationCIDRs:
      - 10.200.0.0/24                         <---- local containers prefix in VRF carrots (vrfID 100107)
      destinationSID: 'fc00:0:a061:e95c::'    <---- prefix is advertised with this LVPN SRv6 SID
      vrfID: 1000107
  ```
** ADD END TO END PING TEST **

** ADD TCPDUMP OF SRV6 ENCAP **

Note: In a future version of this lab we hope to program SRv6 routes/policies using a K8s CNI dataplane such as eBPF (example: [Cilium support for SRv6](https://cilium.io/industries/telcos-datacenters/)). 

### Lab 4 Appendix
We have provided some additional cilium and kubernetes commands in an appendix for you. [Lab 4 Appendix](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-appendix.md)

### End of lab 4
Please proceed to [Lab 5](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_5/lab_5-guide.md)

