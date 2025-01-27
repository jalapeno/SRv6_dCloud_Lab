# Script writes site and link meta data into the Arango graphDB
# requires https://pypi.org/project/python-arango/
# python3 add_meta_data.py

from arango import ArangoClient
import json

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('igp_node'):
    lsn = db.collection('igp_node')

if db.has_collection('peer'):
    pr = db.collection('peer')

if db.has_collection('ipv4_graph'):
    ipv4topo = db.collection('ipv4_graph')

if db.has_collection('ipv6_graph'):
    ipv6topo = db.collection('ipv6_graph')

lsn.properties()
ipv4topo.properties()

print("adding hosts, addresses, country codes, and synthetic latency data to the graph")

# get the ls_node DB key and populate the document with location and latency data
r01 = lsn.get('2_0_0_0000.0000.0001')
r01['location_id'] = 'AMS001'
r01['country_code'] = 'NLD'
r01['address'] = "Frederiksplein 42, 1017 XN Amsterdam, Netherlands"
lsn.update(r01)

r02 = lsn.get('2_0_0_0000.0000.0002')
r02['location_id'] = 'BML001'
r02['country_code'] = 'DEU'
r02['address'] = "Albrechtstraße 110, 12103 Berlin, Germany"
lsn.update(r02)

r03 = lsn.get('2_0_0_0000.0000.0003')
r03['location_id'] = 'WAR001'
r03['country_code'] = 'POL'
r03['address'] = "Alejo Jerozolimskie 65/79, Warsaw, Poland"
lsn.update(r03)

r04 = lsn.get('2_0_0_0000.0000.0004')
r04['location_id'] = 'BUC001'
r04['country_code'] = 'ROM'
r04['address'] = "Clădirea Feper, Bulevardul Dimitrie Pompeiu 8, Bucharest, Romania"
lsn.update(r04)

r05 = lsn.get('2_0_0_0000.0000.0005')
r05['location_id'] = 'LHR001'
r05['country_code'] = 'GBR'
r05['address'] = "Second Floor, Trinity Ct, Trinity St, Peterborough PE1 1DA, United Kingdom"
lsn.update(r05)

r06 = lsn.get('2_0_0_0000.0000.0006')
r06['location_id'] = 'CDG001'
r06['country_code'] = 'FRA'
r06['address'] = "18 Rue la Boétie, 75008 Paris, France"
lsn.update(r06)

r07 = lsn.get('2_0_0_0000.0000.0007')
r07['location_id'] = 'FCO001'
r07['country_code'] = 'ITA'
r07['address'] = "Via dei Tizii, 2C, 00185 Roma Italy"
lsn.update(r07)

# Outbound path (left to right on diagram)

print("adding location, country codes, latency, and link utilization data")

ipv4topo0102 = ipv4topo.get("2_0_0_0_0000.0000.0001_10.1.1.0_0000.0000.0002_10.1.1.1")
ipv4topo0102['latency'] = 10
ipv4topo0102['percent_util_out'] = 35
ipv4topo0102['country_codes'] = ['NLD', 'DEU']
ipv4topo.update(ipv4topo0102)

ipv6topo0102 = ipv6topo.get("2_0_2_0_0000.0000.0001_2001:1:1:1::_0000.0000.0002_2001:1:1:1::1")
ipv6topo0102['latency'] = 10
ipv6topo0102['percent_util_out'] = 35
ipv6topo0102['country_codes'] = ['NLD', 'DEU']
ipv6topo.update(ipv6topo0102)

ipv4topo0105 = ipv4topo.get("2_0_0_0_0000.0000.0001_10.1.1.8_0000.0000.0005_10.1.1.9")
ipv4topo0105['latency'] = 5
ipv4topo0105['percent_util_out'] = 55
ipv4topo0105['country_codes'] = ['NLD', 'GBR']
ipv4topo.update(ipv4topo0105)

ipv6topo0105 = ipv6topo.get("2_0_2_0_0000.0000.0001_2001:1:1:1::8_0000.0000.0005_2001:1:1:1::9")
ipv6topo0105['latency'] = 5
ipv6topo0105['percent_util_out'] = 55
ipv6topo0105['country_codes'] = ['NLD', 'GBR']
ipv6topo.update(ipv6topo0105)

ipv4topo0203 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.2_0000.0000.0003_10.1.1.3")
ipv4topo0203['latency'] = 30
ipv4topo0203['percent_util_out'] = 25
ipv4topo0203['country_codes'] = ['DEU', 'POL']
ipv4topo.update(ipv4topo0203)

