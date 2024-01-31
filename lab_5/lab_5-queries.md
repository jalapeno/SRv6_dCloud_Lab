#### Sample Basic Queries

Query all IGP links in the DB:
```
for x in ls_link return x
```
Query for all IPv4 IGP links:
```
for x in ls_link filter x.mt_id_tlv.mt_id !=2 return x
```
Query for all IPv4 IGP links and return specific k:v pairs:
```
for x in ls_link filter x.mt_id_tlv.mt_id !=2 return { key: x._key, router_id: x.router_id, 
    igp_id: x.igp_router_id, local_ip: x.local_link_ip, remote_ip: x.remote_link_ip }
```
Query for the IGP topology (should match the xrd router topology):
```
for x in ls_topology_v4 return x
```
```
for x in ls_topology_v6 return x
```
Query for the entire network topology (should match the xrd topology plus some spokes out to attached BGP networks):
```
for x in ipv4_topology return x
```
```
for x in ipv6_topology return x
```
Query the ls_node_extended dataset and return specific k:v pairs:
```
for x in ls_node_extended return { node: x.router_id, name: x.name, srv6sid: x.sids[*].srv6_sid }
```

#### Return to lab_5 guide and run the add_meta_data.py step. 
[add_meta_data](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_5/lab_5-guide.md#populating-the-db-with-external-data)
#### Then run this next set of queries
```
for x in ipv4_topology filter x.latency != null return { key: x._key, from: x._from, to: x._to, latency: x.latency, utilization: x.percent_util_out, country_codes: x.country_codes }
```

#### replaces shortest path query #3
```
for v, e in any shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' TO 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' ipv4_topology return  { key: v._key, node: v.name, location: v.location_id, address: v.address, sid: v.sids[*].srv6_sid, latency: e.latency }
```

#### replaces shortest path query #4
```
for v, e in any shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' TO 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' ipv4_topology return  { key: v._key, node: v.name, location: v.location_id, address: v.address, sid: v.sids[*].srv6_sid, latency: e.latency }
```

#### replace least utilized path queries:
```
for v, e, p in 1..6 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' ipv4_topology options {uniqueVertices: "path", bfs: true} filter v._id == 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' return distinct { path: p.vertices[*].name, sid: p.vertices[*].sids[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}

```
```
for v, e, p in 1..6 outbound 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' ipv4_topology options {uniqueVertices: "path", bfs: true} filter v._id == 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' return { path: p.vertices[*].name, sid: p.vertices[*].sids[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}

```

