### Transport BGP global table prefixes over SR/SRv6 and apply manual SR/SRv6 steering policies

#### BGP-LU and SR-MPLS

1. Configure BGP-LU and advertise client prefixes via BGP IPv4 Labeled Unicast, resolving to SR-MPLS next hop

xrd01
```
router bgp 65000
 address-family ipv4 unicast
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

4. Setup tcpdump to monitor traffic: on the XRD VM cd into the util directory and run the tcpdump.sh script
```
cd ~/SRv6_dCloud_Lab/util/

./tcpdump.sh xrd01-xrd02
```
5. Ping from Amsterdam VM to Rome VM:
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

#### SRv6-TE for prefixes in the global table

1. advertise 30.0.0.0 via BGP IPv6 Unicast, resolving to SRv6/IPv6 next hop

xrd07 config - first we'll need to exchange a v4 prefix
```
route-policy drop-20-net
  if destination in (20.0.0.0/24) then
    drop
  else
    pass
  endif
end-policy
!
route-policy drop-30-net
  if destination in (30.0.0.0/24) then
    drop
  else
    pass
  endif
end-policy
!
router bgp 65000
 neighbor 10.0.0.5
  address-family ipv4 unicast
   route-policy drop-30-net out
  !
 !
 neighbor 10.0.0.6
  address-family ipv4 unicast
   route-policy drop-30-net out
  !
 !
!


```

R01 
```
vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
 !
!
interface Loopback9
 vrf carrots
 ipv4 address 10.9.1.1 255.255.255.0
!
route-policy SID($SID)
  set label-index $SID
end-policy
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MAIN
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!

```

R06
```
vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
 !
!
interface Loopback9
 vrf carrots
 ipv4 address 10.9.6.1 255.255.255.0
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MAIN
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!

```

R07
```
vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
 !
!
interface Loopback9
 vrf carrots
 ipv4 address 10.9.7.1 255.255.255.0
!
route-policy SID($SID)
  set label-index $SID
end-policy
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MAIN
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!
```

Validate changes:
```

show segment-routing srv6 sid
show bgp vpnv4 unicast rd 10.0.0.1:0 10.9.1.0/24
ping 10.0.128.5 source lo128
ping fc00:0:8005::1 source lo128
```

Expected output:
```     
RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
Tue Dec 13 18:49:00.104 UTC

*** Locator: 'BGP' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:8001::               uN (PSP/USD)      'default':32769                   sidmgr              InUse  Y 
fc00:0:8001:e004::          uDT4              'carrots'                         bgp-65000           InUse  Y 
fc00:0:8001:e005::          uDT4              'default'                         bgp-65000           InUse  Y 
fc00:0:8001:e006::          uDT6              'default'                         bgp-65000           InUse  Y 

*** Locator: 'MAIN' *** 

fc00:0000:1111::                  uN (PSP/USD)      'default':1                       sidmgr              InUse  Y 
fc00:0:1:e000::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1:e001::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1:e002::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1:e003::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 

RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.1:0 10.9.1.0/24
Tue Dec 13 18:49:43.825 UTC
BGP routing table entry for 10.9.1.0/24, Route Distinguisher: 10.0.0.1:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                   4            4
    SRv6-VPN SID: fc00:0:8001:e004::/64
Last Modified: Dec 13 18:46:11.905 for 00:03:32
Paths: (1 available, best #1)
  Advertised to update-groups (with more than one peer):
    0.2 
  Path #1: Received by speaker 0
  Advertised to update-groups (with more than one peer):
    0.2 
  Local
    0.0.0.0 from 0.0.0.0 (10.0.0.1)
      Origin incomplete, metric 0, localpref 100, weight 32768, valid, redistributed, best, group-best, import-candidate
      Received Path ID 0, Local Path ID 1, version 4
      Extended community: RT:9:9 
RP/0/RP0/CPU0:xrd01#