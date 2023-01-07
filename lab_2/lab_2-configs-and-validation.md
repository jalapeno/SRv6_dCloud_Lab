### Transport BGP global table prefixes over SR/SRv6 and apply manual SR/SRv6 steering policies

#### BGP-LU and SR-MPLS

#### We'll also configure SRv6 transport for BGP, however, we won't use it till later in the lab

1. Configure BGP-LU and advertise client prefixes via BGP IPv4 Labeled Unicast, resolving to SR-MPLS next hop

xrd01
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MAIN
  network 10.101.1.0/24
  network 10.101.2.0/24
  allocate-label all
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   next-hop-self
```
xrd05
```
router bgp 65000
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   route-reflector-client
```
xrd06
```
router bgp 65000
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   route-reflector-client
```
xrd07
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MAIN
  network 10.107.1.0/24
  network 20.0.0.0/24
  network 30.0.0.0/24
  allocate-label all
 !
 neighbor-group ibgp-v4
  address-family ipv4 labeled-unicast
   next-hop-self
```
2. Validate BGP-LU:
```
RP/0/RP0/CPU0:xrd01#sho bgp ipv4 labeled-unicast labels 
Fri Jan  6 16:26:29.446 UTC
BGP router identifier 10.0.0.1, local AS number 65000
BGP generic scan interval 60 secs
Non-stop routing is enabled
BGP table state: Active
Table ID: 0xe0000000   RD version: 34
BGP main routing table version 34
BGP NSR Initial initsync version 12 (Reached)
BGP NSR/ISSU Sync-Group versions 0/0
BGP scan interval 60 secs

Status codes: s suppressed, d damped, h history, * valid, > best
              i - internal, r RIB-failure, S stale, N Nexthop-discard
Origin codes: i - IGP, e - EGP, ? - incomplete
   Network            Next Hop        Rcvd Label      Local Label
*> 10.0.0.1/32        0.0.0.0         nolabel         3
* i10.0.0.5/32        10.0.0.5        3               nolabel
* i10.0.0.6/32        10.0.0.6        3               nolabel
*>i10.0.0.7/32        10.0.0.7        3               24007
* i                   10.0.0.7        nolabel         24007
*> 10.101.1.0/24      0.0.0.0         nolabel         3
*> 10.101.2.0/24      10.101.1.1      nolabel         24006
*>i10.107.1.0/24      10.0.0.7        3               24008
* i                   10.0.0.7        nolabel         24008
*>i20.0.0.0/24        10.0.0.7        24006           24009
* i                   10.0.0.7        nolabel         24009
*>i30.0.0.0/24        10.0.0.7        24007           24010
* i                   10.0.0.7        nolabel         24010

Processed 9 prefixes, 13 paths
```
3. Validate CEF
```
RP/0/RP0/CPU0:xrd01#show cef 20.0.0.0/24
Fri Jan  6 16:21:40.962 UTC
20.0.0.0/24, version 321, internal 0x5000001 0x40 (ptr 0x8734c6d8) [1], 0x600 (0x87979530), 0xa08 (0x8931e468)
 Updated Jan  6 16:15:43.027
 Prefix Len 24, traffic index 0, precedence n/a, priority 4
  gateway array (0x877e1400) reference count 6, flags 0x78, source rib (7), 0 backups
                [3 type 5 flags 0x8441 (0x8935d708) ext 0x0 (0x0)]
  LW-LDI[type=5, refc=3, ptr=0x87979530, sh-ldi=0x8935d708]
  gateway array update type-time 1 Jan  6 16:15:43.027
 LDI Update time Jan  6 16:15:43.027
 LW-LDI-TS Jan  6 16:15:43.027
   via 10.0.0.7/32, 5 dependencies, recursive [flags 0x6000]
    path-idx 0 NHID 0x0 [0x87390f08 0x0]
    recursion-via-/32
    next hop 10.0.0.7/32 via 100007/0/21
     local label 24009 
     next hop 10.1.1.1/32 Gi0/0/0/1    labels imposed {100007 24006}
     next hop 10.1.1.9/32 Gi0/0/0/2    labels imposed {100007 24006}

    Load distribution: 0 (refcount 3)

    Hash  OK  Interface                 Address
    0     Y   recursive                 100007/0    
```
 - Note the labels imposed: 100007 prefix SID for remote node, then label 24xxx for the BGP-LU prefix

4. Validate we have a BGP SRv6 SID
```

```

5. Setup tcpdump to monitor traffic: on the XRD VM cd into the util directory and run the tcpdump.sh script
```
cd ~/SRv6_dCloud_Lab/util/

./tcpdump.sh xrd01-xrd02
```
6. Ping from Amsterdam VM to Rome VM:
```
cisco@amsterdam:~/SRv6_dCloud_Lab$ ping 20.0.0.1 -i .4
PING 20.0.0.1 (20.0.0.1) 56(84) bytes of data.
64 bytes from 20.0.0.1: icmp_seq=22 ttl=59 time=10.6 ms
64 bytes from 20.0.0.1: icmp_seq=23 ttl=59 time=7.69 ms
64 bytes from 20.0.0.1: icmp_seq=24 ttl=59 time=6.39 ms
```
 - tcpdump output should look something like:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd01-xrd02
sudo tcpdump -ni br-5a3eaa9b7732
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-5a3eaa9b7732, link-type EN10MB (Ethernet), capture size 262144 bytes
11:58:24.533265 MPLS (label 100007, exp 0, ttl 62) (label 24006, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 9, seq 22, length 64
11:58:24.538433 IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 9, seq 22, length 64
11:58:24.933216 MPLS (label 100007, exp 0, ttl 62) (label 24006, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 9, seq 23, length 64
11:58:24.936592 IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 9, seq 23, length 64
11:58:25.333398 MPLS (label 100007, exp 0, ttl 62) (label 24006, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 9, seq 24, length 64
11:58:25.336681 IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 9, seq 24, length 64
```

7. tcpdump other links in the network with ping still running
```
./tcpdump.sh xrd02-xrd06
./tcpdump.sh xrd07-xrd07
```