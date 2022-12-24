import argparse
import subprocess

### tcpdump utility for docker network/bridge instances

parser = argparse.ArgumentParser(
    prog = 'tcpdump utility',
    description = 'runs tcpdump on an inteface found in a text file',
    epilog = 'tcpdump.py -f <filename> ')
parser.add_argument("-f", help="tcpdump -f <filename>", default="a string")
args = parser.parse_args()

file = args.f

f = open(file)

subprocess.call(['sudo', 'tcpdump', '-ni', f])