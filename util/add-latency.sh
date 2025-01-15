#!/bin/bash

sudo ip netns exec clab-cleu25-xrd01 tc qdisc add dev Gi0-0-0-1 root netem delay 10000
sudo ip netns exec clab-cleu25-xrd01 tc qdisc add dev Gi0-0-0-2 root netem delay 5000

sudo ip netns exec clab-cleu25-xrd02 tc qdisc add dev Gi0-0-0-1 root netem delay 30000
sudo ip netns exec clab-cleu25-xrd02 tc qdisc add dev Gi0-0-0-2 root netem delay 20000

sudo ip netns exec clab-cleu25-xrd03 tc qdisc add dev Gi0-0-0-1 root netem delay 40000

sudo ip netns exec clab-cleu25-xrd04 tc qdisc add dev Gi0-0-0-1 root netem delay 30000
sudo ip netns exec clab-cleu25-xrd04 tc qdisc add dev Gi0-0-0-2 root netem delay 30000

sudo ip netns exec clab-cleu25-xrd05 tc qdisc add dev Gi0-0-0-2 root netem delay 5000

sudo ip netns exec clab-cleu25-xrd06 tc qdisc add dev Gi0-0-0-0 root netem delay 30000

echo "Latency added to the links"

echo "xrd01: "
sudo ip netns exec clab-cleu25-xrd01 tc qdisc list | grep delay
echo "xrd02: "
sudo ip netns exec clab-cleu25-xrd02 tc qdisc list | grep delay
echo "xrd03: "
sudo ip netns exec clab-cleu25-xrd03 tc qdisc list | grep delay
echo "xrd04: "
sudo ip netns exec clab-cleu25-xrd04 tc qdisc list | grep delay
echo "xrd05: "
sudo ip netns exec clab-cleu25-xrd05 tc qdisc list | grep delay
echo "xrd06: "
sudo ip netns exec clab-cleu25-xrd06 tc qdisc list | grep delay
echo "xrd07: "
sudo ip netns exec clab-cleu25-xrd07 tc qdisc list | grep delay

