### Exploring Jalapeno, Kafka, ArangoDB

#### Continue on the Jalapeno VM

Kafka:
1. List Kafka topics
2. Listen to Kafka topics
```
kubectl exec -it kafka-0 /bin/bash -n jalapeno

cd bin
unset JMX_PORT

./kafka-topics.sh --list  --bootstrap-server localhost:9092
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_link
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.l3vpn_v4

./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic jalapeno.telemetry

```

Switch to web browser and connect to Jalapeno's Arango GraphDB
```
http://198.18.1.101:30852/

user: root
password: jalapeno
DB: jalapeno

```
Explore data collections

Run DB Queries:
```
for l in ls_node return l
```
Note: after running a query comment it out before running the next query. 

Example:

<img src="arango-query.png" width="600">

More sample queries:
```
for l in ls_link return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return { key: l._key, router_id: l.router_id, igp_id: l.igp_router_id, local_ip: l.local_link_ip, remote_ip: l.remote_link_ip }

for l in ls_node_edge return l

for l in sr_topology return l

for l in sr_node return { node: l.router_id, name: l.name, prefix_sid: l.prefix_attr_tlvs.ls_prefix_sid, srv6sid: l.srv6_sid }
```

Return to the Jalapeno VM ssh session and add some synthetic meta data to the DB:
```
cd ~/SRv6_dCloud_Lab/lab_4/
python3 add_meta_data.py
```
Validate meta data with ArangoDB query:
```
for l in sr_topology return { key: l._key, from: l._from, to: l._to, latency: l.latency, utilization: l.percent_util_out, country_codes: l.country_codes }
```

Run the get_nodes.py script:
```
python3 get_nodes.py
cat nodes.json
```
Return to the ArangoDB browser UI and run a graph traversal:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0001' TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology return  { path: v.name, sid: e.srv6_sid, latency: e.latency }

Run it the opposite direction:

for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0007' TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology return  { path: v.name, sid: e.srv6_sid, latency: e.latency }

```
Note, this shortest path result is based purely on hop count.

The graphDB allows us to run a 'weighted traversal' based on any metric or other piece of meta data in the graph.
Graph traversal query for the lowest latency path:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0001' TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology OPTIONS {weightAttribute: 'latency' } return  { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }

Return path:

for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0007' TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology OPTIONS {weightAttribute: 'latency' } return  { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }

``
Backups, data replication, other bulk transfers may not need to take
Graph traversal query for the least utilized path:
```
FOR v, e, p IN 1..6 outbound 'sr_node/2_0_0_0000.0000.0001' sr_topology OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}

Return path:

FOR v, e, p IN 1..6 outbound 'sr_node/2_0_0_0000.0000.0007' sr_topology OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
The previous queries provided paths up to 6-hops in length, which gave several good results and one that didn't make a lot of sense. We can change the number of hops a query will consider, in this case dropping it to 5:

```
FOR v, e, p IN 1..5 outbound 'sr_node/2_0_0_0000.0000.0001' sr_topology OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```