ipv6topo0203 = ipv6topo.get("2_0_2_0_0000.0000.0002_2001:1:1:1::2_0000.0000.0003_2001:1:1:1::3")
ipv6topo0203['latency'] = 30
ipv6topo0203['percent_util_out'] = 25
ipv6topo0203['country_codes'] = ['DEU', 'POL']
ipv6topo.update(ipv6topo0203)

ipv4topo0206 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.10_0000.0000.0006_10.1.1.11")
ipv4topo0206['latency'] = 20
ipv4topo0206['percent_util_out'] = 40
ipv4topo0206['country_codes'] = ['DEU', 'FRA']
ipv4topo.update(ipv4topo0206)

ipv6topo0206 = ipv6topo.get("2_0_2_0_0000.0000.0002_2001:1:1:1::10_0000.0000.0006_2001:1:1:1::11")
ipv6topo0206['latency'] = 20
ipv6topo0206['percent_util_out'] = 40
ipv6topo0206['country_codes'] = ['DEU', 'FRA']
ipv6topo.update(ipv6topo0206)

ipv4topo0304 = ipv4topo.get("2_0_0_0_0000.0000.0003_10.1.1.4_0000.0000.0004_10.1.1.5")
ipv4topo0304['latency'] = 40
ipv4topo0304['percent_util_out'] = 20
ipv4topo0304['country_codes'] = ['POL', 'UKR', 'ROM']
ipv4topo.update(ipv4topo0304)

ipv6topo0304 = ipv6topo.get("2_0_2_0_0000.0000.0003_2001:1:1:1::4_0000.0000.0004_2001:1:1:1::5")
ipv6topo0304['latency'] = 40
ipv6topo0304['percent_util_out'] = 20
ipv6topo0304['country_codes'] = ['POL', 'UKR', 'ROM']
ipv6topo.update(ipv6topo0304)

