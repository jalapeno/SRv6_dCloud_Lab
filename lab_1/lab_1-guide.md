# SRv6 Lab 1 Guide

### Description: 
In Lab 1 the student will validate that the supplied topology is up and running and that all baseline 
connectivity is working. Second, they will validate that the pre-configured ISIS and BGP routing protocols are running and 
seeing the correct topology. Third, there will be lite SR-MPLS configuration on routers 1-7 and 
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
5. Configure and validate SR-MPLS
6. Configure and validate SRv6


## 1. Lab Objectives
The student upon completion of Lab 1 should have achieved the following objectives

* Access to all devices in the lab
* Understanding of the lab topology and components
* Understanding of basic configuration for SR-MPLS
* Understanding of basic configuration for SRv6
   

## 2. Validate Device Access

Device access for this lab is primarly through SSH. All of the VMs within this toplogy can be accessed once you connect through Cisco AnyConnect VPN to the dCloud environment. Please see the management topology network diagram below. In addition their are seven instances of XR routers running in containers on the VM host XRD. The XRD VM acts as a jumpbox for these router containers. For router access you will need to SSH into the XRD VM and then initiate a separate SSH session to each of the routers. The XRD VM is configured for DNS resolution for each router name to save time.

### User Credentials
For all instances you will use the same user credentials:
```
User: cisco Password: cisco123
```

### Management Network Topology

![Management Topology](/topo_drawings/management-network-medium.png)

For full size image see [LINK](/topo_drawings/management-network.png)

### Validate XRD
1. SSH to the Ubuntu VM XRD which is using Docker to host the XRD application

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
    ``` 
    run sudo ./setup-lab_0.sh
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
6. Confirm the docker networks were created. The Network ID are unique on creation
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
7. The XRD router instances should be available for access 2 minutes after spin up.

### Validate Jalaepno
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
3. 

### Validate Client VMs
__Amsterdam__
1. SSH to Amsterdam Client VM from your laptop. 
2. Check that the interface to router xrd01 is `UP` and has the assigned IP `10.101.1.1/24`
    ```
    cisco@amsterdam:~$ ip address show ens192
    3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        link/ether 00:50:56:aa:a0:3f brd ff:ff:ff:ff:ff:ff
        inet 10.101.1.1/24 brd 10.101.1.255 scope global ens192
        valid_lft forever preferred_lft forever
        inet6 fc00:0:101:1:250:56ff:feaa:a03f/64 scope global dynamic mngtmpaddr noprefixroute 
        valid_lft 2591850sec preferred_lft 604650sec
        inet6 fc00:0:101:1::1/64 scope global 
        valid_lft forever preferred_lft forever
        inet6 fe80::250:56ff:feaa:a03f/64 scope link 
        valid_lft forever preferred_lft forever
    ```
3. Check connectivity from Amsterdam to xrd01
    ```
    cisco@amsterdam:~$ ping -c 3 10.101.1.2
    PING 10.101.1.2 (10.101.1.2) 56(84) bytes of data.
    64 bytes from 10.101.1.2: icmp_seq=1 ttl=255 time=1.18 ms
    64 bytes from 10.101.1.2: icmp_seq=2 ttl=255 time=1.18 ms
    64 bytes from 10.101.1.2: icmp_seq=3 ttl=255 time=1.37 ms
    ```

__Rome__
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

### Connect to Routers
1. Starting from the XRD VM log into each routers instance 1-7 consulting the management topology diagram above

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
3. Validate adjacencies and traffic passing on each router. Use the topology diagram to determine neighbors. The client devices Amsterdam and Rome are not running CDP.
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

In this lab we are using ISIS as the underlying IGP to establish link connectivity across routers xrd01 -> xrd07. ISIS has a basic configuration pre-configured setup starting in lab 1. The student will want to confirm that they see a full ISIS topology.

![ISIS Topology](/topo_drawings/isis-topology-medium.png)

For full size image see [LINK](/topo_drawings/isis-topology-large.png)

The ISIS topology can be validated from any router. The command output will vary slightly based on router used.
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

## Validate BGP Topology

In this lab we are using BGP for SRv6 route/community exchange. In the lab we are running as single AS 65000 with BGP running on xrd01, xrd05, xrd06, xrd07.  Routers xrd05 and xrd06 are functioning as route reflectors for the lab. The student will want to confirm that they see a full BGP topology.

![BGP Topology](/topo_drawings/bgp-topology-medium.png)

For full size image see [LINK](/topo_drawings/bgp-topology-large.png)