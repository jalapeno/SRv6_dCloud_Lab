### xrd01 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 1 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:1111::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:1111::/48
   !
  !
 !
 ```

### xrd02 config

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
  passive
  address-family ipv4 unicast
   prefix-sid index 2 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:2222::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:2222::/48
   !
  !
 !
```
 ### xrd03 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 3 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:3333::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:3333::/48
   !
  !
 !
```
 ### xrd04 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 4 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:4444::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:4444::/48
   !
  !
 !
```
 ### xrd05 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 5 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:5555::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:5555::/48
   !
  !
 !
```
 ### xrd06 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 6
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:6666::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:6666::/48
   !
  !
 !
```
 ### xrd07 config
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
  passive
  address-family ipv4 unicast
   prefix-sid index 7 
   !
  !
 !
!
segment-routing
 global-block 100000 163999
 srv6
  encapsulation
   source-address fc00:0000:7777::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0000:7777::/48
   !
  !
 !
 ```