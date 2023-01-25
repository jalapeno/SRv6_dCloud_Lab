# This program is used to set latency values in both the lab topology router links and update the values in AranagoDb
import argparse

# Handle cli options passed in
parser = argparse.ArgumentParser(
    prog = 'Lab Latency Creater',
        description = 'Sets latency on a single link in the lab topology',
        epilog = 'set_latency.py -l <a..i> -ms <0 -300>')
parser.add_argument("-l", help="link identifier values A through I")
parser.add_argument("-ms", help="latency on link in ms")  

args = parser.parse_args()

# Check that the required input arguments were passed in
#if not args.l or not args.ms:
#    print("Required input elements encapsulation type, input file, and/or service type were not entered")
#    print("set_latency.py -l <a..i> -ms <0 -300>")
#    exit()

file='../../util/xrd01-xrd02'

with open(file, 'r') as file:
    data = file.read().rstrip()
print (data)