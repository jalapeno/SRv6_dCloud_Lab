## POC host-based SRv6 and SR-MPLS SDN 

The Rome VM is simulating a linux host or other endpoint that will subscribe to SR and SRv6 services from the XRd network

1. Enable MPLS forwarding on xrd01 and xrd07 host-facing interfaces to allow for forwarding of labeled packets coming from the Rome VM

```
mpls static
 int gigabitEthernet 0/0/0/0
 commit
```
validate:
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

2.  Login to the Rome VM
```
ssh cisco@198.18.128.103
```
Both the Rome and Amsterdam VM's are pre-loaded with a python client that can query Jalapeno and create linux ip routes with SR or SRv6 encapsulations.

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

 - For host-based SR we'll simply use Linux's iproute2 MPLS implemenation. There are a number of decent references to be found; this one is very straightforward: https://liuhangbin.netlify.app/post/mpls-on-linux/

3. On the Rome VM cd into the lab_7 directory where the client resides:
```
cd ~/SRv6_dCloud_Lab/lab_7
```
2. Get familiar with files in the directory; specifically:
```
cat rome.json
cat cleanup_rome_routes.sh
cat client.py
ls netservice

```
4. Set the Rome VM's SRv6 localsid source address:

```
sudo ip sr tunsrc set fc00:0:107:1::1
```
5. Ensure Rome VM is setup to support SR/MPLS:
```
modprobe mpls_router
modprobe mpls_iptunnel
lsmod | grep mpls
```

### Jalapeno python client:
A host or endpoint with this client can request a network service between a given source and destination. Currently supported services are: Low Latency Path, Least Utilized Path, Data Sovereignty Path, and an informational Get All Paths service. The client passes its service request as a Shortest Path query to Jalapeno's Arango graphDB. The DB performs a traversal of its graph and responds with a dataset reflecting the shortest path per the query. The client receives the data, performs some data manipulation as needed and then constructs a local SR or SRv6 route/policy.

Currently the client operates as a CLI tool, which expects to see a set of command line arguments. A user or application may operate the client by specifying the desired network service (-s) and encapsulation(-e), and inputs a json file which contains source and destination info and a few other items.

For ease of use the currently supported network services are abbreviated: 

 - gp = get_all_paths
 - ll = low_latency
 - lu = least_utilized
 - ds = data_sovereignty

Example client command:
```
python3 client.py -f rome.json -e srv6 -s lu
```
client help:
```
python3 client.py -h
``` 
The client's network service modules are located in the netservice directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (gp, ll, lu, or ds) and calculates an SRv6 uSID or SR label stack, which will satisfy the network service request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route/policy.

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

2. Change the 'gp' service's hopcount parameters. Open the netservice/gp.py file in a text editor (vi, vim) and change parameters in line 9. https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_7/netservice/gp.py#L9

```
for v, e, p in 6..6 outbound
```
Save gp.py and re-run the script. You should see more path options in the command line output and log.

3. Try increasing the number of hops the graph may traverse:

 ```
 for v, e, p in 1..8 outbound
 ```
Save the file and re-run the script. You should see more path options in the command line output and log.

### Least Utilized Path
Many segment routing and SDN solutions focus on the low latency path as their primary use case. We absolutely feel low latency is an important network service, especially for real time applications. However, we believe one of the use cases which deliver the most bang for the buck is "Least Utilized Path". The idea behind this use case is that the routing protocol's chosen best path is usually the Best Path. Thus this service looks to steer lower priority traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's best path for higher priority traffic.

1. Cleanup and stale routes and execute the least utilized path service with SR encapsulation
``` 
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e sr -s lu
```
 - The client's command line output should display the new route in the routing table:
```
10.101.1.0/24  encap mpls  100006/100002/100001 via 10.107.1.2 dev ens192 
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
 - Return to the first Rome ssh session and ping
```
ping 10.101.1.1 -i .4
```

4. Validate traffic is encapsulated in the SR label stack. Expected output will be something like:
```
cisco@rome:~$ sudo tcpdump -ni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
22:17:16.770622 MPLS (label 100006, exp 0, ttl 64) (label 100002, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.101.1.1: ICMP echo request, id 30, seq 9, length 64
22:17:16.775121 IP 10.101.1.1 > 10.107.1.1: ICMP echo reply, id 30, seq 9, length 64
```

5. Open an ssh session to the xrd VM and verify the nets.sh script in the util directory has run. The directory should look like this: 
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ls
nets.sh     xrd01-xrd02  xrd02-xrd03  xrd03-xrd04  xrd04-xrd07  xrd06-xrd07
tcpdump.sh  xrd01-xrd05  xrd02-xrd06  xrd04-xrd05  xrd05-xrd06
```

6. Use tcpdump.sh <xrd0x-xrd0y>" to capture packets along the path from Rome VM to Amsterdam VM. Given the label stack seen above, we'll monitor the linux bridges linking xrd07 and xrd06, xrd06 and xrd05, then xrd05 and xrd01:
 - restart the ping if it is stopped
```
./tcpdump.sh xrd06-xrd07
./tcpdump.sh xrd02-xrd06
./tcpdump.sh xrd01-xrd02
```
 - We expect to see SR-MPLS PHP behavior as xrd nodes pop outer labels as the traffic traverses the network. Example output:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06
sudo tcpdump -ni br-9695b2ce572e
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-9695b2ce572e, link-type EN10MB (Ethernet), capture size 262144 bytes
17:17:55.352668 MPLS (label 100001, exp 0, [S], ttl 62) IP 10.107.1.1 > 10.101.1.1: ICMP echo request, id 30, seq 86, length 64
17:17:55.354834 MPLS (label 100007, exp 0, [S], ttl 62) IP 10.101.1.1 > 10.107.1.1: ICMP echo reply, id 30, seq 86, length 64
17:17:55.821760 IS-IS, p2p IIH, src-id 0000.0000.0002, length 1497
17:17:55.854029 MPLS (label 100001, exp 0, [S], ttl 62) IP 10.107.1.1 > 10.101.1.1: ICMP echo request, id 30, seq 87, length 64
17:17:55.856079 MPLS (label 100007, exp 0, [S], ttl 62) IP 10.101.1.1 > 10.107.1.1: ICMP echo reply, id 30, seq 87, length 64
```

7. Cleanup Rome's routes and execute the least utilized path service with SRv6 encapsulation
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e srv6 -s lu
```

8. Repeat, or just spot-check, steps 2 - 6

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