from kafka import KafkaConsumer
from arango import ArangoClient
import json 
from json import loads
import sys

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
    
for i in range(1, 11):
    for message in consumer:
        consumer.commit() 
        message = message.value
        msgobj = json.dumps(message, indent=4)
        msg = msgobj.replace("/", "_" )
        
        print(msg)

        metadata = srv6_local_sids.insert(msg)



