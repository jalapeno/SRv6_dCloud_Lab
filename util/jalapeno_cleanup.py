from arango import ArangoClient
import json

user = "root"
pw = "jalapeno"
dbname = "system"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

db.delete_database(jalapeno)
