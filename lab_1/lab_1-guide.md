# Lab 1 Guide: XRd Topology Setup and Validation
The Cisco Live LTRSPG-2212 lab makes heavy use of the relatively new Dockerized IOS-XR router known as XRd. If you wish to explore XRd and its uses beyond the scope of this lab the xrdocs team has posted a number of XRd tutorials here: https://xrdocs.io/virtual-routing/tags/#xrd-tutorial-series

### Description: 
In Lab 1 the student will launch the XRd topology and validate it is up and running. This will be the baseline 
topology all subsequent lab exercises. Second, they will validate that the pre-configured ISIS and BGP routing protocols are running and seeing the correct topology. 

## Contents
- [Lab 1 Guide: XRd Topology Setup and Validation](#lab-1-guide-xrd-topology-setup-and-validation)
    - [Description:](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Validate Device Access](#validate-device-access)
    - [User Credentials](#user-credentials)
    - [Management Network Topology](#management-network-topology)
    - [Launch and Validate XRD Topology](#launch-and-validate-xrd-topology)
    - [Validate Jalapeno VM](#validate-jalapeno-vm)
    - [Validate Client VMs](#validate-client-vms)
    - [Connect to Routers](#connect-to-routers)
  - [Validate ISIS Topology](#validate-isis-topology)
  - [Validate BGP Topology](#validate-bgp-topology)
    - [End of Lab 1](#end-of-lab-1)
  
## Lab Objectives
The student upon completion of Lab 1 should have achieved the following objectives:

* Access to all devices in the lab
* Deployed the XRd network topology
* Understanding of the lab topology and components
* Confirm IPv4 and IPv6 connectivity   

## Validate Device Access

Device access for this lab is primarly through SSH. All of the VMs within this toplogy can be accessed once you connect through Cisco AnyConnect VPN to the dCloud environment. Please see the management topology network diagram below. In addition we will launch seven instances of XR routers running as containers on the VM host "XRD". The XRD VM acts as a jumpbox for these containerized routers, thus we will SSH into the XRD VM and then initiate a separate SSH session to each of the routers. The XRD VM is configured for DNS resolution for each router name to save time.

### User Credentials
For all instances you will use the same user credentials:
```
User: cisco, Password: cisco123
```

### Management Network Topology

![Management Topology](/topo_drawings/management-network-medium.png)

For full size image see [LINK](/topo_drawings/management-network.png)

### Launch and Validate XRD Topology
1. SSH to the Ubuntu VM XRD where we will launch the XRd routers
```
ssh cisco@198.18.128.100
```

2. Change to the Git repository directory
    - The lab repository folder is found in the home directory ~/SRv6_dCloud_Lab/

3. Validate there are no docker containers running or docker networks for XRD
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/lab_1$ docker ps
    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
    
    cisco@xrd:~/SRv6_dCloud_Lab/lab_1$ docker network ls
    NETWORK ID     NAME      DRIVER    SCOPE
    cfd793a3a770   bridge    bridge    local
    b948b6ba5918   host      host      local
    bdf431ee7377   none      null      local
    ```
4.  Run the setup script, which should clean up any existing XRd containers and docker networks, then launch the topology into the "beginning of lab 1" configuration state 
    - change to the lab_1 directory
    ```
    cisco@xrd:~/SRv6_dCloud_Lab$ cd lab_1
    cisco@xrd:~/SRv6_dCloud_Lab/lab_1$
    ```
    - run setup script
    ``` 
    sudo ./setup-lab_1.sh
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
    cisco@xrd:~/SRv6_dCloud_Lab/lab_1$ docker ps
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
    cisco@xrd:~/SRv6_dCloud_Lab/lab_1$ docker network ls
    NETWORK ID     NAME                  DRIVER    SCOPE
    cfd793a3a770   bridge                bridge    local
    b948b6ba5918   host                  host      local
    8ff8a898b08c   lab_1_macvlan0        macvlan   local
    62e49899e77a   lab_1_macvlan1        macvlan   local
    f7f3312f9e29   lab_1_mgmt            bridge    local
    2d455a6860aa   lab_1_xrd05-host      bridge    local
    00bae5fdbe48   lab_1_xrd06-host      bridge    local
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
Note the docker Network IDs are unique on creation. Docker's network/bridge naming logic is such that the actual Linux bridge instance names are not predictable. Rather than go through some re-naming process the lab setup script calls another small script 'nets.sh' that resolves the bridge name and writes it to a file that we'll use later for running tcpdump on the virtual links between routers in our topology.

 - The scripts and files reside in the lab 'util' directory:
```
cisco@xrd:~/SRv6_dCloud_Lab$ ls ~/SRv6_dCloud_Lab/util/
nets.sh     xrd01-xrd02  xrd02-xrd03  xrd03-xrd04  xrd04-xrd07  xrd06-xrd07
tcpdump.sh  xrd01-xrd05  xrd02-xrd06  xrd04-xrd05  xrd05-xrd06

```
Later we'll use "tcpdump.sh xrd0x-xrd0y" to capture packets along the path through the network. 

7. The XRD router instances should be available for access 2 minutes after spin up.

### Validate Jalapeno VM
The Ubuntu VM Jalapeno has Kubernetes pre-installed and running. Later in lab exercise 5 we will install the open-source Jalapeno application.

Jalapeno will collect BGP Monitoring Protocol (BMP) and streaming telemetry data from the routers, and will serve as a data repository for the SDN clients we'll have running on the Amsterdam and Rome VMs (Labs 5-7).

1. Validate router reachability to Jalapeno VM (no need to check all routers, but will be good to validate xrd01, 05, 06, and 07):
```
cisco@xrd:~$ ssh xrd01
Warning: Permanently added 'xrd01,10.254.254.101' (ECDSA) to the list of known hosts.
Password: 
Last login: Fri Jan  6 21:45:12 2023 from 10.254.254.1

RP/0/RP0/CPU0:xrd01#ping 198.18.128.101
Fri Jan  6 22:25:45.006 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.18.128.101 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/2 ms
RP/0/RP0/CPU0:xrd01#

```

### Validate Client VMs

__Rome__

In our lab the Rome VM represents a standard linux host or endpoint, and is essentially a customer/user of our network.

1. SSH to Rome Client VM from your laptop. 

```
ssh cisco@198.18.128.103
```

2. Check that the interface to router xrd07 is `UP` and has the assigned IP `10.107.1.1/24`
    ```
    cisco@rome:~$ ip address show ens192
    3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        link/ether 00:50:56:aa:ab:cf brd ff:ff:ff:ff:ff:ff
        inet <strong>10.107.1.1/24</strong> brd 10.107.1.255 scope global ens192  <------- Here
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
4. Check connectivity from Rome to Jalapeno VM
```
cisco@rome:~$ ping -c 1 198.18.128.101
PING 198.18.128.101 (198.18.128.101) 56(84) bytes of data.
64 bytes from 198.18.128.101: icmp_seq=1 ttl=64 time=0.428 ms
```

__Amsterdam__

The Amsterdam VM represents a server belonging to a cloud, CDN, or gaming company that serves content to end users (such as the Rome VM) or customer applications over our network. The Amsterdam VM comes with VPP pre-installed. VPP (also known as https://fd.io/) is a very flexible and high performance open source software dataplane. 

1. SSH to Amsterdam Client VM from your laptop. 

```
ssh cisco@198.18.128.102
```

2. Check that the VPP interface facing Ubuntu (host-vpp-in) and the interface facing router xrd01 (GigabitEthernetb/0/0) are `UP` and have their assigned IP addresses. GigabitEthernetb/0/0: `10.101.1.1/24`, and host-vpp-in: `10.101.2.2/24` 
    
    ```
    sudo vppctl show interface address
    ```
    ```
    cisco@amsterdam:~$ sudo vppctl show interface address
    GigabitEthernetb/0/0 (up):
    L3 10.101.1.1/24        <-------HERE
    L3 fc00:0:101:1::1/64
    host-vpp-in (up):
    L3 10.101.2.2/24        <-------HERE
    ```
3. Check connectivity from Amsterdam to xrd01 - we'll issue a ping from VPP itself:
    ```
    sudo vppctl ping 10.101.1.2
    ```
    
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
4. Check connectivity from Amsterdam to Jalapeno VM
```
cisco@amsterdam:~$ ping -c 1 198.18.128.101
PING 198.18.128.101 (198.18.128.101) 56(84) bytes of data.
64 bytes from 198.18.128.101: icmp_seq=1 ttl=64 time=0.619 ms
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

4. SSH to xrd07 and validate IPv6 connectivity to the Rome VM: 
```
ping fc00:0:107:1::1
```

5. Validate adjacencies and traffic passing on each router. Use the topology diagram to determine neighbors. The client devices Amsterdam and Rome are not running CDP.
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
3. On xrd01 validate end-to-end ISIS reachability:
```
ping 10.0.0.7 source lo0
ping fc00:0000:7777::1 source lo0
```
 - Note: normally pinging xrd-to-xrd in this dockerized environment would result in ping times of ~1-3ms. However, the util/nets.sh script, which was triggered at setup, added synthetic latency to the underlying Linux links using the [netem](https://wiki.linuxfoundation.org/networking/netem) 'tc' command line tool. So you'll see a ping RTT of anywhere from ~60ms to ~150ms. This synthetic latency will allow us to really see the effect of later traffic steering execises.

    Command to see the added synthetic latency:
    ```
    sudo tc qdisc list | grep delay
    ```

## Validate BGP Topology

In lab 1 BGP is only exchanging IPv6 prefixes and BGP-LS data. We will setup IPv4 labeled-unicast and SRv6-L3VPN in later lab exercises. In the topology we are running a single ASN 65000 with BGP running on xrd01, xrd05, xrd06, xrd07.  Routers xrd05 and xrd06 are functioning as route reflectors and xrd01 and xrd07 are clients. The student will want to confirm that they see a full BGP topology.

![BGP Topology](/topo_drawings/bgp-topology-medium.png)

For full size image see [LINK](/topo_drawings/bgp-topology-large.png)

1. Log into each router listed in the BGP topology diagram and verify neighbors
    ```
    RP/0/RP0/CPU0:xrd01#show ip bgp neighbors brief

    Neighbor        Spk    AS Description                          Up/Down  NBRState
    10.0.0.5          0 65000 iBGP to xrd05 RR                     00:18:07 Established 
    10.0.0.6          0 65000 iBGP to xrd06 RR                     00:18:24 Established 
    fc00:0000:5555::1       0 65000 iBGPv6 to xrd05 RR                   00:22:02 Established 
    fc00:0000:6666::1       0 65000 iBGPv6 to xrd06 RR                   00:21:16 Established 
    ``` 
2. Verify that router xrd01 is advertising the attached ipv6 network ```fc00:0:101:1::/64``` 
    ```
    RP/0/RP0/CPU0:xrd01#show bgp ipv6 unicast advertised summary
    Tue Jan 10 21:40:56.812 UTC
    Network            Next Hop        From            Advertised to
    fc00:0:101:1::/64  fc00:0:1111::1  Local           fc00:0:5555::1
                                    Local           fc00:0:6666::1
    fc00:0:1111::1/128 fc00:0:1111::1  Local           fc00:0:5555::1
                                    Local           fc00:0:6666::1

    Processed 2 prefixes, 4 paths
    ```
3. Verify that router xrd07 is advertising the attached network ```fc00:0:107:1::/64```   
    ```
    RP/0/RP0/CPU0:xrd07#show bgp ipv6 unicast advertised summary
    Tue Jan 10 21:46:43.311 UTC
    Network            Next Hop        From            Advertised to
    fc00:0:107:1::/64  fc00:0:7777::1  Local           fc00:0:5555::1
                                    Local           fc00:0:6666::1
    fc00:0:7777::1/128 fc00:0:7777::1  Local           fc00:0:5555::1
                                    Local           fc00:0:6666::1

    Processed 2 prefixes, 4 paths
    ```
4. Verify that router xrd01 has received route ```fc00:0:107:1::/64``` from the route reflectors xrd05 and xrd07. Look for ```Paths: (2 available)```
    ```
    RP/0/RP0/CPU0:xrd01#show bgp ipv6 unicast fc00:0:107:1::/64
    Tue Jan 10 21:47:51.153 UTC
    BGP routing table entry for fc00:0:107:1::/64
    Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  17           17
    Last Modified: Jan 10 21:46:29.402 for 00:01:21
    Paths: (2 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best
        Received Path ID 0, Local Path ID 1, version 17
        Originator: 10.0.0.7, Cluster list: 10.0.0.5
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
        Origin IGP, metric 0, localpref 100, valid, internal
        Received Path ID 0, Local Path ID 0, version 0
        Originator: 10.0.0.7, Cluster list: 10.0.0.6
    ```
5. Verify that router xrd07 has received route ```fc00:0:101:1::/64``` from the route reflectors xrd05 and xrd07. Look for ```Paths: (2 available)```
    ```
    RP/0/RP0/CPU0:xrd07#show bgp ipv6 unicast fc00:0:101:1::/64
    Tue Jan 10 21:48:45.627 UTC
    BGP routing table entry for fc00:0:101:1::/64
    Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  18           18
    Last Modified: Jan 10 21:40:29.922 for 00:08:15
    Paths: (2 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:1111::1 (metric 3) from fc00:0:5555::1 (10.0.0.1)
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best
        Received Path ID 0, Local Path ID 1, version 18
        Originator: 10.0.0.1, Cluster list: 10.0.0.5
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:1111::1 (metric 3) from fc00:0:6666::1 (10.0.0.1)
        Origin IGP, metric 0, localpref 100, valid, internal
        Received Path ID 0, Local Path ID 0, version 0
        Originator: 10.0.0.1, Cluster list: 10.0.0.6
    ```

6. Verify the route-reflectors have received BGP-LS NLRIs from xrd01 and xrd07:
    ```
    RP/0/RP0/CPU0:xrd05#show bgp link-state link-state sum
    Tue Jan 10 21:49:40.069 UTC
    BGP router identifier 10.0.0.5, local AS number 65000
    BGP generic scan interval 60 secs
    Non-stop routing is enabled
    BGP table state: Active
    Table ID: 0x0   RD version: 187
    BGP main routing table version 187
    BGP NSR Initial initsync version 1 (Reached)
    BGP NSR/ISSU Sync-Group versions 0/0
    BGP scan interval 60 secs

    BGP is operating in STANDALONE mode.


    Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
    Speaker             187        187        187        187         187           0

    Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
    10.0.0.1          0 65000      55      21      187    0    0 00:18:49         93
    10.0.0.7          0 65000      55      21      187    0    0 00:18:16         93
    ```

7. Optional: display the entire BGP-LS table on the RRs:
    ```
    RP/0/RP0/CPU0:xrd05#show bgp link-state link-state
    Tue Jan 10 21:50:37.406 UTC
    BGP router identifier 10.0.0.5, local AS number 65000
    BGP generic scan interval 60 secs
    Non-stop routing is enabled
    BGP table state: Active
    Table ID: 0x0   RD version: 187
    BGP main routing table version 187
    BGP NSR Initial initsync version 1 (Reached)
    BGP NSR/ISSU Sync-Group versions 0/0
    BGP scan interval 60 secs

    Status codes: s suppressed, d damped, h history, * valid, > best
                i - internal, r RIB-failure, S stale, N Nexthop-discard
    Origin codes: i - IGP, e - EGP, ? - incomplete
    Prefix codes: E link, V node, T IP reacheable route, S SRv6 SID, u/U unknown
                I Identifier, N local node, R remote node, L link, P prefix, S SID
                L1/L2 ISIS level-1/level-2, O OSPF, D direct, S static/peer-node
                a area-ID, l link-ID, t topology-ID, s ISO-ID,
                c confed-ID/ASN, b bgp-identifier, r router-ID, s SID
                i if-address, n nbr-address, o OSPF Route-type, p IP-prefix
                d designated router address
    Network            Next Hop            Metric LocPrf Weight Path
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0001.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0002.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0003.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0004.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0005.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0006.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[V][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0007.00]]/328
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[E][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0001.00]][R[c65000][b0.0.0.0][s0000.0000.0002.00]][L[i10.1.1.0][n10.1.1.1]]/696
                        10.0.0.1                      100      0 i
    * i                   10.0.0.7                      100      0 i
    *>i[E][L2][I0x0][N[c65000][b0.0.0.0][s0000.0000.0001.00]][R[c65000][b0.0.0.0][s0000.0000.0002.00]][L[i2001:1:1:1::][n2001:1:1:1::1][t0x0002]]/936
    --More-- 
    <<< output truncated >>>
    ```

### End of Lab 1
Please proceed to [Lab 2](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_2/lab_2-guide.md)
