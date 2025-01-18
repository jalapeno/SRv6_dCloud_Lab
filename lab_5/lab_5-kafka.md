## Exploring Kafka

From the Kafka homepage: Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.

Jalapeno uses Kafka as a message bus between its data collectors and data processors. Jalapeno's data collectors create Kafka topics then publish their datasets to those topics. The data processors subscribe to the relevant Kafka topics, gather the published data, and write it to either the Arango graphDB or Influx Time-Series DB. This Collector -> Kafka -> Processor -> DB pipeline allows for architectural flexibility and extensibility such that other applications could subscribe to the Jalapeno Kafka topics and use the BMP or telemetry data for their own purposes.

Kafka has a number of built in command line utilities to do things like listing topics or outputting of topic data to the screen, which we'll do in the next section of the lab.

For additional help on Kafka see this external CLI cheat sheet HERE

1. In a separate terminal session ssh to the Jalapeno VM 
    ```
    cisco@198.18.128.101
    pw = cisco123
    ```

2. Login to the Kafka container and cd into the bin directory. 
    ```
    kubectl exec -it kafka-0 -n jalapeno -- /bin/bash

    cd bin
    ls -la
    ```

3. The Jalapeno deployment of Kakfa includes enablement of JMX (Java Management Extensions), which allows for monitoring of Kafka elements such as brokers, topics, Zookeeper, etc. To operate the CLI utilies we'll need to unset the JMX_PORT:  
    ```
    unset JMX_PORT
    ```

4. Run the CLI utility to get a listing of all Kafka topics in our cluster:
    ```
    ./kafka-topics.sh --list  --bootstrap-server localhost:9092
    ```
    - A few seconds after running the *--list* command you should see the following list of topics toward the bottom on the command output. See truncated output below.

    ```
    gobmp.parsed.evpn
    gobmp.parsed.evpn_events
    gobmp.parsed.l3vpn
    gobmp.parsed.l3vpn_events
    gobmp.parsed.l3vpn_v4
    gobmp.parsed.l3vpn_v4_events
    gobmp.parsed.l3vpn_v6
    gobmp.parsed.l3vpn_v6_events
    gobmp.parsed.ls_link
    gobmp.parsed.ls_link_events
    gobmp.parsed.ls_node
    gobmp.parsed.ls_node_events
    gobmp.parsed.ls_prefix
    gobmp.parsed.ls_prefix_events
    gobmp.parsed.ls_srv6_sid
    gobmp.parsed.ls_srv6_sid_events
    gobmp.parsed.peer
    gobmp.parsed.peer_events
    gobmp.parsed.unicast_prefix
    gobmp.parsed.unicast_prefix_events
    gobmp.parsed.unicast_prefix_v4
    gobmp.parsed.unicast_prefix_v4_events
    gobmp.parsed.unicast_prefix_v6
    gobmp.parsed.unicast_prefix_v6_events
    jalapeno.ipv4_graph_events
    jalapeno.ipv6_graph_events
    jalapeno.linkstate_edge_v4_events
    jalapeno.linkstate_edge_v6_events
    jalapeno.ls_node_edge_events
    jalapeno.srv6
    jalapeno.telemetry
    ```

### Monitoring a Kafka topic

The *`kafka-console-consumer.sh`* utility allows one to manually monitor a given topic and see messages as they are published by the GoBMP collector. This gives us a nice troubleshooting tool for scenarios where a router may be sending data to the collector, but the data is not seen in the DB.

In the next set of steps we'll run the CLI to monitor a Kafka topic and watch for data from GoBMP. GoBMP's topics are fairly quiet unless BGP updates are happening, so once we have our monitoring session up we'll clear BGP-LS on the RR, which should result in a flood of data onto the topic.

In this exercise we are going to stitch together several elements that we have worked on throughout this lab. The routers in our lab have a number of topology-relevant configurations, including several that we've added over the course of labs 1 - 4. We will use the tools to examine how that data is communicated through the network and ultimately collected and populated into Jalapeno's DB.

