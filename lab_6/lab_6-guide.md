## Build a POC host-based/cloud-native SRv6 SDN 

Todo:
1. Build and test this lab
2. Writeup lab guide

### Rome client VM
This VM has a client script that will query Jalapeno and create a linux ip route with SRv6 encapsulation

Ref: https://segment-routing.org/index.php/Implementation/Configuration

1. Set your localsid source address:

```
sudo ip sr tunsrc set fc00:0:107:1::1
```

2. Build the script

3. Run the script

```
python3 rome_client.py -s least_utilized -e srv6 -f src_dst.json
```
