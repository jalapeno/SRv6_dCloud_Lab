import argparse
import subprocess
import re

# Handle cli options passed in
link_options = ['A','B','C','D','E','F','G','H','I']
parser = argparse.ArgumentParser(
    prog = 'Lab Latency Creater',
        description = 'Sets latency on a single link in the lab topology',
        epilog = 'set_latency.py -l <a..i> -ms <0 -300>')
parser.add_argument("-l", choices=link_options,required=True, help="link identifier values A through I")
parser.add_argument("-ms", type=int, required=True, help="latency on link in ms")  

args = parser.parse_args()
# Map link cli input to file descriptor and create file locator
file_dict={
    'A':'xrd01-xrd02',
    'B':'xrd01-xrd05',
    'C':'xrd02-xrd06',
    'D':'xrd05-xrd04',
    'E':'xrd02-xrd03',
    'F':'xrd03-xrd04',
    'G':'xrd05-xrd06',
    'H':'xrd04-xrd07',
    'I':'xrd06-xrd07'
}

file = '../../util/' + file_dict.get(args.l) 

# Open and read in the router link file
with open(file, 'r') as file:
    bridge_id = file.read().rstrip()
print (bridge_id)

# Run bridge control and find assocaiated interface to the bridge_id
# using the Popen function to execute the
# command and store the result in temp.
# it returns a tuple that contains the 
# data and the error if any.
result1 = subprocess.Popen(['brctl', 'show'], stdout = subprocess.PIPE)
result2 = subprocess.Popen(['grep', bridge_id],stdin=result1.stdout, stdout=subprocess.PIPE)
    
# we use the communicate function to fetch the output
a = str(result2.communicate())

# splitting the output so that
# we can parse them line by line
b = re.sub(r'\\t|\\n', ',', a)
c = b.split(",")
# search the list for veth interface
for i in c:
 if i[0:4] == "veth":
   interface = i

# Program the upated latency value for the Linux bridge
# Create tc option list
tc_options = "qdisc change dev "+interface +" root netem delay " + str(args.ms)
print (tc_options)
# program the bridge interface with new latench value
result = subprocess.Popen(['tc', tc_options)], stdout = subprocess.PIPE)
print (result)