#### ISIS Link State
   1. Monitor the BGP-LS *`ls_node`* Kafka topic for incoming BMP messages describing ISIS nodes in the network:

        ```
        ./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
        ```

        Optional - enable terminal monitoring and debugging the of BGP-LS address family on one of the route reflectors such as **xrd05**:
        ```
        terminal monitor
        debug bgp update afi link-state link-state in
        ```
        - Fair warning: this will output quite a bit of data when the AFI is cleared
        
   2. Connect to **xrd01** and clear the BGP-LS address family
        ```
        clear bgp link-state link-state * soft
        ```

        On the Kafka console we expect to see 14 json objects representing BMP messages when we perform a soft reset of the BGP session in **xrd01**. This will cause router **xrd01** to repopulate it's ISIS node data which is then mirrored to the BGP route reflectors. Below is one of the records received through BMP by Jalapeno and sent through the Kafka bus for **xrd01** own ISIS link state node record.

        ```json
        {
            "action": "add",
            "router_hash": "0669df0f031fb83e345267a9679bbc6a",
            "domain_id": 0,
            "router_ip": "10.0.0.5",       <---- Reporting router xrd05
            "peer_hash": "ef9f1cc86e4617df24d4675e2b55bbe2",
            "peer_ip": "10.0.0.1",         <---- Source router xrd01
            "peer_asn": 65000,
            "timestamp": "2023-01-13T20:20:51.000164765Z",
            "igp_router_id": "0000.0000.0001",  <-------- Link State Node ID
            "router_id": "10.0.0.1",         <---- Source router xrd01
            "asn": 65000,
            "mt_id_tlv": [
                {
                    "o_flag": false,
                    "a_flag": false,
                    "mt_id": 0
                },
                {
                    "o_flag": false,
                    "a_flag": false,
                    "mt_id": 2
                }
            ],
            "area_id": "49.0901",                <---- Area ID
            "protocol": "IS-IS Level 2",         <---- ISIS Level 2
            "protocol_id": 2,
            "name": "xrd01",
            "ls_sr_capabilities": {              <---- From here down SR xrd01 local attributes meta data
                "flags": {
                    "i_flag": true,
                    "v_flag": false
                },
                "sr_capability_subtlv": [
                    {
                        "range": 64000,
                        "sid": 100000
                    }
                ]
            },
            "sr_algorithm": [
                0,
                1
            ],
            "sr_local_block": {
                "flags": 0,
                "subranges": [
                    {
                        "range_size": 1000,
                        "label": 15000
                    }
                ]
            },
            "srv6_capabilities_tlv": {
                "o_flag": false
            },
            "node_msd": [
                {
                    "msd_type": 1,
                    "msd_value": 10
                }
            ],
            "is_prepolicy": false,
            "is_adj_rib_in": false
        }
        ```
#### SRv6 Locator SID    
   1. Now lets examine the SRv6 locator configuration on **xrd01** with the command: show run segment-routing srv6 locators 
        ```  
        show run segment-routing srv6 locators
        ```
        ```
        segment-routing
        srv6
        locators
            locator MyLocator
            micro-segment behavior unode psp-usd
            prefix fc00:0:1111::/48     <----- xrd01 SRv6 locator defined
        ```

   4. With **xrd01** SID locator identified lets see how that is communicated through the BMP from the route reflectors.
      Monitor the BGP-LS *`ls_srv6_sid`* topic for incoming BMP messages describing SRv6 SIDs in the network:  

      Use ctrl-z to kill the previous kafka console monitor then:
       ```
       ./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_srv6_sid
       ```

       Optional - enable terminal monitoring and debugging the of BGP-LS address family on one of the route reflectors such as **xrd05**:  

       ```
       terminal monitor
       debug bgp update afi vpnv6 unicast in
       ```
       *Fair warning: this will output quite a bit of data when the bgp is cleared*

   5. Again on **xrd01** clear the BGP-LS address family
       ```
       clear bgp link-state link-state * soft
       ```

       One the Kafka console we expect to see 14 json objects representing BMP messages coming from our 2 route reflectors and describing our 7 different ISIS nodes. Example messages:
       ```json
       {
           "action": "add",
           "router_hash": "0669df0f031fb83e345267a9679bbc6a",
           "router_ip": "10.0.0.5",   <---- Reporting router
           "domain_id": 0,
           "peer_hash": "ef9f1cc86e4617df24d4675e2b55bbe2",
           "peer_ip": "10.0.0.1",     <---- Source router
           "peer_asn": 65000,
           "timestamp": "2023-01-13T19:49:01.000764233Z",
           "igp_router_id": "0000.0000.0001",
           "local_node_asn": 65000,
           "protocol_id": 2,
           "protocol": "IS-IS Level 2",
           "nexthop": "10.0.0.1",
           "local_node_hash": "89cd5823cd2cb0cfc304a61117c89a45",
           "mt_id_tlv": {
               "o_flag": false,
               "a_flag": false,
               "mt_id": 2
           },
           "igp_flags": 0,
           "is_prepolicy": false,
           "is_adj_rib_in": false,
           "srv6_sid": "fc00:0:1111::",   <---- xrd01 loactor SID
           "srv6_endpoint_behavior": {
               "endpoint_behavior": 48,
               "flag": 0,
               "algo": 0
           },
           "srv6_sid_structure": {
               "locator_block_length": 32,
               "locator_node_length": 16,
               "function_length": 0,
               "argument_length": 80
           }
       }
       ```

## Back to Lab 5 Guide
[Lab 5 Guide](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_5/lab_5-guide.md)