

# Lab 2: SRv6 uSID Packet Walk [5 Min]

### Description: 
This is a supplemental lab guide used to deconstruct the forwarding process of traffic through the SRv6 lab topology in this lab. In Lab 2 we are setting up a SRv6 topology using the global forwarding table for forwarding packets in the network. This is distinct from Lab 3 where we will add the virtualization concept of L3VPN + SRv6.

## Contents
- [Lab 2: SRv6 uSID Packet Walk \[5 Min\]](#lab-2-srv6-usid-packet-walk-5-min)
    - [Description:](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Packet Walk Results for traffic from Amsterdam to Rome over SRv6](#packet-walk-results-for-traffic-from-amsterdam-to-rome-over-srv6)
  - [IPv4 Encapsulation to SRv6](#ipv4-encapsulation-to-srv6)
  - [SRv6 forwarding](#srv6-forwarding)
  - [Proceed to Lab 3](#proceed-to-lab-3)
  

## Lab Objectives
The student upon completion of Lab 2 should have achieved the following objectives:

* Understand how standard IPv4 or IPv6 packets are encapsulated with SRv6 headers
* Understand the forwarding behavior of SRv6 enabled routers
* Understand how SRv6 routers decapsulate and forward traffic as an IPv4 or IPv6 packet
* Understand how IPv6 only routers can participate in SRv6 networks.

## Packet Walk Results for traffic from Amsterdam to Rome over SRv6

The expected results of a packet capture on XRD01 is to see ICMP ipv4 traffic sourced from Amsterdam (10.101.2.1) to Rome (10.107.1.1) use SRv6 encapsulation acroess the network.

See results below and notice both the ICMP echo and ICMP echo reply packets with SRv6 encapsulation. 
> [!NOTE]
>  In this example the egress and return traffic both happened to be hashed through XRD02.
>  Path selection using the global routing table as you will see in the detailed packet walk below
>  has multiple ECMP path options.

```
./tcpdump.sh xrd01-xrd02
```
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd01-xrd02
sudo tcpdump -ni br-0a7631e659a1
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-0a7631e659a1, link-type EN10MB (Ethernet), capture size 262144 bytes

12:57:01.231407 IP6 fc00:0:1111::1 > fc00:0:7777:e004::: IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 7, seq 15, length 64
12:57:01.296035 IP6 fc00:0:7777::1 > fc00:0:1111:e005::: IP 10.107.1.1 > 10.101.2.1: ICMP echo reply, id 7, seq 15, length 64
```

## IPv4 Encapsulation to SRv6

In Lab 2 this step occurs in Router 1. On ingress from the Amsterdam node we receive an IPv4 packet that needs forwarding to Rome. We will walk through the process of determining that SRv6 encapsulation is required and lookup process.

![Router 1 Topology](/topo_drawings/ltrspg-2212-packet-walk-r1.png)

1. Router 1 receives IPv4 echo request and we see the accompanying echo reply. On the XRD VM run this tcpdump:
    ```
    sudo tcpdump -ni ens224 -v
    ```
    ```
    sudo tcpdump -ni ens224 -v

    17:57:59.454374 IP (tos 0x0, ttl 63, id 55614, offset 0, flags [DF], proto ICMP (1), length 84)
        10.101.2.1 > 10.107.1.1: ICMP echo request, id 13, seq 4, length 64
    17:57:59.511935 IP (tos 0x0, ttl 62, id 9926, offset 0, flags [none], proto ICMP (1), length 84)
        10.107.1.1 > 10.101.2.1: ICMP echo reply, id 13, seq 4, length 64
    ```
2. From Router 1 we can see a lookup of the IPv4 DA address in the bgpv4 global routing table and show the SRv6 SID associated with the route 10.107.1.0/24.
    ```
    show ip bgp ipv4 unicast 10.107.1.0/24
    ```
    ```
    RP/0/RP0/CPU0:xrd01#show ip bgp ipv4 unicast 10.107.1.0/24
    Fri Dec 15 17:25:40.292 UTC
    BGP routing table entry for 10.107.1.0/24
    Versions:
      Process           bRIB/RIB  SendTblVer
      Speaker                  26           26
    Last Modified: Dec 15 17:25:04.827 for 00:00:35
    Paths: (2 available, best #1)
      Not advertised to any peer
      Path #1: Received by speaker 0
      Not advertised to any peer
    Local
      10.0.0.7 (metric 3) from 10.0.0.5 (10.0.0.7)
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best
        Received Path ID 0, Local Path ID 1, version 26
        Originator: 10.0.0.7, Cluster list: 10.0.0.5
        PSID-Type:L3, SubTLV Count:1
         SubTLV:
          T:1(Sid information), Sid:fc00:0:7777:e004::, Behavior:63, SS-TLV Count:1 <---- SID HERE
           SubSubTLV:
            T:1(Sid structure):
    ```
3. Lookup of fc00:0:7777:e004::/48 the in the global IPv6 routing table.
    ```
    show route ipv6 fc00:0:7777:e004::
    ```
    ```
    RP/0/RP0/CPU0:xrd01#show route ipv6 fc00:0:7777:e004::
    Routing entry for fc00:0:7777::/48
     Known via "isis 100", distance 115, metric 4, SRv6-locator, type level-2 <---- Network seen as SRv6 locator
     Installed Dec 15 17:22:21.553 for 00:21:47
     Routing Descriptor Blocks
        fe80::42:c0ff:fea8:c003, from fc00:0:7777::1, via GigabitEthernet0/0/0/1, Protected, ECMP-Backup (Local-LFA)
          Route metric is 4
        fe80::42:c0ff:fea8:d003, from fc00:0:7777::1, via GigabitEthernet0/0/0/2, Protected, ECMP-Backup (Local-LFA)
          Route metric is 4
      No advertising protos. 
    ```

4. Lets now lookup in the CEF table to see the forwarding next hop.
    ```
    show ip cef 10.107.1.0/24
    ```
    ```
    RP/0/RP0/CPU0:xrd01#show ip cef 10.107.1.0/24
    Fri Dec 15 17:39:36.796 UTC
    10.107.1.0/24, version 290, SRv6 Headend, internal 0x5000001 0x40 (ptr 0x87363b40) [1], 0x0 (0x0), 0x0 (0x9b8d0508)
      Updated Dec 15 17:36:15.995
      Prefix Len 24, traffic index 0, precedence n/a, priority 4
        gateway array (0x9b7f90a8) reference count 2, flags 0x2010, source rib (7), 0 backups
                [1 type 3 flags 0x48441 (0x87a4e6a8) ext 0x0 (0x0)]
        LW-LDI[type=0, refc=0, ptr=0x0, sh-ldi=0x0]
        gateway array update type-time 1 Dec 15 17:25:04.700
      LDI Update time Dec 15 17:25:04.741

    Level 1 - Load distribution: 0
    [0] via fc00:0:7777::/128, recursive  <--- Recurisve lookup resolves to SRv6

     via fc00:0:7777::/128, 5 dependencies, recursive [flags 0x6000]
      path-idx 0 NHID 0x0 [0x8717c790 0x0]
      next hop VRF - 'default', table - 0xe0800000
      next hop fc00:0:7777::/128 via fc00:0:7777::/48
      SRv6 H.Encaps.Red SID-list {fc00:0:7777:e004::} <--- uSID value for SRv6 encap

      Load distribution: 0 1 0 1 (refcount 1)

      Hash  OK  Interface                 Address
      0     Y   GigabitEthernet0/0/0/1    fe80::42:c0ff:fea8:c003 <--- ECMP Next-hop
      1     Y   GigabitEthernet0/0/0/2    fe80::42:c0ff:fea8:d003 <--- ECMP Next-hop
      2     Y   GigabitEthernet0/0/0/1    fe80::42:c0ff:fea8:c003 <--- ECMP Next-hop
      3     Y   GigabitEthernet0/0/0/2    fe80::42:c0ff:fea8:d003 <--- ECMP Next-hop
    ```
   
## SRv6 forwarding

In lab_1 When we ran the XRd topology setup script it called the **nets.sh** subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh script resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

![Router 1 Topology](/topo_drawings/ltrspg-2212-packet-walk-r3.png)

1. On the XRD VM cd into the lab util directory:
    ```
    cd ~/SRv6_dCloud_Lab/util/
    ```
2. Run one of the prebuilt tcpdump scripts:
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
3. Run some pings from **xrd01** to **xrd07**:
    ```
    ping 10.0.0.7 source lo0
    ```
    ```
    ping fc00:0000:7777::1 source lo0
    ```

## Proceed to Lab 3
Please proceed to [Lab 3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3/lab_3-guide.md)
