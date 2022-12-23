import json
from arango import ArangoClient

### figure out prefix sid

dbname = "jalapeno"
user = "root"
pw = "jalapeno"

client = ArangoClient(hosts='http://198.18.1.101:30852')
db = client.db(dbname, username=user, password=pw)
cursor = db.aql.execute("""for l in ls_prefix filter l.prefix == "10.0.0.7" return l.prefix_attr_tlvs.ls_prefix_sid """)

lsprefix = [doc for doc in cursor]

q = [item[0] for item in lsprefix]
r = q[0]
print(r)  
print(r['prefix_sid'])   

#p = json.dumps(r, indent=4)
#print(p)

cursor = db.aql.execute("""for l in sr_node filter l._key == "2_0_0_0000.0000.0007" \
    return l.ls_sr_capabilities.sr_capability_subtlv[0].sid """)

sid = [doc for doc in cursor]
pfxsid = sid[0]
print(pfxsid)
print(type(pfxsid))
print(type(r))
ps = (pfxsid + r['prefix_sid'])
print(ps)