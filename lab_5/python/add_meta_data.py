# Script writes site and link meta data into the Arango graphDB
# python3 add_meta_data.py

from arango import ArangoClient

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('ls_node_extended'):
    lsn = db.collection('ls_node_extended')

if db.has_collection('peer'):
    pr = db.collection('peer')

if db.has_collection('ipv4_topology'):
    ipv4topo = db.collection('ipv4_topology')

lsn.properties()
ipv4topo.properties()

print("calculating prefix SIDs")

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
r03['location_id'] = 'IEV001'
r03['country_code'] = 'UKR'
r03['address'] = "O.Gonchara str, Kyiv,Ukraine"
lsn.update(r03)

r04 = lsn.get('2_0_0_0000.0000.0004')
r04['location_id'] = 'IST001'
r04['country_code'] = 'TUR'
r04['address'] = "Büyükdere Cd No:121Şişli, Turkey, 34394"
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

ipv4topo0105 = ipv4topo.get("2_0_0_0_0000.0000.0001_10.1.1.8_0000.0000.0005_10.1.1.9")
ipv4topo0105['latency'] = 5
ipv4topo0105['percent_util_out'] = 55
ipv4topo0105['country_codes'] = ['NLD', 'GBR']
ipv4topo.update(ipv4topo0105)

ipv4topo0203 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.2_0000.0000.0003_10.1.1.3")
ipv4topo0203['latency'] = 30
ipv4topo0203['percent_util_out'] = 25
ipv4topo0203['country_codes'] = ['DEU', 'POL', 'UKR']
ipv4topo.update(ipv4topo0203)

ipv4topo0206 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.10_0000.0000.0006_10.1.1.11")
ipv4topo0206['latency'] = 20
ipv4topo0206['percent_util_out'] = 40
ipv4topo0206['country_codes'] = ['DEU', 'POL', 'UKR']
ipv4topo.update(ipv4topo0206)

ipv4topo0304 = ipv4topo.get("2_0_0_0_0000.0000.0003_10.1.1.4_0000.0000.0004_10.1.1.5")
ipv4topo0304['latency'] = 40
ipv4topo0304['percent_util_out'] = 20
ipv4topo0304['country_codes'] = ['UKR', 'MDA', 'BGR', 'TUR']
ipv4topo.update(ipv4topo0304)

ipv4topo0504 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.12_0000.0000.0004_10.1.1.13")
ipv4topo0504['latency'] = 60
ipv4topo0504['percent_util_out'] = 25
ipv4topo0504['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'SRB', 'BGR', 'TUR']
ipv4topo.update(ipv4topo0504)

ipv4topo0407 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.6_0000.0000.0007_10.1.1.7")
ipv4topo0407['latency'] = 30
ipv4topo0407['percent_util_out'] = 20
ipv4topo0407['country_codes'] = ['TUR', 'GRC', 'ITA']
ipv4topo.update(ipv4topo0407)

ipv4topo0506 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.14_0000.0000.0006_10.1.1.15")
ipv4topo0506['latency'] = 5
ipv4topo0506['percent_util_out'] = 55
ipv4topo0506['country_codes'] = ['GBR', 'FRA']
ipv4topo.update(ipv4topo0506)

ipv4topo0607 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.16_0000.0000.0007_10.1.1.17")
ipv4topo0607['latency'] = 30
ipv4topo0607['percent_util_out'] = 35
ipv4topo0607['country_codes'] = ['FRA', 'ITA']
ipv4topo.update(ipv4topo0607)

# Return path

ipv4topo0201 = ipv4topo.get("2_0_0_0_0000.0000.0002_10.1.1.1_0000.0000.0001_10.1.1.0")
ipv4topo0201['latency'] = 10
ipv4topo0201['percent_util_out'] = 30
ipv4topo0201['country_codes'] = ['NLD', 'DEU']
ipv4topo.update(ipv4topo0201)

ipv4topo0501 = ipv4topo.get("2_0_0_0_0000.0000.0005_10.1.1.9_0000.0000.0001_10.1.1.8")
ipv4topo0501['latency'] = 5
ipv4topo0501['percent_util_out'] = 50
ipv4topo0501['country_codes'] = ['NLD', 'GBR']
ipv4topo.update(ipv4topo0501)

ipv4topo0302 = ipv4topo.get("2_0_0_0_0000.0000.0003_10.1.1.3_0000.0000.0002_10.1.1.2")
ipv4topo0302['latency'] = 30
ipv4topo0302['percent_util_out'] = 25
ipv4topo0302['country_codes'] = ['DEU', 'POL', 'UKR']
ipv4topo.update(ipv4topo0302)

ipv4topo0602 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.11_0000.0000.0002_10.1.1.10")
ipv4topo0602['latency'] = 20
ipv4topo0602['percent_util_out'] = 25
ipv4topo0602['country_codes'] = ['DEU', 'POL', 'UKR']
ipv4topo.update(ipv4topo0602)

ipv4topo0403 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.5_0000.0000.0003_10.1.1.4")
ipv4topo0403['latency'] = 40
ipv4topo0403['percent_util_out'] = 30
ipv4topo0403['country_codes'] = ['UKR', 'MDA', 'BGR', 'TUR']
ipv4topo.update(ipv4topo0403)

ipv4topo0405 = ipv4topo.get("2_0_0_0_0000.0000.0004_10.1.1.13_0000.0000.0005_10.1.1.12")
ipv4topo0405['latency'] = 60
ipv4topo0405['percent_util_out'] = 25
ipv4topo0405['country_codes'] = ['GBR', 'BEL', 'DEU', 'AUT', 'HUN', 'SRB', 'BGR', 'TUR']
ipv4topo.update(ipv4topo0405)

ipv4topo0704 = ipv4topo.get("2_0_0_0_0000.0000.0007_10.1.1.7_0000.0000.0004_10.1.1.6")
ipv4topo0704['latency'] = 30
ipv4topo0704['percent_util_out'] = 30
ipv4topo0704['country_codes'] = ['TUR', 'GRC', 'ITA']
ipv4topo.update(ipv4topo0704)

ipv4topo0605 = ipv4topo.get("2_0_0_0_0000.0000.0006_10.1.1.15_0000.0000.0005_10.1.1.14")
ipv4topo0605['latency'] = 5
ipv4topo0605['percent_util_out'] = 60
ipv4topo0605['country_codes'] = ['GBR', 'FRA']
ipv4topo.update(ipv4topo0605)

ipv4topo0706 = ipv4topo.get("2_0_0_0_0000.0000.0007_10.1.1.17_0000.0000.0006_10.1.1.16")
ipv4topo0706['latency'] = 30
ipv4topo0706['percent_util_out'] = 25
ipv4topo0706['country_codes'] = ['FRA', 'ITA']
ipv4topo.update(ipv4topo0706)

print("meta data added")