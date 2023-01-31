## Contents
- [Contents](#contents)
- [xrd01](#xrd01)
- [xrd05](#xrd05)
- [xrd06](#xrd06)
- [xrd07](#xrd07)

## xrd01
```
conf t

vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
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
interface GigabitEthernet0/0/0/3
 vrf carrots
 ipv4 address 10.101.3.2 255.255.255.0
 ipv6 address fc00:0:101:3::2/64
 no shutdown
!
router bgp 65000
 neighbor-group xrd-ipv6-peer
  address-family vpnv4 unicast
   next-hop-self
  !
  address-family vpnv6 unicast
   next-hop-self
  !
 !
!
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator MyLocator
    alloc mode per-vrf
   !
   redistribute connected
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator MyLocator
    alloc mode per-vrf
   !
   redistribute connected
  !
 !
!
commit

```

## xrd05
```
conf t

router bgp 65000
 neighbor-group xrd-ipv6-peer
  address-family vpnv4 unicast
   route-reflector-client
  !
  address-family vpnv6 unicast
   route-reflector-client
  !
 !
!
commit

```

## xrd06
```
conf t

router bgp 65000
 neighbor-group xrd-ipv6-peer
  address-family vpnv4 unicast
   route-reflector-client
  !
  address-family vpnv6 unicast
   route-reflector-client
  !
 !
!
commit

```

## xrd07
```
conf t

vrf carrots
 address-family ipv4 unicast
  import route-target
   9:9
  !
  export route-target
   9:9
  !
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
interface GigabitEthernet0/0/0/3
 vrf carrots
 ipv4 address 10.107.2.2 255.255.255.0
 ipv6 address fc00:0:107:2::2/64
 no shutdown
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
  !
 !
!
router bgp 65000
 neighbor-group xrd-ipv6-peer
  address-family vpnv4 unicast
   next-hop-self
  !
  address-family vpnv6 unicast
   next-hop-self
  !
 !
!
router bgp 65000
 vrf carrots
  rd auto
  address-family ipv4 unicast
   segment-routing srv6
    locator MyLocator
    alloc mode per-vrf
   !
   redistribute connected
   redistribute static
  !
  address-family ipv6 unicast
   segment-routing srv6
    locator MyLocator
    alloc mode per-vrf
   !
   redistribute connected
   redistribute static
  !
 !
!
commit

```