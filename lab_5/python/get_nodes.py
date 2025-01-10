# get_nodes.py connects to the graphDB, runs a query for "sr nodes", 
# and writes the query response data to a file called 'nodes.json'

import json
from arango import ArangoClient
client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db('jalapeno', username='root', password='jalapeno')
if db.has_collection('igp_node'):
    sr = db.collection('igp_node')

if db.has_collection('peer'):
    pr = db.collection('peer')

if db.has_collection('ipv4_graph'):
    topo = db.collection('ipv4_graph')

sr.properties()
pr.properties()

aql = db.aql
cursor = db.aql.execute("for s in igp_node return \
    { key: s._key, name: s.name, router_id: s.router_id, \
        city: s.location_id, address: s.address, srv6_sid: s.srv6_sid }")
nodes = [doc for doc in cursor]
print("""
querying for srv6 nodes and writing to file 'nodes.json'
""")
nodesObj = json.dumps(nodes, indent=4)
with open("nodes.json", "w") as outfile:
    outfile.write(nodesObj)