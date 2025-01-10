# Lab 4: Jalapeno and BMP [20 Min]

### Description
In Lab 4 we will install the open-source Jalapeno data infrastructure platform. Jalapeno is designed to run on Kubernetes (K8s), which allows for easy integration into existing environments and supports deployment on bare metal, VMs, or in a public cloud. Kubernetes experience is not required for this lab as K8s has been preinstalled on the Jalapeno VM and we have included the required *kubectl* validation commands. 

Prior to deploying Jalapeno we will configure BGP Monitoring Protocol (BMP) on our route reflectors. 

## Contents
- [Lab 4: Jalapeno and BMP \[20 Min\]](#lab-4-jalapeno-and-bmp-20-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Jalapeno Overview](#jalapeno-overview)
    - [Jalapeno Architecture and Data Flow](#jalapeno-architecture-and-data-flow)
  - [Validate Jalapeno](#validate-jalapeno)
  - [BGP Monitoring Protocol (BMP)](#bgp-monitoring-protocol-bmp)
  - [BGP SRv6 locator](#bgp-srv6-locator)
    - [End of Lab 4](#end-of-lab-4)

## Lab Objectives
The student upon completion of Lab 4 should have achieved the following objectives:

* High level understanding of the Jalapeno data collection and topology modeling stack
* Understanding and configuration of BMP

## Jalapeno Overview
Project Jalapeno combines existing open source tools with some new stuff we've developed into a data collection and warehousing infrastructure intended to enable development of network service applications. Think of it as applying microservices architecture and concepts to SDN: give developers the ability to quickly and easily build microservice control planes on top of a common data infrastructure. More information on Jalapeno can be found at the Jalapeno Git repository: [LINK](https://github.com/cisco-open/jalapeno/blob/main/README.md)

### Jalapeno Architecture and Data Flow
![jalapeno_architecture](https://github.com/cisco-open/jalapeno/blob/main/docs/img/jalapeno_architecture.png)

Jalapeno breaks the data collection and warehousing problem down into a series of components and services:
- **Data Collector** services such as GoBMP and Telegraf collect network topology and statistics and publish to Kafka
- **Data Processor** services such as "Topology" (and other future services) subscribe to Kafka topics and write the data they receive to databases
- **Kafka** is used as a message bus between Collectors and Processors
- **Arango GraphDB** is used for modeling topology data
- **InfluxDB** is used for warehousing statistical time-series data
- **Grafana**: is used for visualizing the Influx time-series data and supports user creation of custom dashboards
- **REST API**: is used as a communication layer between the Jalapeno UI and external applications or clients, and the Jalapeno GraphDB
- **Jalapeno UI**: is a web application that allows users to interact with the Jalapeno topology model and path calculation tools. Note: the UI is still under construction, so not all functionality is available yet.

One of the primary goals of the Jalapeno project is to be flexible and extensible. In the future we expect Jalapeno might support any number of data collectors and processors. For example the could be a collector/processor pair that creates an LLDP Topology model in the graphDB. Netflow data could be incorporated via a future integration with a tool like [pmacct](http://www.pmacct.net/). Or an operator might already have a telemetry stack and could choose to selectively integrate Jalapeno's GoBMP/Topology/GraphDB modules into an existing environment running Kafka. We also envision future integrations with other API-driven data warehouses such as Cisco ThousandEyes: https://www.thousandeyes.com/

## Validate Jalapeno 

The Jalapeno package is preinstalled and running on the **Jalapeno** VM

1. Verify k8s pods are running (note, some pods may initially be in a *CrashLoopBackOff* state. These should resolve after 2-3 minutes). For those students new to Kubernetes you can reference this cheat sheet [HERE](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)  

    - ssh to Jalapeno VM
    ```
    ssh cisco@198.18.128.101
    ```
    - verify k8s pods
    ```
    kubectl get pods -A
    ```
    Output should look something like:  

    ```
    NAMESPACE             NAME                                           READY   STATUS    RESTARTS        AGE
    jalapeno-collectors   gobmp-5db68bd644-8kbmw                         1/1     Running   1 (50s ago)     84s
    jalapeno-collectors   telegraf-ingress-deployment-5b456574dc-242f9   1/1     Running   0               84s
    jalapeno              arangodb-0                                     1/1     Running   0               92s
    jalapeno              grafana-deployment-565756bd74-nmp6g            1/1     Running   0               91s
    jalapeno              igp-graph-5f7fcd6f88-4tjjq                     1/1     Running   2 (52s ago)     78s
    jalapeno              influxdb-0                                     1/1     Running   0               92s
    jalapeno              ipv4-graph-7ccc46bc57-zld2p                    1/1     Running   2 (51s ago)     77s
    jalapeno              ipv6-graph-56db757fc9-v7tkm                    1/1     Running   2 (52s ago)     76s
    jalapeno              jalapeno-api-5d8469557-w4dcm                   1/1     Running   0               91s
    jalapeno              jalapeno-ui-54f8f95c5d-9vns7                   1/1     Running   0               90s
    jalapeno              kafka-0                                        1/1     Running   0               92s
    jalapeno              lslinknode-edge-b954577f9-jmkn4                1/1     Running   3 (56s ago)     78s
    jalapeno              srv6-localsids-78c644bc76-bplp9                1/1     Running   0               77s
    jalapeno              telegraf-egress-deployment-5795ffdd9c-8lpd4    1/1     Running   0               78s
    jalapeno              topology-678ddb8bb4-4kmq8                      1/1     Running   1 (46s ago)     79s
    jalapeno              zookeeper-0                                    1/1     Running   0               93s
    kube-system           cilium-k8fht                                   1/1     Running   3 (168m ago)    362d
    kube-system           cilium-operator-6f5db4f885-nmpwb               1/1     Running   3 (168m ago)    362d
    kube-system           coredns-565d847f94-nmt4n                       1/1     Running   0               167m
    kube-system           coredns-565d847f94-sg8fl                       1/1     Running   3 (168m ago)    362d
    kube-system           etcd-jalapeno                                  1/1     Running   19 (168m ago)   362d
    kube-system           kube-apiserver-jalapeno                        1/1     Running   3 (168m ago)    362d
    kube-system           kube-controller-manager-jalapeno               1/1     Running   3 (168m ago)    362d
    kube-system           kube-proxy-g8nbn                               1/1     Running   3 (168m ago)    362d
    kube-system           kube-scheduler-jalapeno                        1/1     Running   3 (168m ago)    362d
    ```

2. Display only the pods in the jalapeno namespace:
    ```
    kubectl get pods -n jalapeno
    ```
    Expected output:
    ```
    cisco@jalapeno:~$ kubectl get pods -n jalapeno
    NAME                                          READY   STATUS    RESTARTS      AGE
    arangodb-0                                    1/1     Running   0             39m  <-------- Arango GraphDB
    grafana-deployment-565756bd74-nmp6g           1/1     Running   0             39m  <-------- Grafana
    igp-graph-5f7fcd6f88-4tjjq                    1/1     Running   2 (38m ago)   39m  <-------- IGP Topology Processor
    influxdb-0                                    1/1     Running   0             39m  <-------- Influx Time-Series DB
    ipv4-graph-7ccc46bc57-zld2p                   1/1     Running   2 (38m ago)   38m  <-------- IPv4 Topology Processor
    ipv6-graph-56db757fc9-v7tkm                   1/1     Running   2 (38m ago)   38m  <-------- IPv6 Topology Processor
    jalapeno-api-5d8469557-w4dcm                  1/1     Running   0             39m  <-------- Jalapeno REST API
    jalapeno-ui-54f8f95c5d-9vns7                  1/1     Running   0             39m  <-------- Jalapeno UI
    kafka-0                                       1/1     Running   0             39m  <-------- Kafka
    lslinknode-edge-b954577f9-jmkn4               1/1     Running   3 (38m ago)   39m  <-------- LS Link & Node Processor
    srv6-localsids-78c644bc76-bplp9               1/1     Running   0             39m  <-------- SRv6 Localsids Processor
    telegraf-egress-deployment-5795ffdd9c-8lpd4   1/1     Running   0             39m  <-------- Telegraf Egress Collector  
    topology-678ddb8bb4-4kmq8                     1/1     Running   1 (38m ago)   39m  <-------- BMP Topology Processor
    zookeeper-0                                   1/1     Running   0             39m  <-------- Zookeeper
    ```

4. Optional: here are some additional k8s commands to try. Note the different outputs when specifying a particular namespace (-n option) vs. all namespaces (-A option):
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

Most transport SDN systems use BGP-LS to gather and model the underlying IGP topology. Jalapeno is intended to be a more generalized data platform to support development of all sorts of use cases such as VPNs or service chains. Because of this, Jalapeno's primary method of capturing topology data is via BMP. BMP provides all BGP AFI/SAFI info, thus Jalapeno is able to model many different kinds of topologies, including the topology of the Internet (at least from the perspective of our peering routers).

We'll first establish a BMP session between our route-reflectors and the open-source GoBMP collector, which comes pre-packaged with the Jalapeno install. We'll then enable BMP monitoring of the RRs' BGP peering sessions with our PE routers **xrd01** and **xrd07**. Once established, the RRs' will stream all BGP NLRI info they receive from the PE routers to the GoBMP collector, which will in turn publish the data to Kafka. We'll get more into the Jalapeno data flow in Lab 5.

Reference: the GoBMP Git Repository can be found [HERE](https://github.com/sbezverk/gobmp)

1. BMP configuration on **xrd05** and **xrd06**:
    ```
    conf t
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
    commit
    ```

2. Validate BMP session establishment and client monitoring (the session may take a couple minutes to become active/established):
    ```
    show bgp bmp summary
    ```

    Expected output:  
    ```
    RP/0/RP0/CPU0:xrd06#show bgp bmp sum
    Sat Dec 16 03:19:26.045 UTC
    ID   Host                 Port     State   Time        NBRs
    1   198.18.128.101       30511    ESTAB   00:00:07    4   
    RP/0/RP0/CPU0:xrd06#

    ```

3. Validate Jalapeno has populated the Arango graphDB with BMP data. Open the Arango web UI at:

    ```
    http://198.18.128.101:30852/
    ```
    - Login and select the "jalapeno" DB from the dropdown:
    ```
    user: root
    password: jalapeno
    DB: jalapeno
    ```
    Once logged the UI should then show you its 'collections' view, which should look something like:

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

5. Test the Jalapeno REST API:

   - From the ssh session on the Jalapeno VM or the XRD VM validate the Jalapeno REST API is running:
    ```
    curl http://198.18.128.101:30800/api/v1/collections
    curl http://198.18.128.101:30800/api/v1/collections/ls_node
    ```
    - We installed the jq tool to help with nicer JSON parsing.
    ```
    curl http://198.18.128.101:30800/api/v1/graphs/igpv4_graph/vertices/keys | jq .
    curl http://198.18.128.101:30800/api/v1/graphs/igpv4_graph/edges | jq .
    ```

   - The API also has auto-generated documentation at: http://198.18.128.101:30800/docs/

We'll test the Jalapeno UI a bit later in the lab.

## BGP SRv6 locator
In lab 1 we configured an SRv6 locator for the BGP global/default table. When we get to lab 6 we'll use these locators as we'll be sending SRv6 encapsulated traffic directly to/from Amsterdam and Rome. With our endpoints performing SRv6 encapsulation our BGP SRv6 locator will provide the end.DT4/6 function at the egress nodes **xrd01** and **xrd07** to be able to pop the SRv6 encap and perform a global table lookup on the underlying payload.

1. Optional: ssh to **xrd01** and re-validate end.DT4/6 SIDs belonging to BGP default table:
    ```
    ssh cisco@clab-cleu25-XR01
    show segment-routing srv6 sid
    ```

    Expected output on **xrd01** should look something like the below table with both a uDT4 and uDT6 SID in the 'default' context:  
    ```
    RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
    Sat Dec 16 03:25:40.943 UTC

    *** Locator: 'MyLocator' *** 

    SID                         Behavior          Context                           Owner               State  RW
    --------------------------  ----------------  --------------------------------  ------------------  -----  --
    fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
    fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e004::          uDT4              'default'                         bgp-65000           InUse  Y 
    fc00:0:1111:e006::          uDT6              'default'                         bgp-65000           InUse  Y
    fc00:0:1111:e005::          uDT4              'carrots'                         bgp-65000           InUse  Y 
    fc00:0:1111:e007::          uDT6              'carrots'                         bgp-65000           InUse  Y 
    fc00:0:1111:e008::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
    fc00:0:1111:e009::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
    RP/0/RP0/CPU0:xrd01#
    ``` 

  
  - The *`kubectl get pods -n jalapeno`* command will show you all the k8s containers that make up the Jalapeno application, including the *`srv6-localsids`* processor. This processor harvests SRv6 SID data from a Kafka streaming telemetry topic and populates it in the *`sr_local_sids`* collection. This data is not available via BMP and is needed to construct full End.DT SIDs that we'll use in lab 6. 
  
    Example:

    ```
    SID                         Behavior          Context                    Owner              
    ----------------------  --------------  -----------------------------  ------------
    fc00:0:1111::           uN (PSP/USD)    'default':4369                 sidmgr     <-------- Collected via BMP
    fc00:0:1111:e000::      uA (PSP/USD)    [Gi0/0/0/1, Link-Local]:0:P    isis-100    <---|   
    fc00:0:1111:e001::      uA (PSP/USD)    [Gi0/0/0/1, Link-Local]:0      isis-100    <---|  These are not available via BMP
    fc00:0:1111:e002::      uA (PSP/USD)    [Gi0/0/0/2, Link-Local]:0:P    isis-100    <---|  We collect and process
    fc00:0:1111:e003::      uA (PSP/USD)    [Gi0/0/0/2, Link-Local]:0      isis-100    <---|  these SIDs via streaming
    fc00:0:1111:e004::      uDT4            'carrots'                      bgp-65000   <---|  telemetry and the 
    fc00:0:1111:e005::      uDT6            'carrots'                      bgp-65000   <---|  "srv6-localsids" processor

    ```
  > [!NOTE]
  > The SRv6 SID streaming telemetry configuration on *`xrd07`*: [SRv6 SID mdt path](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_1/config/xrd07.cfg#L23)

### End of Lab 4
Please proceed to [Lab 5](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_5/lab_5-guide.md)
