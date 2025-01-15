## Contents
- [Contents](#contents)
- [xrd01](#xrd01)
- [xrd02](#xrd02)
- [xrd03](#xrd03)
- [xrd04](#xrd04)
- [xrd05](#xrd05)
- [xrd06](#xrd06)
- [xrd07](#xrd07)
- [Back to Lab 2 Guide](#back-to-lab-2-guide)

## xrd01
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!  
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:1111::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:1111::/48
   !
  !
 !
 commit
 
 ```

## xrd02
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:2222::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:2222::/48
   !
  !
 !
 commit

```

## xrd03
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:3333::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:3333::/48
   !
  !
 !
 commit

```

## xrd04
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:4444::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:4444::/48
   !
  !
 !
 commit

```

## xrd05
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:5555::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:5555::/48
   !
  !
 !
 commit

```

## xrd06
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:6666::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:6666::/48
   !
  !
 !
 commit

```

## xrd07
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:7777::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:7777::/48
   !
  !
 !
 commit

 ```

 ## Back to Lab 2 Guide
[Lab 2 Guide](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_2/lab_2-guide.md#validate-srv6-configuration-and-reachability)