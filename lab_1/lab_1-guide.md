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
   source-address fc00:0:01::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:01::/48
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
   source-address fc00:0:02::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:02::/48
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
   source-address fc00:0:03::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:03::/48
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
   source-address fc00:0:04::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:04::/48
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
   source-address fc00:0:05::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:05::/48
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
   source-address fc00:0:06::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:06::/48
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
   source-address fc00:0:07::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:07::/48
   !
  !
 !
!
```