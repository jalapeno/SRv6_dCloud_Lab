from arango import ArangoClient

user = "username"
pw = "password"
dbname = "database"

client = ArangoClient(hosts='http://198.18.1.101:06852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('sr_node'):
    sr = db.collection('sr_node')

if db.has_collection('peer'):
    pr = db.collection('peer')

if db.has_collection('sr_topology'):
    srt = db.collection('sr_topology')

sr.properties()
srt.properties()

r01 = sr.get('2_0_0_0000.0000.0001')
src = (r01['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r01['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r01['prefix_sid'] = prefix_sid
r01['location_id'] = 'AMS001'
r01['address'] = "Frederiksplein 42, 1017 XN Amsterdam, Netherlands"
sr.update(r01)

r02 = sr.get('2_0_0_0000.0000.0002')
src = (r02['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r02['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r02['prefix_sid'] = prefix_sid
r02['location_id'] = 'BML001'
r02['address'] = "Albrechtstraße 110, 12103 Berlin, Germany"
sr.update(r02)

r03 = sr.get('2_0_0_0000.0000.0003')
src = (r03['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r03['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r03['prefix_sid'] = prefix_sid
r03['location_id'] = 'IEV001'
r03['address'] = "O.Gonchara str, Kyiv,Ukraine"
sr.update(r03)

r04 = sr.get('2_0_0_0000.0000.0004')
src = (r04['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r04['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r04['prefix_sid'] = prefix_sid
r04['location_id'] = 'IST001'
r04['address'] = "Büyükdere Cd No:121Şişli, Turkey, 34394"
sr.update(r04)

r05 = sr.get('2_0_0_0000.0000.0005')
src = (r05['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r05['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r05['prefix_sid'] = prefix_sid
r05['location_id'] = 'LHR001'
r05['address'] = "Second Floor, Trinity Ct, Trinity St, Peterborough PE1 1DA, United Kingdom"
sr.update(r05)

r06 = sr.get('2_0_0_0000.0000.0006')
src = (r06['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r06['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r06['prefix_sid'] = prefix_sid
r06['location_id'] = 'CDG001'
r06['address'] = "18 Rue la Boétie, 75008 Paris, France"
sr.update(r06)

r07 = sr.get('2_0_0_0000.0000.0007')
src = (r07['ls_sr_capabilities'])
srctlv = (src['sr_capability_subtlv'])
sid = [ sub['sid'] for sub in srctlv ]

pat = (r07['prefix_attr_tlvs'])
lps = (pat['ls_prefix_sid'])
idx = [ sub['prefix_sid'] for sub in lps ]

prefix_sid = sid[0] + idx[0]
print(prefix_sid)
r07['prefix_sid'] = prefix_sid
r07['location_id'] = 'FCO001'
r07['address'] = "Via dei Tizii, 2C, 00185 Roma Italy"
sr.update(r07)


srt2506 = srt.get("2_0_0_0_0000.0000.0025_10.1.2.10_0000.0000.0006_10.1.2.11")
srt2506['latency'] = 5
srt2506['percent_util_out'] = 40
srt2506['country_codes'] = ['GBR', 'NLD']
srt.update(srt2506)

srt2502 = srt.get("2_0_0_0_0000.0000.0025_10.1.2.8_0000.0000.0002_10.1.2.9")
srt2502['latency'] = 5
srt2502['percent_util_out'] = 06
srt2502['country_codes'] = ['GBR', 'FRA']
srt.update(srt2502)

srt2504 = srt.get("2_0_0_0_0000.0000.0025_10.1.2.20_0000.0000.0004_10.1.2.21")
srt2504['latency'] = 18
srt2504['percent_util_out'] = 60
srt2504['country_codes'] = ['GBR', 'FRA', 'CHE', 'ITA']
srt.update(srt2504)

srt0603 = srt.get("2_0_0_0_0000.0000.0006_10.1.2.6_0000.0000.0003_10.1.2.7")
srt0603['latency'] = 8
srt0603['percent_util_out'] = 06
srt0603['country_codes'] = ['NLD', 'DEU']
srt.update(srt0603)

srt0065 = srt.get("2_0_0_0_0000.0000.0003_10.1.2.18_0000.0000.0005_10.1.2.19")
srt0065['latency'] = 7
srt0065['percent_util_out'] = 06
srt0065['country_codes'] = ['DEU', 'CZE']
srt.update(srt0065)

srt0504 = srt.get("2_0_0_0_0000.0000.0005_10.1.2.17_0000.0000.0004_10.1.2.16")
srt0504['latency'] = 14
srt0504['percent_util_out'] = 15
srt0504['country_codes'] = ['CZE', 'AUT', 'ITA']
srt.update(srt0504)

srt2604 = srt.get("2_0_0_0_0000.0000.0026_10.1.2.12_0000.0000.0004_10.1.2.13")
srt2604['latency'] = 14
srt2604['percent_util_out'] = 25
srt2604['country_codes'] = ['FRA', 'CHE', 'ITA']
srt.update(srt2604)

srt2606 = srt.get("2_0_0_0_0000.0000.0026_10.1.2.5_0000.0000.0006_10.1.2.4")
srt2606['latency'] = 8
srt2606['percent_util_out'] = 35
srt2606['country_codes'] = ['FRA', 'BEL', 'NLD']
srt.update(srt2606)

srt2625 = srt.get("2_0_0_0_0000.0000.0026_10.1.2.9_0000.0000.0025_10.1.2.8")
srt2625['latency'] = 5
srt2625['percent_util_out'] = 40
srt2625['country_codes'] = ['FRA', 'GBR']
srt.update(srt2625)

srt0064 = srt.get("2_0_0_0_0000.0000.0003_10.1.2.14_0000.0000.0004_10.1.2.15")
srt0064['latency'] = 18
srt0064['percent_util_out'] = 35
srt0064['country_codes'] = ['DEU', 'AUT', 'CHE', 'ITA']
srt.update(srt0064)
  
srt0306 = srt.get("2_0_0_0_0000.0000.0003_10.1.2.7_0000.0000.0006_10.1.2.6")
srt0306['latency'] = 8
srt0306['percent_util_out'] = 06
srt0306['country_codes'] = ['DEU', 'NLD']
srt.update(srt0306)  

srt0425 = srt.get("2_0_0_0_0000.0000.0004_10.1.2.21_0000.0000.0025_10.1.2.20")
srt0425['latency'] = 18
srt0425['percent_util_out'] = 60
srt0425['country_codes'] = ['ITA', 'CHE', 'FRA', 'GBR']
srt.update(srt0425)

srt0426 = srt.get("2_0_0_0_0000.0000.0004_10.1.2.13_0000.0000.0026_10.1.2.12")
srt0426['latency'] = 14
srt0426['percent_util_out'] = 25
srt0426['country_codes'] = ['ITA', 'CHE', 'FRA']
srt.update(srt0426) 

srt0403 = srt.get("2_0_0_0_0000.0000.0004_10.1.2.15_0000.0000.0003_10.1.2.14")
srt0403['latency'] = 18
srt0403['percent_util_out'] = 35
srt0403['country_codes'] = ['ITA', 'CHE', 'AUT', 'DEU']
srt.update(srt0403) 

srt0405 = srt.get("2_0_0_0_0000.0000.0004_10.1.2.16_0000.0000.0005_10.1.2.17")
srt0405['latency'] = 14
srt0405['percent_util_out'] = 15
srt0405['country_codes'] = ['ITA', 'AUT', 'DEU', 'CZE']
srt.update(srt0405)

srt0503 = srt.get("2_0_0_0_0000.0000.0005_10.1.2.19_0000.0000.0003_10.1.2.18")
srt0503['latency'] = 7
srt0503['percent_util_out'] = 06
srt0503['country_codes'] = ['CZE', 'DEU']
srt.update(srt0503)

srt0625 = srt.get("2_0_0_0_0000.0000.0006_10.1.2.11_0000.0000.0025_10.1.2.10")
srt0625['latency'] = 5
srt0625['percent_util_out'] = 06
srt0625['country_codes'] = ['NLD', 'GBR']
srt.update(srt0625)

srt0626 = srt.get("2_0_0_0_0000.0000.0006_10.1.2.4_0000.0000.0026_10.1.2.5")
srt0626['latency'] = 8
srt0626['percent_util_out'] = 06
srt0626['country_codes'] = ['NLD', 'BEL', 'FRA']
srt.update(srt0626)

