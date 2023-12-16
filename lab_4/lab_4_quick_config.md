## Contents
- [Contents](#contents)
- [xrd05](#xrd05)
- [xrd06](#xrd06)


## xrd05
```
conf t

router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:1111::1
  bmp-activate server 1
 !
 neighbor fc00:0:7777::1
  bmp-activate server 1
 !
!
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
commit

```

## xrd06
```
conf t

router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:1111::1
  bmp-activate server 1
 !
 neighbor fc00:0:7777::1
  bmp-activate server 1
 !
!
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
commit

```