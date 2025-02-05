# Lab 4: SRv6 for Kubernetes with Cilium [30 Min]

### Description
Now that we've established SRv6 L3VPNs across our network, we're going to transition from *router-based services* to *host-based services*. And our first step will be to enable SRv6 L3VPN for Kubernetes. The Berlin VM has had Kubernetes pre-installed and is running the *Cilium CNI* (Container Network Interface). In this lab we'll review some basic Kubernetes commands (kubectl) and then we'll setup Cilium BGP peering with our XRd route reflectors. After that we'll configure Cilium SRv6 SID manager and Locator pool. We'll then add a couple containers to our K8s cluster and join them to the carrots VRF.

> [!NOTE]
> This portion of the lab makes use of Cilium Enterprise, which is a licensed set of features. The Cilium SRv6 feature set is in Beta is not available in the open source version. If you are interested in SRv6 on Cilium or other Enterprise features, please contact the relevant Cisco Isovalent sales team.  

Isovalent has also published a number of labs covering a wide range of Cilium, Hubble, and Tetragon features here:

https://cilium.io/labs/

The original version of this lab was developed in partnership with Arkadiusz Kaliwoda, Cisco SE in EMEA SP

## Contents
- [Lab 4: SRv6 for Kubernetes with Cilium \[30 Min\]](#lab-4-srv6-for-kubernetes-with-cilium-30-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Verify pre-installed Cilium is running](#verify-pre-installed-cilium-is-running)
  - [Setup Cilium BGP Peering](#setup-cilium-bgp-peering)
    - [Cilium BGP CRD](#cilium-bgp-crd)
    - [Establish the Cilium BGP global and peer configurations](#establish-the-cilium-bgp-global-and-peer-configurations)
    - [Verify Cilium BGP peering](#verify-cilium-bgp-peering)
    - [Cilium BGP prefix advertisement](#cilium-bgp-prefix-advertisement)
    - [Create the carrots BGP VRF](#create-the-carrots-bgp-vrf)
  - [Cilium SRv6 SID Manager and Locators](#cilium-srv6-sid-manager-and-locators)
  - [Establish Cilium VRFs and Create Pods](#establish-cilium-vrfs-and-create-pods)
    - [Verify Cilium advertised L3vpn prefixes are reaching remote xrd nodes](#verify-cilium-advertised-l3vpn-prefixes-are-reaching-remote-xrd-nodes)
    - [Run a ping test!](#run-a-ping-test)
  - [Create a radish VRF and pod](#create-a-radish-vrf-and-pod)
  - [Lab 4 Appendix](#lab-4-appendix)
  - [End of lab 4](#end-of-lab-4)

## Lab Objectives
The student upon completion of Lab 3 should have achieved the following objectives:

* Understanding of Cilium networking for Kubernetes
* Understanding on how to configure BGP in Cilium
* Understanding on how to configure VRF in Cilium
* Understanding on how to configure SRv6 in Cilium

  
## Verify pre-installed Cilium is running

Kubernetes and Cilium Enterprise are pre-installed on the **Berlin** VM. All of the following steps are to be performed on the **Berlin** VM unless otherwise specified.

1. SSH into the Berlin VM and cd into the lab_4/cilium directory and check out the contents
   ```
   ssh cisco@198.18.128.104
   ```
   ```
   cd ~/SRv6_dCloud_Lab/lab_4/cilium/
   ```

2. Run a couple commands to verify the Cilium Installation

   Display Cilium pods:
   ```
   kubectl get pods -n kube-system
   ```
   The Cilium portion of the output should look someething like this:
   ```yaml
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$    kubectl get pods -n kube-system
   NAME                               READY   STATUS    RESTARTS   AGE
   cilium-envoy-p6pgd               1/1     Running   0          2m36s
   cilium-jbnmh                     1/1     Running   0          2m36s
   cilium-node-init-2m6j8           1/1     Running   0          2m36s
   cilium-operator-d6fc9cf7-7v2gt   1/1     Running   0          2m36s
   cilium-operator-d6fc9cf7-ns6mc   0/1     Pending   0          2m36s
   ```

  Notes on the pods:
  * `Cilium-envoy`: used as a host proxy for enforcing HTTP and other L7 policies as specified in network policies for the cluster. For further reading see: https://docs.cilium.io/en/latest/security/network/proxy/envoy/
  * `Cilium-node-init`: used to initialize the node and install the Cilium agent.
  * `Cilium-operator`: used to manage the Cilium agent on the node. The second operator pod is pending as its waiting for another node to join the cluster.
  * `Cilium-jbnmh`: is the Cilium agent on the node, and the element that will perform BGP peering and programming of eBPF SRv6 forwarding policies.


   Display Cilium DaemonSet status:
   ```
   kubectl get ds -n kube-system cilium
   ```
   The output should show a single Cilium DaemonSet (ds) available, example:
   ```
   cisco@berlin:~$   kubectl get ds -n kube-system cilium
   NAME     DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
   cilium   1         1         1       1            1           kubernetes.io/os=linux   94m
   ```
> [!NOTE]
> A Kubernetes DaemonSet is a feature that ensures a pod runs on all or some nodes in a Kubernetes cluster. DaemonSets are used to deploy background services, such as monitoring agents, network agents (such as Cilium/eBPF), log collectors, and storage volumes.

Now we're ready!

##  Setup Cilium BGP Peering
**Brief explanation of Kubernetes Custom Resource Definitions (CRDs)**

Per: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/

*A custom resource is an extension of the Kubernetes API that is not necessarily available in a default Kubernetes installation. It represents a customization of a particular Kubernetes installation. However, many core Kubernetes functions are now built using custom resources, making Kubernetes more modular.*

Said another way, CRDs enable us to add, update, or delete Kubernetes cluster elements and their configurations. The add/update/delete action might apply to the cluster as a whole, a node in the cluster, an aspect of cluster networking or the CNI (aka, the work we'll do in this lab), or any given element or set of elements within the cluster including pods, services, daemonsets, etc.

A CRD applied to a single element in the K8s cluster would be analogous to configuring BGP on a router. A CRD applied to multiple elements or cluster-wide would be analogous to adding BGP route-reflection to a network as a whole. 

CRDs come in YAML file format and in the next several sections of this lab we'll apply CRDs to the K8s cluster to setup Cilium BGP peering, establish Cilium SRv6 locator ranges, create VRFs, etc.

### Cilium BGP CRD

For the sake of simplicity in this lab we'll use iBGP peering between our Berlin K8s node and our route reflectors **xrd05** and **xrd06**. 

On Berlin VM change to the lab_4/cilium directory and check out the contents
   ```
   cd ~/SRv6_dCloud_Lab/lab_4/cilium/
   ls
   ```

   See the below output:
   * [01-bgp-cluster.yaml](cilium/01-bgp-cluster.yaml) - Cilium BGP global configuration
   * [02-bgp-peer.yaml](cilium/02-bgp-peer.yaml) - Cilium BGP peer address families and route policies
   * [03-bgp-node-override.yaml](cilium/03-bgp-node-override.yaml) - Cilium BGP node override; we use this to specify the BGP source address
   * [04-bgp-advert.yaml](cilium/04-bgp-advert.yaml) - Cilium BGP prefix advertisement(s), including SRv6 locator prefix(s)
   * [05-bgp-vrf.yaml](cilium/05-bgp-vrf.yaml) - Cilium BGP VRF configuration(s
   * [06-srv6-locator-pool.yaml](cilium/06-srv6-locator-pool.yaml) - Cilium SRv6 SID manager and Locator pool configuration
   * [07-vrf-carrots.yaml](cilium/07-vrf-carrots.yaml) - Cilium VRF 'carrots' configuration and pods


Here is a portion of our Cilium BGP configuration in CRD form and with notes:

```yaml
apiVersion: isovalent.com/v1alpha1
kind: IsovalentBGPClusterConfig  # the BGP cluster configuration CRD  
metadata:
  name: cilium-bgp 
spec:
  nodeSelector:
    matchLabels:
      kubernetes.io/hostname: berlin    # node to which this portion of config belongs
  bgpInstances:                         # the k8s cluster could have multiple BGP instances
  - name: "asn65000"                    # for simplicity we're using a single ASN end-to-end
    localASN: 65000
    peers:
    - name: "xrd05-rr"                  # base peering config
      peerASN: 65000                   
      peerAddress: fc00:0:5555::1       
      peerConfigRef:
        name: "cilium-peer"             # reference to additional peer config in another CRD
    - name: "xrd06-rr"
      peerASN: 65000
      peerAddress: fc00:0:6666::1
      peerConfigRef:
        name: "cilium-peer"
```

One of the great things about CRDs is you can combine all the configuration elements into a single file, or you can break it up into multiple files by configuration element: 

In the next few steps we'll walk through applying the configuration one element at a time. For reference the [99-cilium-all.yaml](cilium/99-cilium-all.yaml) file, would apply all the elements at once.

### Establish the Cilium BGP global and peer configurations

![Cilium SRv6 L3VPN](/topo_drawings/cilium-l3vpn-topology.png)

1. On the **Berlin** VM cd into the Lab 4 cilium directory and apply the *Cilium BGP Cluster Config CRD*. BGP Cluster config establishes our Cilium Node's BGP ASN and base BGP peering with the route reflectors **xrd05** and **xrd06**.
   ```
   cd ~/SRv6_dCloud_Lab/lab_4/cilium/
   kubectl apply -f 01-bgp-cluster.yaml
   ```

   Next: The *BGP Peer Config CRD* is where we control address families and other BGP peering or route policies on a per peer or peer-group basis.
   Here is a portion of the BGP Peer Config CRD with notes:
   ```yaml
   metadata:
     name: cilium-peer    # name of the peer-group
   spec:
     families:            # afi/safi address family combinations
       - afi: ipv6
         safi: unicast
         advertisements:
           matchLabels:
             advertise: "bgpv6unicast"   # advertise ipv6 prefixes found in the bgpv6unicast advertisement CR
       - afi: ipv4
         safi: mpls_vpn  # a bit of a misnomer, but we're advertising SRv6 L3VPN, or the equivalent of vpnv4 unicast in XR
   ```

2. Apply the Cilium BGP Peer Config CRD. 
   ```
   kubectl apply -f 02-bgp-peer.yaml
   ```

   Expected output for steps #1 and #2:
   ```
   isovalentbgpclusterconfig.isovalent.com/cilium-bgp created
   isovalentbgppeeringpolicy.isovalent.com/cilium-peer created
   ```
   At this point our peer sessions are not yet established. Next we'll apply the *`localAddress`* parameter which tells Cilium which source address to use for its BGP peering sessions. This knob is comparable to IOS-XR's `update-source` parameter.

   Here is a portion of the node override CRD with notes:
   ```yaml
    metadata:
      name: berlin     # this CRD will only apply to the berlin node
    spec:
      bgpInstances:
        - name: "asn65000"        # required field, must match the name of the bgpInstance in the cluster config
          srv6Responder: true     # instructs BGP to advertise the node's SRv6 Locator (to be created a few steps after this)
          peers:
            - name: "xrd05-rr"                 # must match the name of the peer in the cluster config
              localAddress: fc00:0:8888::1     # the source address to use for the peering session
   ```

4. Apply the node override CRD:
   ```
   kubectl apply -f 03-bgp-node-override.yaml
   ```

   Expected output:
   ```
   isovalentbgpnodeconfigoverride.isovalent.com/berlin created
   ```

### Verify Cilium BGP peering 

1. Verify Cilium BGP has successfully established peering sessions with **xrd05** and **xrd06** with the following cilium CLI. Note, it may take a few seconds for the peering sessions to establish.
   
   We will be using the below command to interact with the Cilium BGP process.
   ```
   cilium bgp peers
   ```

   We expect to have two IPv6 BGP peering sessions established and receiving BGP NLRIs for IPv6 and IPv4/mpls_vpn (aka, SRv6 L3VPN).

   Example:
   ```
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ cilium bgp peers
   Node     Local AS   Peer AS   Peer Address     Session State   Uptime   Family          Received   Advertised
   berlin   65000      65000     fc00:0:5555::1   established     9s       ipv6/unicast    5          0    
                                                                           ipv4/mpls_vpn   5          0    
            65000      65000     fc00:0:6666::1   established     24s      ipv6/unicast    5          0    
                                                                           ipv4/mpls_vpn   5          0  
   ```
   
   To list the additional cli options we will use the -h flag
   ```
   cilium bgp peers -h
   ```
   
### Cilium BGP prefix advertisement

We have not added IPv6 prefix advertisesments yet, hence a zero value in the Advertised output above. Also, **xrd05** and **xrd06**'s peering sessions with Cilium inherited the vpnv4 address family configuration during Lab 3 so we don't need to update their configs. 

Here is a portion of the prefix advertisement CRD with notes:
   ```yaml
    metadata:
      name: bgp-ipv6-unicast
      labels:
        advertise: bgpv6unicast     # this label will be used by the peer config CRD for prefixes to advertise
    spec:
      advertisements:                            # the list of elements to be advertised
        - advertisementType: "SRv6LocatorPool"   # advertise the SRv6 locator pool (to be created a few steps after this)
          selector:
            matchLabels:
              export: "pool0"
        - advertisementType: "PodCIDR"          # advertise the pod CIDR prefix for pods in the default VRF
   ```

1. Apply the BGP ipv6 unicast (global table/default VRF) prefix advertisement CRD:
   ```
   kubectl apply -f 04-bgp-advert.yaml
   ```

2. Verify the prefix advertisement (you should now see a 1 under the ipv6 unicast column):
   ```
   cilium bgp peers
   ```
   ```diff
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ cilium bgp peers
   Node     Local AS   Peer AS   Peer Address     Session State   Uptime   Family          Received   Advertised
   +berlin   65000      65000     fc00:0:5555::1   established     11m48s   ipv6/unicast    6          1
                                                                            ipv4/mpls_vpn   5          0
   +         65000      65000     fc00:0:6666::1   established     11m49s   ipv6/unicast    6          1
                                                                            ipv4/mpls_vpn   5          0
   ```                                                                         

3. Let's get a little more detail on advertised prefixes with the `cilium bgp routes` command. Let's first add a -h flag to see our options

   ```
   cilium bgp routes -h
   ```

   Example output:
   ```
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ cilium bgp routes -h
   Lists BGP routes from all nodes in the cluster - requires cilium >= v1.14.6

   Usage:
     cilium bgp routes <available | advertised> <afi> <safi> [vrouter <asn>] [peer|neighbor <address>] [flags]
   ```

4. Let's get the advertised prefixes:
   ```
   cilium bgp routes advertised ipv6 unicast
   ```

   Example output, as you can see we're currently only advertising the global table pod CIDR:
   ```
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ cilium bgp routes advertised ipv6 unicast
   Node     VRouter   Peer             Prefix             NextHop          Age   Attrs
   berlin   65000     fc00:0:5555::1   2001:db8:42::/64   fc00:0:8888::1   18s   [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:8888::1, NLRIs: [2001:db8:42::/64]}}]   
            65000     fc00:0:6666::1   2001:db8:42::/64   fc00:0:8888::1   18s   [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:8888::1, NLRIs: [2001:db8:42::/64]}}] 
   ```
> [!NOTE]
> The adverstised IPv6 network prefix is the assigned IPv6 used by Cilium on **Berlin**. In addtion the NextHop address listed in the above command lists the IPv6 interface address on the **Berlin** that connects to **xrd02** in the topology. You can see this detail if you run the command *ifconfig cilium_host* and *ifconfig ens192* respectively.

5. Validate that we see the route *2001:db8:42::/64* received on the XR routers. Lets log into **xrd01** and validate we have received the router for **Berlin** in the IPv6 bgp unicast table.
   
   On **xrd01** run the below command:
   ```
   show bgp ipv6 unicast 2001:db8:42::/64
   ```
   ```yaml
   RP/0/RP0/CPU0:xrd01#show bgp ipv6 unicast 2001:db8:42::/64
   Thu Jan 23 21:24:54.885 UTC
   BGP routing table entry for 2001:db8:42::/64
   Versions:
     Process           bRIB/RIB   SendTblVer
     Speaker                 43           43
   Last Modified: Jan 23 20:53:43.418 for 00:31:11
   Paths: (2 available, best #1)
     Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:8888::1 (metric 2) from fc00:0:5555::1 (198.18.4.104)
       Origin IGP, localpref 100, valid, internal, best, group-best
       Received Path ID 0, Local Path ID 1, version 43
       Originator: 198.18.4.104, Cluster list: 10.0.0.5
   Path #2: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:8888::1 (metric 2) from fc00:0:6666::1 (198.18.4.104)
         Origin IGP, localpref 100, valid, internal
         Received Path ID 0, Local Path ID 0, version 0
         Originator: 198.18.4.104, Cluster list: 10.0.0.6
   ```

### Create the carrots BGP VRF
We are now going to apply the BGP configuration for *vrf carrots* per the yaml file here: [05-bgp-vrf.yaml](cilium/05-bgp-vrf.yaml)

Earlier you saw we broke the BGP peering and route advertisement configurations into two separate yaml files. For the VRF we've got both in single file to illustrate the point about config modularity, and to also have one less step to apply. Here is a brief overview of the BGP VRF CRD:
  ```yaml
  ---
  apiVersion: isovalent.com/v1alpha1
  kind: IsovalentBGPVRFConfig      # the BGP VRF configuration CRD
  metadata:
    name: carrots-config   # a meta data label / name of the vrf config
  spec:
    families:
      - afi: ipv4        # the address family (AFI)
        safi: mpls_vpn   # the sub-address family (SAFI)
        advertisements:
          matchLabels:
            advertise: "bgp-carrots"  # a meta data label / name for the route advertisement - this is analogous to a outbound route policy

  ---
  apiVersion: isovalent.com/v1alpha1
  kind: IsovalentBGPAdvertisement      # BGP route advertisement CRD
  metadata:
    name: carrots-adverts     # a meta data label / name for the VRF route advertisement
    labels:
      advertise: bgp-carrots  # a meta data label / name for this particular advertisement
  spec:
    advertisements:
      - advertisementType: "PodCIDR"   # we're going to advertise the k8s pod CIDR or subnet
  ```

1. Apply the carrots BGP VRF configuration:
   ```
   kubectl apply -f 05-bgp-vrf.yaml
   ```

Our Cilium BGP configuration is now complete. Next we'll setup the Cilium SRv6 SID manager and locators.

## Cilium SRv6 SID Manager and Locators
Per Cilium Enterprise documentation:
*The SID Manager manages a cluster-wide pool of SRv6 locator prefixes. You can define a prefix pool using the IsovalentSRv6LocatorPool resource. The Cilium Operator assigns a locator for each node from this prefix.*

So essentially we're going to configure a /40 range from which Cilium will allocate a /48 bit uSID-based locator to each node in the K8s cluster.

Cilium also supports /64 locators, but for simplicity and consistency with our *xrd* nodes we're going to use the very commonly deployed /48 bit locators. Here is a portion of the yaml file CRD with notes:

   ```yaml
   behaviorType: uSID          # options are uSID or SRH
   prefix: fc00:0:A000::/40    # the larger /40 block from which a /48 would be allocated to each node in the cluster
   structure:
     locatorBlockLenBits: 32   # the uSID block length
     locatorNodeLenBits: 16    # the uSID node length - here 32 + 16 results in our /48 bit Locator
   ```

1. Define and apply a Cilium SRv6 locator pool. The full CRD may be reviewed here: [06-srv6-locator-pool.yaml](cilium/06-srv6-locator-pool.yaml)
  
   ```
   kubectl apply -f 06-srv6-locator-pool.yaml
   ```

   Recall the BGP prefix advertisement CRD included a spec for advertising the SRv6 locator pool as well:
   ```yaml
     advertisements:
       - advertisementType: "SRv6LocatorPool"  
         selector:
           matchLabels:
             export: "pool0"
   ```

2. Now that we have a local pool to advertise, let's check our BGP advertised prefixes again:
   ```
   cilium bgp routes advertised ipv6 unicast
   ```

   Example output, Cilium is now advertising the node's Locator...but only to one neighbor (see note below):
   ```yaml
   Node     VRouter   Peer             Prefix             NextHop          Age     Attrs
   berlin   65000     fc00:0:5555::1   2001:db8:42::/64   fc00:0:8888::1   2m52s   [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:8888::1, NLRIs: [2001:db8:42::/64]}}]   
            65000     fc00:0:6666::1   2001:db8:42::/64   fc00:0:8888::1   2m52s   [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:8888::1, NLRIs: [2001:db8:42::/64]}}]   
     --->   65000     fc00:0:6666::1   fc00:0:a01f::/48   fc00:0:8888::1   6s      [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:8888::1, NLRIs: [fc00:0:a01f::/48]}}] 
   ```

> [!IMPORTANT]
> The Cilium image we are currently using has a bug where the SRv6 locator is only advertised to one neighbor. A fix is being incorporated in the 1.18 release.

3. Now that we've created locator pool, let's validate it:
   ```
   kubectl get sidmanager -o yaml
   ```
   
   Or for a more concise output:
   ```
   kubectl get sidmanager -o custom-columns="NAME:.metadata.name,ALLOCATIONS:.spec.locatorAllocations"
   ```

   The truncated output below shows Cilium having allocated the following Locator to Berlin:
   **berlin: fc00:0:a0ba::/48**

   Example output:

   ```yaml
   apiVersion: v1
   items:
   - apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6SIDManager
    metadata:
      name: berlin
      resourceVersion: "48034"
      uid: dd82d5d0-6d84-4cc8-ac31-ed2f3ce857f7
    spec:
      locatorAllocations:
      - locators:
        - behaviorType: uSID
          prefix: fc00:0:a01f::/48               # Berlin's dynamically allocated uSID prefix (Locator)
          structure:
            argumentLenBits: 0
            functionLenBits: 16
            locatorBlockLenBits: 32
            locatorNodeLenBits: 16
        poolRef: pool0
   ```

## Establish Cilium VRFs and Create Pods

In the next step we've combined creation of both the *carrots* VRF and kubernetes namespace, and we've included a couple CRDs to spin up a couple Alpine linux container pods in the VRF/namespace. The goal is to create a forwarding policy so that packets from our container get placed into the *carrots* vrf and then encapsulated in an SRv6 header as detailed in the below diagram.

![Cilium SRv6 L3VPN](/topo_drawings/cilium-packet-forwarding.png)

A brief explanation of the VRF and pods CRD:
```yaml
---
apiVersion: v1
kind: Namespace   # we're creating a new k8s namespace
metadata:
  name: veggies   # called veggies
  labels:
    name: veggies

---
apiVersion: isovalent.com/v1alpha1
kind: IsovalentVRF         # VRF CRD - analogous to the global VRF config on a router
metadata:
  name: carrots
spec:
  vrfID: 99                  # the VRF ID - analogous to the Route Distinguisher on a router
  locatorPoolRef: pool0       # use our previously created locator pool
  rules:
  - selectors:
    - endpointSelector:
        matchLabels:
          vrf: carrots    # analogous to the RT import/export policy on a router
    destinationCIDRs:
    - 0.0.0.0/0

---
apiVersion: v1
kind: Pod   # we're creating a new k8s pod
metadata:
  namespace: veggies   # the pod is in the veggies namespace
  labels:
    app: alpine-ping
    vrf: carrots   # the pod is in the carrots VRF
  name: carrots0   # the pod's name
spec:
  containers:
  - image: alpine:latest   # the pod's image
    imagePullPolicy: IfNotPresent
    name: carrots0
    command:
      - /bin/sh
      - "-c"
      - "sleep 60m"
```

You'll note that the pod is in the *carrots VRF* and the K8s namespace *veggies*. We didn't do this to be overly complext, but rather to illustrate the fact that the namespace and VRF are independent of each other. We could have pods from multiple namespaces in the same VRF and vice versa.

1. Add VRF, namespace, and pods:
   [07-vrf-carrots.yaml](cilium/07-vrf-carrots.yaml)
   ```
   kubectl apply -f 07-vrf-carrots.yaml
   ```

2. Verify the VRF carrots pods are running:
   ```
   kubectl get pods -n veggies
   ```

   Expected output:
   ```
   NAME      READY   STATUS    RESTARTS   AGE
   carrots0   1/1     Running   0          10s
   carrots1   1/1     Running   0          10s
   ``` 

3. Let's get the pods' IP addresses as we'll need them in a few more steps:
   ```
   kubectl get pod -n veggies carrots0 -o jsonpath="{.status.podIPs}" && echo
   kubectl get pod -n veggies carrots1 -o jsonpath="{.status.podIPs}" && echo
   ```

   Expected output should look something like:
   ```
   [{"ip":"10.200.0.242"},{"ip":"2001:db8:42::2131"}]
   [{"ip":"10.200.0.3"},{"ip":"2001:db8:42::dad9"}]
   ```

4. Next we'll verify Cilium has allocated the carrots VRF a SRv6 L3VPN uDT4 SID on Berlin:
   ```
   kubectl get sidmanager berlin -o yaml
   ```

    Example output from sidmanager:
    ```diff
    apiVersion: isovalent.com/v1alpha1
    kind: IsovalentSRv6SIDManager
    metadata:
      creationTimestamp: "2025-01-16T22:16:38Z"
      generation: 3
      name: berlin
      resourceVersion: "49944"
      uid: d0f2730f-ffe9-4282-b457-01ed94b16307
    spec:
      locatorAllocations:
      - locators:
        - behaviorType: uSID
    +     prefix: fc00:0:a0ba::/48     # Berlin's dynamically allocated uSID prefix (Locator)
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
    +   - behavior: uDT4                # uDT4 is uSID 'End' with IPv4 table lookup behavior
          behaviorType: uSID
    +     metadata: carrots             # table to perform the lookup in
          owner: srv6-manager
          sid:
    +       addr: 'fc00:0:a0ba:ec7::'   # Berlin VRF carrots SRv6 Locator + uDT4 Function (ec7)
            structure:
              argumentLenBits: 0
              functionLenBits: 16
              locatorBlockLenBits: 32
              locatorNodeLenBits: 16
    ```

### Verify Cilium advertised L3vpn prefixes are reaching remote xrd nodes

1. On the xrd VM ssh to **xrd01** and run some BGP verification commands.
   ```
   ssh cisco@clab-cleu25-xrd01
   ```
   ```
   show bgp vpnv4 unicast
   show bgp vpnv4 unicast rd 9:9 10.200.0.0/24
   ```

   Somewhere in the output of the first command we expect to find the Cilium advertised L3VPN prefix:
   ```
   *>i10.200.0.0/24      fc00:0:8888::1                100      0 ?
   ```

   In the output of the second command we expect to see detailed information. Here is truncated output:
   ```diff
   Path #1: Received by speaker
   Not advertised to any peer
   Local
       fc00:0:8888::1 (metric 2) from fc00:0:5555::1 (198.18.4.104)
   +     Received Label 0xec70      # uDT4 function bits (ec7) match the SRv6 SID manager output from Cilium
         Origin incomplete, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
         Received Path ID 0, Local Path ID 1, version 20
         Extended community: RT:9:9
         Originator: 198.18.4.104, Cluster list: 10.0.0.5
       PSID-Type:L3, SubTLV Count:1
         SubTLV:
   +    T:1(Sid information), Sid:fc00:0:a0ba::(Transposed), Behavior:63, SS-TLV Count:1  # Sid value matches Berlin's SRv6 Locat
         SubSubTLV:
          T:1(Sid structure):
   ```

2. Back on the Berlin VM, verify SRv6 Egress Policies. This command will give you a rough equivalent to the SRv6 L3VPN FIB table
   ```
   kubectl get IsovalentSRv6EgressPolicy -o yaml
   ```

   Example of partial output:
   ```diff
     - apiVersion: isovalent.com/v1alpha1
       kind: IsovalentSRv6EgressPolicy
       metadata:
         creationTimestamp: "2025-01-17T06:49:36Z"
         generation: 1
         name: bgp-control-plane-31cc5366b9918e658bada220b4232aa252f16e3f93572d69131a842239bbcce5
         resourceVersion: "49954"
         uid: e47b55f9-095d-4b45-a163-522b8f7d6f9a
       spec:
         destinationCIDRs:
         - 40.0.0.0/24
   +     destinationSID: 'fc00:0:7777:e007::'  # SRv6 SID for prefix 40.0.0.0/24 in vrfID 99 (carrots) on xrd07
         vrfID: 99
     - apiVersion: isovalent.com/v1alpha1
       kind: IsovalentSRv6EgressPolicy
       metadata:
         creationTimestamp: "2025-01-17T06:49:36Z"
         generation: 1
         name: bgp-control-plane-46ef5ca48abb5cee93f383fe8966f85194a398116bea35fdf49b17cd1d5fbe79
         resourceVersion: "49948"
         uid: d786342b-9edd-4610-8f78-b11354714c6a
       spec:
         destinationCIDRs:
         - 10.200.0.0/24
   +     destinationSID: 'fc00:0:a0ba:ec7::' # SRv6 SID for local prefix 10.200.0.0/24 in vrfID 99 (carrots)
         vrfID: 99
   ```

### Run a ping test!

3. On the Berlin VM exec into one of the carrotspod containers and ping Amsterdam's interface in the carrots VRF:
    ```
    kubectl exec -it -n veggies carrots0 -- sh
    ```
    ```
    ping 10.101.3.1 -i .4 
    ```

4. Optional: return to the XRd VM and run a tcpdump to capture Cilium's SRv6 encapsulation of outbound packets:

    ```
    sudo ip netns exec clab-cleu25-xrd02 tcpdump -lni Gi0-0-0-3
    ```

    Example output:
    ```yaml
    08:25.416 IP6 fc00:0:8888:0:250:56ff:fe3f:ffff > fc00:0:1111:e008::: IP 10.200.0.242 > 10.101.3.1: ICMP echo request, id 14, seq 0, length 64
    08:25.419 IP6 fc00:0:1111::1 > fc00:0:a0ba:ec7::: IP 10.101.3.1 > 10.200.0.242: ICMP echo reply, id 14, seq 0, length 64
    08:26.416 IP6 fc00:0:8888:0:250:56ff:fe3f:ffff > fc00:0:1111:e008::: IP 10.200.0.242 > 10.101.3.1: ICMP echo request, id 14, seq 1, length 64
    08:26.419 IP6 fc00:0:1111::1 > fc00:0:a0ba:ec7::: IP 10.101.3.1 > 10.200.0.242: ICMP echo reply, id 14, seq 1, length 64
    ```

## Create a radish VRF and pod
In lab 3 we created the *radish VRF* on *xrd07* and bound a loopback interface to it. Then we redistributed VRF radish's *connected* routes. Now we'll create a radish VRF and pod in Cilium.

1. Exit from the carrots pod if you haven't already and apply the radish VRF yaml file:
   [08-vrf-radish.yaml](cilium/08-vrf-radish.yaml)
   ```
   kubectl apply -f 08-vrf-radish.yaml
   ```
  
   Expected output:
   ```
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$    kubectl apply -f 08-vrf-radish.yaml
   isovalentbgpvrfconfig.isovalent.com/radish-config created
   isovalentbgpadvertisement.isovalent.com/radish-adverts created
   isovalentvrf.isovalent.com/radish created
   pod/radish0 created
   ```

2. Verify the radish0 pod is running in the K8s veggies namespace:
   ```
   kubectl get pods -n veggies
   ```

   Expected output:
   ```
   NAME       READY   STATUS    RESTARTS   AGE
   carrots0   1/1     Running   0          8m3s
   carrots1   1/1     Running   0          8m3s
   radish0    1/1     Running   0          103s
   ```

3. Let's exec into the radish0 pod and run a ping!

    ```
    kubectl exec -it -n veggies radish0 -- /bin/sh
    ```
    ```
    ping 100.0.7.1 -i .4
    ```

    Expected output:
    ```
    cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl exec -it -n veggies radish0 -- /bin/sh
    / # ping 100.0.7.1
    PING 100.0.7.1 (100.0.7.1): 56 data bytes
    64 bytes from 100.0.7.1: seq=0 ttl=253 time=4.373 ms
    64 bytes from 100.0.7.1: seq=1 ttl=253 time=3.924 ms
    64 bytes from 100.0.7.1: seq=2 ttl=253 time=4.759 ms
    64 bytes from 100.0.7.1: seq=3 ttl=253 time=4.295 ms
    ```
3. Return to the XRd VM and run a tcpdump to capture Cilium's SRv6 encapsulation of outbound packets:

    ```
    sudo ip netns exec clab-cleu25-xrd02 tcpdump -lni Gi0-0-0-3
    ```

    Example output:
    ```yaml
    16:08:24.320379 IP6 fc00:0:8888:0:250:56ff:fe3f:ffff > fc00:0:7777:e004::: IP 10.200.0.133 > 100.0.7.1: ICMP echo request, id 15, seq 0, length 64
    16:08:24.720482 IP6 fc00:0:8888:0:250:56ff:fe3f:ffff > fc00:0:7777:e004::: IP 10.200.0.133 > 100.0.7.1: ICMP echo request, id 15, seq 1, length 64
    ```
4. Next, to demonstrate the flexibility of Cilium's SRv6 implementation, we'll switch the carrots1 pod from the carrots VRF to the radish VRF and run a ping again:

   ```
   kubectl apply -f 09-carrot-to-radish.yaml
   ```

5. Verify carrots1 is now in the radish VRF:
   ```
   kubectl describe pod -n veggies carrots1 | more
   ```

   Expected output:
   ```diff
   cisco@berlin:~/SRv6_dCloud_Lab/lab_4/cilium$ kubectl describe pod -n veggies carrots1
   +   Name:             carrots1
   Namespace:        veggies
   Priority:         0
   Service Account:  default
   Node:             berlin/198.18.4.104
   Start Time:       Wed, 22 Jan 2025 02:19:34 -0500
   Labels:           app=alpine-ping
   +                 vrf=radish                            # carrots1 is now in the radish VRF
   Annotations:      <none>
   Status:           Running
   IP:               10.200.0.164
   IPs:
        IP:  10.200.0.164
        IP:  2001:db8:42::d582
   ```

> [!NOTE]
> In a future version of this lab we hope to add support for Cilium SRv6-TE. 

## Lab 4 Appendix
We have provided some additional cilium and kubernetes commands in an appendix: [Lab 4 Appendix](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-appendix.md)

## End of lab 4
Please proceed to [Lab 5](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_5/lab_5-guide.md)

