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

R05 ISIS
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

R06 ISIS
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

R07 ISIS
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