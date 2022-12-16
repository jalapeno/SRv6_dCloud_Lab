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

srt0102 = srt.get("2_0_0_0_0000.0000.0001_10.1.1.0_0000.0000.0002_10.1.1.1")
srt0102['latency'] = 10
srt0102['percent_util_out'] = 30
srt0102['country_codes'] = ['NLD', 'DEU']
srt.update(srt0102)

srt0105 = srt.get("2_0_0_0_0000.0000.0001_10.1.1.8_0000.0000.0005_10.1.1.9")
srt0105['latency'] = 10
srt0105['percent_util_out'] = 40
srt0105['country_codes'] = ['NLD', 'GBR']
srt.update(srt0105)

srt0203 = srt.get("2_0_0_0_0000.0000.0002_10.1.1.2_0000.0000.0003_10.1.1.3")
srt0203['latency'] = 30
srt0203['percent_util_out'] = 25
srt0203['country_codes'] = ['DEU', 'POL', 'UKR']
srt.update(srt0203)

