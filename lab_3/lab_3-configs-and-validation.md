## Lab 3 - SRv6 Traffic Engineering for IOS-XR

Todo: 
1. Configure and test XRd SRv6-TE (hopefully it works on 7.8.1)
2. Add SRv6-TE configs to configs in lab_3/config/ folder  
3. Writeup lab_3 guide

xrd01
```
interface Loopback20
 ipv4 address 20.0.0.1 255.255.255.255
!
interface Loopback30
 ipv4 address 30.0.0.1 255.255.255.255
!

ipv4 access-list low-latency
 10 permit ipv4 any 30.0.0.0/24 log
!
ipv4 access-list bulk-transfer
 10 permit ipv4 any 20.0.0.0/24 log
!
class-map match-any low-latency
 match access-group ipv4 low-latency 
 end-class-map
! 
class-map match-any bulk-transfer
 match access-group ipv4 bulk-transfer 
 end-class-map
!
policy-map pf-srte
 class low-latency
  set forward-class 1
 ! 
 class bulk-transfer
  set forward-class 2
 ! 
 class class-default
 ! 
 end-policy-map
! 

segment-routing
 traffic-eng
  segment-lists
   srv6
    sid-format usid-f3216
   !
   segment-list xrd01-05-06-07
    srv6
     index 10 sid fc00:0000:5555::
     index 20 sid fc00:0000:6666::
     index 30 sid fc00:0000:7777::
    !
   !
  !
  policy xrd567
   srv6
    locator MAIN binding-sid dynamic behavior ub6-insert-reduced
   !
   color 10 end-point ipv6 fc00:0000:7777::1
   candidate-paths
    preference 100
     explicit segment-list xrd01-05-06-07
     !
    !
   !
  !
 !

 ```

 xrd07
 ```
 interface Loopback20
 ipv4 address 20.0.0.7 255.255.255.255
!
interface Loopback30
 ipv4 address 30.0.0.7 255.255.255.255
!
router isis 100
 interface Loopback20
  passive
  address-family ipv4 unicast
  !
  address-family ipv6 unicast
  !
 !
 interface Loopback30
  passive
  address-family ipv4 unicast
  !
  address-family ipv6 unicast
  !
 !
 ```