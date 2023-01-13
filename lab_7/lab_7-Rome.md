## POC host-based SRv6 and SR-MPLS SDN 

The Rome VM is simulating a user host or endpoint and will simply use its Linux dataplane to perform SR or SRv6 traffic encapsulation:

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

 - There is no Linux "SR-MPLS" per se, but from the host's perspective its just labels, so we'll use the iproute2 MPLS implemenation. There are a number of decent references to be found; this one is very straightforward: https://liuhangbin.netlify.app/post/mpls-on-linux/

1.  Login to the Rome VM
```
ssh cisco@198.18.128.103
```

2. On the Rome VM cd into the lab_7 directory where the client resides:
```
cd ~/SRv6_dCloud_Lab/lab_7
```
2. Get familiar with files in the directory; specifically:
```
cat rome.json
cat cleanup_rome_routes.sh
cat client.py
ls netservice/

```
4. For SRv6 we'll need to set Rome's SRv6 localsid source address:

```
sudo ip sr tunsrc set fc00:0:107:1::1
```
5. Ensure Rome VM is setup to support SR/MPLS:
```
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
lsmod | grep mpls
```

### Jalapeno python client:
A host or endpoint with this client can request a network service between a given source and destination. The client's currently supported services are: 

 - Low Latency Path
 - Least Utilized Path
 - Data Sovereignty Path
 - Get All Paths (informational only)
 
 When executed the client passes its service request as a Shortest Path query to Jalapeno's Arango graphDB. The DB performs a traversal of its graph and responds with a dataset reflecting the shortest path per the query. The client receives the data, performs some data manipulation as needed and then constructs a local SR or SRv6 route/policy.

Currently the client operates as a CLI tool, which expects to see a set of command line arguments. A user or application may operate the client by specifying the desired network service (-s) and encapsulation(-e), and inputs a json file which contains source and destination info and a few other items.

For ease of use the currently supported network services are abbreviated: 

 - gp = get_all_paths
 - ll = low_latency
 - lu = least_utilized
 - ds = data_sovereignty

1. Access client help with the *-h* argument:
```
python3 client.py -h
``` 
Expected output:
```
cisco@rome:~/SRv6_dCloud_Lab/lab_7$ python3 client.py -h
usage: Jalapeno client [-h] [-e E] [-f F] [-s S]

takes command line input and calls path calculator functions

optional arguments:
  -h, --help  show this help message and exit
  -e E        encapsulation type <sr> <srv6>
  -f F        json file with src, dst, parameters
  -s S        requested network service: sr = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)

client.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp>
```

Example client command with network-service arguments:
```
python3 client.py -f rome.json -e srv6 -s lu
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
ping 10.101.1.1 -i .4
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
Please proceed to [lab_7-Amsterdam.md](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_7/lab_7-Amsterdam.md)