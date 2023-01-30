

# Lab 2: SR-MPLS and SRv6 Install [20 Min]

### Description: 
In Lab 2 the student will perform the basic configuration of SR-MPLS and SRv6 on the lab routers. This will allow for a compare and contrast between the two segment routing standards. You will create and confirm PE and P roles for SR-MPLS. Second you will create basic SRv6 configuration on routers 1-7 and confirm connectivity. 

## Contents
- [Lab 2: SR-MPLS and SRv6 Install \[20 Min\]](#lab-2-sr-mpls-and-srv6-install-20-min)
    - [Description:](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [SR-MPLS Background](#sr-mpls-background)
    - [Validate SR-MPLS is running correctly](#validate-sr-mpls-is-running-correctly)
  - [SRv6](#srv6)
    - [Configuration Steps SRv6](#configuration-steps-srv6)
      - [Configure SRv6 on all routers (xrd01 - xrd07) in the network](#configure-srv6-on-all-routers-xrd01---xrd07-in-the-network)
  - [End-to-End Connectivity](#end-to-end-connectivity)
  - [End of Lab 2](#end-of-lab-2)
  

## Lab Objectives
The student upon completion of Lab 2 should have achieved the following objectives:

* Validation of SR-MPLS setup and forwarding
* Understanding of basic configuration for SRv6
   

## SR-MPLS Background

Segment Routing (SR) is a source-based routing architecture. A node chooses a path and steers a packet through the network via that path by inserting an ordered list of segments, instructing how subsequent nodes in the path that receive the packet should process it. This simplifies operations and reduces resource requirements in the network by removing network state information from intermediary nodes as path information is encoded via the label stack at the ingress node. In addition to this, because the shortest-path segment includes all Equal-Cost Multi-Path (ECMP) paths to the related node, SR supports the ECMP nature of IP by design. All nodes in the lab xrd01 - xrd07 have SR-MPLS pre-configured.

For a full overview of SR-MPLS please see the Wiki here: [LINK](/SR-MPLS.md)  
The Cisco IOS-XR 7.5 Configuration guide for SR-MPLS can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-for-is-is-protocol.html)

### Validate SR-MPLS is running correctly
1. On xrd01 (and perhaps xrd07) verify ISIS segment routing and MPLS forwarding are established:
    ```
    show isis segment-routing label table 
    ```
    - Expected output:
    ```
    RP/0/RP0/CPU0:xrd07#show isis segment-routing label table                

    IS-IS 100 IS Label Table
    Label         Prefix                   Interface
    ----------    ----------------         ---------
    100001        10.0.0.1/32              
    100002        10.0.0.2/32              
    100003        10.0.0.3/32              
    100004        10.0.0.4/32              
    100005        10.0.0.5/32              
    100006        10.0.0.6/32              
    100007        10.0.0.7/32              Loopback0
    ```
    - MPLS forwarding:
    ```
    show mpls forwarding
    ```
    - Expected output:
    ```
    RP/0/RP0/CPU0:xrd07#show mpls forwarding 

    Local  Outgoing    Prefix             Outgoing     Next Hop        Bytes       
    Label  Label       or ID              Interface                    Switched    
    ------ ----------- ------------------ ------------ --------------- ------------
    24002  Pop         10.101.1.0/24                   10.0.0.1        0           
    24003  Unlabelled  10.1.1.4/31        Gi0/0/0/1    10.1.1.6        0           
           100005      10.1.1.4/31        Gi0/0/0/2    10.1.1.16       0            (!)
    24004  Unlabelled  10.1.1.10/31       Gi0/0/0/2    10.1.1.16       0           
           100005      10.1.1.10/31       Gi0/0/0/1    10.1.1.6        0            (!)
    24005  Pop         SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0           
           100005      SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0            (!)
    24006  Pop         SR Adj (idx 3)     Gi0/0/0/1    10.1.1.6        0           
    24007  Pop         SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0           
           100005      SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0            (!)
    24008  Pop         SR Adj (idx 3)     Gi0/0/0/2    10.1.1.16       0           
    100001 100001      SR Pfx (idx 1)     Gi0/0/0/1    10.1.1.6        0           
           100001      SR Pfx (idx 1)     Gi0/0/0/2    10.1.1.16       0           
    100002 100002      SR Pfx (idx 2)     Gi0/0/0/2    10.1.1.16       0           
           100002      SR Pfx (idx 2)     Gi0/0/0/1    10.1.1.6        0            (!)
    100003 100003      SR Pfx (idx 3)     Gi0/0/0/1    10.1.1.6        0           
           100003      SR Pfx (idx 3)     Gi0/0/0/2    10.1.1.16       0            (!)
    100004 Pop         SR Pfx (idx 4)     Gi0/0/0/1    10.1.1.6        0           
           100005      SR Pfx (idx 4)     Gi0/0/0/2    10.1.1.16       0            (!)
    100005 100005      SR Pfx (idx 5)     Gi0/0/0/1    10.1.1.6        0           
           100005      SR Pfx (idx 5)     Gi0/0/0/2    10.1.1.16       1119        
    100006 Pop         SR Pfx (idx 6)     Gi0/0/0/2    10.1.1.16       939         
           100005      SR Pfx (idx 6)     Gi0/0/0/1    10.1.1.6        0            (!)
    100007 Aggregate   SR Pfx (idx 7)     default                      0           
    ```   

## SRv6
Segment Routing over IPv6 (SRv6) extends Segment Routing support with IPv6 data plane.

SRv6 introduces the Network Programming framework that enables a network operator or an application to specify a packet processing program by encoding a sequence of instructions in the IPv6 packet header. Each instruction is implemented on one or several nodes in the network and identified by an SRv6 Segment Identifier (SID) in the packet. 

In SRv6, an IPv6 address represents an instruction. SRv6 uses a new type of IPv6 Routing Extension Header, called the Segment Routing Header (SRH), in order to encode an ordered list of instructions. The active segment is indicated by the destination address of the packet, and the next segment is indicated by a pointer in the SRH.

In our lab we will be working with SRv6 "micro segment" (SRv6 uSID or just "uSID" for short) instruction. SRv6 uSID is a straightforward extension of the SRv6 Network Programming model:

 - The SRv6 Control Plane is leveraged without any change
 - The SRH dataplane encapsulation is leveraged without any change
 - Any SID in the SID list can carry micro segments
 - Based on the Compressed SRv6 Segment List Encoding in SRH [I-D.ietf-spring-srv6-srh-compression] framework

For a full overview of SRv6 please see the Wiki here: [LINK](/SRv6.md)  
The Cisco IOS-XR 7.5 Configuration guide for SRv6 can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-over-ipv6-srv6-micro-sids.html)

SRv6 uSID locator and source address information for nodes in the lab:

| Router Name | Loopback Int|    Locator Prefix    |    Source-address    |                                           
|:------------|:-----------:|:--------------------:|:--------------------:|                          
| xrd01       | loopback 0  | fc00:0000:1111::/48  | fc00:0000:1111::1    |
| xrd02       | loopback 0  | fc00:0000:2222::/48  | fc00:0000:2222::1    |
| xrd03       | loopback 0  | fc00:0000:3333::/48  | fc00:0000:3333::1    |
| xrd04       | loopback 0  | fc00:0000:4444::/48  | fc00:0000:4444::1    |
| xrd05       | loopback 0  | fc00:0000:5555::/48  | fc00:0000:5555::1    |
| xrd06       | loopback 0  | fc00:0000:6666::/48  | fc00:0000:6666::1    |
| xrd07       | loopback 0  | fc00:0000:7777::/48  | fc00:0000:7777::1    |

    
### Configuration Steps SRv6
#### Configure SRv6 on all routers (xrd01 - xrd07) in the network
1. Enable SRv6 globally and define SRv6 locator and source address for outbound encapsulation 
   - the source address should match the router's loopback0 ipv6 address
   - locator should match the first 48-bits of the router's loopback0
   - to keep things simple we're using the same locator name, 'MyLocator', on all nodes in the network
    ```
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

2. Enable SRv6 for ISIS Procotol. 
    ```
    router isis 100
      address-family ipv6 unicast
         segment-routing srv6
           locator MyLocator
       commit
    ```
  - Note: once you've configured one or two routers using the above steps, the full lab 2 configs for each router can be found [HERE](/lab_2/config/lab_2-configs.md) for quick copy-and-pasting

3. Validation SRv6 configuration and reachability
    ```
    show segment-routing srv6 sid
    ```
    ```
    RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid

    *** Locator: 'MyLocator' *** 

       SID                      Behavior          Context                           Owner               State  RW
       -----------------------  ----------------  --------------------------------  ------------------  -----  --
       fc00:0:1111::            uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
       fc00:0:1111:e000         uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
       fc00:0:1111:e001::       uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
       fc00:0:1111:e002::       uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
       fc00:0:1111:e003::       uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    ```

    - Validate the SRv6 prefix-SID configuration. As example for xrd01 look for ```SID value: fc00:0000:1111::```

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

In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

We'll use 'tcpdump.sh' shell script in the util directory to monitor traffic as it traverses the XRd network. Running "./tcpdump.sh xrd0x-xrd0y" will execute Linux TCPdump on the specified Linux bridge instance that links a pair of XRd routers. Note traffic through the network may travel via one or more ECMP paths, so we may need to try tcpdump.sh on different links before we see anything meaningful in the output

1. Open a new ssh session on the **XRD** VM and cd into the lab's util directory:
```
cd ~/SRv6_dCloud_Lab/util/
```
2. Start the tcpdump.sh script to monitor traffic on a link:
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
If nothing shows up on the tcpdump output try tcpdumping on the *`xrd02-xrd06`* OR *`xrd04-xrd05`* link:
Note: the ./tcpdump.sh break sequence is *ctrl-z*
```
sudo ./tcpdump.sh xrd02-xrd06
```
```
sudo ./tcpdump.sh xrd04-xrd05
```
Eventually pings should show up as tcpdump output. We should see SR-MPLS labels on IPv4 pings, example output below:
<pre><code>
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
sudo tcpdump -ni br-1be0f9f81cbd
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
21:56:27.732243 IS-IS, p2p IIH, src-id 0000.0000.0005, length 1497
21:56:29.539521 MPLS (<mark>label 100007</mark>, exp 0, [S], ttl 254) IP 10.0.0.1 > 10.0.0.7: ICMP echo request, id 5699, seq 0, length 80
21:56:29.541126 MPLS (label 100001, exp 0, [S], ttl 254) IP 10.0.0.7 > 10.0.0.1: ICMP echo reply, id 5699, seq 0, length 80
<pre></code>
IPv6 pings will not invoke SRv6 encapsulation at this time. And with ECMP there's always a chance the return traffic takes a different path:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06 
sudo tcpdump -ni br-b50c608fd524
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-b50c608fd524, link-type EN10MB (Ethernet), capture size 262144 bytes
21:59:25.626912 IS-IS, p2p IIH, src-id 0000.0000.0006, length 1497
21:59:28.110163 IP6 fc00:0000:1111::1 > fc00:0000:7777::1: ICMP6, echo request, seq 0, length 60
21:59:28.114200 IP6 fc00:0000:1111::1 > fc00:0000:7777::1: ICMP6, echo request, seq 1, length 60

cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
sudo tcpdump -ni br-1be0f9f81cbd
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
21:59:08.125911 IP6 fc00:0000:7777::1 > fc00:0000:1111::1: ICMP6, echo reply, seq 0, length 60
21:59:08.129554 IP6 fc00:0000:7777::1 > fc00:0000:1111::1: ICMP6, echo reply, seq 1, length 60
```

## End of Lab 2
Please proceed to [Lab 3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_3/lab_3-guide.md)
