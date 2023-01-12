### Kafka Intro
From the Kafka homepage: Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.
https://kafka.apache.org/

Jalapeno uses Kafka as a message bus between its data collectors and data processors. Jalapeno's data collectors create Kafka topics then publish their datasets to those topics. Jalapeno's data processors subscribe to the relevant Kafka topics, gather the published data, and write it to either the graphDB or TSDB. This Collector -> Kafka -> Processor -> DB pipeline allows for architectural flexibility and extensibility such that other applications could subscribe to the Jalapeno Kafka topics and use the BMP or telemetry data for their own purposes.

Kafka has a number of built in command line utilities to do things like listing topics or outputting of topic data to the screen, which we'll do in the next section of the lab. Here's a nice blog post on Kafka's CLI as well:

https://medium.com/@TimvanBaarsen/apache-kafka-cli-commands-cheat-sheet-a6f06eac01b


#### Continue on the Jalapeno VM

1. Login to the Kafka container and cd into the bin directory
```
kubectl exec -it kafka-0 /bin/bash -n jalapeno

cd bin
ls -la
```

2. The Jalapeno deployment of Kakfa includes enablement of JMX (Java Management Extensions), which allows for monitoring of Kafka elements such as brokers, topics, Zookeeper, etc. To operate the CLI utilies we'll need to unset the JMX_PORT:  
```
unset JMX_PORT
```

3. Run the CLI utility to get a listing of all Kafka topics in our cluster:
```
./kafka-topics.sh --list  --bootstrap-server localhost:9092
```
 - A few seconds after running the --list command you should see the following list of topics toward the bottom on the command output:
```
gobmp.parsed.evpn
gobmp.parsed.evpn_events
gobmp.parsed.flowspec
gobmp.parsed.flowspec_events
gobmp.parsed.flowspec_v4
gobmp.parsed.flowspec_v4_events
gobmp.parsed.flowspec_v6
gobmp.parsed.flowspec_v6_events
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
gobmp.parsed.sr_policy
gobmp.parsed.sr_policy_events
gobmp.parsed.sr_policy_v4
gobmp.parsed.sr_policy_v4_events
gobmp.parsed.sr_policy_v6
gobmp.parsed.sr_policy_v6_events
gobmp.parsed.unicast_prefix
gobmp.parsed.unicast_prefix_events
gobmp.parsed.unicast_prefix_v4
gobmp.parsed.unicast_prefix_v4_events
gobmp.parsed.unicast_prefix_v6
gobmp.parsed.unicast_prefix_v6_events
jalapeno.ls_node_edge_events
jalapeno.telemetry
```

### Monitoring a Kafka topic

The kafka-console-consumer.sh utility allows one to manually monitor a given topic and see messages as they are published to Kafka by Jalapeno's GoBMP collector. This gives us a nice troubleshooting tool for scenarios where a router may be sending data to the collector, but the data is not seen in the DB.

In the next set of steps we'll run the CLI to monitor a Kafka topic and watch for data from the GoBMP collector. GoBMP's topics are fairly quiet unless BGP updates are happening. So, once we have our monitoring session up we'll clear bgp-ls on the RR, which should result in a flood of data onto the topic.

1. Monitor the BGP-LS "ls_node" topic for messages describing ISIS nodes in the network:

```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
```

2. Connect to xrd01 and clear the BGP-LS address family
```
clear bgp link-state link-state * soft
```

One the Kafka console we expect to see 14 json objects representing BMP messages coming from our 2 route reflectors and describing our 7 different ISIS nodes. Example:

