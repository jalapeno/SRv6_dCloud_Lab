from arango import ArangoClient
from arango.exceptions import CollectionDeleteError, GraphDeleteError
import json

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

# Collections to delete
collections = [
    'igp_node', 'bgp_node', 'igp_domain', 'ibgp_prefix_v4', 'ibgp_prefix_v6',
    'ebgp_prefix_v4', 'ebgp_prefix_v6', 'inet_prefix_v4', 'inet_prefix_v6',
    'srv6_local_sids', 'igpv4_graph', 'igpv6_graph', 'ipv4_graph', 'ipv6_graph',
    'hosts'
]

# Graphs to delete
graphs = ['ipv4_graph', 'ipv6_graph', 'igpv4_graph', 'igpv6_graph']

# Delete collections
for collection in collections:
    try:
        db.delete_collection(collection)
    except CollectionDeleteError:
        print(f"Collection {collection} not found, skipping")

# Delete graphs
for graph in graphs:
    try:
        db.delete_graph(graph)
    except GraphDeleteError:
        print(f"Graph {graph} not found, skipping")

