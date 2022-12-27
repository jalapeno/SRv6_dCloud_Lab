# SRv6 Lab 1 Guide

### Description: 
In Lab 1 the student will validate that the supplied topology is up and running and that all baseline 
connectivity is working. Second, they will validate that the pre-configured ISIS and BGP routing protocols are running and seeing the correct topology. Third, there will be lite SR-MPLS configuration on routers 1-7 and 
confirm PE and P roles. Last you will create basic SRv6 configuration on routers 1-7 and confirm connectivity. 

## Contents
1. [Lab Objectives](#lab-objectives)
2. [Validate Device Access](#validate-device-access)
    - [Validate XRD VM](#validate-xrd)
    - [Validate Jalapeno VM](#validate-jalapeno)
    - [Validate Client VMs](#validate-client-vms)
    - [Connect to Routers](#connect-to-routers)
3. [Validate ISIS Topology](#validate-isis-topology)
4. [Validate BGP Topology](#validate-bgp-topology)
5. [Configure and validate SR-MPLS](#sr-mpls)
6. [Configure and validate SRv6](#srv6)
7. [Validate end to end connectivity for both SR and SRv6](#end-to-end-connectivity)
  

## Lab Objectives
The student upon completion of Lab 1 should have achieved the following objectives

* Access to all devices in the lab
* Understanding of the lab topology and components
* Understanding of basic configuration for SR-MPLS
* Understanding of basic configuration for SRv6
   

## Validate Device Access

Device access for this lab is primarly through SSH. All of the VMs within this toplogy can be accessed once you connect through Cisco AnyConnect VPN to the dCloud environment. Please see the management topology network diagram below. In addition their are seven instances of XR routers running as containers on the VM host XRD. The XRD VM acts as a jumpbox for these containerized routers. For router access you will need to SSH into the XRD VM and then initiate a separate SSH session to each of the routers. The XRD VM is configured for DNS resolution for each router name to save time.

### User Credentials
For all instances you will use the same user credentials:
```
User: cisco, Password: cisco123
```

### Management Network Topology

![Management Topology](/topo_drawings/management-network-medium.png)

For full size image see [LINK](/topo_drawings/management-network.png)

### Validate XRD
1. SSH to the Ubuntu VM XRD which is using Docker to host the XRD application
```
ssh cisco@198.18.128.100
```

2. Change to the Git repository directory
    - The lab repository folder is found in the home directory ~/SRv6_dCloud_Lab/

3. Validate there are no docker containers running or docker networks for XRD
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker ps
    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
    
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker network ls
    NETWORK ID     NAME      DRIVER    SCOPE
    cfd793a3a770   bridge    bridge    local
    b948b6ba5918   host      host      local
    bdf431ee7377   none      null      local
    ```
4.  Run the setup script stops any existing XRD docker containers and any XRD docker networks
    - change to the lab_0 directory
    ```
    cisco@xrd:~/SRv6_dCloud_Lab$ cd lab_0
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$
    ```
    - run setup script
    ``` 
    sudo ./setup-lab_0.sh
    ```
    - Look for the below output from the end of the script confirming XRD instances 1-7 were created
    ```
    Creating xrd03 ... done
    Creating xrd04 ... done
    Creating xrd06 ... done
    Creating xrd02 ... done
    Creating xrd05 ... done
    Creating xrd07 ... done
    Creating xrd01 ... done
    ```
    Look for status of `done` for each xrd 01 -> 07

5. Check that the docker containers were created and running
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker ps
    CONTAINER ID   IMAGE                            COMMAND                  CREATED              STATUS              PORTS     NAMES
    37960e0fea97   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd07
    1dd2e4ef748f   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd05
    970b0c888565   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd01
    4bd9ccd3e183   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd02
    9af05fddc01f   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd03
    c48dc39398ef   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd04
    7d0436c26cc8   ios-xr/xrd-control-plane:7.8.1   "/bin/sh -c /sbin/xr…"   About a minute ago   Up About a minute             xrd06
    ```
6. Confirm the docker networks were created. 
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker network ls
    NETWORK ID     NAME                  DRIVER    SCOPE
    cfd793a3a770   bridge                bridge    local
    b948b6ba5918   host                  host      local
    8ff8a898b08c   lab_0_macvlan0        macvlan   local
    62e49899e77a   lab_0_macvlan1        macvlan   local
    f7f3312f9e29   lab_0_mgmt            bridge    local
    2d455a6860aa   lab_0_xrd05-host      bridge    local
    00bae5fdbe48   lab_0_xrd06-host      bridge    local
    bdf431ee7377   none                  null      local
    336a27055564   xrd01-gi1-xrd02-gi0   bridge    local
    da281230d4b3   xrd01-gi2-xrd05-gi0   bridge    local
    a9cdde56cefa   xrd01-gi3             bridge    local
    c254a6c88536   xrd02-gi1-xrd03-gi0   bridge    local
    2fec9b3e52a5   xrd02-gi2-xrd06-gi1   bridge    local
    942edff76963   xrd02-gi3             bridge    local
    7a6f21c0cb6a   xrd03-gi1-xrd04-gi0   bridge    local
    3c6d5ff6828f   xrd03-gi2             bridge    local
    e3eb44320373   xrd03-gi3             bridge    local
    c03ebf10229b   xrd04-gi1-xrd07-gi1   bridge    local
    331c62bb019a   xrd04-gi2-xrd05-gi1   bridge    local
    8a2cb5e8083d   xrd04-gi3             bridge    local
    b300884b2030   xrd05-gi2-xrd06-gi2   bridge    local
    b48429454f4c   xrd06-gi0-xrd07-gi2   bridge    local
    84b7ddd7e018   xrd07-gi3             bridge    local
    ```
Note the docker Network IDs are unique on creation. Docker's network/bridge naming logic is such that the actual bridge instance names are not predictable. Rather than go through some renaming process the lab setup script calls another small script that resolves the bridge name and writes it to a file that we'll use later for running tcpdump on the virtual links between routers in our topology.

 - The scripts and files reside in the lab 'util' directory:
```
cisco@xrd:~/SRv6_dCloud_Lab$ ls ~/SRv6_dCloud_Lab/util/
nets.sh     xrd01-xrd02  xrd02-xrd03  xrd03-xrd04  xrd04-xrd07  xrd06-xrd07
tcpdump.sh  xrd01-xrd05  xrd02-xrd06  xrd04-xrd05  xrd05-xrd06
cisco@xrd:~/SRv6_dCloud_Lab$ 
```
Later we'll use "tcpdump.sh <xrd0x-xrd0y>" to capture packets along the path through the network. 

7. The XRD router instances should be available for access 2 minutes after spin up.

### Validate Jalapeno VM
1. SSH to the Ubuntu VM Jalapeno which is using Kubernetes to host the Jalapeno application
2. Check that the interface to routers xrd05 and xrd06 is up and has assigned IP 198.18.1.101
```
    cisco@jalapeno:~$ ip address show ens192
    3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        link/ether 00:50:56:97:15:aa brd ff:ff:ff:ff:ff:ff
        altname enp11s0
        inet 198.18.1.101/24 brd 198.18.1.255 scope global noprefixroute ens192
        valid_lft forever preferred_lft forever
        inet6 fe80::250:56ff:fe97:15aa/64 scope link 
        valid_lft forever preferred_lft forever
```
3. Connect to xrd05 and xrd06 and validate reachability to the Jalapeno VM:
```
cisco@xrd:~/SRv6_dCloud_Lab$ ssh xrd05
Warning: Permanently added 'xrd05,10.254.254.105' (ECDSA) to the list of known hosts.
Password: 
Last login: Mon Dec 26 20:57:32 2022 from 10.254.254.1

RP/0/RP0/CPU0:xrd05#sho run int gi0/0/0/3
Mon Dec 26 20:58:10.227 UTC
interface GigabitEthernet0/0/0/3
 description to Internet
 cdp
 ipv4 address 198.18.1.2 255.255.255.0
 ipv6 address 2001:1:1:1::1a/125
!
RP/0/RP0/CPU0:xrd05#ping 198.18.1.101
Mon Dec 26 20:58:14.751 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.18.1.101 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms
RP/0/RP0/CPU0:xrd05#
```

### Validate Client VMs

__Rome__

In our lab the Rome VM represents a standard linux host or endpoint, and is essentially a customer/user of our network.

1. SSH to Rome Client VM from your laptop. 
2. Check that the interface to router xrd07 is `UP` and has the assigned IP `10.107.1.1/24`
    ```
    cisco@rome:~$ ip address show ens192
    3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        link/ether 00:50:56:aa:ab:cf brd ff:ff:ff:ff:ff:ff
        inet 10.107.1.1/24 brd 10.107.1.255 scope global ens192
        valid_lft forever preferred_lft forever
        inet6 fc00:0:107:1:250:56ff:feaa:abcf/64 scope global dynamic mngtmpaddr noprefixroute 
        valid_lft 2591929sec preferred_lft 604729sec
        inet6 fc00:0:107:1::1/64 scope global 
        valid_lft forever preferred_lft forever
        inet6 fe80::250:56ff:feaa:abcf/64 scope link 
        valid_lft forever preferred_lft forever
    ```
3. Check connectivity from Rome to xrd07
    ```
    cisco@rome:~$ ping -c 3 10.107.1.2
    PING 10.107.1.2 (10.107.1.2) 56(84) bytes of data.
    64 bytes from 10.107.1.2: icmp_seq=1 ttl=255 time=2.70 ms
    64 bytes from 10.107.1.2: icmp_seq=2 ttl=255 time=1.38 ms
    64 bytes from 10.107.1.2: icmp_seq=3 ttl=255 time=1.30 ms
    ```

__Amsterdam__

The Amsterdam VM represents a server belonging to a cloud, CDN, or gaming company that serves content to end users (such as the Rome VM) or customer applications over our network. The Amsterdam VM comes with VPP pre-installed. VPP (also known as https://fd.io/) is a very flexible and high performance open source software dataplane. 

1. SSH to Amsterdam Client VM from your laptop. 
2. Check that the VPP interface facing Ubuntu (host-vpp-in) and the interface facing router xrd01 (GigabitEthernetb/0/0) are `UP` and have their assigned IP addresses. GigabitEthernetb/0/0: `10.101.1.1/24`, and host-vpp-in: `10.101.1.1/24` 
    ```
cisco@amsterdam:~$ sudo vppctl show interface address
GigabitEthernetb/0/0 (up):
  L3 10.101.1.1/24
  L3 fc00:0:101:1::1/64
host-vpp-in (up):
  L3 10.101.2.2/24
    ```
3. Check connectivity from Amsterdam to xrd01 - we'll issue a ping from VPP itself:
    ```
cisco@amsterdam:~$ sudo vppctl ping 10.101.1.2
116 bytes from 10.101.1.2: icmp_seq=1 ttl=255 time=2.7229 ms
116 bytes from 10.101.1.2: icmp_seq=2 ttl=255 time=1.1550 ms
116 bytes from 10.101.1.2: icmp_seq=3 ttl=255 time=1.1341 ms
116 bytes from 10.101.1.2: icmp_seq=4 ttl=255 time=1.2277 ms
116 bytes from 10.101.1.2: icmp_seq=5 ttl=255 time=.8838 ms

Statistics: 5 sent, 5 received, 0% packet loss
cisco@amsterdam:~$ 
    ```

### Connect to Routers
1. Starting from the XRD VM log into each router instance 1-7 per the management topology diagram above. Example:
```
ssh cisco@xrd01
```

2. Confirm that the configured interfaces are in an `UP | UP` state
    ```
    RP/0/RP0/CPU0:xrd01#show ip interface brief
    
    Interface                      IP-Address      Status          Protocol Vrf-Name
    Loopback0                      10.0.0.1        Up              Up       default 
    MgmtEth0/RP0/CPU0/0            10.254.254.101  Up              Up       default 
    GigabitEthernet0/0/0/0         10.101.1.2      Up              Up       default 
    GigabitEthernet0/0/0/1         10.1.1.0        Up              Up       default 
    GigabitEthernet0/0/0/2         10.1.1.8        Up              Up       default 
    GigabitEthernet0/0/0/3         unassigned      Shutdown        Down     default
    ```
3. Validate IPv6 connectivity from xrd01 to Amsterdam VM: 
```
ping fc00:0:101:1::1
```
4. Validate adjacencies and traffic passing on each router. Use the topology diagram to determine neighbors. The client devices Amsterdam and Rome are not running CDP.
    ```
    RP/0/RP0/CPU0:xrd05#show cdp neighbors 
    Wed Dec 21 18:16:57.657 UTC
    Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                    S - Switch, H - Host, I - IGMP, r - Repeater

    Device ID       Local Intrfce    Holdtme Capability Platform  Port ID
    xrd01           Gi0/0/0/0        121     R          XRd Contr Gi0/0/0/2       
    xrd04           Gi0/0/0/1        179     R          XRd Contr Gi0/0/0/2       
    xrd06           Gi0/0/0/2        124     R          XRd Contr Gi0/0/0/2  
    ```

## Validate ISIS Topology

In this lab we are using ISIS as the underlying IGP to establish link connectivity across routers xrd01 -> xrd07. ISIS has basic settings pre-configured at startup in lab 1. The student will want to confirm that they see a full ISIS topology.

![ISIS Topology](/topo_drawings/isis-topology-medium.png)

For full size image see [LINK](/topo_drawings/isis-topology-large.png)

The Cisco IOS-XR 7.5 Configuration guide for SR and ISIS can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-for-is-is-protocol.html)

1. Log into each router and verify that ISIS is up and running on interfaces as identified in the ISIS topology diagram.
    ```
    RP/0/RP0/CPU0:xrd03#show isis interface brief
    Thu Dec 22 17:45:24.348 UTC

    IS-IS 100 Interfaces
        Interface      All     Adjs    Adj Topos  Adv Topos  CLNS   MTU    Prio  
                    OK    L1   L2    Run/Cfg    Run/Cfg                L1   L2
    -----------------  ---  ---------  ---------  ---------  ----  ----  --------
    Lo0                Yes    -    -      0/0        2/2     No       -    -    - 
    Gi0/0/0/0          Yes    -    1      2/2        2/2     Up    1497    -    - 
    Gi0/0/0/1          Yes    -    1      2/2        2/2     Up    1497    -    - 
    ```

2. The ISIS topology can be validated from any router. The command output will vary slightly based on router used.
    ```
    RP/0/RP0/CPU0:xrd03#show isis topology

    IS-IS 100 paths to IPv4 Unicast (Level-1) routers
    System Id          Metric    Next-Hop           Interface       SNPA          
    xrd03              --      

    IS-IS 100 paths to IPv4 Unicast (Level-2) routers
    System Id          Metric    Next-Hop           Interface       SNPA          
    xrd01              2         xrd02              Gi0/0/0/0       *PtoP*        
    xrd02              1         xrd02              Gi0/0/0/0       *PtoP*        
    xrd03              --      
    xrd04              1         xrd04              Gi0/0/0/1       *PtoP*        
    xrd05              2         xrd04              Gi0/0/0/1       *PtoP*        
    xrd06              2         xrd02              Gi0/0/0/0       *PtoP*        
    xrd07              2         xrd04              Gi0/0/0/1       *PtoP* 
    ```
3. Validate end-to-end ISIS reachability:
```
ping 10.0.0.7 source lo0
ping fc00:0:7::1 source lo0
```

## Validate BGP Topology

In this lab we are using BGP for SRv6 route/community exchange. In the lab we are running a single AS 65000 with BGP running on xrd01, xrd05, xrd06, xrd07.  Routers xrd05 and xrd06 are functioning as route reflectors and xrd01 and xrd07 are clients. The student will want to confirm that they see a full BGP topology.

![BGP Topology](/topo_drawings/bgp-topology-medium.png)

For full size image see [LINK](/topo_drawings/bgp-topology-large.png)

The Cisco IOS-XR 7.5 Configuration guide for SR and BGP can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-for-bgp.html)

1. Log into each router listed in the BGP topology diagram and verify neighbors
    ```
    RP/0/RP0/CPU0:xrd01#show ip bgp neighbors brief

    Neighbor        Spk    AS Description                          Up/Down  NBRState
    10.0.0.5          0 65000 iBGP to xrd05 RR                     00:18:07 Established 
    10.0.0.6          0 65000 iBGP to xrd06 RR                     00:18:24 Established 
    fc00:0:5::1       0 65000 iBGPv6 to xrd05 RR                   00:22:02 Established 
    fc00:0:6::1       0 65000 iBGPv6 to xrd06 RR                   00:21:16 Established 
    ``` 
2. Verify that router xrd01 is advertising the attached network ```10.101.1.0/24```
    ```
    RP/0/RP0/CPU0:xrd01#show ip bgp advertised summary
    Network            Next Hop        From            Advertised to
    10.0.0.1/32        10.0.0.1        Local           10.0.0.5
                                       Local           10.0.0.6
    10.101.1.0/24      10.0.0.1        Local           10.0.0.5
                                       Local           10.0.0.6
    ```
3. Verify that router xrd07 is advertising the attached network ```10.107.1.0/24```   
    ```
    RP/0/RP0/CPU0:xrd07#show ip bgp advertised summary
    Thu Dec 22 17:53:57.114 UTC
    Network            Next Hop        From            Advertised to
    10.0.0.7/32        10.0.0.7        Local           10.0.0.5
                                       Local           10.0.0.6
    10.107.1.0/24      10.0.0.7        Local           10.0.0.5
                                       Local           10.0.0.6
    ```
4. Verify that router xrd01 has received route ```10.107.1.0/24``` from the route reflectors xrd05 and xrd07. Look for ```Paths: (2 available)```
    ```
    RP/0/RP0/CPU0:xrd01#show ip bgp 10.107.1.0/24
    BGP routing table entry for 10.107.1.0/24
    Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  16           16
        Local Label: 24003
    Last Modified: Dec 22 17:31:37.792 for 00:24:38
    Paths: (2 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
        10.0.0.7 (metric 3) from 10.0.0.5 (10.0.0.7)
        Received Label 3 
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best, labeled-unicast
        Received Path ID 0, Local Path ID 1, version 16
        Originator: 10.0.0.7, Cluster list: 10.0.0.5
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
        10.0.0.7 (metric 3) from 10.0.0.6 (10.0.0.7)
        Received Label 3 
        Origin IGP, metric 0, localpref 100, valid, internal, labeled-unicast
        Received Path ID 0, Local Path ID 0, version 0
        Originator: 10.0.0.7, Cluster list: 10.0.0.6
    ```
5. Verify that router xrd07 has received route ```10.101.1.0/24``` from the route reflectors xrd05 and xrd07. Look for ```Paths: (2 available)```
    ```
    RP/0/RP0/CPU0:xrd07#show ip bgp 10.101.1.0/24
    Thu Dec 22 17:59:31.604 UTC
    BGP routing table entry for 10.101.1.0/24
    Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  15           15
    Last Modified: Dec 22 17:31:37.792 for 00:27:53
    Paths: (2 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
        10.0.0.1 (metric 3) from 10.0.0.5 (10.0.0.1)
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best
        Received Path ID 0, Local Path ID 1, version 15
        Originator: 10.0.0.1, Cluster list: 10.0.0.5
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
        10.0.0.1 (metric 3) from 10.0.0.6 (10.0.0.1)
        Received Label 3 
        Origin IGP, metric 0, localpref 100, valid, internal, labeled-unicast
        Received Path ID 0, Local Path ID 0, version 0
        Originator: 10.0.0.1, Cluster list: 10.0.0.6
    ```

## SR-MPLS

Segment Routing (SR) is a source-based routing architecture. A node chooses a path and steers a packet through the network via that path by inserting an ordered list of segments, instructing how subsequent nodes in the path that receive the packet should process it. This simplifies operations and reduces resource requirements in the network by removing network state information from intermediary nodes as path information is encoded as an ordered list of segments in label stack at the ingress node. In addition to this, because the shortest-path segment includes all Equal-Cost Multi-Path (ECMP) paths to the related node, SR supports the ECMP nature of IP by design. In Lab 1 we will add some basic SR-MPLS commands to xrd01 -> xrd07. 

For a full overview of SR-MPLS please see the Wiki here: [LINK](/SR-MPLS.md)  
The Cisco IOS-XR 7.5 Configuration guide for SR-MPLS can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-for-is-is-protocol.html)

### Configuration Steps SR-MPLS
1. Enable SR-MPLS globally and define an SRGB (we use 100000 - 163999 for easy reading)
    ```
    segment-routing 
      global-block 100000 163999
    commit
    ```

2. Enable SR-MPLS for ISIS Procotol. 
    ```
    router isis 100    
      address-family ipv4
        segment-routing mpls
    commit
    ```

3. Configure a Prefix-SID on ISIS Loopback Interface
    A prefix segment identifier (SID) is associated with an IP prefix. The prefix SID is manually configured from the segment routing global block. A prefix SID is configured under the loopback interface with the loopback address of the node as the prefix. The prefix segment steers the traffic along the shortest path to its destination. In our lab configurations we will be using Prefix SID Indexes. Consult the table below then configure the prefix SID on routes xrd01 -> xrd07


    | Router Name | Loopback Int| Prefix-SID |                                           
    |:------------|:-----------:|:----------:|                          
    | xrd01       | loopback 0  | 1          |
    | xrd02       | loopback 0  | 2          |
    | xrd03       | loopback 0  | 3          |
    | xrd04       | loopback 0  | 4          |
    | xrd05       | loopback 0  | 5          |
    | xrd06       | loopback 0  | 6          |
    | xrd07       | loopback 0  | 7          |

    Configuration example:
    ```
    router isis 100
      interface loopback 0
        address-family ipv4 unicast 
        prefix-sid index 1
    commit
    ```

4. Verify that ISIS Prefix-SID configuartion. As example for xrd01 look for ```Prefix-SID Index: 1```
    ```
    RP/0/RP0/CPU0:xrd01#show isis database verbose | i Prefix-SID
        Prefix-SID Index: 1, Algorithm:0, R:0 N:1 P:0 E:0 V:0 L:0
        Prefix-SID Index: 1, Algorithm:0, R:0 N:1 P:0 E:0 V:0 L:0
    RP/0/RP0/CPU0:xrd01#
    ```
   - other validations
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
    Validate the mpls forwarding table
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

In our lab we will be working with SRv6 "micro segment" (SRv6 uSID or uSID for short) instruction. SRv6 uSID is a straightforward extension of the SRv6 Network Programming model:

 - The SRv6 Control Plane is leveraged without any change
 - The SRH dataplane encapsulation is leveraged without any change
 - Any SID in the SID list can carry micro segments
 - Based on the Compressed SRv6 Segment List Encoding in SRH [I-D.ietf-spring-srv6-srh-compression] framework

For a full overview of SRv6 please see the Wiki here: [LINK](/SRv6.md)  
The Cisco IOS-XR 7.5 Configuration guide for SRv6 can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/75x/b-segment-routing-cg-cisco8000-75x/configuring-segment-routing-over-ipv6-srv6-micro-sids.html)

SRv6 uSID locator and source address information for nodes in the lab:


    | Router Name | Loopback Int| Locator Prefix | Source-address |                                           
    |:------------|:-----------:|:--------------:|:--------------:|                          
    | xrd01       | loopback 0  | fc00:0:1::/48  | fc00:0:1::1    |
    | xrd02       | loopback 0  | fc00:0:2::/48  | fc00:0:2::1    |
    | xrd03       | loopback 0  | fc00:0:3::/48  | fc00:0:3::1    |
    | xrd04       | loopback 0  | fc00:0:4::/48  | fc00:0:4::1    |
    | xrd05       | loopback 0  | fc00:0:5::/48  | fc00:0:5::1    |
    | xrd06       | loopback 0  | fc00:0:6::/48  | fc00:0:6::1    |
    | xrd07       | loopback 0  | fc00:0:7::/48  | fc00:0:7::1    |

### Configuration Steps SRv6
1. Enable SRv6 globally and define SRv6 locator and source address for outbound encapsulation 
   - the source address should match the router's loopback0 ipv6 address
   - locator should match the first 48-bits of the router's loopback0
    ```
    segment-routing
      srv6
        encapsulation
          source-address fc00:0:1::1

    locators
    locator MAIN
        micro-segment behavior unode psp-usd
        prefix fc00:0:1::/48
    ```

2. Enable SRv6 for ISIS Procotol. 
    ```
    router isis 100
      address-family ipv6 unicast
         segment-routing srv6
           locator MAIN
    ```
 3. Validation SRv6 configuration and reachability
    ```
    RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid

    *** Locator: 'MAIN' *** 

    SID                         Behavior          Context                           Owner               State  RW
    --------------------------  ----------------  --------------------------------  ------------------  -----  --
    fc00:0:1::                  uN (PSP/USD)      'default':1                       sidmgr              InUse  Y 
    fc00:0:1:e000::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1:e001::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1:e002::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1:e003::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1:e004::             uDT4              'carrots'                         bgp-65000           InUse  Y 
    RP/0/RP0/CPU0:xrd01#
    ```

    - Validate the SRv6 prefix-SID configuration. As example for xrd01 look for ```SID value: fc00:0:1::```

    ```
    RP/0/RP0/CPU0:xrd01#show isis segment-routing srv6 locators detail 

    IS-IS 100 SRv6 Locators
    Name                  ID       Algo  Prefix                    Status
    ------                ----     ----  ------                    ------
    MAIN                  1        0     fc00:0:1::/48             Active
    Advertised Level: level-1-2   
    Level: level-1      Metric: 1        Administrative Tag: 0         
    Level: level-2-only Metric: 1        Administrative Tag: 0         
    SID behavior: uN (PSP/USD)
    SID value:    fc00:0:1::
    Block Length: 32, Node Length: 16, Func Length: 0, Args Length: 80
    ```
## End-to-End Connectivity

We'll use the tcpdump.sh in the SRv6_dCloud_Lab/util/ directory to monitor traffic as it traverses the XRd network. Traffic through the network may travel via one or more ECMP paths, so we may need to try tcpdump.sh on different links before we see anything meaningful in the output

1. Open a new ssh session on the XRD VM and cd into the lab's util directory:
```
cd ~/SRv6_dCloud_Lab/util/
```
2. Start the tcpdump.sh script to monitor traffic on a link:
```
./tcpdump.sh xrd05-xrd06
```
3. Run some pings from xrd01 to xrd07:
```
ping 10.0.0.7 source lo0
ping fc00:0:7::1 source lo0
```
If nothing shows up on the tcpdump output try tcpdumping on the xrd02-xrd06 or xrd04-xrd05 link:
```
./tcpdump.sh xrd02-xrd06
./tcpdump.sh xrd04-xrd05
```
Eventually pings should show up as tcpdump output. We should see SR-MPLS labels on IPv4 pings, something like this:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
sudo tcpdump -ni br-1be0f9f81cbd
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
21:56:27.732243 IS-IS, p2p IIH, src-id 0000.0000.0005, length 1497
21:56:29.539521 MPLS (label 100007, exp 0, [S], ttl 254) IP 10.0.0.1 > 10.0.0.7: ICMP echo request, id 5699, seq 0, length 80
21:56:29.541126 MPLS (label 100001, exp 0, [S], ttl 254) IP 10.0.0.7 > 10.0.0.1: ICMP echo reply, id 5699, seq 0, length 80
```
IPv6 pings will not invoke SRv6 encapsulation at this time:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06 
sudo tcpdump -ni br-b50c608fd524
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-b50c608fd524, link-type EN10MB (Ethernet), capture size 262144 bytes
21:59:25.626912 IS-IS, p2p IIH, src-id 0000.0000.0006, length 1497
21:59:28.110163 IP6 fc00:0:1::1 > fc00:0:7::1: ICMP6, echo request, seq 0, length 60
21:59:28.114200 IP6 fc00:0:1::1 > fc00:0:7::1: ICMP6, echo request, seq 1, length 60

cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
sudo tcpdump -ni br-1be0f9f81cbd
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
21:59:08.125911 IP6 fc00:0:7::1 > fc00:0:1::1: ICMP6, echo reply, seq 0, length 60
21:59:08.129554 IP6 fc00:0:7::1 > fc00:0:1::1: ICMP6, echo reply, seq 1, length 60
```
4. Run some pings to/from Amsterdam and Rome VMs:
 - Amsterdam ping Rome (using VPP):

```
sudo vppctl ping 10.107.1.1
```
 - Rome ping Amsterdam: 
```
ping 10.101.1.1
```
Tcpdump.sh output should show SR-MPLS encapsulation of traffic on some set of links through the network. We'll see SRv6 encapsulated traffic in labs 2 - 6.

Feel free to experiment with the tcpdump script on other links while pinging to/from different nodes in the network.

### End of lab 1
Please proceed to [lab_2](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_2)