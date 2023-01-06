# Extend SR-MPLS Topology Lab 2 Guide

### Description: 
In Lab 2 the student will extend the routing topology to include sites Amsterdam and Rome. In addition SR-MPLS will be used to create a baseline end to end routing between the two locations. With SR-MPLS the student will then use show commands and tools like TCPDump to validate how traffic is routed through the neetwork. This is important as Lab 3 will override this behaviour when the student implements SRv6 L3VPN with path selection.


## Contents
1. [Lab Objectives](#lab-objectives)
2. [Learn Default ISIS Path](#learn-default-isis-path)
3. [SR-MPLS Network Routing](#sr-mpls-network-routing)
    - [Validate Local Network](#validate-local-networks)
    - [Enable BGP Labelled Unicast](#enable bgp-label-unicast)
    - [Validate BGP reachability](#validate-bgp-reachability)
4. [Validate End to End Connectivty](#validate-end-to-end-te)
  

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
For full size image see [LINK](/topo_drawings/isis-ecmp-large.png)

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
The location Rome has the network 20.0.0.0/24 which we will advertise into SR-MPLS on router xrd07. First log into xrd07 and validate that you can reach network 20.0.0.0/24 by pinging the ip address 20.0.0.1/24 in Rome. Once you have confirmed connectivity across the Rome metro link xrd07 gi 0/0/0/0 head to the next step.


![SR-MPLS Topology](/topo_drawings/sr-mpls-medium.png)
For full size image see [LINK](/topo_drawings/sr-mpls-large.png)

### Enable BGP Label Unicast
BGP Label Unicast (BGP-LU) is needed to advertise the label information we will need to enable SR-MPLS routing of our desired network traffic 20.0.0.0/24. First lets enable BGP-LU on our PE routers xrd01 and xrd07 plus our BGP route reflectors xrd05 and xrd06. The command *allocate-label all* under the ipv4 unicast which instructs bgp to advertise the networks in the global ipv4 table as labeled routes. Next you will add enable label unicast with the command *address-family ipv4 labeled-unicast* under neighbor-group ibgp-v4 group.

xrd01 and xrd07
```
router bgp 65000
 address-family ipv4 unicast
  allocate-label all
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   next-hop-self
commit
```

route refelctors xrd05 and xrd07
```
router bgp 65000
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   route-reflector-client
commit
```

Now lets get network 20.0.0.0/24 advertised across our routing topology. First log into router xrd01 and enable routing table debugging. This will allow us to see when xrd01 installs the route 20.0.0./24 into the table.

```
RP/0/RP0/CPU0:xrd01#terminal monitor
RP/0/RP0/CPU0:xrd01#debug ip routing 
```

Now in xrd07 go into the BGP configuration and add network 20.0.0./24 to the ipv4 address family.
```
router bgp 65000            
 address-family ipv4 unicast 
  network 20.0.0.0/24
commit
```

You should see in the next BGP update through the BGP route reflector the new route being installed in xrd01. Notice in this example the route was installed with local label *24007*

```
ipv4_rib[1154]: RIB Routing: Vrf: "default", Tbl: "default" IPv4 Unicast, Add active route 20.0.0.0/24 via 10.0.0.7 interface None, metric [200/0] weight 0 (fl: 0x10008/0x2600) label 24007, by client bgp
ipv4_rib[1154]: RIB Routing: Vrf: "default", Tbl: "default" IPv4 Unicast, Add local-label 24007 (1) to 20.0.0.0/24 by proto bgp client bgp
```

Now examine the bgp label table to confirm to confirm. See the truncated output below.

```
RP/0/RP0/CPU0:xrd01#show bgp ipv4 labeled-unicast labels 

Status codes: s suppressed, d damped, h history, * valid, > best
              i - internal, r RIB-failure, S stale, N Nexthop-discard
Origin codes: i - IGP, e - EGP, ? - incomplete
   Network            Next Hop        Rcvd Label      Local Label
*> 10.0.0.1/32        0.0.0.0         nolabel         3
* i10.0.0.5/32        10.0.0.5        nolabel         24006
*>i                   10.0.0.5        3               24006
*>i10.0.0.7/32        10.0.0.7        3               24009
*> 10.101.1.0/24      0.0.0.0         nolabel         3
*> 10.101.2.0/24      10.101.1.1      nolabel         24008
*>i10.107.1.0/24      10.0.0.7        3               24010
*>i20.0.0.0/24        10.0.0.7        24007           24007
```

Last we will look at the CEF table to validate that we received the route from both BGP route reflectors xrd05(10.0.0.5) and xrd06(10.0.0.6) and again you will see that it is associated with local label *24007*

```
RP/0/RP0/CPU0:xrd01#show bgp ipv4 labeled-unicast 20.0.0.0/24    
Fri Jan  6 21:20:01.805 UTC
BGP routing table entry for 20.0.0.0/24
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  58           58
    Local Label: 24007
Last Modified: Jan  6 21:16:38.204 for 00:03:24
Paths: (2 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    10.0.0.7 (metric 3) from 10.0.0.5 (10.0.0.7)
      Received Label 24007 
      Origin IGP, metric 0, localpref 100, valid, internal, best, group-best, labeled-unicast
      Received Path ID 0, Local Path ID 1, version 58
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
  Path #2: Received by speaker 0
  Not advertised to any peer
  Local
    10.0.0.7 (metric 3) from 10.0.0.6 (10.0.0.7)
      Origin IGP, metric 0, localpref 100, valid, internal
      Received Path ID 0, Local Path ID 0, version 0
      Originator: 10.0.0.7, Cluster list: 10.0.0.6
```

cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd01-xrd02
sudo tcpdump -ni br-613d9944c678
[sudo] password for cisco: 
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-613d9944c678, link-type EN10MB (Ethernet), capture size 262144 bytes
16:25:49.085035 IS-IS, p2p IIH, src-id 0000.0000.0002, length 1497
16:25:51.022350 IS-IS, p2p IIH, src-id 0000.0000.0001, length 1497
16:25:51.640600 CDPv2, ttl: 180s, Device-ID 'xrd02', length 148
16:25:52.084003 CDPv2, ttl: 180s, Device-ID 'xrd01', length 148
16:25:58.544203 IS-IS, p2p IIH, src-id 0000.0000.0002, length 1497
16:26:00.155499 IS-IS, p2p IIH, src-id 0000.0000.0001, length 1497
16:26:01.578173 IP6 fc00:0:1111::1.179 > fc00:0:6666::1.46921: Flags [P.], seq 2904722380:2904722399, ack 4037283872, win 32205, length 19: BGP
16:26:01.780550 IP6 fc00:0:6666::1.46921 > fc00:0:1111::1.179: Flags [.], ack 19, win 32424, length 0
16:26:06.602816 IP6 fc00:0:6666::1.46921 > fc00:0:1111::1.179: Flags [P.], seq 1:20, ack 19, win 32424, length 19: BGP
16:26:06.803969 IP6 fc00:0:1111::1.179 > fc00:0:6666::1.46921: Flags [.], ack 20, win 32186, length 0
16:26:08.099680 IS-IS, p2p IIH, src-id 0000.0000.0001, length 1497
16:26:08.306417 IS-IS, p2p IIH, src-id 0000.0000.0002, length 1497
16:26:17.938859 IS-IS, p2p IIH, src-id 0000.0000.0001, length 1497
16:26:18.061634 IS-IS, p2p IIH, src-id 0000.0000.0002, length 1497







### End of lab 2
Please proceed to [lab_3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3)