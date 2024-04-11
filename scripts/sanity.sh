#!/bin/bash

# Get the root directory of the Git repository
tot=$(git rev-parse --show-toplevel)

# Check if git rev-parse command was successful
if [ $? -ne 0 ]; then
    echo "Error: Must be run inside a Git repository"
    exit 1
fi

# TODO: Add more tests when ready

# Test 1: Just basic sanity run
# FIXME: Krittika actually doesn't dump traces to outdir
cd "${tot}";
mkdir -p ./outdir/sanity/;
python3 ./krittika/krittika-sim.py -c ./configs/krittika.cfg -t ./topologies/test.csv -o ./outdir/sanity/ -p ./partitions/temp_part.csv  > ./outdir/sanity/run.log;
