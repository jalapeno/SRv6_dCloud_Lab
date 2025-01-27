#/bin/bash

result=$(bash -c 'sudo ip route del 10.101.2.0/24' 2>&1)

ip route
echo "Route cleanup complete"