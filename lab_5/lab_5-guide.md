# Lab 5: Install Jalapeno and enable BMP

### Description
In Lab 5 we will install the open-source Jalapeno data infrastructure platform. Jalapeno is designed to run on Kubernetes (k8s), which allows for easy integration into existing environments, and the ability to easily deploy on bare metal, VMs, or in a public cloud. Kubernetes experience is not required for Lab 5 as K8s has been preinstalled on the Jalapeno VM and we have included the required *kubectl* validation commands. 

After installing the Jalapeno package the student will then configure BGP Monitoring Protocol (BMP) on our route reflectors. Last we will add an SRv6 Locator to BGP default/global tables, which will be used in a later exercise where Amsterdam and Rome perform SRv6 encapsulation of their own outbound traffic.

## Contents
- [Lab 5: Install Jalapeno and enable BMP](#lab-5-install-jalapeno-and-enable-bmp)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Jalapeno Overview](#jalapeno-overview)
    - [Jalapeno Architecture and Data Flow](#jalapeno-architecture-and-data-flow)
  - [Validate Jalapeno](#validate-jalapeno)
  - [BGP Monitoring Protocol (BMP)](#bgp-monitoring-protocol-bmp)
  - [Configure a BGP SRv6 locator](#configure-a-bgp-srv6-locator)
  - [Install Jalapeno SR-Processors](#install-jalapeno-sr-processors)
      - [Return to the ssh session on the Jalapeno VM](#return-to-the-ssh-session-on-the-jalapeno-vm)
    - [End of Lab 5](#end-of-lab-5)

## Lab Objectives
The student upon completion of Lab 5 should have achieved the following objectives:

* High level understanding of the Jalapeno software stack
* Understanding and configuration of BMP
* Creation of SRv6 locator/function SIDs for BGP IPv4 and IPv6 global tables

## Jalapeno Overview
Project Jalapeno combines existing open source tools with some new stuff we've developed into a data collection and warehousing infrastructure intended to enable development of SDN or network service applications. Think of it as applying microservices architecture and concepts to SDN: give developers the ability to quickly and easily build microservice control planes on top of a common data infrastructure. More information on Jalapeno can be found at the Jalapeno Git repository: [LINK](https://github.com/cisco-open/jalapeno/blob/main/README.md)

### Jalapeno Architecture and Data Flow
![jalapeno_architecture](https://github.com/cisco-open/jalapeno/blob/main/docs/diagrams/jalapeno_architecture.png)

Jalapeno breaks the data collection and warehousing problem down into a series of components and services:
- Data collector services such as GoBMP and Telegraf collect network topology and statistics and publish to Kafka
- Data processor services such as "Topology" (and other future services) subscribe to Kafka topics and write the data they receive to databases
- Arango GraphDB is used for modeling topology data
- InfluxDB is used for warehousing statistical time-series data
- API-Gateway: is currently under construction so for the lab we'll interact directly with the DB
- Jalapeno's installation script will also deploy a Grafana container, which can be used to create dashboards to visualize the Influx time-series data (this is out of scope for CLEU 2023, but is on our roadmap for future labs)

One of the primary goals of the Jalapeno project is to be flexible and extensible. In the future we expect Jalapeno might support any number of data collectors and processors. For example the could be a collector/processor pair that creates an LLDP Topology model in the graphDB. Netflow data could be incorporated via a future integration with pmacct. Or an operator might already have a telemetry stack and could choose to selectively integrate Jalapeno's GoBMP/Topology/GraphDB modules into an existing environment running Kafka. We also envision future integrations with other API-driven data warehouses such as ThousandEyes: https://www.thousandeyes.com/

## Validate Jalapeno 

The Jalapeno package is preinstalled and running on the Jalapeno VM

1. Verify k8s pods are running (note, some pods may initially be in a *CrashLoopBackOff* state. These should resolve after 2-3 minutes). For those students new to Kubernetes you can reference this cheat sheet [HERE](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)  

    ```
    kubectl get pods -A
    ```
    Output should look something like:  

    ```
    cisco@jalapeno:~/jalapeno/install$ kubectl get pods -A
    NAMESPACE             NAME                                           READY   STATUS    RESTARTS        AGE
    jalapeno-collectors   gobmp-5db68bd644-hzs82                         1/1     Running   3 (4m5s ago)    4m25s  
    jalapeno-collectors   telegraf-ingress-deployment-5b456574dc-wdhjk   1/1     Running   1 (4m2s ago)    4m25s  
    jalapeno              arangodb-0                                     1/1     Running   0               4m33s
    jalapeno              grafana-deployment-565756bd74-x2szz            1/1     Running   0               4m32s
    jalapeno              influxdb-0                                     1/1     Running   0               4m32s
    jalapeno              kafka-0                                        1/1     Running   0               4m33s
    jalapeno              lslinknode-edge-b954577f9-k8w6l                1/1     Running   4 (3m35s ago)   4m18s
    jalapeno              telegraf-egress-deployment-5795ffdd9c-t8xrp    1/1     Running   2 (4m11s ago)   4m19s
    jalapeno              topology-678ddb8bb4-rt9jg                      1/1     Running   3 (4m1s ago)    4m19s
    jalapeno              zookeeper-0                                    1/1     Running   0               4m33s
    kube-system           calico-kube-controllers-798cc86c47-d482k       1/1     Running   4 (16m ago)     14d
    kube-system           calico-node-jd7cw                              1/1     Running   4 (16m ago)     14d
    kube-system           coredns-565d847f94-fr8pp                       1/1     Running   4 (16m ago)     14d
    kube-system           coredns-565d847f94-grmtl                       1/1     Running   4 (16m ago)     14d
    kube-system           etcd-jalapeno                                  1/1     Running   5 (16m ago)     14d
    kube-system           kube-apiserver-jalapeno                        1/1     Running   5 (16m ago)     14d
    kube-system           kube-controller-manager-jalapeno               1/1     Running   6 (16m ago)     14d
    kube-system           kube-proxy-pmwft                               1/1     Running   5 (16m ago)     14d
    kube-system           kube-scheduler-jalapeno                        1/1     Running   6 (16m ago)     14d
    ```

2. Here are some additional k8s commands to try. Note the different outputs when specifying a particular namespace (-n option) vs. all namespaces (-A option):
    ```
    kubectl get pods -n jalapeno                      <-------- display all pods/containers in the Jalapeno namespace
    kubectl get pods -n jalapeno-collectors           <-------- display all pods/containers in the Jalapeno-Collectors namespace
    kubectl get services -A                           <-------- display all externally reachable services (BMP, Arango, etc.)
    kubectl get all -A                                <-------- display a summary of all cluster info
    kubectl get nodes                                 <-------- display cluster node info
    kubectl describe pod -n <namespace> <pod name>    <-------- display detailed info about a pod

    example: kubectl describe pod -n jalapeno topology-678ddb8bb4-rt9jg
    ```

## BGP Monitoring Protocol (BMP)

Most transport SDN systems use BGP-LS to gather and model the underlying IGP topology. Jalapeno is intended to be a more generalized data platform to support use cases beyond internal transport such as VPNs or service chains. Because of this, Jalapeno's primary method of capturing topology data is via BMP. BMP provides all BGP AFI/SAFI info, thus Jalapeno is able to model many different kinds of topology, including the topology of the Internet (at least from the perspective of our peering routers).

We'll first establish a BMP session between our route-reflectors and the open-source GoBMP collector (https://github.com/sbezverk/gobmp), which comes pre-packaged with the Jalapeno install. We'll then enable BMP on the RRs' BGP peering sessions with our PE routers xrd01 and xrd07. Once established, the RRs' will stream all BGP NLRI info they receive from the PE routers to the GoBMP collector, which will in turn publish the data to Kafka. We'll get more into the Jalapeno data flow in Lab 6.

1. BMP configuration on xrd05 and xrd06:
    ```
    bmp server 1
      host 198.18.128.101 port 30511
      description jalapeno GoBMP  
      update-source MgmtEth0/RP0/CPU0/0
      flapping-delay 60
      initial-delay 5
      stats-reporting-period 60
      initial-refresh delay 25 spread 2
    
    router bgp 65000
      neighbor 10.0.0.1
        bmp-activate server 1
    
      neighbor fc00:0000:1111::1
        bmp-activate server 1

      neighbor 10.0.0.7
        bmp-activate server 1
    
      neighbor fc00:0000:7777::1
        bmp-activate server 1
    ```

2. Validate BMP session establishment and client monitoring (the session may take a couple minutes to become active/connected):
    ```
    show bgp bmp summary
    ```

    Expected output (truncated):  
    ```
    RP/0/RP0/CPU0:xrd05#show bgp bmp summary
    Fri Jan 20 21:50:08.460 UTC
    ID   Host                 Port     State   Time        NBRs
    1   198.18.128.101       30511    CONNECT 00:00:00    4
    RP/0/RP0/CPU0:xrd05# 

    ```

3. Validate Jalapeno has populated the Arango graphDB with BMP data. Open the Arango web UI at:

    ```
    http://198.18.128.101:30852/
    ```
    ```
    user: root
    password: jalapeno
    DB: jalapeno
    ```
    Once logged in choose the 'jalapeno' DB. The UI should then show you its 'collections' view, which should look something like:

  <img src="images/arango-collections.png" width="1000">

4. Feel free to spot check the various data collections in Arango. Several will be empty as they are for future use. With successful BMP processing we would expect to see data in all the following collections:

 - l3vpn_v4_prefix
 - l3vpn_v6_prefix
 - ls_link
 - ls_node
 - ls_node_edge
 - ls_prefix
 - ls_srv6_sid
 - peer
 - unicast_prefix_v4
 - unicast_prefix_v6

## Configure a BGP SRv6 locator
When we get to lab 7 we'll be sending SRv6 encapsulated traffic directly to/from Amsterdam and Rome. We'll need an SRv6 end.DT4/6 function at the egress nodes (xrd01 and xrd07) to be able to pop the SRv6 encap and perform a global table lookup on the underlying payload. Configuring an SRv6 locator under BGP will trigger creation of the end.DT4/6 functions:

1. Configure SRv6 locators for BGP on both xrd01 and xrd07:
    ```
    router bgp 65000
      address-family ipv4 unicast
        segment-routing srv6
        locator MyLocator
      
      address-family ipv6 unicast
        segment-routing srv6
        locator MyLocator
    ```

2. Validate end.DT4/6 SIDs belonging to BGP default table:
    ```
    show segment-routing srv6 sid
    ```

    Expected output on xrd01:  
    ```
    RP/0/RP0/CPU0:xrd01#sho segment-routing srv6 sid 
    Sun Jan 29 03:29:03.559 UTC

    *** Locator: 'MyLocator' *** 

    SID                         Behavior          Context                           Owner               State  RW
    --------------------------  ----------------  --------------------------------  ------------------  -----  --
    fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
    fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e004::          uDT4              'carrots'                         bgp-65000           InUse  Y 
    fc00:0:1111:e005::          uDT6              'carrots'                         bgp-65000           InUse  Y 
    fc00:0:1111:e006::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
    fc00:0:1111:e007::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
    fc00:0:1111:e008::          uDT4              'default'                         bgp-65000           InUse  Y 
    fc00:0:1111:e009::          uDT6              'default'                         bgp-65000           InUse  Y 
    ``` 
## Install Jalapeno SR-Processors
The SR-Processors are a pair of proof-of-concept data processors that mine Jalapeno's graphDB and create a pair of new data collections. The *`sr-node processor`* loops through various link-state data collections and gathers relevant SR/SRv6 data for each node in the network. The *`sr-topology`* processor generates a graph of the entire network topology (internal and external links, nodes, peers, prefixes, etc.) and populates relevant SR/SRv6 data within the graph collection.

The *`srv6-localsids`* processor harvests SRv6 SID data from a kafka streaming telemetry topic. This data is not available via BMP and is needed to construct full End.DT SIDs in lab 7.  Example:

```

SID                         Behavior          Context                           Owner              
----------------------  --------------  -----------------------------  ------------
fc00:0:1111::           uN (PSP/USD)    'default':4369                 sidmgr     <-------- Collected via BMP
fc00:0:1111:e000::      uA (PSP/USD)    [Gi0/0/0/1, Link-Local]:0:P    isis-100   <----|   
fc00:0:1111:e001::      uA (PSP/USD)    [Gi0/0/0/1, Link-Local]:0      isis-100        |  These are not available via BMP
fc00:0:1111:e002::      uA (PSP/USD)    [Gi0/0/0/2, Link-Local]:0:P    isis-100        |  We collect and process
fc00:0:1111:e003::      uA (PSP/USD)    [Gi0/0/0/2, Link-Local]:0      isis-100        |  these SIDs via streaming
fc00:0:1111:e004::      uDT4            'carrots'                      bgp-65000       |  telemetry and the 
fc00:0:1111:e005::      uDT6            'carrots'                      bgp-65000  <----|  "srv6-localsids" processor
```

#### Return to the ssh session on the Jalapeno VM

1. Install SR-Processors:
  The below command *`kubectl apply`* will input a yaml template file and launch the specified pods.

    ```
    cd ~/SRv6_dCloud_Lab/lab_5/sr-processors
    kubectl apply -f sr-node.yaml 
    kubectl apply -f sr-topology.yaml 
    kubectl apply -f srv6-localsids.yaml
    ```
2. Validate the pods are up and running in the 'jalapeno' namespace:
    ```
    kubectl get pods -n jalapeno
    ```
    #### Expected output:  
    Look for the new pods running in the jalapeno namespace
    ```
    cisco@jalapeno:~/sr-processors$ kubectl get pods -n jalapeno
    NAME                                          READY   STATUS    RESTARTS      AGE
    arangodb-0                                    1/1     Running   0             12m
    grafana-deployment-565756bd74-x2szz           1/1     Running   0             12m
    influxdb-0                                    1/1     Running   0             12m
    kafka-0                                       1/1     Running   0             12m
    lslinknode-edge-b954577f9-k8w6l               1/1     Running   4 (11m ago)   12m
    sr-node-8487488c9f-ftj59                      1/1     Running   0             48s     <--------
    sr-topology-6b45d48c8-h8zns                   1/1     Running   0             39s     <--------
    srv6-localsids-76ff4949d7-hx8mw               1/1     Running   0             33s     <--------
    telegraf-egress-deployment-5795ffdd9c-t8xrp   1/1     Running   2 (12m ago)   12m
    topology-678ddb8bb4-rt9jg                     1/1     Running   3 (11m ago)   12m
    zookeeper-0                                   1/1     Running   0             12m
    ```
3. Check ArangoDB for new *`sr_node`*, *`sr_topology`*, and *`srv6_local_sids`* data collections, and that they contain data. For example, *`sr_node`* should look something like this with seven entries:

  <img src="images/sr_node.png" width="1200">

### End of Lab 5
Please proceed to [Lab 6](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_6/lab_6-guide.md)