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

cmd = ['sudo', 'tcpdump', '-ni', bridge, '&']
print(cmd)
subprocess.run(cmd, capture_output=True, text=True)

cmd2 = ['ls']
subprocess.run(cmd2)