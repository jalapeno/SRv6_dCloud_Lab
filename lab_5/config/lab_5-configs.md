#### xrd05 and xrd06
```
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor fc00:0000:1111::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0000:7777::1
  bmp-activate server 1
  !
 !
!
```
#### xrd01 and xrd07
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator MyLocator
  !
 !
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
```