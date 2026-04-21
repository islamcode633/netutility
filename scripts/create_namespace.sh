#!/bin/bash

sudo ip addr add 10.10.10.2/24 dev eth3p1
sudo ip netns add myns
sudo ip link set dev eth3p2 netns myns
sudo ip netns exec myns sudo ip link set up lo
sudo ip netns exec myns sudo ip link set up eth3p2
sudo ip netns exec myns sudo ip addr flush dev eth3p2
sudo ip netns exec myns sudo ip addr add 10.10.10.3/24 dev eth3p2
