import json
from arango import ArangoClient
client = ArangoClient(hosts='http://52.11.224.254:30852')
#client = ArangoClient(hosts='http://10.200.99.7:30852')
db = client.db('poblano', username='root', password='jalapeno')
if db.has_collection('sr_node'):
    sr = db.collection('sr_node')

if db.has_collection('peer'):
    pr = db.collection('peer')

if db.has_collection('sr_topology'):
    pr = db.collection('sr_topology')

sr.properties()
pr.properties()

aql = db.aql
cursor = db.aql.execute("for s in sr_node return \
    { key: s._key, name: s.name, router_id: s.router_id, \
        city: s.location_id, address: s.address, \
            prefix_sid: s.prefix_sid, srv6_sid: s.srv6_sid }")
nodes = [doc for doc in cursor]

nodesObj = json.dumps(nodes, indent=4)
with open("poblano_nodes.json", "w") as outfile:
    outfile.write(nodesObj)