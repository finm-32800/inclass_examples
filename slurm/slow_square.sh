#!/bin/bash
# The "work": a task that takes five seconds. It squares a number and says
# which machine it ran on.
#
#   bash slow_square.sh 4
N="$1"
sleep 5
echo "$(date +%T)  $(hostname)  ${N} squared is $((N * N))"
