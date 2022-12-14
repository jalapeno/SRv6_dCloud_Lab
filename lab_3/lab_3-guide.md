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

RP/0/RP0/CPU0:xrd06#sho bgp bmp ser 1  
Wed Dec 14 23:24:01.861 UTC
BMP server 1
Host 198.18.128.101 Port 30511
Connected for 00:01:18
Last Disconnect event received : 00:01:24
Precedence:  internet
BGP neighbors: 4
VRF: - (0x60000000)
Update Source: 10.254.254.106 (Mg0/RP0/CPU0/0)
Update Source Vrf ID: 0x60000000

Queue write pulse sent            : Dec 14 23:23:14.170, Dec 14 23:23:05.478 (all)
Queue write pulse received        : Dec 14 23:23:14.170
Update Mode : Route Monitoring Pre-Policy

TCP: 
  Last message sent: Dec 14 23:23:14.170, Status: No Pending Data
  Last write pulse received: Dec 14 23:23:14.172, Waiting: FALSE

Message Stats:
Total msgs dropped   : 0
Total msgs pending   : 0, Max: 3 at Dec 14 23:22:37.260
Total messages sent  : 16
Total bytes sent     : 2790, Time spent: 0.000 secs
           INITIATION: 2
          TERMINATION: 0
         STATS-REPORT: 2
    PER-PEER messages: 12

ROUTE-MON messages   : 8

  Neighbor fc00:0:7::1
Messages pending: 0
Messages dropped: 0
Messages sent   : 6
      PEER-UP   : 2
    PEER-DOWN   : 0
```

Connect to Jalapeno's Arango GraphDB
```
http://198.18.1.101:30852/

user: root
password: jalapeno
DB: jalapeno

```
