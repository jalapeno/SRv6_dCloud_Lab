

### xrd01
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator ISIS
  network 10.101.1.0/24
  network 10.101.2.0/24
  allocate-label all
 neighbor-group xrd-ipv4-peer
  address-family ipv4 labeled-unicast
   next-hop-self
```
### xrd05
```
router bgp 65000
 neighbor-group xrd-ipv4-peer
  address-family ipv4 labeled-unicast
   route-reflector-client
```
### xrd06
```
router bgp 65000
 neighbor-group xrd-ipv4-peer
  address-family ipv4 labeled-unicast
   route-reflector-client
```
### xrd07
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator ISIS
  network 10.107.1.0/24
  network 20.0.0.0/24
  network 30.0.0.0/24
  allocate-label all
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 labeled-unicast
   next-hop-self
```
