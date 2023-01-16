#/bin/bash

brctl show | sed -n 's/.*br-18ba240d4f42//p' > veth-br.txt
N=11; grep -o ".\{$N\}$" <veth-br.txt > veth.txt

sudo tc qdisc add dev r71ge1 root netem delay 120000