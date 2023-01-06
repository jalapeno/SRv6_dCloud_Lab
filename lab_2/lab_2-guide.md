# Extend Topology + SR-MPLS Lab 2 Guide

### Description: 
In Lab 2 the student will extend the routing topology to include sites Amsterdam and Rome. In addition SR-MPLS will be used to create a baseline end to end routing between the two locations. With SR-MPLS the student will then use show commands and tools like TCPDump to validate how traffic is routed through the neetwork. This is important as Lab 3 will override this behaviour when the student implements SRv6 L3VPN with path selection.


## Contents
1. [Lab Objectives](#lab-objectives)
2. [Learn Default ISIS Path](#learn-default-isis-path)
3. [SR-MPLS Network Routing](#sr-mpls-network-routing)
    - [Configure Remote Networks](#configure-remote-test-networks)
    - [Add networks to ISIS](#add-networks-to-isis)
    - [Validate ISIS reachability](#validate-isis-reachability)
4. [Configure SRv6 Steering Policy](#configure-srv6-steering-policy)
    - [Slow Path Policy](#slow-path-policy)
    - [Fast Path Policy](#fast-path-policy)
5. [Validate End to End TE](#validate-end-to-end-te)
  

## Lab Objectives
The student upon completion of Lab 2 should have achieved the following objectives:

* Understanding of ISIS routing policy
* Enable network routing for SR-MPLS
* End to end routing between Amsterdam and Rome
* Diagnostic tools to validate path routing


## Learn Default ISIS Path

ISIS is the underlying IGP in this lab and you validated in Lab 1 reachability between xrd routers. Now we want you to work on validate traffic routing behavior for the default ISIS and SR-MPLS so that we can compare and contrast with SRv6 when implemented in Lab 3. Throughout this lab we will be creating traffic flows. For easy of understand flows will be generated from the Amsterdam  and traveling to networks in Rome. 

In referencing the ISIS topology diagram below we will check examine the routing table on xrd01.

![ISIS Topology](/topo_drawings/isis-ecmp-medium.png)

What we are looking for is xrd07 route 10.0.0.7/32 (Lo0) advertised through ISIS. Seeing the routing table below you will see that xrd01 has two ECMP equal cost paths to both next hops xrd02 and xrd05. So for normal flows traffic passing through xrd01 for networks sourced from xrd07 will get ECMP hashed. In the below command output you can see the two next hop routes installed into the routing table.

```
    RP/0/RP0/CPU0:xrd01#show ip route 10.0.0.7/32

    Routing entry for 10.0.0.7/32
    Known via "isis 100", distance 115, metric 3, type level-2
    Installed Jan  4 22:55:32.815 for 01:35:37
    Routing Descriptor Blocks
        10.1.1.1, from 10.0.0.7, via GigabitEthernet0/0/0/1, Protected, ECMP-Backup (Local-LFA)
        Route metric is 3
        10.1.1.9, from 10.0.0.7, via GigabitEthernet0/0/0/2, Protected, ECMP-Backup (Local-LFA)
        Route metric is 3
```

## SR-MPLS Network Routing
First we are going to need networks that are advertised through SR-MPLS over the top of ISIS. In the next few steps you will quickly bring up and add in network 20.0.0./24 to the topology and validate end to end connectivity. This will be our baseline path to compare and contrast with SRv6

### Configure Remote Test Networks
The location Rome has the network 20.0.0.0/24 which we will advertise into SR-MPLS on router xrd07. First 


![SR-MPLS Topology](/topo_drawings/sr-mpls-medium.png)

### Add Networks to ISIS


### Validate ISIS reachability


## Configure SRv6 Steering Policy

### Slow Path Policy


### Fast Path Policy


## Validate End to End TE






### End of lab 2
Please proceed to [lab_3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3)