from arango import ArangoClient
import json

# Connect to Arango
user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

# Create Arango collection if it doesn't already exist
if db.has_collection('srv6_local_sids'):
    srv6_local_sids = db.collection('srv6_local_sids')
else:
    srv6_local_sids = db.create_collection('srv6_local_sids')

# srv6 locator is the first entry in list of sid data
with open('test-data.json') as data_file:    
    test_data = json.load(data_file)    
loc = test_data[0]
locator = loc['SID']

# Arango query to correlate srv6 locator and router name
aql = db.aql
cursor = db.aql.execute("""for x in sr_node filter x.srv6_sid == """  + '"%s"' % locator +  """ \
    return x.name """)
node = [doc for doc in cursor]

# loop through data to create DB keys (router_name + sid_value) and upload documents to Arango
for d in test_data:
    sid = d['SID']
    d['_key'] = node[0] + "_" + sid
    metadata = srv6_local_sids.insert(d)

newdata = json.dumps(test_data, indent=4)
print(newdata)




