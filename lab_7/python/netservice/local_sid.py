import json
from arango import ArangoClient

# Query DB for least utilized path parameters and return srv6 and sr sid info
def localsid(user, pw, dbname, locator, usid_block):

    client = ArangoClient(hosts='http://198.18.128.101:30852')
    db = client.db(dbname, username=user, password=pw)

    ### From here we're going to get the end.dt localsid and add it to the uSID dest

    locv = locator.replace(usid_block, '')
    #print("locv: ", locv)
    locvar = "%" + locv
    #print(locvar)
    locvar1 = locvar.replace("::", ":")
    #print(locvar1)
    locvar2 = locvar1 + "%" 
    #print(locvar2)

    cursor = db.aql.execute("""for x in srv6_local_sids \
        filter x.fields.table_id == 3758096384 && x.fields.sid like """ + '"%s"' % locvar2 + """ return x.fields.sid """)
    localsidlist = [doc for doc in cursor]
    print("end.dt SID: ", localsidlist)
    localsid = localsidlist[0]
    enddt = localsid.replace(usid_block, '')
    #print(enddt)
    return(enddt)