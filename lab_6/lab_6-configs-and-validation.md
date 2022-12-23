## Build a POC host-based/cloud-native SRv6 SDN 

Todo:
1. Build and test this lab
2. Writeup lab guide

### Rome client VM
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

3. Jalapeno SDN client:
A host or endpoint with this client can request a network service (low latency, least utilized, data sovereignty, etc.) between a given source and destination, and based on the parameters passed to the client. Upon completing its path calculation the client will automatically construct a local SR or SRv6 route/policy.

Example:
```
./client.py -f amsterdam.json -e srv6 -s lu
```
The user or application specifies the desired service (-s) and encapsulation(-e) and inputs a json file which contains source and destination info and a few other items. 

Currently supported netservices: ds = data_sovereignty, gp = get_all_paths, ll = low_latency, lu = least_utilized

The client's service modules are located in the netservice directory. When invoked the client first calls the src_dst.py module, which queries the graphDB and returns database ID info for the source and destination prefixes. The client then runs the selected service module (ds, gp, ll, or lu) and calculates an SRv6 uSID or SR label stack, which will satisfy the netservice request. The netservice module then calls the add_route.py module to create the local SR or SRv6 route/policy.

4. Operate the client:

 - client help:
```
python3 client.py -h
```

 - Get All Paths service:
 - No need to specify encapsulation type:
``` 
python3 client.py -f rome.json -s gp
```
 - check log output:
 ```
cat log/get_paths.json
```
 - we expect to see a json file with source, destination, and path data which includes srv6 sids and sr label stack info

 - Data Sovereignty service:
``` 
python3 client.py -f rome.json -e sr -s ds
```
```
python3 client.py -f rome.json -e srv6 -s ds
```
 - check log output:
 ```
cat log/data_sovereignty.json
```

 - Low Latency service:
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

 - Least Utilized service:
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