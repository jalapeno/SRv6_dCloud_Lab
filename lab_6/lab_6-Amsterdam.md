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
locators:  [None, 'fc00:0:5::', 'fc00:0:6::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:5::', 'fc00:0:4::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:2::', 'fc00:0:6::', 'fc00:0:7::', None]
locators:  [None, 'fc00:0:2::', 'fc00:0:3::', 'fc00:0:4::', 'fc00:0:7::', None]
```

### Least Utilized Path
Least Utilized Path: this service looks to steer lower priority or delay tolerant traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's best path for higher priority traffic.

Note: the client automatically cleans up old VPP routes/SR-policies prior to installing new ones:

1. Execute the least utilized path service with SR encapsulation
``` 
python3 client.py -f amsterdam.json -e sr -s lu
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

7. Use tcpdump.sh <xrd0x-xrd0y>" to capture packets along the path from Rome VM to Amsterdam VM. Given the label stack seen above, we'll monitor the linux bridges linking xrd07 and xrd06, xrd06 and xrd05, then xrd05 and xrd01:
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

8. Cleanup Rome's routes and execute the least utilized path service with SRv6 encapsulation
```
./cleanup_rome_routes.sh 
python3 client.py -f rome.json -e srv6 -s ll
```

9. Repeat, or just spot-check, steps 2 - 7

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
