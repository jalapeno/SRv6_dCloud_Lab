### configure SR, SRv6, and SRv6-L3VPN for BGP

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