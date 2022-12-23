## POC host-based SRv6 and SR-MPLS SDN 

Todo:
1. Build and test this lab
2. Writeup lab guide

### Enable MPLS forwarding on xrd host-facing interfaces:
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
This VM has a client script that will query Jalapeno and create a linux ip route with SRv6 encapsulation

Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

1. cd into the lab_6 directory on Rome VM:
```
cd ~/SRv6_dCloud_Lab/lab_6
```
2. Get familiar with files in the directory
```
cat amsterdam.json
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
python3 client.py -f amsterdam.json -e srv6 -s lu

client help:

python3 client.py -h
```
The user or application specifies the desired service (-s) and encapsulation(-e) and inputs a json file which contains source and destination info and a few other items. 

Currently supported netservices: ds = data_sovereignty, gp = get_all_paths, ll = low_latency, lu = least_utilized

The client's service modules are located in the netservice directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (ds, gp, ll, or lu) and calculates an SRv6 uSID or SR label stack, which will satisfy the netservice request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route/policy.

### Netservices: Get All Paths

No need to specify encapsulation type:
``` 
python3 client.py -f rome.json -s gp
```
 - check log output:
```
more log/get_paths.json
```
 - we expect to see a json file with source, destination, and path data which includes srv6 sids and sr label stack info

### Netservices: Data Sovereignty 
1. DS and Segment Routing:
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
2. DS and SRv6: 
```
python3 client.py -f rome.json -e srv6 -s ds
```
 - rerun the ping/tcpdump test 

### Netservices: Low Latency service
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

5. Least Utilized service:
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