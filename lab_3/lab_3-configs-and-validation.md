## Lab 3: Configure SRv6-L3VPN and SRv6-TE for L3VPN prefixes

### Establish L3VPN peering and prefix exchange

1. Our L3VPN customer is named "carrots":

#### xrd01 
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
interface Loopback9
 vrf carrots
 ipv4 address 10.9.1.1 255.255.255.0
 ipv6 address 10:9:1::1/64
!
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
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
 !
!

```
#### xrd05 
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
We'll include xrd06 as a participant just for kicks
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
interface Loopback9
 vrf carrots
 ipv4 address 10.9.6.1 255.255.255.0
 ipv6 address 10:9:6::1/64
!
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
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!

```

#### xrd07
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
interface Loopback9
 vrf carrots
 ipv4 address 10.9.7.1 255.255.255.0
 ipv6 address 10:9:7::1/64
!
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
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv4 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator MAIN
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!
```

#### Validate changes from xrd01. Output examples section is below:
```
show segment-routing srv6 sid
show bgp vpnv4 unicast
show bgp vpnv4 unicast rd 10.0.0.7:0 10.9.7.0/24
show bgp vpnv6 unicast
ping vrf carrots 10.9.6.1
ping vrf carrots 10:9:6::1 
ping vrf carrots 10.9.7.1
ping vrf carrots 10:9:7::1 
```
### SRv6-TE for L3VPN

1. Attach Rome VM's 2nd NIC to the L3VPN and establish static routes to Rome's loopback addresses (40.0.0.1 and 50.0.0.1). Later in lab 3 we'll SRv6-TE steer traffic to these loopbacks via different paths in the network:

#### xrd07
```
interface GigabitEthernet0/0/0/3
 vrf carrots
 ipv4 address 10.107.2.2 255.255.255.0
 no shutdown
!
router static
 vrf carrots
  address-family ipv4 unicast
   40.0.0.0/24 10.107.2.1
   50.0.0.0/24 10.107.2.1
 ```
2. Validate connectivity
```
RP/0/RP0/CPU0:xrd07#ping vrf carrots 10.107.2.1
Fri Jan  6 23:45:05.410 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.107.2.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/7 ms

RP/0/RP0/CPU0:xrd07#ping vrf carrots 40.0.0.1
Sat Jan  7 00:02:15.594 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 40.0.0.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/3 ms

RP/0/RP0/CPU0:xrd07#ping vrf carrots 50.0.0.1
Sat Jan  7 00:02:22.717 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 50.0.0.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/2 ms
RP/0/RP0/CPU0:xrd07#
```

3. On xrd07 advertise Rome's loopback prefixes with color extended communities:
#### xrd07
```
extcommunity-set opaque low-latency
  50
end-set
!
extcommunity-set opaque bulk-transfer
  40
end-set
!
route-policy set-color
  if destination in (40.0.0.0/24) then
    set extcommunity color bulk-transfer
  endif
  if destination in (50.0.0.0/24) then
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
 !
 vrf carrots
  address-family ipv4 unicast
   redistribute static
  !
 !
