# Lab 4: Configure SRv6-L3VPN and perform SRv6-TE steering of L3VPN prefixes

### Description
In lab 4 we will establish a Layer-3 VPN named "carrots" which will use SRv6 transport and will have endpoints on xrd01, xrd06, and xrd07. xrd01 and xrd06 will only have loopback interfaces participating in the L3VPN. xrd07's gi 0/0/0/3 interface connects to a secondary NIC on the Rome VM and will also be attached to the L3VPN. Once the L3VPN is established and has run some test traffic we will then setup SRv6-TE traffic steering to specific Rome prefixes.

## Contents
1. [Configure SRv6 L3VPN](#configure-srv6-l3vpn)
2. [Validate SRv6 L3VPN](#validate-srv6-l3vpn)
3. [Configure SRv6-TE steering for L3VPN](#configure-srv6-te-steering-for-l3vpn)
4. [Validate SRv6-TE steering of L3VPN traffic](#validate-srv6-te-steering-of-l3vpn-traffic)

### Configure SRv6 L3VPN

1. Configure the VRF on xrd01, 06, and 07:

```
vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
  address-family ipv6 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
 !
!
```

2. Configure interfaces to participate in the L3VPN:

#### xrd01
```
interface Loopback9
 vrf carrots
 ipv4 address 10.9.1.1 255.255.255.0
 ipv6 address 10:9:1::1/64
!
```
<<< Remove xrd06 config>>>
 #### xrd06
```
interface Loopback9
 vrf carrots
 ipv4 address 10.9.6.1 255.255.255.0
 ipv6 address 10:9:6::1/64
```

#### xrd07
In addition to configuring gi 0/0/0/3 to be a member of VRF carrots, xrd07 will need a pair of static routes to get to Rome's "40" and "50" prefixes:
```
interface GigabitEthernet0/0/0/3
 vrf carrots
 ipv4 address 10.107.2.2 255.255.255.0
 ipv6 address fc00:0:107:2::2/64
!
router static
 vrf carrots
  address-family ipv4 unicast
   40.0.0.0/24 10.107.2.1
   50.0.0.0/24 10.107.2.1
  !
  address-family ipv6 unicast
   fc00:0:40::/64 fc00:0:107:2::1
   fc00:0:50::/64 fc00:0:107:2::1
```

3. Ping check from xrd07 gi 0/0/0/3 to Rome VM 2nd NIC:
```
ping vrf carrots 10.107.2.1
ping vrf carrots 40.0.0.1
ping vrf carrots 50.0.0.1
ping vrf carrots fc00:0:107:2::1
ping vrf carrots fc00:0:40::1
ping vrf carrots fc00:0:50::1
```

4. Configure BGP vpnv4 under the IPv6 peering sessions, and the BGP VRF instance on PE routers xrd01 and xrd07:

#### xrd01
We'll redistribute the VRF's connected loopback routes into BGP vpnv4 and vpnv6:
```
router bgp 65000
 neighbor-group ibgp-v6
  address-family vpnv4 unicast
   next-hop-self
  !
  address-family vpnv6 unicast
   next-hop-self
  !
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute connected
 !
!

```

#### xrd05
Just needs RR config:
```
router bgp 65000
 neighbor-group ibgp-v6
  address-family vpnv4 unicast
   route-reflector-client
  !
  address-family vpnv6 unicast
   route-reflector-client
  !
 !
```

#### xrd06
Needs RR config, and has a loopback that'll participate in the L3VPN.
We'll redistribute the VRF's connected loopback routes into BGP vpnv4 and vpnv6:
```
router bgp 65000
 neighbor-group ibgp-v6
  address-family vpnv4 unicast
   route-reflector-client
  !
  address-family vpnv6 unicast
   route-reflector-client
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!

```

#### xrd07
On xrd07 we'll redistribute the VRF's static routes into BGP:
```
router bgp 65000
 neighbor-group ibgp-v6
  address-family vpnv4 unicast
   next-hop-self
  !
  address-family vpnv6 unicast
   next-hop-self
  !
 !
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute static
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator ISIS
    alloc mode per-vrf
   !
   redistribute static
  !
 !
!
```

### Validate SRv6 L3VPN

From xrd01 run the following set of validation commands:
 - Validation command output examples can be found [here](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_4/validation-cmd-output.md)
```
show segment-routing srv6 sid
show bgp vpnv4 unicast
show bgp vpnv4 unicast rd 10.0.0.7:0 10.9.7.0/24
show bgp vpnv6 unicast
show bgp vpnv6 unicast rd 10.0.0.7:0 fc00:0:40::/64
ping vrf carrots 10.9.6.1
ping vrf carrots 10:9:6::1  
ping vrf carrots 40.0.0.1
ping vrf carrots 50.0.0.1
ping vrf carrots fc00:0:40::1
ping vrf carrots fc00:0:50::1
```
### Configure SRv6-TE steering for L3VPN

Rome's L3VPN IPv4 and IPv6 prefixes are associated with two classes of traffic. The "40" destinations (40.0.0.0/24 and fc00:0:40::/64) are for Bulk Transport (content replication or data backups) and thus are latency and loss tolerant. The "50" destinations (50.0.0.0/24 and fc00:0:50::/64) are for real time traffic (live video, etc.) and thus require the lowest latency path available.

1. On xrd07 advertise Rome's loopback prefixes with their respective color extended communities:
#### xrd07
```
extcommunity-set opaque bulk-transfer
  40
end-set
!
extcommunity-set opaque low-latency
  50
end-set
!
route-policy set-color
  if destination in (40.0.0.0/24) then
    set extcommunity color bulk-transfer
  endif
  if destination in (50.0.0.0/24) then
    set extcommunity color low-latency
  endif
  if destination in (fc00:0:40::/64) then
    set extcommunity color bulk-transfer
  endif
  if destination in (fc00:0:50::/64) then
    set extcommunity color low-latency
  endif
  pass
end-policy
!
router bgp 65000
 neighbor-group ibgp-v6
  address-family vpnv4 unicast
   route-policy set-color out
  !
  address-family vpnv6 unicast
   route-policy set-color out
 !
```

2. Validate vpnv4 and v6 prefixes are received at xrd01 and that they have their color extcomms:
#### xrd01
```
show bgp vpnv4 uni vrf carrots 40.0.0.0/24
show bgp vpnv4 uni vrf carrots 50.0.0.0/24
show bgp vpnv6 uni vrf carrots fc00:0:40::/64
show bgp vpnv6 uni vrf carrots fc00:0:50::/64
```
Examples:
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
Sat Jan  7 21:27:26.645 UTC
BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  58           58
Last Modified: Jan  7 21:27:19.204 for 00:00:07
Paths: (1 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
      Received Path ID 0, Local Path ID 1, version 30
      Extended community: Color:40 RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
      Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:0

RP/0/RP0/CPU0:xrd01#show bgp vpnv6 uni vrf carrots fc00:0:50::/64
Sat Jan  7 21:27:56.050 UTC
BGP routing table entry for fc00:0:50::/64, Route Distinguisher: 10.0.0.1:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  46           46
Last Modified: Jan  7 21:27:19.204 for 00:00:36
Paths: (1 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0050
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
      Received Path ID 0, Local Path ID 1, version 34
      Extended community: Color:50 RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:62, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
      Source AFI: VPNv6 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:0

```

3. On xrd01 configure a pair of SRv6-TE segment lists for traffic steering: 
 - xrd2347 will be explicit path: xrd01 -> 02 -> 03 -> 04 -> 07
 - xrd567 will be explicit path: xrd01 -> 05 -> 06 -> 07
```
segment-routing
 traffic-eng
  segment-lists
   srv6
    sid-format usid-f3216
   !
   segment-list xrd2347
    srv6
     index 10 sid fc00:0:3333::
     index 20 sid fc00:0:4444::
    !
   !
  !
   segment-list xrd567
    srv6
     index 10 sid fc00:0:5555::
     index 20 sid fc00:0:6666::
    !
   !
  ! 
```

4. On xrd01 configure our bulk transport and low latency SRv6 steering policies:
```
  policy bulk-transfer
   srv6
    locator ISIS binding-sid dynamic behavior ub6-insert-reduced
   !
   color 40 end-point ipv6 fc00:0:7777::1
   candidate-paths
    preference 100
     explicit segment-list xrd2347
     !
    !
   !
  !
  policy low-latency
   srv6
    locator ISIS binding-sid dynamic behavior ub6-insert-reduced
   !
   color 50 end-point ipv6 fc00:0:7777::1
   candidate-paths
    preference 100
     explicit segment-list xrd567
     !
    !
   !
  ! 

```
### Validate SRv6-TE steering of L3VPN traffic
#### Validate bulk traffic takes the non-shortest path: xrd01 -> 02 -> 03 -> 04 -> 07 
1. Run the tcpdump.sh script in the util directory on the following links in the network
```
./tcpdump.sh xrd01-xrd02
./tcpdump.sh xrd02-xrd03
./tcpdump.sh xrd03-xrd04
./tcpdump.sh xrd04-xrd07
```

2. Ping from xrd01 to Rome's bulk transport destination IPv4 and IPv6 addresses:
```
ping vrf carrots 40.0.0.1 count 3
ping vrf carrots fc00:0:40::1 count 3
```
Example: tcpdump.sh output should look something like below on the xrd02-xrd03 link with both outer SRv6 uSID header and inner IPv4/6 headers. Note in this case the outbound traffic is taking a non-shortest path.  We don't have a specific policy for return traffic so it will take one of the ECMP shortest paths; thus we do not see replies in the tcpdump output:
```
16:37:30.292761 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e004::: IP 10.9.1.1 > 40.0.0.1: ICMP echo request, id 56816, seq 0, length 80
16:37:30.298145 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e004::: IP 10.9.1.1 > 40.0.0.1: ICMP echo request, id 56816, seq 1, length 80
16:37:30.302781 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e004::: IP 10.9.1.1 > 40.0.0.1: ICMP echo request, id 56816, seq 2, length 80


16:38:10.502018 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e005::: IP6 10:9:1::1 > fc00:0:40::1: ICMP6, echo request, seq 0, length 60
16:38:10.506355 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e005::: IP6 10:9:1::1 > fc00:0:40::1: ICMP6, echo request, seq 1, length 60
16:38:10.510069 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e005::: IP6 10:9:1::1 > fc00:0:40::1: ICMP6, echo request, seq 2, length 60
```

#### Validate low latency traffic takes the path: xrd01 -> 05 -> 06 -> 07 
1. Run the tcpdump.sh script in the util directory against xrd01's outbound interfaces:
```
./tcpdump.sh xrd01-xrd05
./tcpdump.sh xrd05-xrd06
./tcpdump.sh xrd06-xrd07
```

2. Ping from xrd01 to Rome's low latency destination IPv4 and IPv6 addresses:
```
ping vrf carrots 50.0.0.1 count 3
ping vrf carrots fc00:0:50::1 count 3
```
Example: tcpdump.sh output should look something like below on the xrd05-xrd06 link. In this case xrd05 -> 06 -> 07 is one of the IGP shortest paths. The v4 flow's replies are taking the same return path, however the v6 flow's replies have been hashed onto one of the other ECMP paths:
```
16:50:26.667875 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e004::: IP 10.9.1.1 > 50.0.0.1: ICMP echo request, id 59290, seq 0, length 80
16:50:26.670199 IP6 fc00:0:7777::1 > fc00:0:1111:e004::: IP 50.0.0.1 > 10.9.1.1: ICMP echo reply, id 59290, seq 0, length 80
16:50:26.672654 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e004::: IP 10.9.1.1 > 50.0.0.1: ICMP echo request, id 59290, seq 1, length 80
16:50:26.674647 IP6 fc00:0:7777::1 > fc00:0:1111:e004::: IP 50.0.0.1 > 10.9.1.1: ICMP echo reply, id 59290, seq 1, length 80
16:50:26.676429 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e004::: IP 10.9.1.1 > 50.0.0.1: ICMP echo request, id 59290, seq 2, length 80
16:50:26.677974 IP6 fc00:0:7777::1 > fc00:0:1111:e004::: IP 50.0.0.1 > 10.9.1.1: ICMP echo reply, id 59290, seq 2, length 80


16:50:37.953305 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e005::: IP6 10:9:1::1 > fc00:0:50::1: ICMP6, echo request, seq 0, length 60
16:50:37.958148 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e005::: IP6 10:9:1::1 > fc00:0:50::1: ICMP6, echo request, seq 1, length 60
16:50:37.961713 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e005::: IP6 10:9:1::1 > fc00:0:50::1: ICMP6, echo request, seq 2, length 60
16:50:42.047007 IS-IS, p2p IIH, src-id 0000.0000.0006, length 1497

```
Found the return traffic:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05
sudo tcpdump -ni br-9c9433e006cf
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-9c9433e006cf, link-type EN10MB (Ethernet), capture size 262144 bytes
16:55:37.491924 IS-IS, p2p IIH, src-id 0000.0000.0005, length 1497
16:55:38.814093 IP6 fc00:0:7777::1 > fc00:0:1111:e005::: IP6 fc00:0:50::1 > 10:9:1::1: ICMP6, echo reply, seq 0, length 60
16:55:38.817918 IP6 fc00:0:7777::1 > fc00:0:1111:e005::: IP6 fc00:0:50::1 > 10:9:1::1: ICMP6, echo reply, seq 1, length 60
16:55:38.821203 IP6 fc00:0:7777::1 > fc00:0:1111:e005::: IP6 fc00:0:50::1 > 10:9:1::1: ICMP6, echo reply, seq 2, length 60
```


### End of lab 4
Please proceed to [Lab 5](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_5/lab_5-guide.md)
