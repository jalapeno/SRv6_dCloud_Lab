from arango import ArangoClient
import json

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)


db.delete_collection('igp_node')
db.delete_collection('bgp_node')
db.delete_collection('igp_domain')
db.delete_collection('ibgp_prefix_v4')
db.delete_collection('ibgp_prefix_v6')
db.delete_collection('ebgp_prefix_v4')
db.delete_collection('ebgp_prefix_v6')
db.delete_collection('inet_prefix_v4')
db.delete_collection('inet_prefix_v6')
db.delete_collection('srv6_local_sids')
db.delete_collection('igpv4_graph')
db.delete_collection('igpv6_graph')
db.delete_collection('ipv4_graph')
db.delete_collection('ipv6_graph')
db.delete_graph('ipv4_graph')
db.delete_graph('ipv6_graph')
db.delete_graph('igpv4_graph')
db.delete_graph('igpv6_graph')
db.delete_collection('hosts')

