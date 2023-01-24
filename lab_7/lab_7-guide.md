## Lab 7: Host-Based SR/SRv6 and building your own SDN App (BYO-SDN-App)

### Description
The goal of the Jalapeno model is to enable applications to directly control their network experience. We envision a process where the application or endpoint requests some Jalapeno network service for its traffic. The Jalapeno network-service queries the DB and provides a response, which includes an SR-MPLS or SRv6 SID stack. The application or endpoint would then encapsulate its own outbound traffic; aka, the SR or SRv6 encapsulation/decapsulation would be performed at the host where the Application resides. The host-based SR/SRv6 encap/decap could be executed at the Linux networking layer, by an onboard dataplane element such as a vSwitch or VPP, or by a CNI dataplane such as eBPF. The encapsulated traffic, once transmitted from the host will reach the SR/SRv6 transport network and will be statelessly forwarded per the SR/SRv6 encapsulation, thus executing the requested network service treatment. Essentially the application or endpoint will be steering its own traffic through the network and thus executing its own SR/SRv6 network program.


## Contents
- [Lab Objectives](#lab-objectives)
- [XRd SR Support for VMs](#enable-xrd-router-support-for-sr-vm-traffic)
- [Rome SR Configuration](#rome-sr-configuration)


## Lab Objectives
The student upon completion of Lab 6 should have achieved the following objectives:

* Understanding of the SR & SRv6 stack available in Linux
* Understanding the use of VPP as a host-based SR and/or SRv6 forwarding element 
* How to query Jalapeno from Python for SR data
* Using Python craft specific SR headers for traffic routing
* Using Python to create and program your own SR-MPLS and SRv6 network path

*Note: the python code used in this lab has a dependency on the python-arango module. The module has been preinstalled on both the Rome and Amsterdam VMs, however, if one wishes to recreate this lab in their own environment, any client node will need to install the module:*
```
sudo apt install python3-pip
pip install python-arango 
```

## Enable XRd router support for SR VM Traffic
Both the Rome and Amsterdam VM's are pre-loaded with a python client (jalapeno.py) that will execute our Jalapeno network service per the process described above. As the client is run it will program a local route or SR-policy with SR/SRv6 encapsulation, which will allow the VM to "self-encapsulate" its outbound traffic, The xrd network will statelessly forward the traffic per the SR/SRv6 encapsulation.

In order to forward inbound labeled packets received from the Rome and Amsterdam VMs we'll need to enable MPLS forwarding on xrd01's and xrd07's VM-facing interfaces:

1. Enable MPLS forwarding on the VM-facing interfaces on both xrd01 and xrd07: 

```
mpls static
 int gigabitEthernet 0/0/0/0
 commit
```
Validate MPLS forwarding is enabled:
```
show mpls interface
```
Expected output:
```
Fri Dec 23 23:24:11.146 UTC
Interface                  LDP      Tunnel   Static   Enabled 
-------------------------- -------- -------- -------- --------
GigabitEthernet0/0/0/0     No       No       Yes      Yes
GigabitEthernet0/0/0/1     No       No       No       Yes
GigabitEthernet0/0/0/2     No       No       No       Yes
```

## Rome VM: Linux-based Segment Routing & SRv6 

The Rome VM is simulating a user host or endpoint and will use its Linux dataplane to perform SR or SRv6 traffic encapsulation:

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

 - There is no Linux "SR-MPLS" per se, but from the host's perspective its just MPLS labels, so we'll use the iproute2 MPLS implemenation. Ubuntu iproute2 manpage: https://manpages.ubuntu.com/manpages/jammy/man8/ip-route.8.html

### Preliminary steps for SR/SRv6 on Rome VM
   1.  Login to the Rome VM
   ```
   ssh cisco@198.18.128.103
   ```

   2. On the Rome VM cd into the lab_7 directory where the jalapeno.py client resides:
   ```
   cd ~/SRv6_dCloud_Lab/lab_7
   ```
   3. Get familiar with files in the directory; specifically:
   ```
   cat rome.json                 <------- data jalapeno.py will use to execute its query and program its SR/SRv6 route
   cat cleanup_rome_routes.sh    <------- script to cleanup any old SR/SRv6 routes
   cat jalapeno.py               <------- python client that takes cmd line args to request/execute an SR/SRv6 network service
   ls netservice/                <------- contains python libraries available to jalapeno.py for calculating SR/SRv6 route instructions

   ```
   4. For SRv6 outbound encapsulation we'll need to set Rome's SRv6 source address:

   ```
   sudo ip sr tunsrc set fc00:0:107:1::1
   ```

   - Note: For host-based SR/MPLS the Linux MPLS modules aren't loaded by default, however, we already enabled them on the Rome VM. If you're setting up a similar lab in your own environment, here are the commands to load them: 
   ```
   sudo modprobe mpls_router
   sudo modprobe mpls_iptunnel
   ```

   5. Validate Rome VM's MPLS modules are loaded:
   ```
   lsmod | grep mpls
   ```
   Output should look something like this:
   ```
   cisco@rome:~$ lsmod | grep mpls
    mpls_iptunnel          20480  0                    <----- Currently no MPLS tunnels/routes configured
    mpls_router            40960  1 mpls_iptunnel
    ip_tunnel              24576  1 mpls_router
   ```
  Each line in the output has three columns:

  * Module - The first column shows the name of the module.
  * Size - The second column shows the size of the module in bytes.
  * Used by - The third column shows a number that indicates how many instances of the module are currently used. A value of zero means that the module is not used. The comma-separated list after the number shows what is using the module.
  
   - Reference: https://linuxize.com/post/lsmod-command-in-linux/


### Jalapeno python client:
A host or endpoint with this client can request a network service between a given source and destination. The client's currently supported services are: 

 - Low Latency Path
 - Least Utilized Path
 - Data Sovereignty Path
 - Get All Paths (informational only)
 
 When executed the client passes its service request as a Shortest Path query to Jalapeno's Arango graph database. The database performs a traversal of its graph and responds with a dataset reflecting the shortest path based on the parameters of the query. The client receives the data, performs some data manipulation as needed and then constructs a local SR or SRv6 route/policy for any traffic it would send to the destination.

Currently the client operates as a CLI tool, which expects to see a set of command line arguments. A user or application may operate the client by specifying the desired network service (-s) and encapsulation (-e), and inputs a json file which contains source and destination info and a few other items.

For ease of use the currently supported network services are abbreviated: 

 - gp = get_all_paths
 - ll = low_latency
 - lu = least_utilized
 - ds = data_sovereignty

1. Access client help with the *-h* argument:
    ```
    python3 jalapeno.py -h
    ``` 
    Expected output:
    ```
    cisco@rome:~/SRv6_dCloud_Lab/lab_7$ python3 jalapeno.py -h
    usage: Jalapeno client [-h] [-e E] [-f F] [-s S]

    takes command line input and calls path calculator functions

    optional arguments:
    -h, --help  show this help message and exit
    -e E        encapsulation type <sr> or <srv6>
    -f F        json file with src, dst, parameters
    -s S        requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)

    jalapeno.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp>
    ```

    Example client command with network-service arguments:
    ```
    python3 jalapeno.py -f rome.json -e srv6 -s lu
    ```

The client's network service modules are located in the *netservice* directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (gp, ll, lu, or ds) and calculates an SRv6 uSID or SR label stack, which will satisfy the network service request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route/policy.

## Network Services
### Get All Paths

The Get All Paths Service will query the DB for all paths which meet certain parameters, between source and destination prefixes.

1. Run the 'gp' service (no need to specify encapsulation type):
``` 
python3 client.py -f rome.json -s gp
```
 - check log output:
```
more log/get_paths.json
```
 - We can expect to see a json file with source, destination, and path data which includes srv6 sids and sr label stack info
 - The client will also print several pieces of data out to the command line as it performs its logic. Note this line which provides a summary of the relevant paths by outputing the SRv6 locators along each path:

 https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_7/netservice/gp.py#L37

  - Sample command line output:
```
locators:  [None, 'fc00:0000:6666::', 'fc00:0000:2222::', 'fc00:0000:1111::', None]
locators:  [None, 'fc00:0000:6666::', 'fc00:0000:5555::', 'fc00:0000:1111::', None]
locators:  [None, 'fc00:0000:4444::', 'fc00:0000:5555::', 'fc00:0000:1111::', None]
locators:  [None, 'fc00:0000:4444::', 'fc00:0000:3333::', 'fc00:0000:2222::', 'fc00:0000:1111::', None]
```
You can also experiment with the script's graph traversal parameters to limit or expand the number of vertex 'hops' the query will search for. Note: ArangoDB considers the source and destination vertices as 'hops' when doing its graph traversal.

2. Change the 'gp' service's hopcount parameters. Open the netservice/gp.py file in a text editor (vi, vim) and change parameters in line 9: 

https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_7/netservice/gp.py#L9

```
for v, e, p in 6..6 outbound
```
Save gp.py and re-run the script. You should see fewer path options in the command line output and log.

3. Try increasing the number of hops the graph may traverse:

 ```
 for v, e, p in 1..8 outbound
 ```
Save the file and re-run the script. You should see more path options in the command line output and log.

### Least Utilized Path
Many segment routing and SDN solutions focus on the low latency path as their primary use case. We absolutely feel low latency is an important network service, especially for real time applications. However, we believe one of the use cases which deliver the most bang for the buck is "Least Utilized Path". The idea behind this use case is that the routing protocol's chosen best path is usually *The Best Path*. Thus the *Least Utilized* service looks to steer lower priority traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's best path for higher priority traffic.

1. Cleanup any stale routes on the VM and execute the least utilized path service with SR encapsulation
``` 
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e sr -s lu
```
 - The client's command line output should display the new route in the routing table:
```
src data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'src_peer': '10.0.0.7'}]
dest data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'dst_peer': '10.0.0.1'}]
Least Utilized Service
locators:  ['fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
prefix_sids:  [100006, 100002, 100001]
srv6 sid:  fc00:0:6666:2222:1111::
adding linux SR route: ip route add 10.101.2.0/24 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192
RTNETLINK answers: File exists
default via 198.18.128.1 dev ens160 proto static 
10.0.0.0/24 via 10.107.1.2 dev ens192 proto static 
10.1.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.2.0/24  encap mpls  100006/100002/100001 via 10.107.1.2 dev ens192         <-------------------
10.101.2.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.3.0/24 via 10.107.2.2 dev ens224 proto static 
10.107.1.0/24 dev ens192 proto kernel scope link src 10.107.1.1 
10.107.2.0/24 dev ens224 proto kernel scope link src 10.107.2.1 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.103 
```

2. Check log output and linux ip route:
 ```
cat log/least_utilized.json

ip route

```

3. Run a ping test 
 - Open up a second ssh session to the Rome VM
 - Start tcpdump on 2nd ssh session. This will capture packets outbound from Rome VM going toward xrd07:
```
sudo tcpdump -ni ens192
```
 - Return to the first Rome ssh session and ping Amsterdam with Rome source address 20.0.0.1. The "-i .3" argument sets the ping interval to 300ms
```
ping 10.101.2.1 -I 20.0.0.1 -i .3
```

4. Check the Rome tcpdump to validate traffic is encapsulated in the SR label stack. Expected output will be something like:
```
cisco@rome:~$ sudo tcpdump -ni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
04:15:48.834889 MPLS (label 100006, exp 0, ttl 64) (label 100002, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 20.0.0.1 > 10.101.2.1: ICMP echo request, id 11, seq 1, length 64
04:15:48.843360 IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 11, seq 1, length 64
04:15:49.136057 MPLS (label 100006, exp 0, ttl 64) (label 100002, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 20.0.0.1 > 10.101.2.1: ICMP echo request, id 11, seq 2, length 64
04:15:49.147006 IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 11, seq 2, length 64
```

5. Return to an SSH session on the XRD VM and use tcpdump.sh <xrd0x-xrd0y>" to capture packets along the path from Rome VM to Amsterdam VM. Given the label stack seen above, we'll monitor the linux bridges linking xrd07 to xrd06, xrd06 to xrd02, then xrd02 to xrd01:
 - restart the ping if it is stopped
```
cd cd ~/SRv6_dCloud_Lab/util/
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd02-xrd06
./tcpdump.sh xrd01-xrd02
```
 - We expect to see SR-MPLS PHP behavior on the *echo request* packets as the nodes pop outer labels as the traffic traverses the network. Example output for the link between xrd06 and xrd02:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06
sudo tcpdump -ni br-07e02174172b
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-07e02174172b, link-type EN10MB (Ethernet), capture size 262144 bytes
23:19:39.310524 MPLS (label 100001, exp 0, [S], ttl 62) IP 20.0.0.1 > 10.101.2.1: ICMP echo request, id 11, seq 767, length 64
23:19:39.315326 MPLS (label 100007, exp 0, ttl 61) (label 24009, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 11, seq 767, length 64
23:19:39.610924 MPLS (label 100001, exp 0, [S], ttl 62) IP 20.0.0.1 > 10.101.2.1: ICMP echo request, id 11, seq 768, length 64
23:19:39.667534 MPLS (label 100007, exp 0, ttl 61) (label 24009, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 11, seq 768, length 64
23:19:39.911902 MPLS (label 100001, exp 0, [S], ttl 62) IP 20.0.0.1 > 10.101.2.1: ICMP echo request, id 11, seq 769, length 64
23:19:39.924014 MPLS (label 100007, exp 0, ttl 61) (label 24009, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 11, seq 769, length 64
```

6. Cleanup Rome's routes and execute the least utilized path service with SRv6 encapsulation
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e srv6 -s lu
```
Expected client.py console output:
```
cisco@rome:~/SRv6_dCloud_Lab/lab_7$ python3 client.py -f rome.json -e srv6 -s lu
src data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'src_peer': '10.0.0.7'}]
dest data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'dst_peer': '10.0.0.1'}]
Least Utilized Service
locators:  ['fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
prefix_sids:  [100006, 100002, 100001]
srv6 sid:  fc00:0:6666:2222:1111::
adding linux SRv6 route: ip route add 10.101.2.0/24 encap seg6 mode encap segs fc00:0:6666:2222:1111:: dev ens192
default via 198.18.128.1 dev ens160 proto static 
10.0.0.0/24 via 10.107.1.2 dev ens192 proto static 
10.1.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.2.0/24  encap seg6 mode encap segs 1 [ fc00:0:6666:2222:1111:: ] dev ens192 scope link    <-------------
10.101.3.0/24 via 10.107.2.2 dev ens224 proto static 
10.107.1.0/24 dev ens192 proto kernel scope link src 10.107.1.1 
10.107.2.0/24 dev ens224 proto kernel scope link src 10.107.2.1 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.103
```

7. Repeat, or just spot-check the ping and tcpdump steps describe in 3 - 5

### Low Latency Path
The procedure is the same as Least Utilized Path

1. SR on Rome VM:
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e sr -s ll
ping 10.101.2.1 -i .4
```
2. SRv6 on Rome VM:
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e srv6 -s ll
ping 10.101.1.1 -i .4
```
3. tcpdump script On XRD VM:
```
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd01-xrd05
```

### Data Sovereignty Path 

The procedure is the same as Least Utilized Path
 
1. SR on Rome VM:
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e sr -s ll
ping 10.101.1.1 -i .4
```
2. SRv6 on Rome VM:
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e srv6 -s ll
ping 10.101.1.1 -i .4
```
3. tcpdump on XRD VM:
```
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd01-xrd05
```

## Amsterdam
## POC host-based SRv6 and SR-MPLS SDN 

Todo:
1. Build and test this lab
2. Writeup lab guide

### Login to the Amsterdam VM
```
ssh cisco@198.18.128.102
```
In our lab the Amsterdam VM represents a content server whose application owners wish to provide optimal user experience, while balancing out the need for bulk content replication.  They've chosen to use VPP as their host-based SR/SRv6 forwarding engine, and have subscribed to the network services made available by our Jalapeno system.

Like the Rome VM, Amsterdam has the same python client that can query Jalapeno for SR/SRv6 path data, and then program its local VPP dataplane with ip route with SR/SRv6 encapsulation

1. On the Amsterdam VM cd into the lab_7 directory:
```
cd ~/SRv6_dCloud_Lab/lab_7
```
2. Everything is the same as on the Rome VM with some different parameters in amsterdam.json:
```
cat amsterdam.json
```
3. Amsterdam has a Linux veth pair connecting kernel forwarding to its onboard VPP instance. The VM has preconfigured ip routes (see /etc/netplan/00-installer-config.yaml) pointing to VPP via its "ams-out" interface:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_7$ ip link | grep ams-out
4: vpp-in@ams-out: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
5: ams-out@vpp-in: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000

cisco@amsterdam:~/SRv6_dCloud_Lab/lab_7$ ip route
default via 198.18.128.1 dev ens160 proto static 
default via 198.18.128.1 dev ens160 proto static metric 100 
10.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
10.101.2.0/24 dev ams-out proto kernel scope link src 10.101.2.1 
10.107.0.0/20 via 10.101.2.2 dev ams-out proto static 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.102 
```
4. VPP has been given a startup config which establishes IP connectivity to the network as a whole on bootup.
```
cat /etc/vpp/startup.conf
```
 - Note the 'unix' and 'dpdk' sections of the config:
```
unix {
  nodaemon
  log /var/log/vpp/vpp.log
  full-coredump
  cli-listen /run/vpp/cli.sock
  gid vpp
  startup-config /home/cisco/SRv6_dCloud_Lab/lab_0/config/vpp.conf
}
dpdk {
  dev 0000:0b:00.0
}
```
 - VPP startup-config file: https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_1/config/vpp.conf

5. VPP's CLI may be invoked directly:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_7$ sudo vppctl
    _______    _        _   _____  ___ 
 __/ __/ _ \  (_)__    | | / / _ \/ _ \
 _/ _// // / / / _ \   | |/ / ___/ ___/
 /_/ /____(_)_/\___/   |___/_/  /_/    

vpp# show interface address
GigabitEthernetb/0/0 (up):
  L3 10.101.1.1/24
  L3 fc00:0:101:1::1/64
host-vpp-in (up):
  L3 10.101.2.2/24
local0 (dn):
vpp# 
```
6. Or driven from the Linux command line:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_7$ sudo vppctl show interface address
GigabitEthernetb/0/0 (up):
  L3 10.101.1.1/24
  L3 fc00:0:101:1::1/64
host-vpp-in (up):
  L3 10.101.2.2/24
local0 (dn):
```
7. Other handy VPP commands:
```
quit                     # exit VPP CLI
show ip fib              # show VPP's forwarding table, which will include SR and SRv6 policy/encap info later
sudo vppctl show ip fib  # same command but executed from Linux
show interface           # interface status and stats
```

### Jalapeno SDN client:
The client operates on Amsterdam the same way it operates on the Rome VM, and it supports the same set of network services. amsterdam.json specifies to the use of a VPP dataplane, therefore the client will construct a VPP SR or SRv6 route/policy upon completing its path calculation.

For ease of use the currently supported network services are abbreviated: 

 - gp = get_all_paths
 - ll = low_latency
 - lu = least_utilized
 - ds = data_sovereignty

client help:
```
python3 client.py -h
``` 
## Network Services
### Get All Paths

The Get All Paths Service will query the DB for all paths which meet certain parameters, between source and destination prefixes.

1. Run the 'gp' service :
``` 
python3 client.py -f amsterdam.json -s gp
```
 - check log output:
```
more log/get_paths.json
```
 - We can expect to see a json file with source, destination, and SR/SRv6 path data
 - The client will also output data to the command line. Example:

```
locators:  [None, 'fc00:0000:5555::', 'fc00:0000:6666::', 'fc00:0000:7777::', None]
locators:  [None, 'fc00:0000:5555::', 'fc00:0000:4444::', 'fc00:0000:7777::', None]
locators:  [None, 'fc00:0000:2222::', 'fc00:0000:6666::', 'fc00:0000:7777::', None]
locators:  [None, 'fc00:0000:2222::', 'fc00:0000:3333::', 'fc00:0000:4444::', 'fc00:0000:7777::', None]
```

### Least Utilized Path
Least Utilized Path: this service looks to steer lower priority or delay tolerant traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's best path for higher priority traffic.

Note: the client automatically cleans up old VPP routes/SR-policies prior to installing new ones:

1. Execute the least utilized path service with SR encapsulation
``` 
python3 client.py -f amsterdam.json -e sr -s lu
```
 - The client's command line output will include info on VPP's new forwarding table:
```
 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:30 buckets:1 uRPF:30 to:[0:0]]
    [0] [@13]: mpls-label[@1]:[100002:64:0:neos][100003:64:0:neos][100004:64:0:neos][100007:64:0:eos]
        [@1]: mpls via 10.101.1.2 GigabitEthernetb/0/0: mtu:9000 next:2 flags:[] 02420a6501020050568655478847 
```

2. Check log output:
 ```
cat log/least_utilized.json

ip route

```

3. Run a ping test 
 - From an ssh session on the XRd VM start a tcpdump on the interface facing the Amsterdam VM:
```
sudo tcpdump -ni ens224
```
 - Return to the first Amsterdam ssh session and ping
```
ping 10.107.1.1 -i .4
```

4. Validate outbound traffic is encapsulated in the SR label stack. Expected output will be something like:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ sudo tcpdump -ni ens224
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens224, link-type EN10MB (Ethernet), capture size 262144 bytes
23:39:02.390485 MPLS (label 100002, exp 0, ttl 64) (label 100003, exp 0, ttl 64) (label 100004, exp 0, ttl 64) (label 100007, exp 0, [S], ttl 64) IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 16, seq 10, length 64
23:39:02.395566 IP 10.107.1.1 > 10.101.2.1: ICMP echo reply, id 16, seq 10, length 64
23:39:02.790503 MPLS (label 100002, exp 0, ttl 64) (label 100003, exp 0, ttl 64) (label 100004, exp 0, ttl 64) (label 100007, exp 0, [S], ttl 64) IP 10.101.2.1 > 10.107.1.1: ICMP echo request, id 16, seq 11, length 64
23:39:02.795213 IP 10.107.1.1 > 10.101.2.1: ICMP echo reply, id 16, seq 11, length 64
```

5. Continuing on the XRd VM use the tcpdump.sh <xrd0x-xrd0y> script to capture packets along the path from Amsterdam VM to Rome VM. Given the label stack seen above, we'll monitor the linux bridges along this path: xrd01 --> xrd02 --> xrd03 --> xrd04 --> xrd07
 - restart the ping if it is stopped
```
./tcpdump.sh xrd01-xrd02
./tcpdump.sh xrd02-xrd03
./tcpdump.sh xrd03-xrd04
./tcpdump.sh xrd04-xrd07
```
 - Just like with previous SR services we expect to see SR-MPLS PHP behavior as xrd nodes pop outer labels as the traffic traverses the network. Example output:

6. Execute the least utilized path service with SRv6 encapsulation
```
python3 client.py -f amsterdam.json -e srv6 -s lu
```

7. Repeat, or just spot-check, steps 2 - 5

### Low Latency Path
The procedure is the same as Least Utilized Path

1. SR on Amsterdam VM:
```
python3 client.py -f amsterdam.json -e sr -s ll
ping 10.107.1.1 -i .4
```
2. SRv6 on Amsterdam VM:
```
python3 client.py -f amsterdam.json -e srv6 -s ll
ping 10.107.1.1 -i .4
```
3. tcpdump script On XRD VM:
```
./tcpdump.sh xrd01-xrd05
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd06-xrd07
```

### Data Sovereignty Path 

The procedure is the same as Least Utilized Path
 
1. SR on Amsterdam VM:
```
python3 client.py -f amsterdam.json -e sr -s ll
ping 10.107.1.1 -i .4
```
2. SRv6 on Amsterdam VM:
```
python3 client.py -f amsterdam.json -e srv6 -s ll
ping 10.107.1.1 -i .4
```
3. tcpdump on XRD VM:
```
./tcpdump.sh xrd01-xrd05
./tcpdump.sh xrd05-xrd04
./tcpdump.sh xrd04-xrd07
```
### You have reached the end of LTRSPG-2212, hooray!