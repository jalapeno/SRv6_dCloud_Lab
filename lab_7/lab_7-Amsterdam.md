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

1. On the Amsterdam VM cd into the lab_6 directory:
```
cd ~/SRv6_dCloud_Lab/lab_6
```
2. Everything is the same as on the Rome VM with some different parameters in amsterdam.json:
```
cat amsterdam.json
```
3. Amsterdam has a Linux veth pair connecting kernel forwarding to its onboard VPP instance. The VM has preconfigured ip routes (see /etc/netplan/00-installer-config.yaml) pointing to VPP via its "ams-out" interface:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ ip link | grep ams-out
4: vpp-in@ams-out: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
5: ams-out@vpp-in: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000

cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ ip route
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
 - VPP startup-config file: https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_0/config/vpp.conf

5. VPP's CLI may be invoked directly:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ sudo vppctl
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
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ sudo vppctl show interface address
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
