from kafka import KafkaConsumer
from arango import ArangoClient
import json 
from json import loads
import re

consumer = KafkaConsumer(
    'jalapeno.srv6',
     bootstrap_servers=['198.18.128.101:30092'],
     auto_offset_reset='latest',
     enable_auto_commit=False,
     group_id='jalapeno',
     max_poll_records=20,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('srv6_local_sids'):
    srv6_local_sids = db.collection('srv6_local_sids')
else:
    srv6_local_sids = db.create_collection('srv6_local_sids')
 
for message in consumer:
    consumer.commit() 
    message = message.value
    msgobj = json.dumps(message, indent=4)
    msg = msgobj.replace("/", "_" )
    msg = (re.sub("sid_context_key_u_dt4_u_dt_base_ctx_table_id", "table_id", msg))
    msg = (re.sub("sid_context_key_u_dt6_u_dt_base_ctx_table_id", "table_id", msg))
    msgdict = json.loads(msg)
    #print(msgdict['fields']['sid'])
    sid = msgdict['fields']['sid']
    name = msgdict['tags']['source']

    #print(name, sid)
    key = name + "_" + sid
    id = "srv6_local_sids/" + key
    msgdict['_key'] = key

    if db.has_document(id):
        print("document exists: ", id)
    else:
        metadata = srv6_local_sids.insert(msgdict)
    
        print("document added: ", msgdict['_key'])


