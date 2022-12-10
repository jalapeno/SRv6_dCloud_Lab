### configure SR, SRv6 for ISIS

R01 
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 1
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:1::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:1::/48
   !
  !
 !
!

```

R02
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 2
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:2::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:2::/48
   !
  !
 !
!

```

R03
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 3
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:3::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:3::/48
   !
  !
 !
!
```

R04
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 4
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:4::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:4::/48
   !
  !
 !
!
```

R05 
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 5
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:5::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:5::/48
   !
  !
 !
!
```

R06
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 6
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:6::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:6::/48
   !
  !
 !
!
```

R07
```
router isis 100 
 address-family ipv4 unicast 
  segment-routing mpls 
 ! 
 address-family ipv6 unicast 
  segment-routing srv6 
   locator MAIN 
  !
 !
!
interface Loopback0
 address-family ipv4 unicast
  prefix-sid index 7
 !       
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0:7::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:7::/48
   !
  !
 !
!
```

Validate changes:
```

show mpls forwarding
show segment-routing srv6 sid
```

Expected output:
```
RP/0/RP0/CPU0:xrd07#sho segment-routing srv6 sid
Sat Dec 10 18:07:04.723 UTC

*** Locator: 'MAIN' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:7::                  uN (PSP/USD)      'default':7                       sidmgr              InUse  Y 
fc00:0:7:e000::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:7:e001::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:7:e002::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:7:e003::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
RP/0/RP0/CPU0:xrd07#
RP/0/RP0/CPU0:xrd07#
RP/0/RP0/CPU0:xrd07#sho mpls for
Sat Dec 10 18:07:07.515 UTC
Local  Outgoing    Prefix             Outgoing     Next Hop        Bytes       
Label  Label       or ID              Interface                    Switched    
------ ----------- ------------------ ------------ --------------- ------------
24003  Unlabelled  10.1.1.4/31        Gi0/0/0/1    10.1.1.6        0           
       100005      10.1.1.4/31        Gi0/0/0/2    10.1.1.16       0            (!)
24004  Unlabelled  10.1.1.10/31       Gi0/0/0/2    10.1.1.16       0           
       100005      10.1.1.10/31       Gi0/0/0/1    10.1.1.6        0            (!)
24005  Pop         SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0            (!)
24006  Pop         SR Adj (idx 3)     Gi0/0/0/1    10.1.1.6        0           
24007  Pop         SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0           
       100005      SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0            (!)
24008  Pop         SR Adj (idx 3)     Gi0/0/0/2    10.1.1.16       0           
100001 100001      SR Pfx (idx 1)     Gi0/0/0/1    10.1.1.6        0           
       100001      SR Pfx (idx 1)     Gi0/0/0/2    10.1.1.16       0           
100002 100002      SR Pfx (idx 2)     Gi0/0/0/2    10.1.1.16       0           
       100002      SR Pfx (idx 2)     Gi0/0/0/1    10.1.1.6        0            (!)
100003 100003      SR Pfx (idx 3)     Gi0/0/0/1    10.1.1.6        0           
       100003      SR Pfx (idx 3)     Gi0/0/0/2    10.1.1.16       0            (!)
100004 Pop         SR Pfx (idx 4)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Pfx (idx 4)     Gi0/0/0/2    10.1.1.16       0            (!)
100005 100005      SR Pfx (idx 5)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Pfx (idx 5)     Gi0/0/0/2    10.1.1.16       836         
100006 Pop         SR Pfx (idx 6)     Gi0/0/0/2    10.1.1.16       880         
       100005      SR Pfx (idx 6)     Gi0/0/0/1    10.1.1.6        0            (!)
RP/0/RP0/CPU0:xrd07#
```