ipv4topo0504 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.12_0000.0000.0004_10.1.1.13")
ipv4topo0504['latency'] = 60
ipv4topo0504['percent_util_out'] = 25
ipv4topo0504['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'ROM']
ipv4topo.update(ipv4topo0504)

ipv6topo0504 = ipv6topo.get("2_0_2_0_0000.0000.0005_2001:1:1:1::12_0000.0000.0004_2001:1:1:1::13")
ipv6topo0504['latency'] = 60
ipv6topo0504['percent_util_out'] = 25
ipv6topo0504['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'ROM']
ipv6topo.update(ipv6topo0504)

ipv4topo0407 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.6_0000.0000.0007_10.1.1.7")
ipv4topo0407['latency'] = 30
ipv4topo0407['percent_util_out'] = 20
ipv4topo0407['country_codes'] = ['ROM', 'SRB', 'BIH', 'HRV', 'ITA']
ipv4topo.update(ipv4topo0407)

ipv6topo0407 = ipv6topo.get("2_0_2_0_0000.0000.0004_2001:1:1:1::6_0000.0000.0007_2001:1:1:1::7")
ipv6topo0407['latency'] = 30
ipv6topo0407['percent_util_out'] = 20
ipv6topo0407['country_codes'] = ['ROM', 'SRB', 'BIH', 'HRV', 'ITA']
ipv6topo.update(ipv6topo0407)

ipv4topo0506 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.14_0000.0000.0006_10.1.1.15")
ipv4topo0506['latency'] = 5
ipv4topo0506['percent_util_out'] = 55
ipv4topo0506['country_codes'] = ['GBR', 'FRA']
ipv4topo.update(ipv4topo0506)

ipv6topo0506 = ipv6topo.get("2_0_2_0_0000.0000.0005_2001:1:1:1::14_0000.0000.0006_2001:1:1:1::15")
ipv6topo0506['latency'] = 5
ipv6topo0506['percent_util_out'] = 55
ipv6topo0506['country_codes'] = ['GBR', 'FRA']
ipv6topo.update(ipv6topo0506)

ipv4topo0607 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.16_0000.0000.0007_10.1.1.17")
ipv4topo0607['latency'] = 30
ipv4topo0607['percent_util_out'] = 35
ipv4topo0607['country_codes'] = ['FRA', 'ITA']
ipv4topo.update(ipv4topo0607)

ipv6topo0607 = ipv6topo.get("2_0_2_0_0000.0000.0006_2001:1:1:1::16_0000.0000.0007_2001:1:1:1::17")
ipv6topo0607['latency'] = 30
ipv6topo0607['percent_util_out'] = 35
ipv6topo0607['country_codes'] = ['FRA', 'ITA']
ipv6topo.update(ipv6topo0607)

# Return path

ipv4topo0201 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.1_0000.0000.0001_10.1.1.0")
ipv4topo0201['latency'] = 10
ipv4topo0201['percent_util_out'] = 30
ipv4topo0201['country_codes'] = ['NLD', 'DEU']
ipv4topo.update(ipv4topo0201)

ipv6topo0201 = ipv6topo.get("2_0_2_0_0000.0000.0002_2001:1:1:1::1_0000.0000.0001_2001:1:1:1::")
ipv6topo0201['latency'] = 10
ipv6topo0201['percent_util_out'] = 30
ipv6topo0201['country_codes'] = ['NLD', 'DEU']
ipv6topo.update(ipv6topo0201)

ipv4topo0501 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.9_0000.0000.0001_10.1.1.8")
ipv4topo0501['latency'] = 5
ipv4topo0501['percent_util_out'] = 50
ipv4topo0501['country_codes'] = ['NLD', 'GBR']
ipv4topo.update(ipv4topo0501)

ipv6topo0501 = ipv6topo.get("2_0_2_0_0000.0000.0005_2001:1:1:1::9_0000.0000.0001_2001:1:1:1::8")
ipv6topo0501['latency'] = 5
ipv6topo0501['percent_util_out'] = 50
ipv6topo0501['country_codes'] = ['NLD', 'GBR']
ipv6topo.update(ipv6topo0501)

ipv4topo0302 = ipv4topo.get("2_0_0_0_0000.0000.0003_10.1.1.3_0000.0000.0002_10.1.1.2")
ipv4topo0302['latency'] = 30
ipv4topo0302['percent_util_out'] = 25
ipv4topo0302['country_codes'] = ['DEU', 'POL']
ipv4topo.update(ipv4topo0302)

ipv6topo0302 = ipv6topo.get("2_0_2_0_0000.0000.0003_2001:1:1:1::3_0000.0000.0002_2001:1:1:1::2")
ipv6topo0302['latency'] = 30
ipv6topo0302['percent_util_out'] = 25
ipv6topo0302['country_codes'] = ['DEU', 'POL']
ipv6topo.update(ipv6topo0302)

ipv4topo0602 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.11_0000.0000.0002_10.1.1.10")
ipv4topo0602['latency'] = 20
ipv4topo0602['percent_util_out'] = 25
ipv4topo0602['country_codes'] = ['FRA', 'ITA']
ipv4topo.update(ipv4topo0602)

ipv6topo0602 = ipv6topo.get("2_0_2_0_0000.0000.0006_2001:1:1:1::11_0000.0000.0002_2001:1:1:1::10")
ipv6topo0602['latency'] = 20
ipv6topo0602['percent_util_out'] = 25
ipv6topo0602['country_codes'] = ['FRA', 'ITA']
ipv6topo.update(ipv6topo0602)

ipv4topo0403 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.5_0000.0000.0003_10.1.1.4")
ipv4topo0403['latency'] = 40
ipv4topo0403['percent_util_out'] = 30
ipv4topo0403['country_codes'] = ['POL', 'UKR', 'ROM']
ipv4topo.update(ipv4topo0403)

ipv6topo0403 = ipv6topo.get("2_0_2_0_0000.0000.0004_2001:1:1:1::5_0000.0000.0003_2001:1:1:1::4")
ipv6topo0403['latency'] = 40
ipv6topo0403['percent_util_out'] = 30
ipv6topo0403['country_codes'] = ['POL', 'UKR', 'ROM']
ipv6topo.update(ipv6topo0403)

ipv4topo0405 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.13_0000.0000.0005_10.1.1.12")
ipv4topo0405['latency'] = 60
ipv4topo0405['percent_util_out'] = 25
ipv4topo0405['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'ROM']
ipv4topo.update(ipv4topo0405)

ipv6topo0405 = ipv6topo.get("2_0_2_0_0000.0000.0004_2001:1:1:1::13_0000.0000.0005_2001:1:1:1::12")
ipv6topo0405['latency'] = 60
ipv6topo0405['percent_util_out'] = 25
ipv6topo0405['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'ROM']
ipv6topo.update(ipv6topo0405)

ipv4topo0704 = ipv4topo.get("2_0_0_0_0000.0000.0007_10.1.1.7_0000.0000.0004_10.1.1.6")
ipv4topo0704['latency'] = 30
ipv4topo0704['percent_util_out'] = 30
ipv4topo0704['country_codes'] = ['ROM', 'SRB', 'BIH', 'HRV', 'ITA']
ipv4topo.update(ipv4topo0704)

ipv6topo0704 = ipv6topo.get("2_0_2_0_0000.0000.0007_2001:1:1:1::7_0000.0000.0004_2001:1:1:1::6")
ipv6topo0704['latency'] = 30
ipv6topo0704['percent_util_out'] = 30
ipv6topo0704['country_codes'] = ['ROM', 'SRB', 'BIH', 'HRV', 'ITA']
ipv6topo.update(ipv6topo0704)

ipv4topo0605 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.15_0000.0000.0005_10.1.1.14")
ipv4topo0605['latency'] = 5
ipv4topo0605['percent_util_out'] = 60
ipv4topo0605['country_codes'] = ['GBR', 'FRA']
ipv4topo.update(ipv4topo0605)

ipv6topo0605 = ipv6topo.get("2_0_2_0_0000.0000.0006_2001:1:1:1::15_0000.0000.0005_2001:1:1:1::14")
ipv6topo0605['latency'] = 5
ipv6topo0605['percent_util_out'] = 60
ipv6topo0605['country_codes'] = ['GBR', 'FRA']
ipv6topo.update(ipv6topo0605)

ipv4topo0706 = ipv4topo.get("2_0_0_0_0000.0000.0007_10.1.1.17_0000.0000.0006_10.1.1.16")
ipv4topo0706['latency'] = 30
ipv4topo0706['percent_util_out'] = 25
ipv4topo0706['country_codes'] = ['FRA', 'ITA']
ipv4topo.update(ipv4topo0706)

ipv6topo0706 = ipv6topo.get("2_0_2_0_0000.0000.0007_2001:1:1:1::17_0000.0000.0006_2001:1:1:1::16")
ipv6topo0706['latency'] = 30
ipv6topo0706['percent_util_out'] = 25
ipv6topo0706['country_codes'] = ['FRA', 'ITA']
ipv6topo.update(ipv6topo0706)

print("meta data added")

try:
    # Read the hosts data from JSON file
    with open('hosts.json', 'r') as f:
        hosts_data = json.load(f)
    
    # Create hosts collection if it doesn't exist
    if not db.has_collection('hosts'):
        db.create_collection('hosts')
    
    hosts_collection = db.collection('hosts')
    
    # AQL query to insert/update hosts data
    aql = """
    FOR host in @hosts
        UPSERT { _key: host._key }
        INSERT host
        REPLACE host
        IN hosts
        RETURN NEW
    """
    
    # Execute AQL query
    db.aql.execute(aql, bind_vars={'hosts': hosts_data})
    print(f"Successfully inserted/updated {len(hosts_data)} hosts records")
except Exception as e:
    print(f"Error processing hosts data: {e}")

try:
    # Read the IPv4 edge data from JSON file
    with open('hosts-v4-edge.json', 'r') as f:  # Fixed string quotes
        edge_data = json.load(f)
    
    # Ensure ipv4_graph collection exists
    if not db.has_collection('ipv4_graph'):
        db.create_collection('ipv4_graph', edge=True)  # Note: edge=True for edge collection
    
    edge_collection = db.collection('ipv4_graph')
    
    # AQL query to insert/update edge data
    aql = """
    FOR edge in @edges
        UPSERT { _key: edge._key }
        INSERT edge
        REPLACE edge
        IN ipv4_graph
        RETURN NEW
    """
    
    # Execute AQL query
    db.aql.execute(aql, bind_vars={'edges': edge_data})
    print(f"Successfully inserted/updated {len(edge_data)} IPv4 edge records")
except Exception as e:
    print(f"Error processing IPv4 edge data: {e}")

try:
    # Read the IPv6 edge data from JSON file
    with open('hosts-v6-edge.json', 'r') as f:  # Fixed string quotes
        edge_data = json.load(f)
    
    # Ensure ipv6_graph collection exists
    if not db.has_collection('ipv6_graph'):
        db.create_collection('ipv6_graph', edge=True)  # Note: edge=True for edge collection
    
    edge_collection = db.collection('ipv6_graph')
    
    # AQL query to insert/update edge data
    aql = """
    FOR edge in @edges
        UPSERT { _key: edge._key }
        INSERT edge
        REPLACE edge
        IN ipv6_graph
        RETURN NEW
    """
    
    # Execute AQL query
    db.aql.execute(aql, bind_vars={'edges': edge_data})
    print(f"Successfully inserted/updated {len(edge_data)} IPv6 edge records")
except Exception as e:
    print(f"Error processing IPv6 edge data: {e}")