```
4. Validate vpnv4 prefix is received at xrd01 and that it has color 40:
#### xrd01
```
RP/0/RP0/CPU0:xrd01#sho bgp vpnv4 uni rd 10.0.0.7:0 40.0.0.0/24
Sat Jan  7 00:12:32.799 UTC
BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.7:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  33           33
Last Modified: Jan  7 00:11:46.204 for 00:00:46
Paths: (2 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 1, version 28
      Extended community: Color:40 RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
  Path #2: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 0, version 0
      Extended community: Color:40 RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.6
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
```
5. Configure SRv6-TE policies on xrd01
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
     index 30 sid fc00:0:7777::
    !
   !
  !
   segment-list xrd567
    srv6
     index 10 sid fc00:0:5555::
     index 20 sid fc00:0:6666::
     index 30 sid fc00:0:7777::
    !
   !
  ! 
  policy bulk-transfer
   srv6
    locator MAIN binding-sid dynamic behavior ub6-insert-reduced
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
    locator MAIN binding-sid dynamic behavior ub6-insert-reduced
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

#### BGP L3VPN validation output should look something like:
```     
RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
Fri Jan  6 22:39:38.429 UTC

*** Locator: 'MAIN' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e004::          uDT4              'carrots'                         bgp-65000           InUse  Y 
fc00:0:1111:e005::          uDT6              'carrots'                         bgp-65000           InUse  Y 
```
```
RP/0/RP0/CPU0:xrd01#sho bgp vpnv4 uni            
Fri Jan  6 22:40:22.354 UTC
BGP router identifier 10.0.0.1, local AS number 65000
BGP generic scan interval 60 secs
Non-stop routing is enabled
BGP table state: Active
Table ID: 0x0
BGP main routing table version 10
BGP NSR Initial initsync version 1 (Reached)
BGP NSR/ISSU Sync-Group versions 0/0
BGP scan interval 60 secs

Status codes: s suppressed, d damped, h history, * valid, > best
              i - internal, r RIB-failure, S stale, N Nexthop-discard
Origin codes: i - IGP, e - EGP, ? - incomplete
   Network            Next Hop            Metric LocPrf Weight Path
Route Distinguisher: 10.0.0.1:0 (default for vrf carrots)
Route Distinguisher Version: 10
*> 10.9.1.0/24        0.0.0.0                  0         32768 ?
*>i10.9.6.0/24        fc00:0:6666::1           0    100      0 ?
*>i10.9.7.0/24        fc00:0:7777::1           0    100      0 ?
Route Distinguisher: 10.0.0.6:0
Route Distinguisher Version: 5
*>i10.9.6.0/24        fc00:0:6666::1           0    100      0 ?
Route Distinguisher: 10.0.0.7:0
Route Distinguisher Version: 9
*>i10.9.7.0/24        fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?

Processed 5 prefixes, 6 paths
```
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.7:0 10.9.7.0/24
Fri Jan  6 22:41:30.888 UTC
BGP routing table entry for 10.9.7.0/24, Route Distinguisher: 10.0.0.7:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                   9            9
Last Modified: Jan  6 22:38:54.204 for 00:02:36
Paths: (2 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 1, version 9
      Extended community: RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
  Path #2: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 0, version 0
      Extended community: RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.6
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
RP/0/RP0/CPU0:xrd01#
```
```
RP/0/RP0/CPU0:xrd01#sho bgp vpnv6 uni
Fri Jan  6 22:51:11.395 UTC
BGP router identifier 10.0.0.1, local AS number 65000
BGP generic scan interval 60 secs
Non-stop routing is enabled
BGP table state: Active
Table ID: 0x0
BGP main routing table version 12
BGP NSR Initial initsync version 1 (Reached)
BGP NSR/ISSU Sync-Group versions 0/0
BGP scan interval 60 secs

Status codes: s suppressed, d damped, h history, * valid, > best
              i - internal, r RIB-failure, S stale, N Nexthop-discard
Origin codes: i - IGP, e - EGP, ? - incomplete
   Network            Next Hop            Metric LocPrf Weight Path
Route Distinguisher: 10.0.0.1:0 (default for vrf carrots)
Route Distinguisher Version: 12
*> 10:9:1::/64        ::                       0         32768 ?
*>i10:9:6::/64        fc00:0:6666::1           0    100      0 ?
*>i10:9:7::/64        fc00:0:7777::1           0    100      0 ?
Route Distinguisher: 10.0.0.6:0
Route Distinguisher Version: 7
*>i10:9:6::/64        fc00:0:6666::1           0    100      0 ?
Route Distinguisher: 10.0.0.7:0
Route Distinguisher Version: 11
*>i10:9:7::/64        fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?

Processed 5 prefixes, 6 paths
```
```
RP/0/RP0/CPU0:xrd01#ping vrf carrots 10.9.7.1
Fri Jan  6 22:42:18.318 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.9.7.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/5 ms
RP/0/RP0/CPU0:xrd01#
```
```
RP/0/RP0/CPU0:xrd01#ping vrf carrots 10:9:7::1           
Fri Jan  6 22:51:54.571 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10:9:7::1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/4 ms
```
Todo: 
1. Configure and test XRd SRv6-TE (hopefully it works on 7.8.1)
2. Writeup lab_3 guide