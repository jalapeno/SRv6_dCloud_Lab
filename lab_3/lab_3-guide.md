# Lab 3: Configure SRv6 L3VPN and SRv6-TE [30 Min]

### Description
In Lab 3 we will establish a Layer-3 VPN named *`carrots`* which will use SRv6 transport and will have endpoints on **xrd01** and **xrd07**. We will also preconfigure VRF *`radish`* on **xrd07**, which we'll make use of in Lab 4. In order to extend L3VPN *`carrots`* to the Amsterdam and Rome VM we will be adding VRF *`carrots`* to interfaces on **xrd01** and **xrd07** that connect to seconrday NICs on the Amsterdam and Rome. Once the L3VPN is established and you run test traffic between Amsterdam and Rome we will then setup SRv6-TE traffic steering from Amsterdam to specific Rome prefixes.

## Contents
- [Lab 3: Configure SRv6 L3VPN and SRv6-TE \[30 Min\]](#lab-3-configure-srv6-l3vpn-and-srv6-te-30-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Configure SRv6 L3VPN](#configure-srv6-l3vpn)
    - [Configure VRF](#configure-vrf)
    - [Add VRF to router interfaces for L3VPN](#add-vrf-to-router-interfaces-for-l3vpn)
    - [Configure BGP L3VPN Peering](#configure-bgp-l3vpn-peering)
  - [Validate SRv6 L3VPN](#validate-srv6-l3vpn)
  - [Configure SRv6-TE steering for L3VPN](#configure-srv6-te-steering-for-l3vpn)
    - [Create SRv6-TE steering policy](#create-srv6-te-steering-policy)
    - [Validate SRv6-TE steering of L3VPN traffic](#validate-srv6-te-steering-of-l3vpn-traffic)
    - [Validate bulk traffic takes the non-shortest path: **xrd01 -\> 02 -\> 03 -\> 04 -\> 07**](#validate-bulk-traffic-takes-the-non-shortest-path-xrd01---02---03---04---07)
      - [Validate low latency traffic takes the path: xrd01 -\> 05 -\> 06 -\> 07](#validate-low-latency-traffic-takes-the-path-xrd01---05---06---07)
    - [End of Lab 3](#end-of-lab-3)

## Lab Objectives
The student upon completion of Lab 3 should have achieved the following objectives:

* Understanding of SRv6 L3VPN
* Configuration of SRv6 L3VPN in XR
* Configuration of SRv6 TE policy
* Demonstartion of SRv6 TE traffic steering

## Configure SRv6 L3VPN
The SRv6-based IPv4/IPv6 L3VPN featureset enables operation of IPv4/IPv6 L3VPN over a SRv6 data plane. Traditionally L3VPN has been operated over MPLS or SR-MPLS based systems. SRv6 L3VPN uses the locator/function aspect of SRv6 Segment IDs (SIDs) instead of PE + VPN labels. 

Example: 

|     Locator    | Function |                                         
|:---------------|:--------:|
| fc00:0000:7777:|   e004:: |


SRv6 L3VPN functionality interconnects multiple sites to resemble a private network service over public or multi-tenant infrastructure. The basic SRv6 configuration was completed in [Lab 2](/lab_2/lab_2-guide.md).

In this lab a BGP SID will be allocated in per-VRF mode and provides End.DT4 or End.DT6 functionality. End.DT4/6 represents the Endpoint with decapsulation and IPv4 or v6 lookup in a specific VRF table.

For more details on SRv6 network programming Endpoint Behavior functionality please see RFC 8986 [LINK](https://datatracker.ietf.org/doc/html/rfc8986#name-enddt6-decapsulation-and-sp)

BGP encodes the SRv6 SID in the prefix-SID attribute of the IPv4/6 L3VPN Network Layer Reachability Information (NLRI) and advertises it to IPv6 peering over an SRv6 network. The Ingress PE (provider edge) router encapsulates the VRF IPv4/6 traffic with the SRv6 VPN SID and sends it over the SRv6 network.


  ### Configure VRF
  Time to configure our VRFs for IPv4 and IPv6 VPN. The *carrots* VRF will be setup on the two edge routers in our SP network: **xrd01** and **xrd07**. Intermediate routers do not need to be VRF aware and are instead forwarding on the SRv6 data plane. (technically the intermediate routers don't need to be SRv6 aware and could simply perform IPv6 forwarding based on the outer IPv6 header). The *radish* VRF will be setup on **xrd07** and will be used in Lab 4.

  Configure the VRF on **xrd01** and **xrd07**:

> [!NOTE]
> the below commands are also available in the *`quick config doc`* [HERE](/lab_3/lab_3_quick_config.md)  


  On both **xrd01** and **xrd07**:
  ```yaml
  conf t
  vrf carrots
    address-family ipv4 unicast
      import route-target
      9:9
      export route-target
      9:9
    
    address-family ipv6 unicast
      import route-target
      9:9
      export route-target
      9:9

    commit
  ```

  Only on **xrd07**:
  ```yaml
  conf t
  vrf radish
    address-family ipv4 unicast
      import route-target
      10:10
      export route-target
      10:10
    address-family ipv6 unicast
      import route-target
      10:10
      export route-target
      10:10
    commit
  ```

### Add VRF to router interfaces for L3VPN
  Now that our VRF *carrots* has been created lets get the VRF added to the applicable interfaces. For **xrd01** we will use  interface *GigabitEthernet0/0/0/3* which connects to Amsterdam over link *M*. For **xrd07** we will use interface *GigabitEthernet0/0/0/3* which connects to Rome over link *K*.

![L3VPN VRF Carrots](/topo_drawings/l3vpn-vrf-carrots.png)

 1. Add VRF to interfaces

    **xrd01**
    ```yaml
    conf t
    
    interface GigabitEthernet0/0/0/3
      vrf carrots
      ipv4 address 10.101.3.2 255.255.255.0
      ipv6 address fc00:0:101:3::2/64
      no shutdown
    commit
    ```

    **xrd07**  
    ```yaml
    conf t
    
    interface GigabitEthernet0/0/0/3
      vrf carrots
      ipv4 address 10.107.2.2 255.255.255.0
      ipv6 address fc00:0:107:2::2/64
      no shutdown
    interface Loopback100
      vrf radish
      ipv4 address 100.0.7.1 255.255.255.0
      ipv6 address 2001:db8:100:7::1/64
    commit
    ```


 2. Add VRF static routes  
     In addition to configuring *GigabitEthernet0/0/0/3* to be a member of VRF carrots, **xrd07** will need a pair of static routes for reachability to **Rome's** "40" and "50" network prefixes. Later we'll create SRv6-TE steering policies for traffic to the "40" and "50" prefixes:  

    **xrd07**
    ```yaml
    conf t
    
    router static
      vrf carrots
        address-family ipv4 unicast
          40.0.0.0/24 10.107.2.1
          50.0.0.0/24 10.107.2.1
        address-family ipv6 unicast
          fc00:0:40::/64 fc00:0:107:2::1
          fc00:0:50::/64 fc00:0:107:2::1
        commit
    ```

3. Verify **Rome** VRF prefix reachability  
    Ping check from xrd07 gi 0/0/0/3 to Rome VM via 2nd NIC:  
    ```
    ping vrf carrots 10.107.2.1
    ping vrf carrots 40.0.0.1
    ping vrf carrots 50.0.0.1
    ping vrf carrots fc00:0:107:2::1
    ping vrf carrots fc00:0:40::1
    ping vrf carrots fc00:0:50::1
    ```

4. Verify **Amsterdam** VRF prefix reachability  
    Ping check from **xrd01** gi 0/0/0/3 to **Amsterdam** VM via 2nd NIC:  
    ```
    ping vrf carrots 10.101.3.1
    ping vrf carrots fc00:0:101:3::1
    ```

### Configure BGP L3VPN Peering
1. Enable BGP L3VPN
    The next step is to add the L3VPN configuration into BGP. The *carrots* L3VPN is dual-stack so we will be adding both vpnv4 and vpnv6 address-families to the BGP neighbor-group for ipv6 peers. For example you will enable L3VPN in the neighbor-group template by issuing the *address-family vpnv4/6 unicast* command.

    **xrd01** and **xrd07**
    ```yaml
    conf t
    router bgp 65000
      neighbor-group xrd-ipv6-peer
        address-family vpnv4 unicast
        next-hop-self

        address-family vpnv6 unicast
        next-hop-self
      commit
    ```

2. Enable SRv6 for VRF carrots and redistribute connected/static
    Next we add VRF *carrots* into BGP and enable SRv6 to the ipv4 and ipv6 address family with the command *`segment-routing srv6`*. In addition we will tie the VRF to the SRv6 locator *`MyLocator`* configured in an earlier lab.

   Last on **xrd01** we will redistribute connected routes using the command *`redistribute connected`*. This will trigger the two interfaces ipv4 and ipv6 networks facing the Amsterdam VM to advertise in VRF *carrots*.

   On **xrd07** we will need to redistribute both the connected and static routes to provide reachability to Rome and its additional prefixes. For **xrd07** we will add *`redistribute connected`* to VRF *radish* and both *`redistribute connected`* and *`redistribute static`* for VRF *carrots*.

    **xrd01**  
    ```yaml
    conf t
    router bgp 65000
      vrf carrots
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
      
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
        commit
    ```

    **xrd07**  
    ```yaml
    conf t
    router bgp 65000
      vrf carrots
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected
      
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected

      vrf radish
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
      commit
      ```

3. The BGP route reflectors will also need to have L3VPN capability added to their peering group.

   BGP Route Reflectors **xrd05**, **xrd06**  
    ```yaml
    conf t
    router bgp 65000
    neighbor-group xrd-ipv6-peer
      address-family vpnv4 unicast
      route-reflector-client
      
      address-family vpnv6 unicast
      route-reflector-client
    commit
    ```

## Validate SRv6 L3VPN

Validation command output examples can be found at this [LINK](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_3/validation-cmd-output.md)

> [!NOTE]
> **xrd01** and **xrd07** are configured to use dynamic RD allocation, so the L3VPN RD+prefix combination shown in the lab guide may differ from the one you see in your environment. For example, **xrd07** might advertise the 40.0.0.0/24 prefix with rd 10.0.0.7:0 or it might be rd 10.0.0.7:1
> 
1. From **xrd01** run the following set of validation commands (for the sake of time you can paste them in as a group, or spot check some subset of commands):
   ```
   show segment-routing srv6 sid
   show bgp vpnv4 unicast
   show bgp vpnv4 unicast rd 10.0.0.7:1 40.0.0.0/24
   show bgp vpnv6 unicast
   show bgp vpnv6 unicast rd 10.0.0.7:1 fc00:0:40::/64 
   ping vrf carrots 40.0.0.1
   ping vrf carrots 50.0.0.1
   ping vrf carrots fc00:0:40::1
   ping vrf carrots fc00:0:50::1
   ```
   
   Example validation for vpnv4 route
   ```yaml
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.7:1 40.0.0.0/24   
   Tue Jan 31 23:36:41.390 UTC
   BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.7:1   <--- WE HAVE A ROUTE. YAH
   Versions:
     Process           bRIB/RIB  SendTblVer
     Speaker                  11           11
     Last Modified: Jan 31 23:34:44.948 for 00:01:56
     Paths: (2 available, best #1)
       Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)   <--------- SOURCE xrd07
         Received Label 0xe0040
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
         Received Path ID 0, Local Path ID 1, version 5
         Extended community: RT:9:9 
         Originator: 10.0.0.7, Cluster list: 10.0.0.5             <------- FROM RR xrd05
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
           SubSubTLV:
             T:1(Sid structure):
     Path #2: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
         Received Label 0xe0040
         Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
         Received Path ID 0, Local Path ID 0, version 0
         Extended community: RT:9:9 
         Originator: 10.0.0.7, Cluster list: 10.0.0.6             <------- FROM RR xrd06
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
           SubSubTLV:
             T:1(Sid structure):
   ```

## Configure SRv6-TE steering for L3VPN
**Rome's** L3VPN IPv4 and IPv6 prefixes are associated with two classes of traffic:

* The **"40"** destinations (40.0.0.0/24 and fc00:0:40::/64) are bulk transport destinations (content replication or data backups) and thus are latency and loss tolerant. 
  
* The **"50"** destinations (50.0.0.0/24 and fc00:0:50::/64) are for real time traffic (live video, etc.) and thus require the lowest latency path available.

We will use the below diagram for reference:

![L3VPN Topology](/topo_drawings/l3vpn-slow-fast-path.png)

### Create SRv6-TE steering policy
For our SRv6-TE purposes we'll leverage the on-demand nexthop (ODN) feature set. Here is a nice example and explanation of ODN: [HERE](https://xrdocs.io/design/blogs/latest-converged-sdn-transport-ig)

In our lab we will configure **xrd07** as the egress PE router with the ODN method. This will trigger **xrd07** to advertise its L3VPN routes with color extended communities. We'll do this by first defining the *`extcomms`*, then setting up route-policies to match on destination prefixes and set the *`extcomm`* values.

The ingress PE, **xrd01**, will then be configured with SRv6 segment-lists and SRv6 ODN steering policies that match routes with the respective color and apply the appropriate SID stack on outbound traffic.

1. Prior to configuring SRV6-TE policy lets get a baseline look at our vpvn4 route as viewed from **xrd01**
   Run the following command:
   ```
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   ```

   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   Thu Jan 23 17:12:01.018 UTC
   BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
   Versions:
     Process           bRIB/RIB   SendTblVer
     Speaker                 63           63
   Last Modified: Jan 23 17:11:58.418 for 00:00:02
   Paths: (1 available, best #1)
     Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
         Received Label 0xe0060
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 63
   +     Extended community: RT:9:9
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
         PSID-Type:L3, SubTLV Count:1
          SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::(Transposed), Behavior:63, SS-TLV Count:1
               SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```
      
2. On **xrd07** advertise Rome's "40" and "50" prefixes with their respective color extended communities:
   **xrd07**
   ```yaml
   conf t
   extcommunity-set opaque bulk-transfer
     40
   end-set
 
   extcommunity-set opaque low-latency
     50
   end-set

   route-policy set-color
     if destination in (40.0.0.0/24) then
       set extcommunity color bulk-transfer
     endif
     if destination in (50.0.0.0/24) then
       set extcommunity color low-latency
     endif
     if destination in (fc00:0:40::/64) then
       set extcommunity color bulk-transfer
     endif
     if destination in (fc00:0:50::/64) then
       set extcommunity color low-latency
     endif
     pass
   end-policy

   router bgp 65000
   neighbor-group xrd-ipv6-peer
     address-family vpnv4 unicast
     route-policy set-color out
    
     address-family vpnv6 unicast
     route-policy set-color out
   commit
   ```

3. Validate vpnv4 and v6 prefixes are received at **xrd01** and that they have their color extcomms:
   **xrd01**
   ```
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24 
   show bgp vpnv4 uni vrf carrots 50.0.0.0/24
   show bgp vpnv6 uni vrf carrots fc00:0:40::/64
   show bgp vpnv6 uni vrf carrots fc00:0:50::/64
   ```
   - We now rerun the same command from step #1 and see that there is now an extended community *Color:40* tag
   ```
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   ```
   
   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   Thu Jan 23 17:16:49.248 UTC
   BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
   Versions:
     Process           bRIB/RIB   SendTblVer
     Speaker                 67           67
   Last Modified: Jan 23 17:16:39.418 for 00:00:09
   Paths: (1 available, best #1)
     Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
         Received Label 0xe0060
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 67
   +     Extended community: Color:40 RT:9:9
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
         PSID-Type:L3, SubTLV Count:1
          SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::(Transposed), Behavior:63, SS-TLV Count:1
            SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```

4. On **xrd01** configure a pair of SRv6-TE segment lists for steering traffic over these specific paths through the network: 
    - Segment list *xrd2347* will execute the explicit path: xrd01 -> 02 -> 03 -> 04 -> 07
    - Segment list *xrd567* will execute the explicit path: xrd01 -> 05 -> 06 -> 07

   **xrd01**
   ```yaml
   conf t
   segment-routing
    traffic-eng
     segment-lists
      srv6
       sid-format usid-f3216
      
      segment-list xrd2347
       srv6
        index 10 sid fc00:0:2222::
        index 20 sid fc00:0:3333::
        index 30 sid fc00:0:4444::

      segment-list xrd567
       srv6
        index 10 sid fc00:0:5555::
        index 20 sid fc00:0:6666::
     commit
   ```

5. On **xrd01** configure our bulk transport and low latency SRv6 steering policies. Low latency traffic will be forced over the *xrd01-05-06-07* path, and bulk transport traffic will take the longer *xrd01-02-03-04-07* path:
  
   **xrd01**
   ```yaml
   conf t
   segment-routing
   traffic-eng
     policy bulk-transfer
     srv6
       locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
     
     color 40 end-point ipv6 fc00:0:7777::1
     candidate-paths
       preference 100
       explicit segment-list xrd2347
      
     policy low-latency
     srv6
       locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
    
     color 50 end-point ipv6 fc00:0:7777::1
     candidate-paths
       preference 100
       explicit segment-list xrd567
     commit
   ```

6. Validate **xrd01's** SRv6-TE SID policy is enabled and up:
   ```
   show segment-routing srv6 sid
   show segment-routing traffic-eng policy
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24 
   ```
   
   Example output again now with TE policy applied on **xrd01**:

   
   Example output, note the additional uDT VRF carrots and SRv6-TE **uB6 Insert.Red** SIDs added to the list:
   ```yaml
   RP/0/RP0/CPU0:xrd01#  show segment-routing srv6 sid
   Sat Dec 16 02:45:31.772 UTC
 
   *** Locator: 'MyLocator' *** 

   SID                         Behavior          Context                           Owner               State  RW
   --------------------------  ----------------  --------------------------------  ------------------  -----  --
   fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
   fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
   fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
   fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
   fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
   fc00:0:1111:e004::          uDT6              'default'                         bgp-65000           InUse  Y 
   fc00:0:1111:e005::          uDT4              'default'                         bgp-65000           InUse  Y 
   fc00:0:1111:e006::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
   fc00:0:1111:e007::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
   fc00:0:1111:e008::          uDT4              'carrots'                         bgp-65000           InUse  Y 
   fc00:0:1111:e009::          uDT6              'carrots'                         bgp-65000           InUse  Y 
   ```
   
   ```diff
   RP/0/RP0/CPU0:xrd01#show segment-routing traffic-eng policy color 40
   SR-TE policy database
   ---------------------

   Color: 40, End-point: fc00:0:7777::1
     Name: srte_c_40_ep_fc00:0:7777::1
       Status:
   +      Admin: up  Operational: up for 00:09:43 (since Jan 23 17:37:50.369)
       Candidate-paths:
        Preference: 100 (configuration) (active)
         Name: bulk-transfer
         Requested BSID: dynamic
         Constraints:
           Protection Type: protected-preferred
           Maximum SID Depth: 25
   +     Explicit: segment-list xrd2347 (valid)
           Weight: 1, Metric Type: TE
             SID[0]: fc00:0:2222::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
             SID[1]: fc00:0:3333::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
             SID[2]: fc00:0:4444::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
         SRv6 Information:
           Locator: MyLocator
           Binding SID requested: Dynamic
           Binding SID behavior: uB6 (Insert.Red)
     Attributes:
       Binding SID: fc00:0:1111:e009::
       Forward Class: Not Configured
       Steering labeled-services disabled: no
       Steering BGP disabled: no
       IPv6 caps enable: yes
       Invalidation drop enabled: no
       Max Install Standby Candidate Paths: 0
       Path Type: SRV6
   ```
   
   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   Sat Jan  7 21:27:26.645 UTC
   BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
   Versions:
     Process           bRIB/RIB  SendTblVer
     Speaker                  58           58
   Last Modified: Jan  7 21:27:19.204 for 00:00:07
   Paths: (1 available, best #1)
     Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
         Received Label 0xe0040
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 30
   +     Extended community: Color:40 RT:9:9                      
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
   +     SR policy color 40, up, not-registered, bsid fc00:0:1111:e009::
   
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
           SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```
### Validate SRv6-TE steering of L3VPN traffic
### Validate bulk traffic takes the non-shortest path: **xrd01 -> 02 -> 03 -> 04 -> 07** 


1. Start a new SSH session to the XRD VM and run a tcpdump in the **xrd01's** outbound interface to **xrd02** (Gi0-0-0-1):
    ```
    sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-1
    ```

2. Lets now tie the SRv6 TE policy configured to what we expect to see in the tcpdump. What your looking for in the below output is the translation of the previously configured SRv6 TE policy below translated into the actual SRv6 packet header. So the TE bulk policy configured was:

   ```
      segment-list xrd2347
       srv6
        index 10 sid fc00:0:2222::
        index 20 sid fc00:0:3333::
        index 30 sid fc00:0:4444::
   ```
   And we expect to see in the packet header the follow tag order shown below in the tcpdump output:
   ```
   2222:3333:7777
   ```
> [!IMPORTANT]
> Notice that the above that the above SID stack the last hop xrd04 (4444). As mentioned in the lecture XR looks at the penultimate hop and does a calculation using the ISIS topology table and determines that **xrd03** best forwarding path to **xrd07** (7777) is through **xrd04**. Therefor for effiecency it drops the penultimate hop off the SID stack.

3. From an SSH session to the Amsterdam VM ping the bulk transport destination IPv4 and IPv6 addresses.
    ```
    ping 40.0.0.1 -i 1
    ```

   ```yaml
   cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-1
   tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
   listening on Gi0-0-0-1, link-type EN10MB (Ethernet), capture size 262144 bytes
   23:30:36.415073 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e006::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 1, seq 47, length 64
   23:30:36.815397 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e006::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 1, seq 48, length 64
   23:30:37.216952 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e006::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 1, seq 49, length 64
   ```

   Now lets try the IPv6 bulk transport destination
   ```
   ping fc00:0:40::1 -i 1
   ```
   ```yaml
   cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-1
   tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
   listening on Gi0-0-0-1, link-type EN10MB (Ethernet), capture size 262144 bytes
   13:04:46.481863 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:40::1: ICMP6, echo request, seq 2, length 64
   13:04:47.483568 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:40::1: ICMP6, echo request, seq 3, length 64
   13:04:48.484592 IP6 fc00:0:1111::1 > fc00:0:2222:3333:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:40::1: ICMP6, echo request, seq 4, length 64
   ```

4. Optional, run tcpdump on the outbound interfaces of xrd02, xrd03, and xrd04 to see SRv6 uSID shift-and-forward behavior:
    ```
    sudo ip netns exec clab-cleu25-xrd02 tcpdump -lni Gi0-0-0-1
    ```
    ```
    sudo ip netns exec clab-cleu25-xrd03 tcpdump -lni Gi0-0-0-1
    ```
    ```
    sudo ip netns exec clab-cleu25-xrd04 tcpdump -lni Gi0-0-0-1
    ```

    Example output from tcpdump on xrd02:
    ```yaml
    cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd02 tcpdump -lni Gi0-0-0-1
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on Gi0-0-0-1, link-type EN10MB (Ethernet), capture size 262144 bytes

    23:35:34.304332 IP6 fc00:0:1111::1 > fc00:0:3333:7777:e006::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 1, seq 790, length 64
    23:35:34.705547 IP6 fc00:0:1111::1 > fc00:0:3333:7777:e006::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 1, seq 791, length 64
    ```

#### Validate low latency traffic takes the path: xrd01 -> 05 -> 06 -> 07 
1.  Start a new tcpdump session on **xrd01's** outbound interface to **xrd05** (Gi0-0-0-2):
    ```
    sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-2
    ```

2.  Lets test and validate that our SRv6 TE policy is applied on **xrd01**. From **Amsterdam** we will ping to **Rome's** to the low latency destination using both the IPv4 and IPv6 addresses:
    ```
    ping 50.0.0.1 -i 1
    ```

    What your looking for in the below output is the translation of the previously configured SRv6 TE policy below translated into the actual SRv6 packet header. So the TE low latency policy configured was:

    ```
    segment-list xrd2347
       srv6
         index 10 sid fc00:0:5555::
         index 20 sid fc00:0:6666::
    ```

    Normally we might expect the tcpudmp output to show *5555:6666:7777* in the packet header, however, when the XRd headend router performs its SRv6-TE policy calculation it recognizes that **xrd05's** best path to **xrd07** is through **xrd06**, so it doesn't need to include the *6666* in the SID stack.

   
    ```yaml
    cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-2
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on Gi0-0-0-2, link-type EN10MB (Ethernet), capture size 262144 bytes
    23:45:51.894299 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e006::: IP 10.101.3.1 > 50.0.0.1: ICMP echo request, id 6, seq 629, length 64
    23:45:51.898852 IP6 fc00:0:7777::1 > fc00:0:1111:e009::: IP 50.0.0.1 > 10.101.3.1: ICMP echo reply, id 6, seq 629, length 64
    23:45:52.295091 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e006::: IP 10.101.3.1 > 50.0.0.1: ICMP echo request, id 6, seq 630, length 64
    23:45:52.298848 IP6 fc00:0:7777::1 > fc00:0:1111:e009::: IP 50.0.0.1 > 10.101.3.1: ICMP echo reply, id 6, seq 630, length 64
    23:45:52.695944 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e006::: IP 10.101.3.1 > 50.0.0.1: ICMP echo request, id 6, seq 631, length 64
    ```

    Now lets try the same ping test using the IPv6 address:
    
    ```
    ping fc00:0:50::1 -i 1
    ```

    ```yaml
    13:42:18.216436 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:50::1: ICMP6, echo request, seq 8, length 64
    13:42:18.617008 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:50::1: ICMP6, echo request, seq 9, length 64
    13:42:19.419534 IP6 fc00:0:1111::1 > fc00:0:5555:7777:e009::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:50::1: ICMP6, echo request, seq 11, length 64
    ```

3.  Optional, run tcpdump on the outbound interfaces of xrd05 and xrd06 to see SRv6 uSID shift-and-forward behavior:
    ```
    sudo ip netns exec clab-cleu25-xrd05 tcpdump -lni Gi0-0-0-1
    ```
    ```
    sudo ip netns exec clab-cleu25-xrd06 tcpdump -lni Gi0-0-0-1
    ```

### End of Lab 3
Please proceed to [Lab 4](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-guide.md)
