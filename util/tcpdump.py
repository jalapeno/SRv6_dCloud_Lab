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

with open(file,"r") as f:
    bridge = f.read()
    print("bridge: ", bridge)

r = subprocess.run(['sudo', 'tcpdump', '-ni', bridge], capture_output=True, text=True)

print(r.stdout)
with open('command.txt','w') as c:
    c.write(r.stdout)