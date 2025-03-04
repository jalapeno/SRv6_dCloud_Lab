#!/bin/sh

sudo brctl addbr xrd01-amsterdam1
sudo brctl addbr xrd01-amsterdam2
sudo brctl addbr xrd02-berlin1

sudo clab deploy -t lab_1-topology.yml


