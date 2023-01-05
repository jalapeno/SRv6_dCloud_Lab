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

fc00:0:1::                  uN (PSP/USD)      'default':1                       sidmgr              InUse  Y 
fc00:0:1:e000::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1:e001::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1:e002::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1:e003::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 

Todo: 
1. Configure and test XRd SRv6-TE (hopefully it works on 7.8.1)
2. Add SRv6-TE configs to configs in lab_3/config/ folder  
3. Writeup lab_3 guide