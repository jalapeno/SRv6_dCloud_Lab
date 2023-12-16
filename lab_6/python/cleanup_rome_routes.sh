#/bin/bash

result=$(bash -c 'sudo ip route del 10.101.2.0/24' 2>&1)
result=$(bash -c 'sudo ip route add 10.101.2.0/24 via 10.107.1.2 dev ens192 ' 2>&1)

ip route
echo "Route cleanup complete"