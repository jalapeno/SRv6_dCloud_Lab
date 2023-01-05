# SRv6 Lab 2 Guide

### Description: 
In Lab 2 the student will baseline the  IPv4 and IPv6 routing behaviour as configured by the ISIS routing protocol. The student will see that the topology supports multiple ECMP paths across the topology. Next the student will using SRv6 to create two policy paths through the network: a slow-path and fast-path. We will add some new additional networks to the topology for testing. Finally we will link through SRv6 policy remote test network reachability to SRv6 paths and thereby create a deterministic data plane.

## Contents
1. [Lab Objectives](#lab-objectives)
2. [Learn Default ISIS Path](#learn-default-isis-path)
3. [Configure Explicit Path](#create-srv6-paths)
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
* How to create a SRv6 path policy
* How to create a SRv6 steering policy and link to a path policy
* How to test and validate SRv6 traffic flows

## Learn Default ISIS Path

Before starting down the path of creating SRv6 steering policy you need to understand the baseline routing within the lab to determine if your configurations later in Lab 2 are performing as configured. Throughout this lab we will be creating traffic flows. For easy of understand flows will be generated from the Amsterdam  and traveling to networks in Rome. 

In referencing the ISIS topology diagram below we will check examine the routing table on xrd01.

![ISIS Topology](/topo_drawings/isis-topolog-medium.png)

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

## Create SRv6 Paths


### Configure Remote Test Networks


### Add Networks to ISIS


### Validate ISIS reachability


## Configure SRv6 Steering Policy

### Slow Path Policy


### Fast Path Policy


## Validate End to End TE






### End of lab 2
Please proceed to [lab_3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3)