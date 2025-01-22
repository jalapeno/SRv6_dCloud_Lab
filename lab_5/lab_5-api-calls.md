## Example API Calls

Basic shortest path calculation:
```
curl "http://localhost:8000/api/v1/graphs/ipv6_graph/shortest_path?source=hosts/amsterdam&destination=hosts/rome" | jq .
```

Shortest path calculation - lowest latency:
```
curl "http://localhost:8000/api/v1/graphs/ipv6_graph/shortest_path/latency?source=hosts/amsterdam&destination=hosts/rome" | jq .
```

Shortest path calculation - lowest utilization:
```
curl "http://localhost:8000/api/v1/graphs/ipv6_graph/shortest_path/utilization?source=hosts/amsterdam&destination=hosts/rome" | jq .
```

Shortest path calculation - lowest load:
```
curl "http://localhost:8000/api/v1/graphs/ipv6_graph/shortest_path/load?source=hosts/amsterdam&destination=hosts/rome" | jq .
```

Shortest path calculation - next best path:
```
curl "http://localhost:8000/api/v1/graphs/ipv6_graph/shortest_path/next-best-path?source=hosts/amsterdam&destination=hosts/rome&direction=outbound" | jq .
```
