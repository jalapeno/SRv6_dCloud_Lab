## POC host-based SRv6 and SR-MPLS SDN 

Todo:
1. Finish writeup

### Enable MPLS forwarding on xrd01 and xrd07 host-facing interfaces:
```
RP/0/RP0/CPU0:xrd07(config)#
```
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

### Login to the Rome VM
```
ssh cisco@198.18.128.103
```
This VM has a client script that will query Jalapeno and create linux ip routes with SR or SRv6 encapsulations.

Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

For host-based SR we'll simply use Linux's iproute2 MPLS implemenation. There are a number of decent references to be found; this one is very straightforward: https://liuhangbin.netlify.app/post/mpls-on-linux/

1. On the Rome VM cd into the lab_6 directory:
```
cd ~/SRv6_dCloud_Lab/lab_6
```
2. Get familiar with files in the directory; specifically:
```
cat rome.json
cat cleanup_rome_routes.sh
ls netservice
cat client.py

```
3. Set your localsid source address:

```
sudo ip sr tunsrc set fc00:0:107:1::1
```
4. Ensure Rome VM is setup to support SR/MPLS:
```
modprobe mpls_router
modprobe mpls_iptunnel
lsmod | grep mpls
```

### Jalapeno SDN client:
A host or endpoint with this client can request a network service (low latency, least utilized, data sovereignty, etc.) between a given source and destination, and based on the parameters passed to the client. Upon completing its path calculation the client will automatically construct a local SR or SRv6 route/policy.

Example:
```
python3 client.py -f rome.json -e srv6 -s lu

client help:

python3 client.py -h
```
The user or application specifies the desired service (-s) and encapsulation(-e) and inputs a json file which contains source and destination info and a few other items. 

Currently supported netservices: ds = data_sovereignty, gp = get_all_paths, ll = low_latency, lu = least_utilized

The client's service modules are located in the netservice directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (ds, gp, ll, or lu) and calculates an SRv6 uSID or SR label stack, which will satisfy the netservice request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route/policy.

## Network Services
### Get All Paths Service 

1. Run the 'gp' service 
No need to specify encapsulation type:
``` 
python3 client.py -f rome.json -s gp
```
 - check log output:
```
more log/get_paths.json
```
 - we expect to see a json file with source, destination, and path data which includes srv6 sids and sr label stack info
 - the script will print several pieces of data out to the command line as it performs its logic. Notably this line which provides a summary of the relevants paths by outputing the SRv6 locators along each path:

 https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_6/netservice/gp.py#L37

You can also experiment with the script's graph traversal parameters to limit or expand the number of vertex 'hops' the query will search for. Note: ArangoDB considers the source and destination vertices as 'hops' when doing the traversal.

2. Change the 'gp' service's hopcount parameters. Open the netservice/gp.py file in a text editor (vi, vim) and change parameters in line 9. https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_6/netservice/gp.py#L9

```
for v, e, p in 6..6 outbound
```
Save the file and re-run the script.

3. Another example:

 ```
 for v, e, p in 1..8 outbound
 ```

### Data Sovereignty Service 
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

### Low Latency Service
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

### Least Utilized service:
``` 
python3 client.py -f rome.json -e sr -s lu
```
```
python3 client.py -f rome.json -e srv6 -s lu
```
 - check log output:
 ```
cat log/least_utilized.json
```