## Lab 8: Host-Based SR/SRv6 and building your own SDN App (BYO-SDN-App)

### Description
Lab 8 is divided into two primary parts. Part 1 is host-based SR/SRv6 using Linux kernel capabilities on the Rome VM. Part 2 will be host-based SR/SRv6 using VPP on the Amsterdam VM.

The goal of the Jalapeno model is to enable applications to directly control their network experience. We envision a process where the application or endpoint requests some Jalapeno *network service* for its traffic. The Jalapeno network-service queries the DB and provides a response, which includes an SR-MPLS or SRv6 SID stack. The application or endpoint would then encapsulate its own outbound traffic; aka, the SR or SRv6 encapsulation/decapsulation would be performed at the host where the Application resides. 

The host-based SR/SRv6 encap/decap could be executed at the Linux networking layer, or by an onboard dataplane element such as a vSwitch or VPP, or by a CNI dataplane such as eBPF. The encapsulated traffic, once transmitted from the host, will reach the SR/SRv6 transport network and will be statelessly forwarded per the SR/SRv6 encapsulation, thus executing the requested network service. 


## Contents
- [Lab 8: Host-Based SR/SRv6 and building your own SDN App (BYO-SDN-App)](#lab-8-host-based-srsrv6-and-building-your-own-sdn-app-byo-sdn-app)
  - [Description](#description)
- [Contents](#contents)
- [Lab Objectives](#lab-objectives)
- [Enable XRd forwarding of SR-MPLS traffic coming from Linux hosts](#enable-xrd-forwarding-of-sr-mpls-traffic-coming-from-linux-hosts)
- [Rome VM: Segment Routing \& SRv6 on Linux](#rome-vm-segment-routing--srv6-on-linux)
  - [Preliminary steps for SR/SRv6 on Rome VM](#preliminary-steps-for-srsrv6-on-rome-vm)
- [Jalapeno python client:](#jalapeno-python-client)
- [Rome Network Services](#rome-network-services)
  - [Get All Paths](#get-all-paths)
  - [Least Utilized Path](#least-utilized-path)
  - [Low Latency Path](#low-latency-path)
    - [While jalapeno.py supports both SR and SRv6 for its Network Services, for the remainder of Lab 8 we will focus just on SRv6](#while-jalapenopy-supports-both-sr-and-srv6-for-its-network-services-for-the-remainder-of-lab-8-we-will-focus-just-on-srv6)
  - [Low Latency Re-Route](#low-latency-re-route)
  - [Data Sovereignty Path](#data-sovereignty-path)
- [Amsterdam VM](#amsterdam-vm)
  - [POC host-based SRv6 and SR-MPLS SDN using the VPP dataplane](#poc-host-based-srv6-and-sr-mpls-sdn-using-the-vpp-dataplane)
  - [Jalapeno SDN client:](#jalapeno-sdn-client)
- [Amsterdam Network Services](#amsterdam-network-services)
  - [Get All Paths](#get-all-paths-1)
  - [Least Utilized Path](#least-utilized-path-1)
  - [Low Latency Path](#low-latency-path-1)
  - [Data Sovereignty Path](#data-sovereignty-path-1)
  - [You have reached the end of LTRSPG-2212, hooray!](#you-have-reached-the-end-of-ltrspg-2212-hooray)

## Lab Objectives
The student upon completion of Lab 8 should have achieved the following objectives:

* Understanding of the SR & SRv6 stack available in Linux
* Understanding the use of VPP as a host-based SR and/or SRv6 forwarding element 
* How to query Jalapeno from Python for network topology and SR/SRv6 data
* Using Python to craft specific SR/SRv6 headers for traffic steering or other use cases
* Using Python to to program SR-MPLS or SRv6 forwarding entries on a Linux host

*Note: the python code used in this lab has a dependency on the python-arango module. The module has been preinstalled on both the Rome and Amsterdam VMs, however, if one wishes to recreate this lab in their own environment, any client node will need to install the module. We also suggest upgrading the http 'requests' library as that will eliminate some cosmetic http error codes.*
```
sudo apt install python3-pip
pip install python-arango 
pip3 install --upgrade requests
```


1. Deploy the srv6-localsids-processor
```
cd ~/SRv6_dCloud_Lab/lab_8/python/
python3 srv6-localsids-processor.py
```
Expected output:
```
document added:  xrd01_fc00:0:1111::
document added:  xrd01_fc00:0:1111:e000::
document added:  xrd01_fc00:0:1111:e001::
document added:  xrd01_fc00:0:1111:e002::
document added:  xrd01_fc00:0:1111:e003::
document added:  xrd01_fc00:0:1111:e004::
document added:  xrd01_fc00:0:1111:e005::
document added:  xrd01_fc00:0:1111:e006::
document added:  xrd01_fc00:0:1111:e007::
document added:  xrd01_fc00:0:1111:e008::
document added:  xrd01_fc00:0:1111:e009::
document added:  xrd07_fc00:0:7777::
document added:  xrd07_fc00:0:7777:e000::
document added:  xrd07_fc00:0:7777:e001::
document added:  xrd07_fc00:0:7777:e002::
document added:  xrd07_fc00:0:7777:e003::
document added:  xrd07_fc00:0:7777:e004::
document added:  xrd07_fc00:0:7777:e005::
document added:  xrd07_fc00:0:7777:e006::
document added:  xrd07_fc00:0:7777:e007::
```
1. Check that Arango as an *`srv6_local_sids`* data collection, and that it is populated
2. you can now kill the processor with ctrl-c. It'll kick out python errors, but no worries...


## Enable XRd forwarding of SR-MPLS traffic coming from Linux hosts
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

## Rome VM: Segment Routing & SRv6 on Linux

The Rome VM is simulating a user host or endpoint and will use its Linux dataplane to perform SR or SRv6 traffic encapsulation:

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

 - There is no Linux "SR-MPLS" per se, but from the host's perspective its just MPLS labels, so we'll use the iproute2 MPLS implemenation. Ubuntu iproute2 manpage: https://manpages.ubuntu.com/manpages/jammy/man8/ip-route.8.html

### Preliminary steps for SR/SRv6 on Rome VM
   1.  Login to the Rome VM
   ```
   ssh cisco@198.18.128.103
   ```

   2. On the Rome VM cd into the lab_8 directory where the jalapeno.py client resides:
   ```
   cd ~/SRv6_dCloud_Lab/lab_8
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


## Jalapeno python client:
Both the Rome and Amsterdam VM's are pre-loaded with a python client (jalapeno.py) that will execute our Jalapeno network service per the process described above. As the client is run it will program a local route or SR-policy with SR/SRv6 encapsulation, which will allow the VM to "self-encapsulate" its outbound traffic, The xrd network will statelessly forward the traffic per the SR/SRv6 encapsulation.

A host or endpoint with the jalapeno.py client can request a network service between a given source and destination. The client's currently supported network services are: 

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

1. cd into the lab_8 python directory and access client help with the *-h* argument:
    ```
    cd ~/SRv6_dCloud_Lab/lab_8/python
    python3 jalapeno.py -h
    ``` 
    Expected output:
    ```
    cisco@rome:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -h
    usage: Jalapeno client [-h] [-e E] [-f F] [-s S]

    takes command line input and calls path calculator functions

    optional arguments:
    -h, --help  show this help message and exit
    -e E        encapsulation type <sr> <srv6>
    -f F        json file with src, dst, parameters
    -s S        requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)

    jalapeno.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp>
    ```

    Example client command with network-service arguments:
    ```
    python3 jalapeno.py -f rome.json -e srv6 -s lu
    ```

The client's network service modules are located in the lab_8 *python/netservice/* directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (gp, ll, lu, or ds) queries and calculates an SRv6 uSID or SR label stack, which will satisfy the network service request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route or policy.

## Rome Network Services
### Get All Paths

The Get All Paths Service will query the DB for all paths up to 6-hops in length between a pair of source and destination prefixes.

1. Run the 'gp' service (you can specify either sr or srv6 for encap):
``` 
python3 jalapeno.py -f rome.json -s gp -e sr
```
 - All the jalapeno network services will output some data to the console. More verbose data will be logged to the lab_8/python/log directory. Check log output:
```
more log/get_paths.json
```
 - We can expect to see a json file with source, destination, and path data which includes srv6 sids and sr label stack info
 - The code contains a number of console logging instances that are commented out, and some that are active. Note this line which provides a summary of the relevant paths by outputing the SRv6 locators along each path:

 https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_8/python/netservice/gp.py#L38

  - Sample command line output:
```
cisco@rome:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f rome.json -s gp -e sr
src data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'src_peer': '10.0.0.7'}]
dest data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'dst_peer': '10.0.0.1'}]
Get All Paths Service
number of paths found:  4
SRv6 locators for path:  ['fc00:0:4444::', 'fc00:0:5555::', 'fc00:0:1111::']
SR prefix sids for path:  [100004, 100005, 100001]
SRv6 locators for path:  ['fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
SR prefix sids for path:  [100006, 100002, 100001]
SRv6 locators for path:  ['fc00:0:6666::', 'fc00:0:5555::', 'fc00:0:1111::']
SR prefix sids for path:  [100006, 100005, 100001]
SRv6 locators for path:  ['fc00:0:4444::', 'fc00:0:3333::', 'fc00:0:2222::', 'fc00:0:1111::']
SR prefix sids for path:  [100004, 100003, 100002, 100001]
All paths data from unicast_prefix_v4/20.0.0.0_24_10.0.0.7 to unicast_prefix_v4/10.101.2.0_24_10.0.0.1 logged to log/get_paths.json
```
Like in Lab 6 we can also experiment with the script's graph traversal parameters to limit or expand the number of vertex 'hops' the query will search for. Note: ArangoDB considers the source and destination vertices as 'hops' when doing its graph traversal.

2. Optional: change the 'gp' service's hopcount parameters. Open the netservice/gp.py file in a text editor (vi, vim) and change parameters in line 9: 

https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_8/python/netservice/gp.py#L9

Change it to read:
```
for v, e, p in 6..6 outbound
```
Save gp.py and re-run the script. The *6..6* syntax indicates the traversal should ONLY consider paths 6 hops in length. Given our topology a re-run of the client *python3 jalapeno.py -f rome.json -s gp -e sr* you should output only a single path option in the command line output and log.

Example:
```
locators along path:  [None, 'fc00:0:4444::', 'fc00:0:3333::', 'fc00:0:2222::', 'fc00:0:1111::', None]
```

3. Optional: try increasing the number of hops the graph may traverse:

 ```
 for v, e, p in 1..8 outbound
 ```
Save the file and re-run the script. You should see 8 total path options in the command line output and log.

### Least Utilized Path
Many segment routing and other SDN solutions focus on the low latency path as their primary use case. We absolutely feel low latency is an important network service, especially for real time applications. However, we believe one of the use cases which deliver the most bang for the buck is "Least Utilized Path". The idea behind this use case is that the routing protocol's chosen best path is usually *The Best Path*. Thus the *Least Utilized* service looks to steer lower priority traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's best path for higher priority traffic.

1. Cleanup any stale routes on the VM and execute the least utilized path service with SR encapsulation
``` 
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e sr -s lu
```
 - The client's command line output should display the new route in the routing table:
```
cisco@rome:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f rome.json -e sr -s lu
src data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'src_peer': '10.0.0.7'}]
dest data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'dst_peer': '10.0.0.1'}]
Least Utilized Service
locators:  ['fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
prefix_sids:  [100006, 100002, 100001]
srv6 sid:  fc00:0:6666:2222:1111::
adding linux SR route: ip route add 10.101.2.0/24 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192
RTNETLINK answers: File exists
show linux route table: 
default via 198.18.128.1 dev ens160 proto static 
10.0.0.0/24 via 10.107.1.2 dev ens192 proto static 
10.1.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.2.0/24  encap mpls  100006/100002/100001 via 10.107.1.2 dev ens192    <------------
10.101.2.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.3.0/24 via 10.107.2.2 dev ens224 proto static 
10.107.1.0/24 dev ens192 proto kernel scope link src 20.0.0.1 
10.107.2.0/24 dev ens224 proto kernel scope link src 10.107.2.1 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.103  
```

2. Check log output and linux ip route:
 ```
cat log/least_util.json

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
```

6. Cleanup Rome's routes and execute the least utilized path service with SRv6 encapsulation
```
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e srv6 -s lu
```
Expected console output:
```
cisco@rome:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f rome.json -e srv6 -s lu
src data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'src_peer': '10.0.0.7'}]
dest data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'dst_peer': '10.0.0.1'}]
Least Utilized Service
locators:  ['fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
prefix_sids:  [100006, 100002, 100001]
srv6 sid:  fc00:0:6666:2222:1111::
adding linux SRv6 route: ip route add 10.101.2.0/24 encap seg6 mode encap segs fc00:0:6666:2222:1111:: dev ens192
Show Linux Route Table: 
default via 198.18.128.1 dev ens160 proto static 
10.0.0.0/24 via 10.107.1.2 dev ens192 proto static 
10.1.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.1.0/24 via 10.107.1.2 dev ens192 proto static 
10.101.2.0/24  encap seg6 mode encap segs 1 [ fc00:0:6666:2222:1111:: ] dev ens192 scope link  <------------
10.101.3.0/24 via 10.107.2.2 dev ens224 proto static 
10.107.1.0/24 dev ens192 proto kernel scope link src 20.0.0.1 
10.107.2.0/24 dev ens224 proto kernel scope link src 10.107.2.1 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.103 
```

7. Repeat, or just spot-check the ping and tcpdump steps describe in 3 - 5

### Low Latency Path
The Low Latency Path service will calculate an SR/SRv6 encapsulation instruction for sending traffic over the lowest latency path from a source to a given destination. The procedure for testing/running the Low Latency Path service is the same as the one we followed with Least Utilized Path. 

Looking at the below diagram the low latency path from Rome to Amsterdam across the network should follow the path in the below diagram. Traffic should flow in the direction of **xrd07** -> **xrd06** -> **xrd05** -> **xrd01**

![Low Latency Path](/topo_drawings/low-latency-path.png)

For full size image see [LINK](/topo_drawings/low-latency-path.png)

#### While jalapeno.py supports both SR and SRv6 for its Network Services, for the remainder of Lab 8 we will focus just on SRv6

1. Low latency SRv6 service on Rome VM:
```
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e srv6 -s ll
ping 10.101.2.1 -I 20.0.0.1 -i .3
```
2. Run the tcpdump scripts On the XRD VM to see labeled or SRv6 encapsulated traffic traverse the network:
```
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd01-xrd05
```

### Low Latency Re-Route
Now we are going to simulate a recalculation of the SRv6 topology. The *Sub-Standard Construction Company* has taken out fiber link "G" with a backhoe. Luckily you have paid for optical path redundancy and the link has failed to a geographicaly different route path. The result though is that the primary path latency of *5ms* has increased to *25 ms*. This should cause a new low latency route. Time to test it out!

![Low Latency Path](/topo_drawings/low-latency-alternate-path.png)

For full size image see [LINK](/topo_drawings/low-latency-alternate-path.png)

1. Link "G" needs to have the latency in your topology updated. We will use the Python script located in /lab_8/python/set_latency.py to change the link latency in the lab and then update the ArangoDb topology database with the new value. Set latency has two cli requirements -l (link letter) [A,B,C,D,E,F,G,H,I] and -ms (milliseconds latency) xxx values.

```
python3 set_latency.py -l G -ms 25
```
2. Low latency SRv6 service on Rome VM:
```
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e srv6 -s ll
ping 10.101.2.1 -I 20.0.0.1 -i .3
```

3. Run an iPerf3 test

Amsterdam VM
  ```
  cisco@rome:~$ iperf3 -s -D
  ```

Rome VM
  ```
  cisco@amsterdam:~$ iperf3 -c 10.101.2.1
  Connecting to host 10.101.2.1, port 5201
  [  5] local 10.101.2.1 port 50706 connected to 20.0.0.1 port 5201
  [ ID] Interval           Transfer     Bitrate         Retr  Cwnd
  [  5]   0.00-1.00   sec  76.4 KBytes   625 Kbits/sec    1   1.41 KBytes       
  [  5]   1.00-2.00   sec  0.00 Bytes  0.00 bits/sec    1   1.41 KBytes       
  [  5]   2.00-3.00   sec  0.00 Bytes  0.00 bits/sec    1   1.41 KBytes       
  [  5]   3.00-4.00   sec  0.00 Bytes  0.00 bits/sec    0   1.41 KBytes       
  [  5]   4.00-5.00   sec  0.00 Bytes  0.00 bits/sec    1   1.41 KBytes       
  [  5]   5.00-6.00   sec  0.00 Bytes  0.00 bits/sec    0   1.41 KBytes       
  [  5]   6.00-7.00   sec  0.00 Bytes  0.00 bits/sec    0   1.41 KBytes       
  [  5]   7.00-8.00   sec  0.00 Bytes  0.00 bits/sec    0   1.41 KBytes       
  [  5]   8.00-9.00   sec  0.00 Bytes  0.00 bits/sec    1   1.41 KBytes       
  [  5]   9.00-10.00  sec  0.00 Bytes  0.00 bits/sec    0   1.41 KBytes       
  - - - - - - - - - - - - - - - - - - - - - - - - -
  [ ID] Interval           Transfer     Bitrate         Retr
  [  5]   0.00-10.00  sec  76.4 KBytes  62.5 Kbits/sec    5             sender
  [  5]   0.00-10.06  sec  0.00 Bytes  0.00 bits/sec                  receiver

  iperf Done.
  ```

4. Optional: run the tcpdump scripts On the XRD VM to see the SRv6 encapsulated traffic traverse the network:
```
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd01-xrd05
```


### Data Sovereignty Path
The Data Sovereignty service enables the user or application to steer their traffic through a path or geography that is considered safe per legal guidelines or other regulatory framework. In our case the "DS" service allows us to choose a country (or countries) to avoid when transmitting traffic from a source to a given destination. The country to avoid is specified as a country code in the rome.json and amsterdam.json files. In our testing we've specified that traffic should avoid France (FRA). xrd06 is located in Paris, so all requests to the DS service should produce a shortest-path result that avoids xrd06.

The procedure for testing/running the Data Sovereignty Service is the same as the one we followed with Least Utilized and Low Latency Path.
 
1. SRv6 on Rome VM:
```
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e srv6 -s ds
ping 10.101.2.1 -I 20.0.0.1 -i .3
```
3. tcpdump on XRD VM:
```
./tcpdump.sh xrd04-xrd07
./tcpdump.sh xrd04-xrd05
./tcpdump.sh xrd01-xrd05
```


## Amsterdam VM
### POC host-based SRv6 and SR-MPLS SDN using the VPP dataplane
In our lab the Amsterdam VM represents a content server whose application owners wish to provide optimal user experience, while balancing out the need for bulk content replication.  They've chosen to use VPP as their host-based SR/SRv6 forwarding engine, and have subscribed to the network services made available by our Jalapeno system.

Like the Rome VM, Amsterdam has the same python client that can query Jalapeno for SR/SRv6 path data, and then program its local VPP dataplane with ip route with SR/SRv6 encapsulation.

1. Login to the Amsterdam VM
```
ssh cisco@198.18.128.102
```

2. cd into the lab_8/python/ directory:
```
cd ~/SRv6_dCloud_Lab/lab_8/python/
```
2. Everything is the same as on the Rome VM with some different parameters in amsterdam.json:
```
cat ./amsterdam.json
```
3. Amsterdam has a Linux veth pair connecting kernel forwarding to its onboard VPP instance. The VM has preconfigured ip routes (see /etc/netplan/00-installer-config.yaml) pointing to VPP via its "ams-out" interface:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8$ ip link | grep ams-out
4: vpp-in@ams-out: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
5: ams-out@vpp-in: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000

cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8$ ip route
default via 198.18.128.1 dev ens160 proto static 
default via 198.18.128.1 dev ens160 proto static metric 100 
10.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
10.101.1.0/24 via 10.101.2.2 dev ams-out proto static 
10.101.2.0/24 dev ams-out proto kernel scope link src 10.101.2.1 
10.101.3.0/24 dev ens224 proto kernel scope link src 10.101.3.1 
10.107.0.0/20 via 10.101.2.2 dev ams-out proto static 
20.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
30.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
40.0.0.0/24 via 10.101.3.2 dev ens224 proto static 
50.0.0.0/24 via 10.101.3.2 dev ens224 proto static 
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
  startup-config /home/cisco/SRv6_dCloud_Lab/lab_1/config/vpp.conf
}
dpdk {
  dev 0000:0b:00.0
}
```
 - VPP startup-config file: https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_1/config/vpp.conf

5. VPP's CLI may be invoked directly:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ sudo vppctl
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
vpp# quit
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$
```
6. Or driven from the Linux command line:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8$ sudo vppctl show interface address
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
The client operates on Amsterdam the same way it operates on the Rome VM, and it supports the same set of network services. amsterdam.json specifies to the use of a *VPP* dataplane, therefore the client will construct a VPP SR or SRv6 route/policy upon completing its path calculation.


## Amsterdam Network Services
### Get All Paths

The Get All Paths Service will query the DB for all paths which meet certain parameters, between source and destination prefixes.

1. Run the 'gp' service from Amsterdam:
``` 
python3 jalapeno.py -f amsterdam.json -e srv6 -s gp
```
 - check log output:
```
more log/get_paths.json
```
 - We can expect to see a json file with source, destination, and SR/SRv6 path data
 - Expected console output:

```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f amsterdam.json -e srv6 -s gp
src data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'src_peer': '10.0.0.1'}]
dest data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'dst_peer': '10.0.0.7'}]
Get All Paths Service
number of paths found:  4
SRv6 locators for path:  ['fc00:0:2222::', 'fc00:0:6666::', 'fc00:0:7777::']
SR prefix sids for path:  [100002, 100006, 100007]
SRv6 locators for path:  ['fc00:0:5555::', 'fc00:0:4444::', 'fc00:0:7777::']
SR prefix sids for path:  [100005, 100004, 100007]
SRv6 locators for path:  ['fc00:0:5555::', 'fc00:0:6666::', 'fc00:0:7777::']
SR prefix sids for path:  [100005, 100006, 100007]
SRv6 locators for path:  ['fc00:0:2222::', 'fc00:0:3333::', 'fc00:0:4444::', 'fc00:0:7777::']
SR prefix sids for path:  [100002, 100003, 100004, 100007]
All paths data from unicast_prefix_v4/10.101.2.0_24_10.0.0.1 to unicast_prefix_v4/20.0.0.0_24_10.0.0.7 logged to log/get_paths.json
```

### Least Utilized Path
The Least Utilized Path service behaves the same on Amsterdam as on Rome, except that it will program VPP forwarding. If encapsulation-type *'sr'* is chosen, the service simply programs VPP with a labeled IP route entry. If encap *'srv6'* is chosen the service will program VPP with a Binding-SID and SR-Policy. 

Once the "LU" path service is executed Amsterdam will be able to steer content replication traffic away from the best path and onto the least utilized path, thus preserving the routing protocol's best path for streaming video.

Note: the client automatically cleans up old VPP routes/SR-policies prior to installing new ones:

1. Execute the least utilized path service with SR encapsulation
``` 
python3 jalapeno.py -f amsterdam.json -e sr -s lu
```
 - The client's command line output will include info on VPP's new forwarding table:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f amsterdam.json -e sr -s lu
src data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'src_peer': '10.0.0.1'}]
dest data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'dst_peer': '10.0.0.7'}]
Least Utilized Service
locators:  ['fc00:0:2222::', 'fc00:0:3333::', 'fc00:0:4444::', 'fc00:0:7777::']
prefix_sids:  [100002, 100003, 100004, 100007]
srv6 sid:  fc00:0:2222:3333:4444:7777::
adding vpp route to:  20.0.0.0/24 with SR label stack [100002, 100003, 100004, 100007]
100002 100003 100004 100007
ipv4-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
20.0.0.0/24 fib:0 index:22 locks:2
  CLI refs:1 src-flags:added,contributing,active,
    path-list:[22] locks:8 flags:shared, uPRF-list:20 len:1 itfs:[1, ]
      path:[32] pl-index:22 ip4 weight=1 pref=0 attached-nexthop:  oper-flags:resolved,
        10.101.1.2 GigabitEthernetb/0/0
      [@0]: ipv4 via 10.101.1.2 GigabitEthernetb/0/0: mtu:9000 next:3 flags:[] 02420a6501020050569722bb0800
    Extensions:
     path:32  labels:[[100002 pipe ttl:0 exp:0][100003 pipe ttl:0 exp:0][100004 pipe ttl:0 exp:0][100007 pipe ttl:0 exp:0]]
 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:24 buckets:1 uRPF:20 to:[0:0]]
    [0] [@13]: mpls-label[@0]:[100002:64:0:neos][100003:64:0:neos][100004:64:0:neos][100007:64:0:eos]          <----------
        [@1]: mpls via 10.101.1.2 GigabitEthernetb/0/0: mtu:9000 next:2 flags:[] 02420a6501020050569722bb8847 
```

2. Check log output and local routing table. You can also check the VPP FIB entry from linux:
 ```
cat log/least_utilized.json
ip route
sudo vppctl show ip fib 20.0.0.0/24
```

3. Run a ping test 
 - From an ssh session on the XRd VM start a tcpdump on the interface facing the Amsterdam VM:
```
sudo tcpdump -ni ens224
```
 - Return to the first Amsterdam ssh session and ping
```
ping 20.0.0.1 -i .4
```

4. Validate outbound traffic is encapsulated in the SR label stack. Expected output will be something like:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ sudo tcpdump -ni ens224
<snip>
23:39:02.390485 MPLS (label 100002, exp 0, ttl 64) (label 100003, exp 0, ttl 64) (label 100004, exp 0, ttl 64) (label 100007, exp 0, [S], ttl 64) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 16, seq 10, length 64
23:39:02.395566 IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 16, seq 10, length 64
```

5. Continuing on the XRd VM use the tcpdump.sh <xrd0x-xrd0y> script to capture packets along the path from Amsterdam VM to Rome VM. Given the label stack seen above, we'll monitor the linux bridges along this path: xrd01 --> xrd02 --> xrd03 --> xrd04 --> xrd07
 - restart the ping if it is stopped
 - you can run all the listed tcpdumps, or simply spot check
```
./tcpdump.sh xrd01-xrd02
./tcpdump.sh xrd02-xrd03
./tcpdump.sh xrd03-xrd04
./tcpdump.sh xrd04-xrd07
```
 - Just like with previous SR services we expect to see SR-MPLS PHP behavior as xrd nodes pop outer labels as the traffic traverses the network. Example output:

6. Execute the least utilized path service with SRv6 encapsulation
```
python3 jalapeno.py -f amsterdam.json -e srv6 -s lu
```

Expected output:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f amsterdam.json -e srv6 -s lu
src data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'src_peer': '10.0.0.1'}]
dest data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'dst_peer': '10.0.0.7'}]
Least Utilized Service
locators:  ['fc00:0:2222::', 'fc00:0:3333::', 'fc00:0:4444::', 'fc00:0:7777::']
prefix_sids:  [100002, 100003, 100004, 100007]
srv6 sid:  fc00:0:2222:3333:4444:7777::
adding vpp sr-policy to:  20.0.0.0/24 , with SRv6 encap:  fc00:0:2222:3333:4444:7777::
sr steer: The requested SR steering policy could not be deleted.
sr policy: BUG: sr policy returns -1
ipv4-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
20.0.0.0/24 fib:0 index:36 locks:2
  SR refs:1 entry-flags:uRPF-exempt, src-flags:added,contributing,active,
    path-list:[41] locks:2 flags:shared, uPRF-list:39 len:0 itfs:[]
      path:[49] pl-index:41 ip6 weight=1 pref=0 recursive:  oper-flags:resolved,
        via 101::101 in fib:3 via-fib:35 via-dpo:[dpo-load-balance:37]

 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:38 buckets:1 uRPF:38 to:[0:0]]
    [0] [@15]: dpo-load-balance: [proto:ip4 index:37 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@14]: SR: Segment List index:[0]
	Segments:< fc00:0:2222:3333:4444:7777:: > - Weight: 1
```

7. Repeat, or just spot-check, steps 2 - 5

### Low Latency Path
The procedure on Amsterdam is the same as Least Utilized Path. As with Rome, we'll focus on SRv6 for these final steps.

1. Low latency SRv6 path on Amsterdam VM:
```
python3 jalapeno.py -f amsterdam.json -e srv6 -s ll
ping 20.0.0.1 -i .4
```
Example output:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f amsterdam.json -e srv6 -s ll
src data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'src_peer': '10.0.0.1'}]
dest data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'dst_peer': '10.0.0.7'}]
Low Latency Service
locators:  ['fc00:0:5555::', 'fc00:0:6666::', 'fc00:0:7777::']
prefix_sids:  [100005, 100006, 100007]
srv6 sid:  fc00:0:5555:6666:7777::
adding vpp sr-policy to:  20.0.0.0/24 , with SRv6 encap:  fc00:0:5555:6666:7777::
unknown input `20.0.0.0/24'
Display VPP FIB entry: 
ipv4-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
20.0.0.0/24 fib:0 index:33 locks:2
  SR refs:1 entry-flags:uRPF-exempt, src-flags:added,contributing,active,
    path-list:[37] locks:2 flags:shared, uPRF-list:36 len:0 itfs:[]
      path:[45] pl-index:37 ip6 weight=1 pref=0 recursive:  oper-flags:resolved,
        via 101::101 in fib:2 via-fib:30 via-dpo:[dpo-load-balance:32]

 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:35 buckets:1 uRPF:37 to:[0:0]]
    [0] [@15]: dpo-load-balance: [proto:ip4 index:32 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@14]: SR: Segment List index:[0]
	Segments:< fc00:0:5555:6666:7777:: > - Weight: 1
```

3. The Low latency path should be xrd01 -> xrd05 -> xrd06 -> xrd07 -> Rome. So we can run the tcpdump script On XRD VM as follows (or just check one or two tcpdumps):
```
./tcpdump.sh xrd01-xrd05
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd06-xrd07
```

### Data Sovereignty Path 

The procedure on Amsterdam is the same as the previous two services. In amsterdam.json we've specified 'FRA' as the country to avoid, so all results should avoid xrd06.
 
1. Data Sovereignty via SRv6 path from Amsterdam VM:
```
python3 jalapeno.py -f amsterdam.json -e srv6 -s ds
ping 20.0.0.1 -i .4
```
Example output:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_8/python$ python3 jalapeno.py -f amsterdam.json -e srv6 -s ds
src data:  [{'id': 'unicast_prefix_v4/10.101.2.0_24_10.0.0.1', 'src_peer': '10.0.0.1'}]
dest data:  [{'id': 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7', 'dst_peer': '10.0.0.7'}]
Data Sovereignty Service
dst:  20.0.0.0/24
path:  [{'path': [None, 'xrd05', 'xrd04', 'xrd07', None], 'sid': [None, 'fc00:0:5555::', 'fc00:0:4444::', 'fc00:0:7777::', None], 'prefix_sid': [None, 100005, 100004, 100007, None], 'countries_traversed': [[], ['NLD', 'GBR'], ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'SRB', 'BGR', 'TUR'], ['TUR', 'GRC', 'ITA'], []], 'latency': 95, 'percent_util_out': 33.333333333333336}]
locators:  ['fc00:0:5555::', 'fc00:0:4444::', 'fc00:0:7777::']
srv6 sid:  fc00:0:5555:4444:7777::
prefix_sids:  [100005, 100004, 100007]
adding vpp sr-policy to:  20.0.0.0/24 , with SRv6 encap:  fc00:0:5555:4444:7777::
sr steer: The requested SR steering policy could not be deleted.
sr policy: BUG: sr policy returns -1
Display VPP FIB entry: 
ipv4-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
20.0.0.0/24 fib:0 index:36 locks:2
  SR refs:1 entry-flags:uRPF-exempt, src-flags:added,contributing,active,
    path-list:[40] locks:2 flags:shared, uPRF-list:39 len:0 itfs:[]
      path:[48] pl-index:40 ip6 weight=1 pref=0 recursive:  oper-flags:resolved,
        via 101::101 in fib:2 via-fib:33 via-dpo:[dpo-load-balance:36]

 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:38 buckets:1 uRPF:40 to:[0:0]]
    [0] [@15]: dpo-load-balance: [proto:ip4 index:36 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@14]: SR: Segment List index:[0]
	Segments:< fc00:0:5555:4444:7777:: > - Weight: 1
```
3. tcpdump options on XRD VM:
```
./tcpdump.sh xrd01-xrd05
./tcpdump.sh xrd05-xrd04
./tcpdump.sh xrd04-xrd07
```
### You have reached the end of LTRSPG-2212, hooray!