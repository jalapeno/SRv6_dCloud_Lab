### configure BGP Monitoring Protocol (BMP)

R05
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
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

R06
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
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

Validate changes:
```
ping 198.18.128.101
show bgp bmp server 1
```

Expected output:
```
RP/0/RP0/CPU0:xrd06#ping 198.18.128.101
Wed Dec 14 23:00:18.649 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.18.128.101, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/7 ms