<code>{"action":"add","router_hash":"0669df0f031fb83e345267a9679bbc6a","domain_id":0,"router_ip":"10.0.0.5","peer_hash":"ef9f1cc86e4617df24d4675e2b55bbe2","peer_ip":"10.0.0.1","peer_asn":65000,"timestamp":"2023-01-12T21:47:51.000349811Z","igp_router_id":"0000.0000.0004","router_id":"10.0.0.4","asn":65000,"mt_id_tlv":[{"o_flag":false,"a_flag":false,"mt_id":0},{"o_flag":false,"a_flag":false,"mt_id":2}],"area_id":"49.0901","protocol":"IS-IS Level 2","protocol_id":2,"name":"xrd04","ls_sr_capabilities":{"flags":{"i_flag":true,"v_flag":false},"sr_capability_subtlv":[{"range":64000,"sid":100000}]},"sr_algorithm":[0,1],"sr_local_block":{"flags":0,"subranges":[{"range_size":1000,"label":15000}]},"srv6_capabilities_tlv":{"o_flag":false},"node_msd":[{"msd_type":1,"msd_value":10}],"is_prepolicy":false,"is_adj_rib_in":false}


{"action":"add","router_hash":"9e3a5bee3d95ebf710f509bd2177324b","domain_id":0,"router_ip":"10.0.0.6","peer_hash":"ef9f1cc86e4617df24d4675e2b55bbe2","peer_ip":"10.0.0.1","peer_asn":65000,"timestamp":"2023-01-12T21:47:51.000350197Z","igp_router_id":"0000.0000.0004","router_id":"10.0.0.4","asn":65000,"mt_id_tlv":[{"o_flag":false,"a_flag":false,"mt_id":0},{"o_flag":false,"a_flag":false,"mt_id":2}],"area_id":"49.0901","protocol":"IS-IS Level 2","protocol_id":2,"name":"xrd04","ls_sr_capabilities":{"flags":{"i_flag":true,"v_flag":false},"sr_capability_subtlv":[{"range":64000,"sid":100000}]},"sr_algorithm":[0,1],"sr_local_block":{"flags":0,"subranges":[{"range_size":1000,"label":15000}]},"srv6_capabilities_tlv":{"o_flag":false},"node_msd":[{"msd_type":1,"msd_value":10}],"is_prepolicy":false,"is_adj_rib_in":false}
</code>


 - ISIS link, prefix, and SRv6 SID data is published to the ls_link, ls_prefix, and ls_srv6_sid topics respectively:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_link
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_prefix
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_srv6_sid
```
 - L3VPN prefix data is published to the l3vpn topics:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.l3vpn_v4
```
 - We won't be using streaming telemetry in this lab, however MDT is configured on the nodes in the lab and the Telegraf collector publishes the data to the jalapeno.telemetry topic:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic jalapeno.telemetry
```

3. The gobmp topics should be fairly quiet unless BGP updates are happening. Try clearing bgp-ls or bgp-vpnv4 on one of the RRs and see what data comes through when monitoring the Kafka topic.

```
clear bgp vpnv4 unicast * soft
clear bgp link-state link-state * soft
```

Example GoBMP message published to Kafka when monitoring the l3vpn_v4 topic and clearing bgp-vpnv4 on xrd05:
```
{"action":"add","router_hash":"0669df0f031fb83e345267a9679bbc6a","router_ip":"10.0.0.5","base_attrs":{"base_attr_hash":"b41cebdba45850cdb7f6994b4675fa4c","origin":"incomplete","local_pref":100,"is_atomic_agg":false,"ext_community_list":["rt=9:9"]},"peer_hash":"e0b24585a43db7cc196f5e42d48e8b5f","peer_ip":"fc00:0:1111::1","peer_asn":65000,"timestamp":"2023-01-08T04:22:14.000588527Z","prefix":"10.9.1.0","prefix_len":24,"is_ipv4":true,"nexthop":"fc00:0:1111::1","is_nexthop_ipv4":false,"labels":[14681088],"is_prepolicy":false,"is_adj_rib_in":false,"vpn_rd":"10.0.0.1:0","vpn_rd_type":1,"prefix_sid":{"srv6_l3_service":{"sub_tlvs":{"1":[{"sid":"fc00:0:1111::","endpoint_behavior":63,"sub_sub_tlvs":{"1":[{"locator_block_length":32,"locator_node_length":16,"function_length":16,"argument_length":0,"transposition_length":16,"transposition_offset":48}]}}]}}}}
```
