# Extend SR-MPLS Topology lab 3 Guide

### Description: 
In lab 3 the student will extend the routing topology to include sites Amsterdam and Rome. In addition SR-MPLS will be used to create a baseline end to end routing between the two locations. With SR-MPLS the student will then use show commands and tools like TCPDump to validate how traffic is routed through the neetwork. This is important as Lab 3 will override this behaviour when the student implements SRv6 L3VPN with path selection.


## Contents
1. [Lab Objectives](#lab-objectives)
2. [Learn Default ISIS Path](#learn-default-isis-path)
3. [BGP-LU over SR-MPLS](#bgp-labeled-unicast-bgp-lu-over-sr-mpls-network-routing)
    - [Validate Local Network](#configure-remote-test-networks)
    - [Enable BGP Labeled Unicast](#enable-bgp-labeled-unicast)
    - [Advertise BGP-LU Prefixes](#advertise-bgp-lu-prefixes)
    - [Validate BGP routes](#validate-bgp-routes)
4. [Validate End to End Connectivity](#validate-end-to-end-connectivity)
  

## Lab Objectives
The student upon completion of lab 3 should have achieved the following objectives:

* Understanding of ISIS routing policy
* Enable BGP Labeled Unicast network routing over the SR-MPLS underlay
* End to end routing between Amsterdam and Rome
* Diagnostic tools to validate path routing


## Learn Default ISIS Path

ISIS is the underlying IGP in this lab and you validated in Lab 1 reachability between xrd routers. Now we want you to work on validate traffic routing behavior for the default ISIS and SR-MPLS so that we can compare and contrast with SRv6 when implemented in Lab 3. Throughout this lab we will be creating traffic flows generated from the Amsterdam VM and traveling to networks in Rome and vice-versa. 

In referencing the ISIS topology diagram below we will examine the routing table on xrd01.

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

## BGP Labeled Unicast (BGP-LU) over SR-MPLS Network Routing
First we are going to need networks that are advertised through BGP-LU over the top of ISIS. In the next few steps you will quickly bring up and add in network 20.0.0./24 to the topology and validate end to end connectivity. This will be our baseline path to compare and contrast with SRv6

For further reference the Cisco IOS-XR 7.5 Configuration guide for SR and BGP can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-for-bgp.html)

### Configure Remote Test Networks
The location Rome has the network 20.0.0.0/24 which we will advertise via BGP-LU on router xrd07. First log into xrd07 and validate that you can reach network 20.0.0.0/24 by pinging the ip address 20.0.0.1/24 in Rome. Once you have confirmed connectivity across the Rome metro link xrd07 gi 0/0/0/0 head to the next step.


![SR-MPLS Topology](/topo_drawings/sr-mpls-medium.png)
For full size image see [LINK](/topo_drawings/sr-mpls-large.png)

### Enable BGP Labeled Unicast
BGP Labeled Unicast (BGP-LU) is needed to advertise the label information we will need to enable SR-MPLS routing of our desired network traffic 20.0.0.0/24. First lets enable BGP-LU on our PE routers xrd01 and xrd07 plus our BGP route reflectors xrd05 and xrd06. The command *allocate-label all* under the ipv4 unicast which instructs bgp to advertise the networks in the global ipv4 table as labeled routes. Next you will add enable labeled unicast with the command *address-family ipv4 labeled-unicast* under neighbor-group xrd-ipv4-peer group.

xrd01 and xrd07
  ```
  router bgp 65000
  address-family ipv4 unicast
    allocate-label all
  neighbor-group xrd-ipv4-peer
    address-family ipv4 labeled-unicast
    next-hop-self
  commit
  ```

route refelctors xrd05 and xrd07
  ```
  router bgp 65000
  neighbor-group xrd-ipv4-peer
    address-family ipv4 labeled-unicast
    route-reflector-client
  commit
```

Now lets get network 20.0.0.0/24 advertised across our routing topology. First log into router xrd01 and enable routing table debugging. This will allow us to see when xrd01 installs the route 20.0.0./24 into the table.

  ```
  RP/0/RP0/CPU0:xrd01#terminal monitor
  RP/0/RP0/CPU0:xrd01#debug ip routing 
  ```
### Advertise BGP-LU prefixes
xrd01 - Routes for Amsterdam
  ```
  router bgp 65000            
  address-family ipv4 unicast 
    network 10.101.1.0/24
    network 10.101.2.0/24
  commit
  ```

xrd07 - Routes for Rome
  ```
  router bgp 65000            
  address-family ipv4 unicast 
    network 20.0.0.0/24
  commit
  ```
* hopefully we can remove the following line: 

Log into the BGP route reflectors xrd05 and xrd06 and reset the bgp neighbor connections using _clear bgp *_

### Validate BGP routes
You should now see BGP update the new route being installed in xrd01 and xrd07. Notice in this example for xrd01 that route 20.0.0.0/24 was installed with local label *24007*

  ```
  ipv4_rib[1154]: RIB Routing: Vrf: "default", Tbl: "default" IPv4 Unicast, Add active route 20.0.0.0/24 via 10.0.0.7 interface None, metric [200/0] weight 0 (fl: 0x10008/0x2600) label 24007, by client bgp
  ipv4_rib[1154]: RIB Routing: Vrf: "default", Tbl: "default" IPv4 Unicast, Add local-label 24007 (1) to 20.0.0.0/24 by proto bgp client bgp
  ```
#### The next section uses the following validation commands:
```
show bgp ipv4 labeled-unicast labels
show bgp ipv4 labeled-unicast 20.0.0.0/24
show cef 20.0.0.0/24
```
1. Examine the bgp label table to confirm prefixes and label allocation. See the truncated example output below.

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
2. Next on xrd01 we can look at BGP-LU prefix specific attributes to validate that we received the route from both BGP route reflectors xrd05(10.0.0.5) and xrd06(10.0.0.6) and again you will see that it is associated with local label *24007*

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

3. We can do the same on XRD07 for the routes

  ```
  RP/0/RP0/CPU0:xrd07#show bgp ipv4 labeled-unicast labels 

  Status codes: s suppressed, d damped, h history, * valid, > best
                i - internal, r RIB-failure, S stale, N Nexthop-discard
  Origin codes: i - IGP, e - EGP, ? - incomplete
    Network            Next Hop        Rcvd Label      Local Label
  *>i10.0.0.1/32        10.0.0.1        3               24009
  * i                   10.0.0.1        nolabel         24009
  * i10.0.0.5/32        10.0.0.5        nolabel         24008
  *>i                   10.0.0.5        3               24008
  * i10.0.0.6/32        10.0.0.6        nolabel         24006
  *>i                   10.0.0.6        3               24006
  *> 10.0.0.7/32        0.0.0.0         nolabel         3
  *>i10.101.1.0/24      10.0.0.1        3               24010
  * i                   10.0.0.1        nolabel         24010
  *>i10.101.2.0/24      10.0.0.1        24008           24011
  * i                   10.0.0.1        nolabel         24011
  *> 10.107.1.0/24      0.0.0.0         nolabel         3
  *> 20.0.0.0/24        10.107.1.1      nolabel         24007

  Processed 8 prefixes, 13 paths
  ```

4. Last we will look at the CEF table on xrd01 to verify the prefix is installed for labeled forwarding:

```
RP/0/RP0/CPU0:xrd01#sho cef 20.0.0.0/24
Sat Jan  7 18:11:21.229 UTC
20.0.0.0/24, version 175, internal 0x5000001 0x40 (ptr 0x87303a80) [1], 0x600 (0x879794a0), 0xa08 (0x89d5e648)
 Updated Jan  7 17:55:22.234
 Prefix Len 24, traffic index 0, precedence n/a, priority 4
  gateway array (0x877e1b40) reference count 6, flags 0x78, source rib (7), 0 backups
                [3 type 5 flags 0x8441 (0x89ddd7c8) ext 0x0 (0x0)]
  LW-LDI[type=5, refc=3, ptr=0x879794a0, sh-ldi=0x89ddd7c8]
  gateway array update type-time 1 Jan  7 17:55:22.234
 LDI Update time Jan  7 17:55:22.234
 LW-LDI-TS Jan  7 17:55:22.234
   via 10.0.0.7/32, 3 dependencies, recursive [flags 0x6000]
    path-idx 0 NHID 0x0 [0x87348230 0x0]
    recursion-via-/32
    next hop 10.0.0.7/32 via 100007/0/21
     local label 24010 
     next hop 10.1.1.1/32 Gi0/0/0/1    labels imposed {100007 24007}
     next hop 10.1.1.9/32 Gi0/0/0/2    labels imposed {100007 24007}

    Load distribution: 0 (refcount 3)

    Hash  OK  Interface                 Address
    0     Y   recursive                 100007/0       
RP/0/RP0/CPU0:xrd01#
```

### Validate end to end connectivity
Let's next use what we learned in step one of the lab guide about how xrd01 will use ECMP to load balance flows towards xrd07. We will test connectivity by initiating a ping from xrd01 to the address 20.0.0.1 in Rome. What we don't know is which path it will take as the next-hop could be either xrd02 or xrd05. In addition, we want to confirm that the path is using SR-MPLS forwarding.

Lets use TCPDump to validate our configuration and SR-MPLS forwarding:
1. Open up two new ssh sessions to the XRD VM and change to the *~/SRv6_dCloud_Lab/util* directory. 
```
cd ~/SRv6_dCloud_Lab/util
```
In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs wrote them to text files in this directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need. 

With that understanding the *util* directory also contains a shell script called 'tcpdump.sh'. Running "./tcpdump.sh <filename>" will execute Linux TCPdump allowing us to monitor the traffic exiting xrd01 along the path to its destination and back.


2. In terminal window-1 run the command *./tcpdump.sh xrd01-xrd02*

3. In terminal window-2 run the command *./tcpdump.sh xrd01-xrd05*

```
./tcpdump.sh xrd01-xrd02
./tcpdump.sh xrd01-xrd05
```

4. Initiate a ping from Amsterdam to Rome 20.0.0.1 (or from xrd01 to Rome)
```
cisco@amsterdam:~$ ping 20.0.0.1 -i .4
```

We should see TCPDump output something like this:

  ```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd01-xrd02 
sudo tcpdump -ni br-613d9944c678
[sudo] password for cisco: 
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-613d9944c678, link-type EN10MB (Ethernet), capture size 262144 bytes
13:26:32.704104 MPLS (label 100007, exp 0, ttl 62) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 20, seq 39, length 64
13:26:32.706566 MPLS (label 24008, exp 0, [S], ttl 61) IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 20, seq 39, length 64
13:26:32.903937 MPLS (label 100007, exp 0, ttl 62) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 20, seq 40, length 64
13:26:32.906271 MPLS (label 24008, exp 0, [S], ttl 61) IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 20, seq 40, length 64
  ```
3. We can run the tcpdump.sh script against any of the underlying links in the network:

```
./tcpdump.sh xrd02-xrd06
./tcpdump.sh xrd06-xrd07
```
Example output
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06
sudo tcpdump -ni br-65c7870958c4
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-65c7870958c4, link-type EN10MB (Ethernet), capture size 262144 bytes
13:28:02.047690 MPLS (label 100007, exp 0, ttl 61) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 20, seq 484, length 64
13:28:02.050055 MPLS (label 100001, exp 0, ttl 62) (label 24008, exp 0, [S], ttl 63) IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 20, seq 484, length 64
```

### Amsterdam to Rome Test using iPerf
An alternate quick way to look for the flow of traffic through the network is to clear counters on the router's potential egress interfaces and then run a measurable amount of traffic and see which interface packet counters increment. To continue in our validation from the previous step we will go to router xrd02 and determine if our packet flow next-hops to router xrd03 or xrd06.

Lets get our test setup ready. For this test we will be using a tool called iPerf3 which allows us to do various types of traffic generation. 

  1. Log into the Rome VM with ssh.
  2. Run the following cli command to start iPerf3 and run it as a service *iperf3 -s -D*
  3. Log into xrd02 with ssh.
  4. On xrd02 run the command *clear counter interface gi x/x/x/x* on the interface facing xrd03 and xrd06
  5. Log into the Amsterdam VM with ssh.
  6. Run the following cli command to start iPerf3 test: *iperf3 -c 20.0.0.1*
  7. Go back to xrd02 and now look at the interface counters and see which incremented by several hundred packets
  8. You can repeat this hop by hop through the network to determine the flow path.

See the command output that demonstrates this test below. Some output truncated for brevity:

Rome VM
  ```
  cisco@rome:~$ iperf3 -s -D
  ```

Amsterdam VM
  ```
  cisco@amsterdam:~$ iperf3 -c 20.0.0.1
  Connecting to host 20.0.0.1, port 5201
  [  5] local 10.101.2.1 port 41106 connected to 20.0.0.1 port 5201
  [ ID] Interval           Transfer     Bitrate         Retr  Cwnd
  [  5]   0.00-1.00   sec   107 KBytes   877 Kbits/sec   15   2.82 KBytes       
  [  5]   1.00-2.00   sec  0.00 Bytes  0.00 bits/sec   15   2.82 KBytes       
  [  5]   2.00-3.00   sec  93.1 KBytes   763 Kbits/sec   32   2.82 KBytes       
  [  5]   3.00-4.00   sec   124 KBytes  1.02 Mbits/sec   30   2.82 KBytes       
  [  5]   4.00-5.00   sec   124 KBytes  1.02 Mbits/sec   30   2.82 KBytes       
  [  5]   5.00-6.00   sec  93.1 KBytes   762 Kbits/sec   28   2.82 KBytes       
  [  5]   6.00-7.00   sec   124 KBytes  1.02 Mbits/sec   30   2.82 KBytes       
  [  5]   7.00-8.00   sec   124 KBytes  1.02 Mbits/sec   30   2.82 KBytes       
  [  5]   8.00-9.00   sec  93.1 KBytes   762 Kbits/sec   30   2.82 KBytes       
  [  5]   9.00-10.00  sec   124 KBytes  1.02 Mbits/sec   30   2.82 KBytes       
  - - - - - - - - - - - - - - - - - - - - - - - - -
  [ ID] Interval           Transfer     Bitrate         Retr
  [  5]   0.00-10.00  sec  1007 KBytes   825 Kbits/sec  270             sender
  [  5]   0.00-10.01  sec   948 KBytes   776 Kbits/sec                  receiver

  iperf Done.
  ```

The command output below demonstrates that our iPerf traffic was forward from xrd02 out interface gi0/0/0/2 to xrd06

On xrd02: 
  ```
  RP/0/RP0/CPU0:xrd02#clear counter int gi 0/0/0/1
  Clear "show interface" counters on this interface [confirm] 

  RP/0/RP0/CPU0:xrd02#clear counter int gi 0/0/0/2
  Clear "show interface" counters on this interface [confirm] 

  RP/0/RP0/CPU0:xrd02#show int gi 0/0/0/1
  Sat Jan  7 17:04:10.888 UTC
  GigabitEthernet0/0/0/1 is up, line protocol is up 
    <<<<<<<<<<<>>>>>>>>>>>
    5 minute input rate 0 bits/sec, 0 packets/sec
    5 minute output rate 0 bits/sec, 0 packets/sec
      3 packets input, 3198 bytes, 0 total input drops
      0 drops for unrecognized upper-level protocol
      Received 0 broadcast packets, 3 multicast packets
                0 runts, 0 giants, 0 throttles, 0 parity
      0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
      3 packets output, 3198 bytes, 0 total output drops
      Output 0 broadcast packets, 3 multicast packets
      0 output errors, 0 underruns, 0 applique, 0 resets
      0 output buffer failures, 0 output buffers swapped out
      0 carrier transitions


  RP/0/RP0/CPU0:xrd02#show int gi 0/0/0/2
  Sat Jan  7 17:04:12.647 UTC
  GigabitEthernet0/0/0/2 is up, line protocol is up 
    <<<<<<<<<<<>>>>>>>>>>>
    Last input never, output never
    Last clearing of "show interface" counters 00:00:14
    5 minute input rate 0 bits/sec, 0 packets/sec
    5 minute output rate 0 bits/sec, 0 packets/sec
      2 packets input, 1684 bytes, 0 total input drops
      0 drops for unrecognized upper-level protocol
      Received 0 broadcast packets, 2 multicast packets
                0 runts, 0 giants, 0 throttles, 0 parity
      0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
      3 packets output, 3198 bytes, 0 total output drops
      Output 0 broadcast packets, 3 multicast packets
      0 output errors, 0 underruns, 0 applique, 0 resets
      0 output buffer failures, 0 output buffers swapped out
      0 carrier transitions


  RP/0/RP0/CPU0:xrd02#show int gi 0/0/0/1
  Sat Jan  7 17:04:36.707 UTC
  GigabitEthernet0/0/0/1 is up, line protocol is up 
   <<<<<<<<<<<>>>>>>>>>>>
    Last clearing of "show interface" counters 00:00:42
    5 minute input rate 0 bits/sec, 0 packets/sec
    5 minute output rate 0 bits/sec, 0 packets/sec
      8 packets input, 7878 bytes, 0 total input drops
      0 drops for unrecognized upper-level protocol
      Received 0 broadcast packets, 7 multicast packets
                0 runts, 0 giants, 0 throttles, 0 parity
      0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
      8 packets output, 8724 bytes, 0 total output drops
      Output 0 broadcast packets, 7 multicast packets
      0 output errors, 0 underruns, 0 applique, 0 resets
      0 output buffer failures, 0 output buffers swapped out
      0 carrier transitions


  RP/0/RP0/CPU0:xrd02#show int gi 0/0/0/2
  Sat Jan  7 17:04:40.084 UTC
  GigabitEthernet0/0/0/2 is up, line protocol is up 
    <<<<<<<<<<<>>>>>>>>>>>
    Last clearing of "show interface" counters 00:00:42
    5 minute input rate 0 bits/sec, 0 packets/sec
    5 minute output rate 0 bits/sec, 0 packets/sec
      691 packets input, 73245 bytes, 0 total input drops        <---------------
      0 drops for unrecognized upper-level protocol
      Received 0 broadcast packets, 6 multicast packets
                0 runts, 0 giants, 0 throttles, 0 parity
      0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
      841 packets output, 1059352 bytes, 0 total output drops    <---------------
      Output 0 broadcast packets, 7 multicast packets
      0 output errors, 0 underruns, 0 applique, 0 resets
      0 output buffer failures, 0 output buffers swapped out
      0 carrier transitions
  ```
Note: the tcpdump.sh script can also be active while running iperf:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06
sudo tcpdump -ni br-65c7870958c4
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-65c7870958c4, link-type EN10MB (Ethernet), capture size 262144 bytes
13:30:17.006509 MPLS (label 100007, exp 0, ttl 61) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1.43938 > 20.0.0.1.5201: Flags [S], seq 3759648417, win 64240, options [mss 1460,sackOK,TS val 1262297038 ecr 0,nop,wscale 7], length 0
13:30:17.008579 MPLS (label 100001, exp 0, ttl 62) (label 24008, exp 0, [S], ttl 63) IP 20.0.0.1.5201 > 10.101.2.1.43938: Flags [S.], seq 399849138, ack 3759648418, win 65160, options [mss 1460,sackOK,TS val 1943388697 ecr 1262297038,nop,wscale 7], length 0
13:30:17.014429 MPLS (label 100007, exp 0, ttl 61) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1.43938 > 20.0.0.1.5201: Flags [.], ack 1, win 502, options [nop,nop,TS val 1262297045 ecr 1943388697], length 0
13:30:17.014448 MPLS (label 100007, exp 0, ttl 61) (label 24007, exp 0, [S], ttl 62) IP 10.101.2.1.43938 > 20.0.0.1.5201: Flags [P.], seq 1:38, ack 1, win 502, options [nop,nop,TS val 1262297045 ecr 1943388697], length 37
13:30:17.016005 MPLS (label 100001, exp 0, ttl 62) (label 24008, exp 0, [S], ttl 63) IP 20.0.0.1.5201 > 10.101.2.1.43938: Flags [.], ack 38, win 509, options [nop,nop,TS val 1943388705 ecr 1262297045], length 0
```

### End of lab 3
Please proceed to [Lab 4](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-guide.md)