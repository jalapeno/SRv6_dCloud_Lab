1. SRv6 SID validation (note the SIDs attached to the VRF):

```
RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
Sat Jan  7 21:03:02.074 UTC

*** Locator: 'MyLocator' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e004::          uDT4              'default'                         bgp-65000           InUse  Y 
fc00:0:1111:e005::          uDT6              'default'                         bgp-65000           InUse  Y 
fc00:0:1111:e006::          uDT4              'carrots'                         bgp-65000           InUse  Y 
fc00:0:1111:e007::          uDT6              'carrots'                         bgp-65000           InUse  Y 
```

2. Display BGP vpnv4 address-family info:
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast
Wed Jan 31 21:30:56.690 UTC
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
Route Distinguisher Version: 9
*> 10.101.3.0/24      0.0.0.0                  0         32768 ?
*>i10.107.2.0/24      fc00:0:7777::1           0    100      0 ?
*>i40.0.0.0/24        fc00:0:7777::1           0    100      0 ?
*>i50.0.0.0/24        fc00:0:7777::1           0    100      0 ?
Route Distinguisher: 10.0.0.7:0
Route Distinguisher Version: 12
*>i10.107.2.0/24      fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
*>i40.0.0.0/24        fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
*>i50.0.0.0/24        fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
```

3. Display data on a specific SRv6 L3VPN ipv4 prefix:
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.7:0 10.9.7.0/24
Sat Jan  7 21:05:55.230 UTC
BGP routing table entry for 10.9.7.0/24, Route Distinguisher: 10.0.0.7:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  24           24
Last Modified: Jan  7 00:10:32.204 for 20:55:23
Paths: (2 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0040
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 1, version 24
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
```

4. Display BGP vpnv6 address-family info:
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv6 unicast
Wed Jan 31 22:03:53.334 UTC
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
Route Distinguisher Version: 9
*>ifc00:0:40::/64     fc00:0:7777::1           0    100      0 ?
*>ifc00:0:50::/64     fc00:0:7777::1           0    100      0 ?
*> fc00:0:101:3::/64  ::                       0         32768 ?
*>ifc00:0:107:2::/64  fc00:0:7777::1           0    100      0 ?
Route Distinguisher: 10.0.0.7:0
Route Distinguisher Version: 12
*>ifc00:0:40::/64     fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
*>ifc00:0:50::/64     fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
*>ifc00:0:107:2::/64  fc00:0:7777::1           0    100      0 ?
* i                   fc00:0:7777::1           0    100      0 ?
          
Processed 7 prefixes, 10 paths
```
5. Display data on a specific SRv6 L3VPN ipv6 prefix:
```
RP/0/RP0/CPU0:xrd01#show bgp vpnv6 unicast rd 10.0.0.7:0 fc00:0:40::/64 
Sat Jan  7 21:07:47.124 UTC
BGP routing table entry for fc00:0:40::/64, Route Distinguisher: 10.0.0.7:0
Versions:
  Process           bRIB/RIB  SendTblVer
  Speaker                  25           25
Last Modified: Jan  7 21:00:03.204 for 00:07:44
Paths: (2 available, best #1)
  Not advertised to any peer
  Path #1: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
      Received Label 0xe0050
      Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 1, version 23
      Extended community: RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.5
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:62, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
  Path #2: Received by speaker 0
  Not advertised to any peer
  Local
    fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
      Received Label 0xe0050
      Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
      Received Path ID 0, Local Path ID 0, version 0
      Extended community: RT:9:9 
      Originator: 10.0.0.7, Cluster list: 10.0.0.6
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
        T:1(Sid information), Sid:fc00:0:7777::, Behavior:62, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
```
6. Pings from xrd01:
```
Success rate is 100 percent (5/5), round-trip min/avg/max = 2/2/3 ms
RP/0/RP0/CPU0:xrd01#ping vrf carrots 40.0.0.1
Sat Jan  7 21:09:05.650 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 40.0.0.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/4 ms
RP/0/RP0/CPU0:xrd01#ping vrf carrots 50.0.0.1
Sat Jan  7 21:09:11.047 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 50.0.0.1 timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/5 ms
RP/0/RP0/CPU0:xrd01#ping vrf carrots fc00:0:40::1
Sat Jan  7 21:09:15.889 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to fc00:0:40::1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/4 ms
RP/0/RP0/CPU0:xrd01#ping vrf carrots fc00:0:50::1
Sat Jan  7 21:09:21.763 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to fc00:0:50::1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/3/5 ms
```

[back to lab 3 guide](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_3/lab_3-guide.md#validate-srv6-l3vpn)
 



