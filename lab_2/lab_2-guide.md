

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
      - [do we keep this (requires re-creating the shell script), or do we just have users run the verbose tcpdump command? Or take the packet walk doc and merge it into here and call it good?](#do-we-keep-this-requires-re-creating-the-shell-script-or-do-we-just-have-users-run-the-verbose-tcpdump-command-or-take-the-packet-walk-doc-and-merge-it-into-here-and-call-it-good)
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
> Once you've configured xrd01 using the above, please proceed to configure the remainder of the routers using the configs found in the `*quick config doc*` [HERE](/lab_2/lab_2_quick_config.md) 

#### Validate SRv6 configuration and reachability

1. Validation commands
    ```
    show segment-routing srv6 sid
    ```
    ```
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
    fc00:0:1111:e004::          uDT4              'default'                         bgp-65000           InUse  Y 
    fc00:0:1111:e005::          uDT6              'default'                         bgp-65000           InUse  Y
    ```
> [!NOTE]
> The bottom two entries. These SIDs belong to BGP and represent End.DT behaviors. Any packet arriving with either of these SIDs as the outer IPv6 destination address will be decasulated and then an LPM lookup in the global/default routing table will be performed on the inner destination address. More on this later in the *`SRv6 Packet Walk`* section.

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
In this lab we will make extensive use of tcpdump to look at traffic on routed links. Containerlab makes this a fairly easy process as the underlying router links run in Linux network namespaces. There are two pieces of information we need to run a tcpdump command; the *network namespace* and *interface name*.

For the  *network namespace* use the below command 
```
sudo ip netns ls
```
For the list of *interface names* created in a *network namespace* use the following command
```
sudo ip netns clab-cleu25-xrd01 iplink show
```
```diff
cisco@xrd:~/SRv6_dCloud_Lab/lab_1$ sudo ip netns exec clab-cleu25-xrd01 ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

169: eth0@if170: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
    link/ether 02:42:0a:fe:fe:65 brd ff:ff:ff:ff:ff:ff link-netnsid 0

177: Gi0-0-0-2@if178: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:a2:6d:3f brd ff:ff:ff:ff:ff:ff link-netns clab-cleu25-xrd05

+183: Gi0-0-0-1@if184: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default 
+    link/ether aa:c1:ab:94:44:ec brd ff:ff:ff:ff:ff:ff link-netns clab-cleu25-xrd02

196: <!--- Gi0-0-0-0 ---> @if6: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:d2:30:a0 brd ff:ff:ff:ff:ff:ff link-netnsid 0

199: **Gi0-0-0-3** @if5: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default 
    link/ether aa:c1:ab:f2:a2:fe brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

An example tcpdump command would look like this:
```
sudo ip netns exec clab-cleu25-XR01 tcpdump -ni Gi0-0-0-1
```
#### do we keep this (requires re-creating the shell script), or do we just have users run the verbose tcpdump command? Or take the packet walk doc and merge it into here and call it good?

In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

We'll use 'tcpdump.sh' shell script in the util directory to monitor traffic as it traverses the XRd network. Running "./tcpdump.sh xrd0x-xrd0y" will execute Linux TCPdump on the specified Linux bridge instance that links a pair of XRd routers. Note traffic through the network may travel via one or more ECMP paths, so we may need to try tcpdump.sh on different links before we see anything meaningful in the output

1. On the **XRD** VM cd into the lab's util directory:
  ```
  cd ~/SRv6_dCloud_Lab/util/
  ```
2. Start the tcpdump.sh script to monitor traffic on a link:
  ```
  ./tcpdump.sh xrd05-xrd06
  ```
3. Start an SSH session to the Amsterdam VM and ping the Rome VM
  ```
  ssh cisco@198.18.128.102

  ping 10.107.1.1 -i .3 -c 4
  ```

  Example tcpdump.sh output:
  ```
  cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd05-xrd06
  sudo tcpdump -ni br-343a0d248d8e
  tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
  listening on br-343a0d248d8e, link-type EN10MB (Ethernet), capture size 262144 bytes
  17:44:54.447013 IP6 fc00:0:1111::1 > fc00:0:7777:e004::: IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 12, seq 13, length 64
  17:44:55.454992 IP6 fc00:0:1111::1 > fc00:0:7777:e004::: IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 12, seq 14, length 64
  17:44:56.455127 IP6 fc00:0:1111::1 > fc00:0:7777:e004::: IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 12, seq 15, length 64
  ```

In the example above the outbound ICMP echo requests are captured and you can see the outer IPv6/SRv6 encapsulation. The echo replies are not shown as the network has hashed the replies over a different path. In your case if nothing shows up on the tcpdump output you can try tcpdumping on the *`xrd02-xrd06`* OR *`xrd04-xrd05`* link and run the Amsterdam ping again:

Note: the ./tcpdump.sh break sequence is *ctrl-z*
  ```
  sudo ./tcpdump.sh xrd02-xrd06
  ```
  ```
  sudo ./tcpdump.sh xrd04-xrd05
  ```
Eventually pings should show up as tcpdump output. 

## SRv6 Packet Walk
This is an optional section of the lab where we expand on the routing table behaviours during forwarding operations. 
Please use this link for the packet walk. [Packet Walk](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_2/lab_2-packet-walk.md)

## End of Lab 2
Please proceed to [Lab 3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3/lab_3-guide.md)
