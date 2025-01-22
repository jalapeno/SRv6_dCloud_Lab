

# Lab 2: Base SRv6 Configuration and Validation [20 Min]

### Description: 
In Lab 2 the student will perform the basic ISIS and BGP SRv6 configuration on the lab routers.  

## Contents
- [Lab 2: Base SRv6 Configuration and Validation \[20 Min\]](#lab-2-base-srv6-configuration-and-validation-20-min)
    - [Description:](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Segment Routing Background](#segment-routing-background)
  - [SRv6](#srv6)
    - [SRv6 Configuration Steps](#srv6-configuration-steps)
      - [Configure SRv6 on xrd01](#configure-srv6-on-xrd01)
      - [Validate SRv6 configuration and reachability](#validate-srv6-configuration-and-reachability)
  - [End-to-End Connectivity](#end-to-end-connectivity)
    - [Viewing Router to Router traffic in containerlab](#viewing-router-to-router-traffic-in-containerlab)
  - [SRv6 Packet Walk](#srv6-packet-walk)
  - [End of Lab 2](#end-of-lab-2)
  

## Lab Objectives
The student upon completion of Lab 2 should have achieved the following objectives:

* Understanding baseline SRv6 configuration and validation for ISIS and BGP
* Validate SRv6 forwarding for BGP advertised prefixes
   

## Segment Routing Background

Segment Routing (SR) is a source-based routing architecture. A node chooses a path and steers a packet through the network via that path by inserting an ordered list of segments, instructing how subsequent nodes in the path that receive the packet should process it. This simplifies operations and reduces resource requirements in the network by removing network state from intermediary nodes as path information is encoded via the label stack or SRv6 SID(s) at the ingress node. Also, because the shortest-path segment includes all Equal-Cost Multi-Path (ECMP) paths to the related node, SR supports the ECMP nature of IP by design. 

For more information on SR and SRv6 the segment-routing.net site has a number of tutorials and links to other resources: 

[segment-routing.net](https://www.segment-routing.net/)  
  

## SRv6
Segment Routing over IPv6 (SRv6) extends Segment Routing support via the IPv6 data plane.

SRv6 introduces the Network Programming framework that enables a network operator or an application to specify a packet processing program by encoding a sequence of instructions in the IPv6 packet header. Each instruction is implemented on one or several nodes in the network and identified by an SRv6 Segment Identifier (SID) in the packet. 

In SRv6, the IPv6 destination address represents a set of one or more instructions. SRv6 uses a new type of IPv6 Routing Extension Header, called the Segment Routing Header (SRH), in order to encode an ordered list of instructions. The active segment is indicated by the destination address of the packet, and the next segment is indicated by a pointer in the SRH.

In our lab we will use SRv6 "micro segment" (SRv6 uSID or just "uSID" for short) instead of the full SRH. SRv6 uSID is a straightforward extension of the SRv6 Network Programming model.

With SRv6 uSID:

 - The outer IPv6 destination address becomes the uSID carrier with the first 32-bits representing the uSID block, and the 6 remaining 16-bit chunks of the address become uSIDs or instructions
 - The existing ISIS and BGP Control Plane is leveraged without any change
 - The SRH can be used if our uSID instruction set extends beyond the 6 available in the outer IPv6 destination address
 - SRv6 uSID is based on the Compressed SRv6 Segment List Encoding in SRH [I-D.ietf-spring-srv6-srh-compression] framework

For reference one of the most recent IOS-XR Configuration guides for SR/SRv6 and ISIS can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/24xx/configuration/guide/b-segment-routing-cg-cisco8000-24xx/configuring-segment-routing-over-ipv6-srv6-micro-sids.html)

SRv6 uSID locator and source address information for nodes in the lab:

| Router Name | Loopback Int|    Locator Prefix    |   Source-address    |                                           
|:------------|:-----------:|:--------------------:|:--------------------:|                          
| xrd01       | loopback 0  | fc00:0000:1111::/48  | fc00:0000:1111::1    |
| xrd02       | loopback 0  | fc00:0000:2222::/48  | fc00:0000:2222::1    |
| xrd03       | loopback 0  | fc00:0000:3333::/48  | fc00:0000:3333::1    |
| xrd04       | loopback 0  | fc00:0000:4444::/48  | fc00:0000:4444::1    |
| xrd05       | loopback 0  | fc00:0000:5555::/48  | fc00:0000:5555::1    |
| xrd06       | loopback 0  | fc00:0000:6666::/48  | fc00:0000:6666::1    |
| xrd07       | loopback 0  | fc00:0000:7777::/48  | fc00:0000:7777::1    |

    
### SRv6 Configuration Steps 

   - reference the above table
   - the source address should match the router's loopback0 ipv6 address
   - locator should match the first 48-bits of the router's loopback0
   - to keep things simple we're using the same locator name, 'MyLocator', on all nodes in the network.

#### Configure SRv6 on xrd01
1. SSH to xrd01 and enable SRv6 globally and define SRv6 locator and source address for outbound encapsulation 

    ```
    ssh cisco@clab-cleu25-xrd01
    ```
    ```
    conf t

    segment-routing
      srv6
        encapsulation
          source-address fc00:0000:1111::1
        locators
          locator MyLocator
            micro-segment behavior unode psp-usd
            prefix fc00:0000:1111::/48
       commit
    ```

2. Enable SRv6 for ISIS  
    ```
    router isis 100
      address-family ipv6 unicast
         segment-routing srv6
           locator MyLocator
       commit
    ```

3. Enable SRv6 for BGP 
    ```
    router bgp 65000
    address-family ipv4 unicast
      segment-routing srv6
      locator MyLocator
      !
    ! 
    address-family ipv6 unicast
      segment-routing srv6
      locator MyLocator
      !
    !
    neighbor-group xrd-ipv4-peer
      address-family ipv4 unicast
      !
    ! 
    neighbor-group xrd-ipv6-peer
      address-family ipv6 unicast
      !
    !
    commit
    ```

> [!NOTE]
> Once you've configured xrd01 using the above, please proceed to configure the remainder of the routers using the configs found in the *quick config document* [HERE](/lab_2/lab_2_quick_config.md) 

#### Validate SRv6 configuration and reachability

1. Validation commands
    ```
    show segment-routing srv6 sid
    ```
    ```diff
    RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
    Fri Dec 15 22:37:40.028 UTC

    *** Locator: 'MyLocator' *** 

    SID                         Behavior          Context                           Owner               State  RW
    --------------------------  ----------------  --------------------------------  ------------------  -----  --
    fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
    fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    +fc00:0:1111:e004::         uDT4              'default'                         bgp-65000           InUse  Y 
    +fc00:0:1111:e005::         uDT6              'default'                         bgp-65000           InUse  Y
    ```
> [!NOTE]
> The bottom two entries. These SIDs belong to BGP and represent End.DT behaviors. Any packet arriving with either of these SIDs as the outer IPv6 destination address will be decapsulated and then an LPM lookup in the global/default routing table will be performed on the inner destination address. More on this later in the *`SRv6 Packet Walk`* section.

2. Validate the SRv6 prefix-SID configuration. As example for xrd01 look for *SID value: fc00:0000:1111::*
    ```
    show isis segment-routing srv6 locators detail 
    ```

    ```
    RP/0/RP0/CPU0:xrd01#show isis segment-routing srv6 locators detail 

    IS-IS 100 SRv6 Locators
    Name                  ID       Algo  Prefix                    Status
    ------                ----     ----  ------                    ------
    MyLocator             1        0     fc00:0000:1111::/48       Active
    Advertised Level: level-1-2   
    Level: level-1      Metric: 1        Administrative Tag: 0         
    Level: level-2-only Metric: 1        Administrative Tag: 0         
    SID behavior: uN (PSP/USD)
    SID value:    fc00:0000:1111::                      <------------ HERE
    Block Length: 32, Node Length: 16, Func Length: 0, Args Length: 80
    ```

## End-to-End Connectivity

### Viewing Router to Router traffic in containerlab
In this lab we will make extensive use of tcpdump to look at traffic on routed links. Containerlab makes this a fairly easy process as the underlying router links run in Linux network namespaces. 

The command we will use for tcpdump is *sudo ip netns exec <network namespace> tcpdump -lni <interface name>*

There are two pieces of information we need to run a tcpdump command; the *network namespace* and *interface name*.

For a list of *network namespaces* use the below command on the *XRD VM*: 
```
sudo ip netns ls
```

Example:
```
cisco@xrd:~$ sudo ip netns ls 
clab-cleu25-xrd05 (id: 5)
clab-cleu25-xrd02 (id: 2)
clab-cleu25-xrd06 (id: 4)
clab-cleu25-xrd03 (id: 6)
clab-cleu25-xrd04 (id: 1)
clab-cleu25-xrd07 (id: 3)
clab-cleu25-xrd01 (id: 0)
```

For the list of *interface names* created in a *network namespace* use the following command(s):
```
sudo ip netns exec clab-cleu25-xrd01 ip link show
```

Example:
```diff
cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd01 ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
20: eth0@if21: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
    link/ether 02:42:0a:fe:fe:65 brd ff:ff:ff:ff:ff:ff link-netnsid 0
+27: Gi0-0-0-1@if26: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:03:1f:f2 brd ff:ff:ff:ff:ff:ff link-netns clab-cleu25-xrd02
33: Gi0-0-0-2@if32: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:eb:38:c7 brd ff:ff:ff:ff:ff:ff link-netns clab-cleu25-xrd05
44: Gi0-0-0-0@if6: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:8e:00:d8 brd ff:ff:ff:ff:ff:ff link-netnsid 0
46: Gi0-0-0-3@if5: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:a7:f8:f3 brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

Now that we have the network namespace and interface name we can run a tcpdump command. An example tcpdump command capturing traffic on xrd01 Gig0/0/0/1 would look like this:
```
sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-1
```

Examples:
```
cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-1
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on Gi0-0-0-1, link-type EN10MB (Ethernet), capture size 262144 bytes
16:52:42.426927 IP6 fc00:0:6666::1.59565 > fc00:0:1111::1.179: Flags [P.], seq 3163804341:3163804360, ack 1727025708, win 31875, length 19: BGP
16:52:42.628050 IP6 fc00:0:1111::1.179 > fc00:0:6666::1.59565: Flags [.], ack 19, win 31846, length 0
```

1. Optional: ssh to **xrd01** and run a ping to **xrd02** that will be captured by the tcpdump:
    ```
    ping fc00:0:2222::1
    or 
    ping 10.0.0.2
    ```

## SRv6 Packet Walk
This is an optional section of the lab where we expand on the routing table behaviours during forwarding operations. 
Please use this link for the packet walk. [Packet Walk](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_2/lab_2-packet-walk.md)

## End of Lab 2
Please proceed to [Lab 3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3/lab_3-guide.md)
