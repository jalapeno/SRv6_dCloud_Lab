import json
from arango import ArangoClient
from math import ceil
from copy import copy

username = "username"
password = "password"
database = "database"
source = "source"
destination = "destination"

f = open("src_dst.json")
sd = json.load(f)

user = sd[username]
pw = sd[password]
dbname = sd[database]
src = sd[source]
dst = sd[destination]

client = ArangoClient(hosts='http://52.11.224.254:30852')
#client = ArangoClient(hosts='http://10.200.99.7:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('sr_topology'):
    srt = db.collection('sr_topology')

srt.properties()

# Get source node to begin graph traversal
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % src +  """ \
    && u.base_attrs.local_pref != Null return u.peer_ip """)
src_peer = [doc for doc in cursor]
print("src peer ip: ", src_peer)
pr = src_peer[0]
aql = db.aql
cursor = db.aql.execute("""for s in sr_node filter s.router_id == """  + '"%s"' % pr +  """ return s._id """)
src_node = [doc for doc in cursor]
print("source node: ", src_node)

# Get destination prefix ID in edge collection
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % dst +  """ \
        && u.base_attrs.local_pref == Null return { id: u._id, dest_peer: u.peer_ip } """)
dst_dict = [doc for doc in cursor]
print(dst_dict)

id = "id"
dest_peer = "dest_peer"
dest_id = [a_dict[id] for a_dict in dst_dict]

s = src_node[0]
d = dst_dict[0]
# print("src_node, dst_dict, dest_id", s, d, d[id])
# print("dest_peer", d[dest_peer])
# print("peer: ", pr)

aql = db.aql

cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % s +  """ \
    TO """ + '"%s"' % d[id] +  """ sr_topology \
            return  { node: v._key, sid: e.srv6_sid } """)
spf = [doc for doc in cursor]
print("spf: ", spf)

cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % s +  """ \
    TO """ + '"%s"' % d[id] +  """ sr_topology \
        OPTIONS {weightAttribute: 'latency' } \
            return  { node: v._key, name: v.name, sid: e.srv6_sid, latency: e.latency } """)
path = [doc for doc in cursor]
print("path: ", path)

# result = []
# for item in spf:
#     for item2 in path:
#         if item2['sid'] == None:
#             path.remove(item2)
#         if item['sid'] == item2['sid']:
#             if item2['sid'] == None:
#                 item2.remove(item2)
#             print("match: ", item2)
            # new_item = copy(item)
            # new_item['port'] = item2['if']
            # result.append(new_item)


hopcount = len(path)
print("hops: ", hopcount)
pq = ceil((hopcount/2)-1)
print(pq)
pq_node = (path[pq])
print("pqnode: ", pq_node)
sid = 'sid'
usid_block = 'fc00:0:'

sids = [a_dict[sid] for a_dict in path]
print(sids)

for sid in list(sids):
    if sid == None:
        sids.remove(sid)
print(sids)

usid = []
for s in sids:
    if s != None and usid_block in s:
        usid_list = s.split(usid_block)
        sid = usid_list[1]
        usid_int = sid.split(':')
        u = int(usid_int[0])
        usid.append(u)

ipv6_separator = ":"

sidlist = ""
for word in usid:
    sidlist += str(word) + ":"
#print(sidlist)

srv6_sid = usid_block + sidlist + ipv6_separator

if pr == d[dest_peer]:
    print(""" 
    Source and destination are reachable via the same router, no optimization available
    
    """)
else:
    pathdict = {
            'statusCode': 200,
            'source': src,
            'destination': dst,
            'sid': srv6_sid,
            'path': path
        }

    pathobj = json.dumps(pathdict, indent=4)
    print(pathobj)

