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
   source-address fc00:0:1::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:1::/48
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
   source-address fc00:0:2::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:2::/48
   !
  !
 !

 ### xrd03 config

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
   source-address fc00:0:3::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:3::/48
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
   source-address fc00:0:4::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:4::/48
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
   source-address fc00:0:5::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:5::/48
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
   source-address fc00:0:6::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:6::/48
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
   source-address fc00:0:7::1
  !
  locators
   locator MAIN
    micro-segment behavior unode psp-usd
    prefix fc00:0:7::/48
   !
  !
 !
```
### Validate SR and SRv6 config
#### Segment Routing 
```
RP/0/RP0/CPU0:xrd07#show isis segment-routing label table                
Wed Dec 21 20:09:51.478 UTC

IS-IS 100 IS Label Table
Label         Prefix                   Interface
----------    ----------------         ---------
100001        10.0.0.1/32              
100002        10.0.0.2/32              
100003        10.0.0.3/32              
100004        10.0.0.4/32              
100005        10.0.0.5/32              
100006        10.0.0.6/32              
100007        10.0.0.7/32              Loopback0
RP/0/RP0/CPU0:xrd07#

RP/0/RP0/CPU0:xrd07#show mpls forwarding 
Wed Dec 21 20:05:16.531 UTC
Local  Outgoing    Prefix             Outgoing     Next Hop        Bytes       
Label  Label       or ID              Interface                    Switched    
------ ----------- ------------------ ------------ --------------- ------------
24002  Pop         10.101.1.0/24                   10.0.0.1        0           
24003  Unlabelled  10.1.1.4/31        Gi0/0/0/1    10.1.1.6        0           
       100005      10.1.1.4/31        Gi0/0/0/2    10.1.1.16       0            (!)
24004  Unlabelled  10.1.1.10/31       Gi0/0/0/2    10.1.1.16       0           
       100005      10.1.1.10/31       Gi0/0/0/1    10.1.1.6        0            (!)
24005  Pop         SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0            (!)
24006  Pop         SR Adj (idx 3)     Gi0/0/0/1    10.1.1.6        0           
24007  Pop         SR Adj (idx 1)     Gi0/0/0/2    10.1.1.16       0           
       100005      SR Adj (idx 1)     Gi0/0/0/1    10.1.1.6        0            (!)
24008  Pop         SR Adj (idx 3)     Gi0/0/0/2    10.1.1.16       0           
100001 100001      SR Pfx (idx 1)     Gi0/0/0/1    10.1.1.6        0           
       100001      SR Pfx (idx 1)     Gi0/0/0/2    10.1.1.16       0           
100002 100002      SR Pfx (idx 2)     Gi0/0/0/2    10.1.1.16       0           
       100002      SR Pfx (idx 2)     Gi0/0/0/1    10.1.1.6        0            (!)
100003 100003      SR Pfx (idx 3)     Gi0/0/0/1    10.1.1.6        0           
       100003      SR Pfx (idx 3)     Gi0/0/0/2    10.1.1.16       0            (!)
100004 Pop         SR Pfx (idx 4)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Pfx (idx 4)     Gi0/0/0/2    10.1.1.16       0            (!)
100005 100005      SR Pfx (idx 5)     Gi0/0/0/1    10.1.1.6        0           
       100005      SR Pfx (idx 5)     Gi0/0/0/2    10.1.1.16       1119        
100006 Pop         SR Pfx (idx 6)     Gi0/0/0/2    10.1.1.16       939         
       100005      SR Pfx (idx 6)     Gi0/0/0/1    10.1.1.6        0            (!)
100007 Aggregate   SR Pfx (idx 7)     default                      0           
RP/0/RP0/CPU0:xrd07#
```
#### SRv6 validation:
```
RP/0/RP0/CPU0:xrd07#show segment-routing srv6 locator 
Wed Dec 21 20:06:39.503 UTC
Name                  ID       Algo  Prefix                    Status   Flags   
--------------------  -------  ----  ------------------------  -------  --------
MAIN                  1        0     fc00:0:7::/48             Up       U       
RP/0/RP0/CPU0:xrd07#

RP/0/RP0/CPU0:xrd07#show segment-routing srv6 sid 
Wed Dec 21 20:07:36.226 UTC

*** Locator: 'MAIN' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:7::                  uN (PSP/USD)      'default':7                       sidmgr              InUse  Y 
fc00:0:7:e000::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:7:e001::             uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:7:e002::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:7:e003::             uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
RP/0/RP0/CPU0:xrd07#
```

