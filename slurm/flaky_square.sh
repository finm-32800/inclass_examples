#!/bin/bash
# Like slow_square.sh, but the task for the number 3 fails until a file named
# "fixed" exists in this folder. It stands in for the one month of data that
# has a bad row.
#
#   bash flaky_square.sh 3     # fails
#   touch fixed
#   bash flaky_square.sh 3     # works
N="$1"
sleep 5
if [ "${N}" = "3" ] && [ ! -e fixed ]; then
    echo "$(date +%T)  $(hostname)  task ${N} FAILED" >&2
    exit 1
fi
echo "$(date +%T)  $(hostname)  ${N} squared is $((N * N))"
