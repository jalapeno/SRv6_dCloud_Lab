import argparse
import json
from rome import least_util

parser = argparse.ArgumentParser(
    prog = 'Jalapeno client',
    description = 'takes command line input and calls path calculator functions',
    epilog = 'client.py -f <json file> -e <sr or srv6> -s <ll, lu, or ds>')
parser.add_argument("-e", help="encapsulation type <sr> <srv6>", default="a string")
parser.add_argument("-f", help="json file with src, dst, parameters", default="a string") 
parser.add_argument("-s", help="requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty)", default="a string")
args = parser.parse_args()

encap = args.e
file = args.f
service = args.s

username = "username"
password = "password"
database = "database"
source = "source"
destination = "destination"
country = "country"

f = open(file)
sd = json.load(f)

user = sd[username]
pw = sd[password]
dbname = sd[database]
src = sd[source]
dst = sd[destination]
cc = sd[country]

print(src, dst, dbname, user, pw, cc, encap)

if encap == "srv6":
    print("encap: ", encap)
    if service == "lu":
        srv6_lu = least_util.lu_calc(src, dst, user, pw, dbname)
    if service == "ll":
        srv6_ll = low_latency.ll_calc(src, dst, user, pw, dbname)  
    