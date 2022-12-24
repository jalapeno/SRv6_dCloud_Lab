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

3. On the Rome VM cd into the lab_6 directory where the client resides:
```
cd ~/SRv6_dCloud_Lab/lab_6
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

 https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_6/netservice/gp.py#L37

  - Sample command line output:
```
locators:  [None, 'fc00:0:5::', 'fc00:0:6::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:5::', 'fc00:0:4::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:2::', 'fc00:0:6::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:2::', 'fc00:0:3::', 'fc00:0:4::', 'fc00:0:7::', None]
```
You can also experiment with the script's graph traversal parameters to limit or expand the number of vertex 'hops' the query will search for. Note: ArangoDB considers the source and destination vertices as 'hops' when doing its graph traversal.

2. Change the 'gp' service's hopcount parameters. Open the netservice/gp.py file in a text editor (vi, vim) and change parameters in line 9. https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_6/netservice/gp.py#L9

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

1. Execute the least utilized path service with SR encapsulation
``` 
python3 client.py -f rome.json -e sr -s lu
```
```
python3 client.py -f rome.json -e srv6 -s lu
```
2. Check log output and linux ip route:
 ```
cat log/least_utilized.json

ip route

```
3. Run a ping test 
 - Open up a second ssh session to the Rome VM
 - Start tcpdump on 2nd ssh session:
```
sudo tcpdump -ni ens192
```
 - Return to the first Rome ssh session and ping
```
ping 10.0.0.1 -i .4
```
4. Validate traffic is encapsulated in the SR label stack. Expected output will be something like:
```
cisco@rome:~$ sudo tcpdump -ni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
23:30:45.565960 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 1, length 64
23:30:45.571246 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 1, length 64
23:30:45.966843 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 2, length 64
23:30:45.971546 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 2, length 64
23:30:46.368126 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 3, length 64
23:30:46.372139 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 3, length 64
```
3. Use tcpdump on the xrd VM to trace labeled packets through the network
 - On the xrd VM cd into the lab_6 directory
 - run the dockernets.sh shell script, which will write the appropriate linux bridge names to a file
```
# ingress to xrd07
sudo tcpdump -ni ens192

### Low Latency Path

``` 
python3 client.py -f rome.json -e sr -s ll
```
```
python3 client.py -f rome.json -e srv6 -s ll
```
 - check log output:
 ```
cat log/low_latency.json
```

### Data Sovereignty Path 
#### DS and Segment Routing
1. Run the client
``` 
python3 client.py -f rome.json -e sr -s ds
```
 - check log output:
 ```
cat log/data_sovereignty.json
```
2. Ping test 
 - Open up a second ssh session to Rome VM
 - Start tcpdump:
```
sudo tcpdump -ni ens192
```
 - Start ping on first Rome ssh session:
```
ping 10.0.0.1 -i .4
```
 - Validate traffic is encapsulated in the SR label stack. Expected output:
```
cisco@rome:~$ sudo tcpdump -ni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
23:30:45.565960 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 1, length 64
23:30:45.571246 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 1, length 64
23:30:45.966843 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 2, length 64
23:30:45.971546 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 2, length 64
23:30:46.368126 MPLS (label 100004, exp 0, ttl 64) (label 100005, exp 0, ttl 64) (label 100001, exp 0, [S], ttl 64) IP 10.107.1.1 > 10.0.0.1: ICMP echo request, id 3, seq 3, length 64
23:30:46.372139 IP 10.0.0.1 > 10.107.1.1: ICMP echo reply, id 3, seq 3, length 64
```
3. Use tcpdump on the xrd VM to trace labeled packets through the network
 - On the xrd VM cd into the lab_6 directory
 - run the dockernets.sh shell script, which will write the appropriate linux bridge names to a file
```
# ingress to xrd07
sudo tcpdump -ni ens192




#### DS and SRv6
1. cleanup any old routes:
```
./cleanup_rome_routes.sh
```
2. re-run the client with SRv6 encap:
```
python3 client.py -f rome.json -e srv6 -s ds
```
4. IPv6 ND may not have worked. Login to xrd07 and ping Rome vm
```
ping fc00:0:107:1::1
```
5. re-run the ping/tcpdump test. Expected output:
```
cisco@rome:~$ sudo tcpdump -ni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
23:40:41.614862 IP6 fe80::250:56ff:fe86:8789 > fc00:0:107:1::2: ICMP6, neighbor solicitation, who has fc00:0:107:1::2, length 32
23:40:41.615999 IP6 fc00:0:107:1::2 > fe80::250:56ff:fe86:8789: ICMP6, neighbor advertisement, tgt is fc00:0:107:1::2, length 32
23:40:42.665521 IP6 fc00:0:107:1::1 > fc00:0:4:5:1::: srcrt (len=2, type=4, segleft=0[|srcrt]
23:40:43.086871 IP6 fc00:0:107:1::1 > fc00:0:4:5:1::: srcrt (len=2, type=4, segleft=0[|srcrt]
23:40:43.502868 IP6 fc00:0:107:1::1 > fc00:0:4:5:1::: srcrt (len=2, type=4, segleft=0[|srcrt]
23:40:43.918911 IP6 fc00:0:107:1::1 > fc00:0:4:5:1::: srcrt (len=2, type=4, segleft=0[|srcrt]
```
